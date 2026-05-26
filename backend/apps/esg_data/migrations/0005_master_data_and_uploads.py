# Generated manually for master data models

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0003_department"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("esg_data", "0004_emissioncategory_metricdefinition_emission_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="ESGCategoryMaster",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(db_index=True, max_length=1, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "esg_categories",
                "ordering": ["code"],
                "verbose_name_plural": "ESG categories",
            },
        ),
        migrations.CreateModel(
            name="EmissionScope",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(db_index=True, max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "emission_scopes",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="CollectionMethod",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(db_index=True, max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "collection_methods",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DataSource",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("code", models.CharField(db_index=True, max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("erp", "ERP"),
                            ("utility", "Utility"),
                            ("travel", "Travel"),
                            ("manual", "Manual"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=30,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "data_sources",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DataUpload",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("file_name", models.CharField(max_length=255)),
                ("source_type", models.CharField(default="manual", max_length=30)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Success"), ("partial", "Partial"), ("failed", "Failed")],
                        default="success",
                        max_length=20,
                    ),
                ),
                ("rows_created", models.PositiveIntegerField(default=0)),
                ("rows_updated", models.PositiveIntegerField(default=0)),
                ("rows_failed", models.PositiveIntegerField(default=0)),
                ("preview_rows", models.JSONField(default=list, help_text="First rows parsed for preview")),
                ("error_details", models.JSONField(default=list)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_uploads",
                        to="organizations.organization",
                    ),
                ),
                (
                    "reporting_period",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="uploads",
                        to="esg_data.reportingperiod",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="data_uploads",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "esg_data_uploads",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AlterField(
            model_name="esgdatapoint",
            name="collection_method",
            field=models.CharField(
                default="manual_entry",
                help_text="Collection method code from master data",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="esgdatapoint",
            name="data_source",
            field=models.CharField(
                blank=True,
                help_text="Data source code or label from master data",
                max_length=100,
            ),
        ),
    ]
