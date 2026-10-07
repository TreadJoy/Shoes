from django.db import migrations

PART_TYPES = [
    {
        "code": "TONGUE",
        "name": "Tongue",
        "description": (
            "Removable upper component positioned beneath the laces."
        ),
        "display_order": 10,
    },
    {
        "code": "LOGO",
        "name": "Logo",
        "description": (
            "Removable decorative or branded logo component."
        ),
        "display_order": 20,
    },
    {
        "code": "SOLE",
        "name": "Sole",
        "description": (
            "Removable lower component that interfaces with the ground."
        ),
        "display_order": 30,
    },
    {
        "code": "OUTER_SHELL",
        "name": "Outer Shell",
        "description": (
            "Removable exterior body or upper shell component."
        ),
        "display_order": 40,
    },
    {
        "code": "BACK_PANEL",
        "name": "Back Panel",
        "description": (
            "Removable rear exterior panel of the shoe."
        ),
        "display_order": 50,
    },
    {
        "code": "LACES",
        "name": "Laces",
        "description": (
            "Removable fastening lace set."
        ),
        "display_order": 60,
    },
]

def seed_part_types(apps, schema_editor):
    PartType = apps.get_model("products", "PartType")

    for values in PART_TYPES:
        code = values["code"]

        PartType.objects.update_or_create(
            code=code,
            defaults={
                "name": values["name"],
                "description": values["description"],
                "display_order": values["display_order"],
                "is_active": True,
            },
        )

class Migration(migrations.Migration):

    dependencies = [
        ("products", "0007_add_modular_part_catalog"),
    ]

    operations = [
        migrations.RunPython(
            seed_part_types,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
