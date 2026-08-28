from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError


class Product(models.Model):

    AUDIENCE_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
        ("unisex", "Unisex"),
    ]

    CATEGORY_CHOICES = [
        ("shoes", "Shoes"),
        ("socks", "Socks"),
        ("hats", "Hats"),
        ("accessories", "Accessories"),
    ]

    name = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        unique=True
    )
    description = models.TextField(
        blank=True
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    sale_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default="unisex"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="shoes"
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True
    )
    is_featured = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="product_price_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(sale_price__isnull=True)
                    | models.Q(sale_price__gte=0)
                ),
                name="product_sale_price_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(sale_price__isnull=True)
                    | models.Q(sale_price__lte=models.F("price"))
                ),
                name="product_sale_price_not_above_price",
            ),
        ]

    def current_price(self):
        if self.sale_price is not None:
            return self.sale_price

        return self.price

    def total_stock(self):
        result = self.variants.filter(
            is_active=True,
        ).aggregate(
            total=models.Sum("stock_quantity")
        )
        return result["total"] or 0

    def __str__(self):
        return self.name

class CompatibilityGroup(models.Model):
    """
    Defines one physical interchangability standard.

    Product variants and modular parts assigned to the same group
    are mechanically compatible.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        db_comment=(
            "Stable business identifier for the compatibility group. "
            "Example: TJ-CORE-V1_S090-STD"
        ),
    )
    name = models.CharField(
        max_length=100,
        db_comment=(
            "Human-readable name for admins. "
        ),
    )

    platform_code = models.CharField(
        max_length=30,
        default="TJ-CORE",
        db_comment=(
            "Modular platform or mechanical interface family. "
        ),
    )
    platform_version = models.PositiveSmallIntegerField(
        default=1,
        db_comment=(
            "Version of the modular attachment interface. "
        ),
    )
    internal_size_code = models.CharField(
        max_length=20,
        db_comment=(
            "Internal physical size identifier, independant of "
            "customer-facing size labels. "
        ),
    )
    width_code = models.CharField(
        max_length=20,
        db_comment=(
            "Physical width of the attachment, used for compatibility "
        ),
    )
    description = models.TextField(
        blank=True,
        db_comment=(
            "Explanation of what product and parts belong to this group."
        ),
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "platform_code",
            "platform_version",
            "internal_size_code",
            "width_code",
        ]
        db_table_comment = (
            "Defines physical interchangability groups for modular "
            "TreadJoy shoes and detachable parts."
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "platform_code",
                    "platform_version",
                    "internal_size_code",
                    "width_code",
                ],
                name="unique_modular_compatibility_group",
            ),
        ]

    def __str__(self):
        return self.code

class PartType(models.Model):
    """
    Controlled list of modular component categories.

    Examples: tongue, logo, sole, outer shell, back panel, and laces.
    """
    code = models.CharField(
        max_length=30,
        unique=True,
        db_comment="Unique identifier for the part type.",
    )
    name = models.CharField(
        max_length=50,
        db_comment="Human-readable name for admins.",
    )
    description = models.TextField(
        blank=True,
        db_comment="Explanation of what the part is and where it fits in the shoe.",
    )
    display_order = models.PositiveSmallIntegerField(
        default=0,
        db_comment="Order in which to display the part type in the admin UI.",
    )
    is_active = models.BooleanField(
        default=True,
        db_comment="Whether the part type is available for selection.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    class Meta:
        ordering = [
            "display_order",
            "code",
        ]
        db_table_comment = "Controlled lookup table of modular component categories."

    def __str__(self):
        return self.name

class Part(models.Model):
    """
    A modular component design independent of shoe size.

    Example: a particular white mesh tongue design.
    """

    part_type = models.ForeignKey(
        PartType,
        on_delete=models.PROTECT,
        related_name="parts",
        db_comment=(
            "Component category to which this part design belongs."
        ),
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        db_comment=(
            "Stable business identifier for the part design. "
            "This should not change when its display name changes."
        ),
    )
    name = models.CharField(
        max_length=100,
        db_comment="Customer- and administrator-facing part name.",
    )
    description = models.TextField(
        blank=True,
        db_comment="Description of the part design and its features.",
    )
    color_name = models.CharField(
        max_length=50,
        blank=True,
        db_comment="Human-readable primary color of the part.",
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        db_comment="Primary material or material description.",
    )
    image = models.ImageField(
        upload_to="parts/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True,
        db_comment=(
            "Inactive parts remain available for history but cannot "
            "be assigned to new shoe configurations."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["part_type", "name"]
        db_table_comment = (
            "Size-independent modular part designs, such as a "
            "specific tongue, sole, shell, logo, panel, or lace design."
        )

    def __str__(self):
        return f"{self.part_type.name}: {self.name}"


class PartVariant(models.Model):
    """
    A physical, inventory-tracked version of a part for one
    compatibility group.
    """

    part = models.ForeignKey(
        Part,
        on_delete=models.PROTECT,
        related_name="variants",
        db_comment="Part design represented by this physical SKU.",
    )
    compatibility_group = models.ForeignKey(
        CompatibilityGroup,
        on_delete=models.PROTECT,
        related_name="part_variants",
        db_comment=(
            "Physical compatibility group determining which shoe "
            "variants can use this part."
        ),
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        db_comment=(
            "Unique inventory identifier for this size-compatible part."
        ),
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        db_comment=(
            "Number of inventory units currently available."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        db_comment=(
            "Inactive variants remain available for historical records "
            "but cannot be selected for new configurations."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "part",
            "compatibility_group",
        ]
        db_table_comment = (
            "Inventory-tracked modular part SKUs. Each row connects "
            "one part design to one physical compatibility group."
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "part",
                    "compatibility_group",
                ],
                name="unique_part_compatibility_variant",
            ),
            models.CheckConstraint(
                condition=models.Q(stock_quantity__gte=0),
                name="part_variant_stock_nonnegative",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "compatibility_group",
                    "is_active",
                ],
                name="partvar_compat_active_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.part.name} — "
            f"{self.compatibility_group.code}"
        )

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )
    compatibility_group = models.ForeignKey(
        CompatibilityGroup,
        on_delete=models.PROTECT,
        related_name="product_variants",
        blank=True,
        null=True,
        db_comment=(
            "Physical compatibility group shared by interchangable "
            "shoe variants and modular parts."
        ),
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
    )
    size = models.CharField(
        max_length=20,
    )
    color = models.CharField(
        max_length=50,
    )
    stock_quantity = models.PositiveIntegerField(
        default=0
    )
    price_override = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    # Nullable during the expand/dual-read release. New and backfilled rows
    # use this as the authoritative launch selling price; the legacy override
    # fallback remains only for rows created before the backfill completes.
    selling_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    compare_at_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "size", "color"],
                name="unique_product_size_color",
            ),
            models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name="variant_stock_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                        models.Q(price_override__gte=0)
                        | models.Q(price_override__isnull=True)
                ),
                name="variant_price_override_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(selling_price__gte=0)
                    | models.Q(selling_price__isnull=True)
                ),
                name="variant_selling_price_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(compare_at_price__gte=0)
                    | models.Q(compare_at_price__isnull=True)
                ),
                name="variant_compare_at_price_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(selling_price__isnull=True)
                    | models.Q(compare_at_price__isnull=True)
                    | models.Q(compare_at_price__gt=models.F("selling_price"))
                ),
                name="variant_compare_at_price_above_selling_price",
            ),
        ]
        ordering = ["product", "color", "size"]

    def current_price(self):
        if self.selling_price is not None:
            return self.selling_price

        if self.price_override is not None:
            return self.price_override

        return self.product.current_price()

    def compare_price(self):
        if self.compare_at_price is not None:
            return self.compare_at_price
        effective_price = self.current_price()
        return self.product.price if self.product.price > effective_price else None

    def save(self, *args, **kwargs):
        if self.selling_price is None and self.product_id:
            product = getattr(self, "product", None)
            if product is None:
                product = Product.objects.get(pk=self.product_id)
            self.selling_price = (
                self.price_override
                if self.price_override is not None
                else product.current_price()
            )
            if self.compare_at_price is None and product.price > self.selling_price:
                self.compare_at_price = product.price
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.product.name} -"
            f"{self.color}, Size {self.size}"
        )


class PreorderBatch(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        PAUSED = "paused", "Paused"
        CLOSED = "closed", "Closed"

    code = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="preorder_batches",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    estimated_tender_start = models.DateField()
    estimated_tender_end = models.DateField()
    total_capacity = models.PositiveIntegerField()
    committed_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_capacity__gte=1),
                name="preorder_batch_capacity_positive",
            ),
            models.CheckConstraint(
                condition=Q(committed_quantity__lte=models.F("total_capacity")),
                name="preorder_batch_committed_within_capacity",
            ),
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(status__in=["open", "paused"]),
                name="unique_live_preorder_batch_per_product",
            ),
        ]

    @property
    def remaining_quantity(self):
        return self.total_capacity - self.committed_quantity

    @property
    def has_confirmed_payments(self):
        return self.committed_quantity > 0

    def clean(self):
        super().clean()
        errors = {}

        if (
            self.estimated_tender_start
            and self.estimated_tender_end
            and self.estimated_tender_end < self.estimated_tender_start
        ):
            errors["estimated_tender_end"] = (
                "The estimated tender end must be on or after the start date."
            )

        previous = None
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).first()

        if not self.pk and self.status != self.Status.DRAFT:
            errors["status"] = (
                "Create the batch as draft, add SKU allocations, then open it."
            )

        if previous:
            allowed_transitions = {
                self.Status.DRAFT: {self.Status.DRAFT, self.Status.OPEN},
                self.Status.OPEN: {
                    self.Status.OPEN,
                    self.Status.PAUSED,
                    self.Status.CLOSED,
                },
                self.Status.PAUSED: {
                    self.Status.PAUSED,
                    self.Status.OPEN,
                    self.Status.CLOSED,
                },
                self.Status.CLOSED: {self.Status.CLOSED},
            }
            if self.status not in allowed_transitions[previous.status]:
                errors["status"] = (
                    f"A {previous.get_status_display().lower()} batch cannot "
                    f"transition to {self.get_status_display().lower()}."
                )

            promised_dates_changed = (
                previous.estimated_tender_start != self.estimated_tender_start
                or previous.estimated_tender_end != self.estimated_tender_end
            )
            if previous.committed_quantity and promised_dates_changed:
                errors["estimated_tender_start"] = (
                    "The shipping window is locked after the first confirmed payment."
                )

        if self.status in [self.Status.OPEN, self.Status.PAUSED] and self.pk:
            active_variant_ids = set(
                self.product.variants.filter(is_active=True)
                .values_list("id", flat=True)
            )
            allocated_variant_ids = set(
                self.variant_allocations.values_list("variant_id", flat=True)
            )
            if not active_variant_ids.issubset(allocated_variant_ids):
                errors["status"] = (
                    "Every active product variant must have exactly one allocation "
                    "before the batch can open or pause."
                )

            combined_capacity = sum(
                self.variant_allocations.values_list("capacity", flat=True)
            )
            if combined_capacity < self.total_capacity:
                errors["total_capacity"] = (
                    "Total capacity cannot exceed combined SKU capacity."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} — {self.product.name} ({self.get_status_display()})"


class PreorderVariantAllocation(models.Model):
    batch = models.ForeignKey(
        PreorderBatch,
        on_delete=models.PROTECT,
        related_name="variant_allocations",
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="preorder_allocations",
    )
    capacity = models.PositiveIntegerField()
    committed_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["variant_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "variant"],
                name="unique_preorder_batch_variant",
            ),
            models.CheckConstraint(
                condition=Q(committed_quantity__lte=models.F("capacity")),
                name="preorder_variant_committed_within_capacity",
            ),
        ]

    @property
    def remaining_quantity(self):
        return self.capacity - self.committed_quantity

    def clean(self):
        super().clean()
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).first()
            if previous and previous.variant_id != self.variant_id:
                raise ValidationError({
                    "variant": "A batch allocation cannot be moved to another SKU."
                })
        if (
            self.batch_id
            and self.variant_id
            and self.batch.product_id != self.variant.product_id
        ):
            raise ValidationError({
                "variant": "The variant must belong to the batch product."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch.code}: {self.variant.sku}"


class PreorderBatchEvent(models.Model):
    class EventType(models.TextChoices):
        CREATED = "created", "Created"
        STATUS_CHANGED = "status_changed", "Status Changed"
        BATCH_CAPACITY_CHANGED = "batch_capacity_changed", "Batch Capacity Changed"
        SKU_CAPACITY_CHANGED = "sku_capacity_changed", "SKU Capacity Changed"

    batch = models.ForeignKey(
        PreorderBatch,
        on_delete=models.PROTECT,
        related_name="events",
    )
    variant_allocation = models.ForeignKey(
        PreorderVariantAllocation,
        on_delete=models.PROTECT,
        related_name="events",
        blank=True,
        null=True,
    )
    event_type = models.CharField(max_length=40, choices=EventType.choices)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    previous_capacity = models.PositiveIntegerField(blank=True, null=True)
    new_capacity = models.PositiveIntegerField(blank=True, null=True)
    reason = models.TextField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="preorder_batch_events",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Preorder batch events are append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Preorder batch events are append-only.")

    def __str__(self):
        return f"{self.batch.code}: {self.get_event_type_display()}"

class ProductVariantComponent(models.Model):
    """
    Assigns one modular part SKU to one component slot in a
    sellable shoe variant.

    This table represents the product variant's standard bill
    of materials. It does not represent a customer's customized
    order selection.
    """

    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="components",
        db_comment=(
            "Sellable shoe SKU whose standard configuration"
            "includes this component."
        ),
    )
    part_type = models.ForeignKey(
        PartType,
        on_delete=models.PROTECT,
        related_name="product_variant_components",
        db_comment=(
            "Component slot filled by this assignment, such as "
            "TONGUE, SOLE, or LACES."
        ),
    )
    part_variant = models.ForeignKey(
        PartVariant,
        on_delete=models.PROTECT,
        related_name="product_variant_components",
        db_comment=(
            "Physical modular part SKU included in the shoe variant.",
        ),
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        db_comment=(
            "Number of modular parts included in the shoe variant."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "product_variant",
            "part_type"
        ]
        db_table_comment = (
            "Standard bill of materials connecting sellable shoe "
            "variants to their included modular part SKUs."
        )
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product_variant",
                    "part_type",
                ],
                name="unique_product_variant_component",
            ),
            models.CheckConstraint(
                check=models.Q(quantity__gte=1),
                name="product_variant_component_quantity_positive",
            ),
        ]
        indexes = [
            models.Index(
                fields=[
                    "product_variant",
                    "part_type",
                ],
                name="prodvarcomp_variant_type_idx",
            ),
        ]
    def clean(self):
        """
        Validate rules involving records in related tables.

        A normal database CHECK constraint cannot compare values
        stored in multiple related tables, so these rules are
        enforced through Django validation.
        """
        errors = {}

        if self.part_variant_id and self.part_type_id:
            actual_part_type_id = (
                self.part_variant.part.part_type_id
            )

            if actual_part_type_id != self.part_type_id:
                errors["part_variant"] = (
                    "The selected part variant does not belong to "
                    "the assigned part type."
                )

        if self.product_variant_id and self.part_variant_id:
            shoe_group_id = (
                self.product_variant.compatibility_group_id
            )
            part_group_id = (
                self.part_variant.compatibility_group_id
            )

            if shoe_group_id is None:
                errors["product_variant"] = (
                    "The product variant must have a compatibility "
                    "group before components can be assigned."
                )
            elif shoe_group_id != part_group_id:
                errors["part_variant"] = (
                    "The selected part variant is not compatible "
                    "with this product variant."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Django does not automatically run full_clean() during save().
        # Calling it here protects normal application and admin writes.
        self.full_clean()
        return super().save(*args, **kwargs)
    def __str__(self):
        return(
            f"{self.product_variant.sku} - "
            f"{self.part_type.code}: "
            f"{self.part_variant.sku}"
        )
