from django.contrib.admin import register, ModelAdmin, SimpleListFilter
from ibms.admin import export_as_csv_action
from .models import CostCentre, FinancialYear, SFMMetric, Quarter, MeasurementValue, Outcomes


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
    search_fields = ['fy__financialYear', 'servicePriorityNo', 'metricID']
    list_display = ['fy', 'servicePriorityNo', 'metricID']
    list_filter = ['fy', 'servicePriorityNo', 'metricID']
    actions = [
        export_as_csv_action(
            translations=['financialYear', 'servicePriorityNo', 'metricID', 'descriptor', 'example'],
            fields=['fy', 'servicePriorityNo', 'metricID', 'descriptor', 'example'])]


@register(Quarter)
class QuarterAdmin(ModelAdmin):
    search_fields = ['fy__financialYear', 'quarter', 'description']
    list_display = ['fy', 'quarter', 'description']
    list_filter = ['fy', 'quarter', 'description']
    actions = [
        export_as_csv_action(
            translations=['financialYear', 'quarter', 'description'],
            fields=['fy', 'quarter', 'description'])]


@register(MeasurementValue)
class MeasurementValueAdmin(ModelAdmin):
    class FYFilter(SimpleListFilter):
        title = 'financial year'
        parameter_name = 'fy'

        def lookups(self, request, model_admin):
            return [(fy.pk, fy.financialYear) for fy in FinancialYear.objects.all()]

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(quarter__fy__pk=self.value())

    search_fields = ['sfmMetric__metricID', 'quarter__fy__financialYear', 'costCentre__costCentre', 'comment']
    list_display = ['quarter', 'costCentre', 'sfmMetric', 'planned', 'status']
    list_filter = [FYFilter, 'quarter', 'costCentre', 'status', 'sfmMetric']
    readonly_fields = ('measurementType', 'value')
    actions = [
        export_as_csv_action(
            translations=['quarter', 'costCentre', 'sfmMetric', 'planned', 'status', 'comment', 'measurementType', 'value'],
            fields=['quarter', 'costCentre', 'sfmMetric', 'planned', 'status', 'comment', 'measurementType', 'value'])]


@register(Outcomes)
class OutcomesAdmin(ModelAdmin):
    search_fields = ['costCentre__costCentre', 'costCentre__name', 'comment']
    list_display = ['costCentre', 'comment']
    list_filter = ['costCentre']
    actions = [export_as_csv_action(translations=['costCentre', 'comment'], fields=['costCentre', 'comment'])]
