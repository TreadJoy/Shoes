from django import forms
from django.conf import settings
from django.contrib.admin.actions import delete_selected
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms.models import BaseInlineFormSet
from .models import (
    CompatibilityGroup,
    Part,
    PartType,
    PartVariant,
    PreorderBatch,
    PreorderBatchEvent,
    PreorderVariantAllocation,
    Product,
    ProductVariant,
    ProductVariantComponent,
)
from .services import (
    HERITAGE_COURT_COMPONENT_CODES,
    HERITAGE_COURT_V1,
    component_bom_issues,
    update_preorder_variant_capacity,
)


class PreorderBatchAdminForm(forms.ModelForm):
    change_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Required when changing an existing preorder batch.",
    )

    class Meta:
        model = PreorderBatch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["change_reason"].required = True


class PreorderVariantAllocationInline(admin.TabularInline):
    model = PreorderVariantAllocation
    extra = 0
    can_delete = False
    fields = (
        "variant",
        "capacity",
        "committed_quantity",
        "remaining_display",
    )
    readonly_fields = (
        "committed_quantity",
        "remaining_display",
    )
    autocomplete_fields = ("variant",)

    @admin.display(description="Remaining")
    def remaining_display(self, obj):
        return obj.remaining_quantity if obj.pk else "-"


class PreorderBatchEventInline(admin.TabularInline):
    model = PreorderBatchEvent
    extra = 0
    can_delete = False
    fields = (
        "event_type",
        "variant_allocation",
        "previous_status",
        "new_status",
        "previous_capacity",
        "new_capacity",
        "reason",
        "actor",
        "created_at",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

class ProductVariantComponentInline(admin.TabularInline):
    model = ProductVariantComponent
    extra = 0
    fields = (
        "part_type",
        "part_variant",
        "quantity",
    )
    autocomplete_fields = (
        "part_type",
        "part_variant",
    )

    def get_formset(self, request, obj=None, **kwargs):
        class ProtectedComponentFormSet(BaseInlineFormSet):
            def clean(self):
                super().clean()
                blocked = False
                for form in self.forms:
                    if (
                        not form.cleaned_data.get("DELETE")
                        or not form.instance.pk
                    ):
                        continue
                    variant = self.instance
                    if (
                        variant.is_active
                        and variant.product.component_standard == HERITAGE_COURT_V1
                    ):
                        form.add_error(
                            "part_type",
                            "Required Heritage Court component slots cannot be "
                            "removed while the variant is active.",
                        )
                        blocked = True
                if blocked:
                    raise ValidationError(
                        "Required Heritage Court component slots cannot be "
                        "removed while the variant is active."
                    )

        kwargs["formset"] = ProtectedComponentFormSet
        return super().get_formset(request, obj, **kwargs)


@admin.register(PartType)
class PartTypeAdmin(admin.ModelAdmin):
    actions = ("delete_selected_part_types",)
    list_display = (
        "code",
        "name",
        "display_order",
        "interchangeability_status",
        "is_active",
        "updated_at",
    )
    search_fields = (
        "code",
        "name",
        "description",
    )
    ordering = (
        "display_order",
        "code",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.code in HERITAGE_COURT_COMPONENT_CODES:
            return ("code", "display_order", "interchangeability_status")
        return super().get_readonly_fields(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.code in HERITAGE_COURT_COMPONENT_CODES:
            return False
        return super().has_delete_permission(request, obj)

    def get_deleted_objects(self, objs, request):
        objs = list(objs)
        result = super().get_deleted_objects(objs, request)
        if (
            super().has_delete_permission(request)
            and any(obj.code in HERITAGE_COURT_COMPONENT_CODES for obj in objs)
        ):
            deleted, model_count, perms_needed, protected = result
            perms_needed.discard(self.opts.verbose_name)
            return deleted, model_count, perms_needed, protected
        return result

    @admin.action(
        description="Delete selected part types",
        permissions=["delete"],
    )
    def delete_selected_part_types(self, request, queryset):
        try:
            with transaction.atomic():
                return delete_selected(self, request, queryset)
        except ValidationError as error:
            self.message_user(
                request,
                "Part type: " + " ".join(error.messages),
                level=messages.ERROR,
            )


class PartVariantInline(admin.TabularInline):
    model = PartVariant
    extra = 0
    fields = (
        "sku",
        "compatibility_group",
        "is_active",
    )
    autocomplete_fields = (
        "compatibility_group",
    )


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "part_type",
        "color_name",
        "material",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "part_type",
        "is_active",
        "color_name",
    )
    search_fields = (
        "code",
        "name",
        "description",
        "material",
    )
    list_select_related = (
        "part_type",
    )
    autocomplete_fields = (
        "part_type",
    )
    inlines = [
        PartVariantInline,
    ]


@admin.register(PartVariant)
class PartVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "part",
        "part_type_display",
        "compatibility_group",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "part__part_type",
        "compatibility_group",
        "is_active",
    )
    search_fields = (
        "sku",
        "part__code",
        "part__name",
        "compatibility_group__code",
    )
    list_select_related = (
        "part",
        "part__part_type",
        "compatibility_group",
    )
    autocomplete_fields = (
        "part",
        "compatibility_group",
    )

    @admin.display(
        description="Part type",
        ordering="part__part_type__name",
    )
    def part_type_display(self, obj):
        return obj.part.part_type.name

class ProductVariantInLine(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "sku",
        "size",
        "compatibility_group",
        "color",
        "stock_quantity",
        "selling_price",
        "compare_at_price",
        "is_active",
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "audience",
        "component_standard",
        "price",
        "sale_price",
        "total_stock_display",
        "preorder_status_display",
        "is_active",
        "is_featured",
    )
    list_filter = (
        "category",
        "audience",
        "component_standard",
        "is_active",
        "is_featured",
    )
    search_fields = (
        "name",
        "description",
        "slug",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }
    inlines = [ProductVariantInLine]

    @admin.display(description="Total Variant Stock")
    def total_stock_display(self, obj):
        return obj.total_stock()

    @admin.display(description="Preorder")
    def preorder_status_display(self, obj):
        batch = obj.preorder_batches.filter(
            status__in=[
                PreorderBatch.Status.OPEN,
                PreorderBatch.Status.PAUSED,
            ]
        ).first()
        return batch.get_status_display() if batch else "Stocked"

@admin.register(CompatibilityGroup)
class CompatibilityGroupAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "platform_code",
        "platform_version",
        "internal_size_code",
        "width_code",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "platform_code",
        "platform_version",
        "width_code",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
        "internal_size_code",
        "description",
    )
    ordering = (
        "platform_code",
        "platform_version",
        "internal_size_code",
        "width_code",
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "product",
        "component_bom_readiness",
        "size",
        "compatibility_group",
        "color",
        "stock_quantity",
        "selling_price",
        "compare_at_price",
        "is_active",
        "updated_at",
    )
    list_filter = (
        "is_active",
        "color",
        "product",
        "compatibility_group",
    )
    search_fields = (
        "sku",
        "product__name",
        "size",
        "color",
        "compatibility_group__code",
    )
    list_select_related = (
        "product",
        "compatibility_group",
    )
    inlines = [
        ProductVariantComponentInline,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            "components__part_type",
            "components__part_variant__part",
            "components__part_variant__compatibility_group",
        )

    @admin.display(description="Component BOM readiness")
    def component_bom_readiness(self, obj):
        if obj.product.component_standard != HERITAGE_COURT_V1:
            return "Not required"
        issues = component_bom_issues(
            obj,
            assignments=list(obj.components.all()),
        ).get("is_active", [])
        if not issues:
            return "Ready"
        return "Not ready: " + " ".join(issues)

