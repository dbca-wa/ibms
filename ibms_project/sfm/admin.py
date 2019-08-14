from django.contrib.admin import register, ModelAdmin
from ibms.admin import export_as_csv_action
from .models import CostCentre, FinancialYear, SFMMetric, MeasurementType, Quarter, MeasurementValue, Outcomes


@register(CostCentre)
class CostCentreAdmin(ModelAdmin):
    search_fields = ['costCentre', 'name']
    list_display = ['__str__']
    list_filter = ['costCentre', 'name']
    actions = [export_as_csv_action(translations=['costCentre'], fields=['costCentre'])]


@register(FinancialYear)
class FinancialYearAdmin(ModelAdmin):
    search_fields = ['financialYear']
    list_display = ['financialYear']
    list_filter = ['financialYear']
    actions = [export_as_csv_action(translations=['financialYear'], fields=['financialYear'])]


@register(SFMMetric)
class SFMMetricAdmin(ModelAdmin):
    search_fields = ['fy', 'servicePriorityNo', 'metricID']
    list_display = ['fy', 'servicePriorityNo', 'metricID']
    list_filter = ['fy', 'servicePriorityNo', 'metricID']
    actions = [
        export_as_csv_action(
            translations=['financialYear', 'servicePriorityNo', 'metricID', 'descriptor', 'example'],
            fields=['fy', 'servicePriorityNo', 'metricID', 'descriptor', 'example'])]


@register(MeasurementType)
class MeasurementTypeAdmin(ModelAdmin):
    search_fields = ['unit']
    list_display = ['unit']
    list_filter = ['unit']
    actions = [export_as_csv_action(translations=['unit'], fields=['unit'])]


@register(Quarter)
class QuarterAdmin(ModelAdmin):
    search_fields = ['fy', 'quarter', 'description']
    list_display = ['fy', 'quarter', 'description']
    list_filter = ['fy', 'quarter', 'description']
    actions = [
        export_as_csv_action(
            translations=['financialYear', 'quarter', 'description'],
            fields=['fy', 'quarter', 'description'])]


@register(MeasurementValue)
class MeasurementValueAdmin(ModelAdmin):
    search_fields = ['sfmMetric__metricID', 'quarter__financialYear__financialYear', 'costCentre__costCentre']
    list_display = ['quarter', 'sfmMetric', 'measurementType', 'costCentre', 'value']
    list_filter = ['quarter', 'sfmMetric', 'measurementType', 'costCentre']
    actions = [
        export_as_csv_action(
            translations=['quarter', 'sfmMetric', 'measurementType', 'costCentre', 'value', 'comment'],
            fields=['quarter', 'sfmMetric', 'measurementType', 'costCentre', 'value', 'comment'])]


@register(Outcomes)
class OutcomesAdmin(ModelAdmin):
    search_fields = ['costCentre', 'comment']
    list_display = ['costCentre', 'comment']
    list_filter = ['costCentre']
    actions = [export_as_csv_action(translations=['costCentre', 'comment'], fields=['costCentre', 'comment'])]
