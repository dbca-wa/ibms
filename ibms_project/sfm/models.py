from django.db import models

REGION_CHOICES = [
    ("Goldfields", "Goldfields"),
    ("Kimberley", "Kimberley"),
    ("Midwest", "Midwest"),
    ("Pilbara", "Pilbara"),
    ("South Coast", "South Coast"),
    ("South West", "South West"),
    ("Swan", "Swan"),
    ("Warren", "Warren"),
    ("Wheatbelt", "Wheatbelt"),
]


class CostCentre(models.Model):
    costCentre = models.CharField(max_length=6, unique=True, verbose_name="cost centre")
    name = models.CharField(max_length=128, null=True, blank=True)
    region = models.CharField(max_length=100, choices=REGION_CHOICES, null=True, blank=True)

    class Meta:
        ordering = ("costCentre",)

    def __str__(self):
        if self.name:
            return f"{self.costCentre} - {self.name}"
        return self.costCentre


class FinancialYear(models.Model):
    financialYear = models.CharField(max_length=10, primary_key=True, verbose_name="financial year")

    class Meta:
        ordering = ("financialYear",)

    def __str__(self):
        return self.financialYear


class SFMMetric(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    region = models.CharField(max_length=100, choices=REGION_CHOICES, null=True, blank=True)
    servicePriorityNo = models.CharField(max_length=100, verbose_name="service priority number", null=False, blank=True, default="-1")
    metricID = models.TextField(verbose_name="metric ID", db_index=True, null=True, blank=True)
    descriptor = models.TextField(null=True, blank=True)
    example = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("fy", "region", "metricID")
        unique_together = ("fy", "metricID")
        verbose_name = "SFM metric"

    def __str__(self):
        return self.metricID


class MeasurementType(models.Model):
    unit = models.CharField(max_length=50, null=False, blank=True)

    def __str__(self):
        return self.unit


class Quarter(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT)
    quarter = models.IntegerField()
    description = models.TextField(null=True)

    class Meta:
        ordering = ("fy", "quarter")

    def __str__(self):
        return f"{self.fy.financialYear} {self.description}"


class MeasurementValue(models.Model):
    STATUS_CHOICES = (
        ("not started", "Not started"),
        ("in progress", "In progress"),
        ("completed", "Completed"),
    )
    quarter = models.ForeignKey(Quarter, on_delete=models.PROTECT)
    costCentre = models.ForeignKey(CostCentre, verbose_name="cost centre", on_delete=models.PROTECT, null=True, blank=True)
    region = models.CharField(max_length=100, choices=REGION_CHOICES, null=True, blank=True)
    sfmMetric = models.ForeignKey(SFMMetric, verbose_name="SFM metric", on_delete=models.PROTECT)
    planned = models.BooleanField(null=True, verbose_name="action planned")
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, null=True, blank=True)
    measurementType = models.ForeignKey(
        MeasurementType, null=True, blank=True, on_delete=models.PROTECT, verbose_name="measurement type", help_text="Deprecated field"
    )
    value = models.FloatField(null=True, blank=True, help_text="Deprecated field")
    comment = models.TextField(null=True)

    def __str__(self):
        return f"{self.quarter} {self.costCentre}: {self.sfmMetric}"


class Outcomes(models.Model):
    costCentre = models.ForeignKey(CostCentre, on_delete=models.PROTECT, verbose_name="cost centre")
    comment = models.TextField(null=False)

    class Meta:
        verbose_name_plural = "outcomes"

    def __str__(self):
        return self.comment
