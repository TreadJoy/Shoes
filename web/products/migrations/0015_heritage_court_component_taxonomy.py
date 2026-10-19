from django.db import migrations


LEGACY_TYPES = {
    "TONGUE": {
        "name": "Tongue",
        "description": "Removable upper component positioned beneath the laces.",
        "display_order": 10,
    },
    "LOGO": {
        "name": "Logo",
        "description": "Removable decorative or branded logo component.",
        "display_order": 20,
    },
    "SOLE": {
        "name": "Sole",
        "description": "Removable lower component that interfaces with the ground.",
        "display_order": 30,
    },
    "OUTER_SHELL": {
        "name": "Outer Shell",
        "description": "Removable exterior body or upper shell component.",
        "display_order": 40,
    },
    "BACK_PANEL": {
        "name": "Back Panel",
        "description": "Removable rear exterior panel of the shoe.",
        "display_order": 50,
    },
    "LACES": {
        "name": "Laces",
        "description": "Removable fastening lace set.",
        "display_order": 60,
    },
}

CANONICAL_TYPES = (
    (
        "FRONT_SHELL",
        "Front Shell",
        "Visual group identified as the front shell in the current prototype. Attachment and removal mechanics are unverified.",
        10,
        "unverified",
    ),
    (
        "BOOTIE_AND_SOLE",
        "Bootie and Sole",
        "The bootie and sole stay together as one visual group, designated permanent in the current prototype.",
        20,
        "permanent",
    ),
    (
        "TONGUE",
        "Tongue",
        "Visual group identified as the tongue in the current prototype. Attachment and removal mechanics are unverified.",
        30,
        "unverified",
    ),
    (
        "LACES",
        "Laces",
        "Visual group identified as the laces in the current prototype. Interchangeability is unverified.",
        40,
        "unverified",
    ),
    (
        "BACK_PANEL",
        "Back Panel",
        "Visual group identified as the back panel in the current prototype. Attachment and removal mechanics are unverified.",
        50,
        "unverified",
    ),
    (
        "LOGO_HOLDER",
        "Logo Holder",
        "Visual group identified as the logo holder in the current prototype. Attachment and removal mechanics are unverified.",
        60,
        "unverified",
    ),
    (
        "BACK_LOOP",
        "Back Loop",
        "Visual group identified as the back loop in the current prototype. Its function and interchangeability are unverified.",
        70,
        "unverified",
    ),
)


def seed_heritage_court_types(apps, schema_editor):
    PartType = apps.get_model("products", "PartType")

    for code in ("OUTER_SHELL", "LOGO", "SOLE"):
        PartType.objects.filter(code=code).update(
            is_active=False,
            interchangeability_status="unverified",
        )

    for code, name, description, display_order, status in CANONICAL_TYPES:
        PartType.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "description": description,
                "display_order": display_order,
                "interchangeability_status": status,
                "is_active": True,
            },
        )


def restore_legacy_types(apps, schema_editor):
    PartType = apps.get_model("products", "PartType")

    for code, values in LEGACY_TYPES.items():
        PartType.objects.update_or_create(
            code=code,
            defaults={
                **values,
                "is_active": True,
                "interchangeability_status": "unverified",
            },
        )

    PartType.objects.filter(
        code__in=("FRONT_SHELL", "BOOTIE_AND_SOLE", "LOGO_HOLDER", "BACK_LOOP")
    ).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0014_product_component_standard_and_parttype_interchangeability_status"),
    ]

    operations = [
        migrations.RunPython(seed_heritage_court_types, restore_legacy_types),
    ]
