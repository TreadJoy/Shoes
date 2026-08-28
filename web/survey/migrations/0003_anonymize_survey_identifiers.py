from django.db import migrations


def clear_legacy_identifiers(apps, schema_editor):
    SurveyResponse = apps.get_model("survey", "SurveyResponse")
    SurveyResponse.objects.update(user=None, session_key="")


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0002_surveyresponse_session_key_surveyresponse_user"),
    ]

    operations = [
        migrations.RunPython(clear_legacy_identifiers, migrations.RunPython.noop),
    ]