@admin.register(ProductVariantComponent)
class ProductVariantComponentAdmin(admin.ModelAdmin):
    actions = ("delete_selected_components",)
    list_display = (
        "product_variant",
        "part_type",
        "part_variant",
        "quantity",
        "updated_at",
    )
    list_filter = (
        "part_type",
        "product_variant__compatibility_group",
    )
    search_fields = (
        "product_variant__sku",
        "product_variant__product__name",
        "part_variant__sku",
        "part_variant__part__code",
    )
    list_select_related = (
        "product_variant",
        "product_variant__product",
        "product_variant__compatibility_group",
        "part_type",
        "part_variant",
        "part_variant__part",
        "part_variant__compatibility_group",
    )
    autocomplete_fields = (
        "product_variant",
        "part_type",
        "part_variant",
    )

    def has_delete_permission(self, request, obj=None):
        if (
            obj is not None
            and obj.product_variant.is_active
            and obj.product_variant.product.component_standard == HERITAGE_COURT_V1
        ):
            return False
        return super().has_delete_permission(request, obj)

    def get_deleted_objects(self, objs, request):
        objs = list(objs)
        result = super().get_deleted_objects(objs, request)
        if (
            super().has_delete_permission(request)
            and any(
                obj.product_variant.is_active
                and obj.product_variant.product.component_standard
                == HERITAGE_COURT_V1
                for obj in objs
            )
        ):
            deleted, model_count, perms_needed, protected = result
            perms_needed.discard(self.opts.verbose_name)
            return deleted, model_count, perms_needed, protected
        return result

    @admin.action(
        description="Delete selected component assignments",
        permissions=["delete"],
    )
    def delete_selected_components(self, request, queryset):
        try:
            with transaction.atomic():
                return delete_selected(self, request, queryset)
        except ValidationError as error:
            messages_by_field = getattr(error, "message_dict", {})
            field_errors = messages_by_field.get("part_type", error.messages)
            self.message_user(
                request,
                "Part type: " + " ".join(field_errors),
                level=messages.ERROR,
            )


