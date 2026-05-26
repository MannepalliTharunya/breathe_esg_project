from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="report_type",
            field=models.CharField(
                choices=[
                    ("gri", "GRI Standards"),
                    ("tcfd", "TCFD"),
                    ("sasb", "SASB"),
                    ("cdp", "CDP"),
                    ("csrd", "CSRD"),
                    ("brsr", "BRSR"),
                    ("ghg_protocol", "GHG Protocol"),
                    ("custom", "Custom"),
                ],
                max_length=20,
            ),
        ),
    ]
