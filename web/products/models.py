from django.db import models
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

    def is_in_stock(self):
        return self.total_stock() > 0

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
        ]
        ordering = ["product", "color", "size"]

    def current_price(self):
        if self.price_override is not None:
            return self.price_override

        return self.product.current_price()

    def __str__(self):
        return (
            f"{self.product.name} -"
            f"{self.color}, Size {self.size}"
        )

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