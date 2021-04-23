from django.db import models


class CostCentre(models.Model):
    costCentre = models.CharField(max_length=6, verbose_name="cost centre")
    name = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        if self.name:
            return "{} - {}".format(self.costCentre, self.name)
        return self.costCentre


class FinancialYear(models.Model):
    financialYear = models.CharField(max_length=10, primary_key=True, verbose_name="financial year")

    def __str__(self):
        return self.financialYear


class SFMMetric(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT)
    servicePriorityNo = models.CharField(max_length=100, verbose_name="service priority number", null=False, blank=True, default="-1")
    metricID = models.TextField(verbose_name="metric ID", null=True, blank=True)
    descriptor = models.TextField(null=True, blank=True)
    example = models.TextField(null=True, blank=True)

    class Meta:
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

    def __str__(self):
        return "{} {}".format(self.fy.financialYear, self.description)


class MeasurementValue(models.Model):
    STATUS_CHOICES = (
        ("Not started", "Not started"),
        ("In progress", "In progress"),
        ("Completed", "Completed"),
    )
    quarter = models.ForeignKey(Quarter, on_delete=models.PROTECT)
    costCentre = models.ForeignKey(
        CostCentre, verbose_name="cost centre", on_delete=models.PROTECT)
    sfmMetric = models.ForeignKey(
        SFMMetric, verbose_name="SFM metric", on_delete=models.PROTECT)
    planned = models.BooleanField(null=True, verbose_name="action planned")
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, null=True, blank=True)
    measurementType = models.ForeignKey(
        MeasurementType, null=True, blank=True, on_delete=models.PROTECT,
        verbose_name="measurement type", help_text="Deprecated field")
    value = models.FloatField(null=True, blank=True, help_text="Deprecated field")
    comment = models.TextField(null=True)


class Outcomes(models.Model):
    costCentre = models.ForeignKey(CostCentre, on_delete=models.PROTECT, verbose_name="cost centre")
    comment = models.TextField(null=False)

    class Meta:
        verbose_name_plural = "outcomes"

    def __str__(self):
        return self.comment