@admin.register(PreorderBatch)
class PreorderBatchAdmin(admin.ModelAdmin):
    form = PreorderBatchAdminForm
    list_display = (
        "code",
        "product",
        "status",
        "estimated_tender_start",
        "estimated_tender_end",
        "total_capacity",
        "committed_quantity",
        "remaining_display",
        "paid_shortfall_count",
    )
    list_filter = ("status", "estimated_tender_start")
    search_fields = ("code", "product__name", "product__slug")
    list_select_related = ("product",)
    inlines = (
        PreorderVariantAllocationInline,
        PreorderBatchEventInline,
    )
    readonly_fields = (
        "committed_quantity",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Remaining")
    def remaining_display(self, obj):
        return obj.remaining_quantity

    @admin.display(description="Paid shortfalls")
    def paid_shortfall_count(self, obj):
        if not settings.IS_COMMERCE_MODE:
            return 0
        from web.orders.models import InventoryAllocation

        return InventoryAllocation.objects.filter(
            order__preorder_batch=obj,
            status__in=[
                InventoryAllocation.Status.REVIEW_REQUIRED,
                InventoryAllocation.Status.REFUND_PENDING,
                InventoryAllocation.Status.REFUNDED,
            ],
        ).count()

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            fields.extend(["code", "product"])
        if obj is not None and obj.has_confirmed_payments:
            fields.extend([
                "estimated_tender_start",
                "estimated_tender_end",
            ])
        return tuple(fields)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        reason = (form.cleaned_data.get("change_reason") or "").strip()
        request._preorder_change_reason = reason

        if not change:
            super().save_model(request, obj, form, change)
            PreorderBatchEvent.objects.create(
                batch=obj,
                event_type=PreorderBatchEvent.EventType.CREATED,
                reason="Preorder batch created.",
                actor=request.user,
            )
            return

        previous = PreorderBatch.objects.select_for_update().get(pk=obj.pk)
        previous_status = previous.status
        previous_capacity = previous.total_capacity
        super().save_model(request, obj, form, change)

        if obj.status != previous_status:
            PreorderBatchEvent.objects.create(
                batch=obj,
                event_type=PreorderBatchEvent.EventType.STATUS_CHANGED,
                previous_status=previous_status,
                new_status=obj.status,
                reason=reason,
                actor=request.user,
            )
        if obj.total_capacity != previous_capacity:
            PreorderBatchEvent.objects.create(
                batch=obj,
                event_type=PreorderBatchEvent.EventType.BATCH_CAPACITY_CHANGED,
                previous_capacity=previous_capacity,
                new_capacity=obj.total_capacity,
                reason=reason,
                actor=request.user,
            )

    @transaction.atomic
    def save_formset(self, request, form, formset, change):
        if formset.model is not PreorderVariantAllocation:
            return super().save_formset(request, form, formset, change)

        instances = formset.save(commit=False)
        reason = getattr(request, "_preorder_change_reason", "")

        for instance in instances:
            matching_form = next(
                item_form
                for item_form in formset.forms
                if item_form.instance is instance
            )
            if instance.pk and "capacity" in matching_form.changed_data:
                update_preorder_variant_capacity(
                    instance,
                    new_capacity=instance.capacity,
                    actor=request.user,
                    reason=reason,
                )
            else:
                instance.save()

        formset.save_m2m()
        form.instance.full_clean()

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PreorderVariantAllocation)
class PreorderVariantAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "batch",
        "variant",
        "capacity",
        "committed_quantity",
        "remaining_display",
    )
    list_filter = ("batch__status", "batch")
    search_fields = ("batch__code", "variant__sku", "variant__product__name")
    list_select_related = ("batch", "variant", "variant__product")
    readonly_fields = ("committed_quantity", "created_at", "updated_at")

    @admin.display(description="Remaining")
    def remaining_display(self, obj):
        return obj.remaining_quantity

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            fields.extend(["batch", "variant", "capacity"])
        return tuple(fields)

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PreorderBatchEvent)
class PreorderBatchEventAdmin(admin.ModelAdmin):
    list_display = (
        "batch",
        "event_type",
        "variant_allocation",
        "actor",
        "created_at",
    )
    list_filter = ("event_type", "created_at")
    search_fields = ("batch__code", "reason", "actor__username")
    readonly_fields = (
        "batch",
        "variant_allocation",
        "event_type",
        "previous_status",
        "new_status",
        "previous_capacity",
        "new_capacity",
        "reason",
        "actor",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
