# Generated by Django 5.2.3 on 2025-07-02 17:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DataSource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("api_url", models.URLField()),
                ("is_active", models.BooleanField(default=True)),
                ("last_checked", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ICSProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "birth_place",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("birth_pib_per_capita", models.FloatField(blank=True, null=True)),
                ("father_job", models.CharField(blank=True, max_length=200, null=True)),
                ("father_salary", models.FloatField(blank=True, null=True)),
                ("mother_job", models.CharField(blank=True, max_length=200, null=True)),
                ("mother_salary", models.FloatField(blank=True, null=True)),
                ("family_property_value", models.FloatField(blank=True, null=True)),
                ("family_financial_value", models.FloatField(blank=True, null=True)),
                (
                    "inheritance_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("recebeu", "Recebeu herança"),
                            ("sem", "Não recebeu/deserdado"),
                            ("aguardando", "Aguardando herança"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                ("benefits_value", models.FloatField(blank=True, null=True)),
                ("tax_paid", models.FloatField(blank=True, null=True)),
                ("ics_score", models.FloatField(blank=True, null=True)),
                ("ics_explanation", models.TextField(blank=True, null=True)),
                ("ics_confidence", models.FloatField(blank=True, null=True)),
                ("raw_data", models.JSONField(default=dict)),
            ],
            options={
                "verbose_name": "Perfil ICS",
                "verbose_name_plural": "Perfis ICS",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="APICache",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cache_key", models.CharField(max_length=255, unique=True)),
                ("data", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["cache_key"], name="core_apicac_cache_k_c60a13_idx"
                    ),
                    models.Index(
                        fields=["expires_at"], name="core_apicac_expires_f7238f_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="CalculationLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("calculation_data", models.JSONField()),
                ("weights_used", models.JSONField()),
                ("result", models.FloatField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.icsprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]
