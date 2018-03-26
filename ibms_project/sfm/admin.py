from django.contrib import admin
from ibms.admin import export_as_csv_action
from sfm import models


class CostCentreAdmin(admin.ModelAdmin):
    search_fields = ['costCentre', 'name']
    list_display = ['__str__']
    list_filter = ['costCentre', 'name']
    actions = [export_as_csv_action(translations=['costCentre'], fields=['costCentre'])]


class FinancialYearAdmin(admin.ModelAdmin):
    search_fields = ['financialYear']
    list_display = ['financialYear']
    list_filter = ['financialYear']
    actions = [export_as_csv_action(translations=['financialYear'], fields=['financialYear'])]


class SFMMetricAdmin(admin.ModelAdmin):
    search_fields = ['financialYear', 'servicePriorityNo', 'metricID']
    list_display = ['financialYear', 'servicePriorityNo',  'metricID']
    list_filter = ['financialYear', 'servicePriorityNo',  'metricID']
    actions = [export_as_csv_action(translations=['financialYear', 'servicePriorityNo',  'metricID', 'descriptor', 'example'],
fields=['financialYear', 'servicePriorityNo',  'metricID', 'descriptor', 'example'])]


class MeasurementTypeAdmin(admin.ModelAdmin):
    search_fields = ['unit']
    list_display = ['unit']
    list_filter = ['unit']
    actions = [export_as_csv_action(translations=['unit'], fields=['unit'])]


class QuarterAdmin(admin.ModelAdmin):
    search_fields = ['financialYear', 'quarter', 'description']
    list_display = ['financialYear', 'quarter', 'description']
    list_filter = ['financialYear', 'quarter', 'description']
    actions = [export_as_csv_action(translations=['financialYear', 'quarter', 'description'],
        fields=['financialYear', 'quarter', 'description'])]


class MeasurementValueAdmin(admin.ModelAdmin):
    search_fields = ['sfmMetric__metricID', 'quarter__financialYear__financialYear', 'costCentre__costCentre']
    list_display = ['quarter', 'sfmMetric', 'measurementType', 'costCentre', 'value']
    list_filter = ['quarter', 'sfmMetric', 'measurementType', 'costCentre']
    actions = [export_as_csv_action(translations=['quarter', 'sfmMetric', 'measurementType', 'costCentre', 'value', 'comment'],
        fields=['quarter', 'sfmMetric', 'measurementType', 'costCentre', 'value', 'comment'])]


class OutcomesAdmin(admin.ModelAdmin):
    search_fields = ['costCentre', 'comment']
    list_display = ['costCentre', 'comment']
    list_filter = ['costCentre']
    actions = [export_as_csv_action(translations=['costCentre', 'comment'],
        fields=['costCentre', 'comment'])]


admin.site.register(models.CostCentre, CostCentreAdmin)
admin.site.register(models.FinancialYear, FinancialYearAdmin)
admin.site.register(models.SFMMetric, SFMMetricAdmin)
admin.site.register(models.MeasurementType, MeasurementTypeAdmin)
admin.site.register(models.Quarter, QuarterAdmin)
admin.site.register(models.MeasurementValue, MeasurementValueAdmin)
admin.site.register(models.Outcomes, OutcomesAdmin)
