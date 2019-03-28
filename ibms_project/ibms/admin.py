import csv
from django.contrib.admin import register, ModelAdmin
from django.http import HttpResponse

from .models import (
    IBMData, GLPivDownload, CorporateStrategy, GeneralServicePriority, NCServicePriority,
    PVSServicePriority, SFMServicePriority, ERServicePriority, NCStrategicPlan, Outcomes,
    ServicePriorityMappings)


def export_as_csv_action(fields=None, translations=None, exclude=None,
                         header=True, description='Export selected objects to CSV'):
    '''
    This function adds an "Export as CSV" action to a model in the Django admin site.
    Register the action using the ModelAdmin ``action`` option.
    ``fields`` and ``exclude`` work the same as those Django ModelForm options (use one or the other).
    ``header`` defines whether or not the column names are output as the first row.

    Ref: http://djangosnippets.org/snippets/2020/
    '''
    def export_as_csv(modeladmin, request, queryset):
        '''
        Generic csv export admin action.
        '''
        opts = modeladmin.model._meta
        field_names = [field.name for field in opts.fields]
        if fields:
            field_names = fields
        elif exclude:
            excludeset = set(exclude)
            field_names = [f for f in field_names if not (f in excludeset)]
        # Create the response object.
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = 'attachment; filename={0}.csv'.format(str(opts).replace('.', '_'))
        # Write the CSV to the response object.
        writer = csv.writer(response)
        # writer.writerow(list(translations))
        if header:
            writer.writerow(list(translations))
        else:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv


@register(IBMData)
class IBMDataAdmin(ModelAdmin):
    search_fields = ('financialYear', 'ibmIdentifier', 'budgetArea', 'corporatePlanNo', 'strategicPlanNo')
    list_display = ('financialYear', 'ibmIdentifier', 'budgetArea', 'corporatePlanNo', 'strategicPlanNo')
    list_filter = ('financialYear', 'costCentre', 'budgetArea', 'service', 'corporatePlanNo')
    actions = [
        export_as_csv_action(
            translations=[
                'financialYear', 'ibmIdentifier', 'costCentre', 'account', 'service', 'activity', 'project', 'job',
                'budgetArea', 'projectSponsor', 'corporatePlanNo', 'strategicPlanNo',
                'regionalSpecificInfo', 'servicePriorityID', 'annualWPInfo'],
            fields=[
                'financialYear', 'ibmIdentifier', 'costCentre', 'account', 'service', 'activity', 'project', 'job',
                'budgetArea', 'projectSponsor', 'corporatePlanNo', 'strategicPlanNo',
                'regionalSpecificInfo', 'servicePriorityID', 'annualWPInfo'])]


@register(GLPivDownload)
class GLPivDownloadAdmin(ModelAdmin):
    search_fields = (
        'financialYear', 'costCentre', 'account', 'service', 'activity', 'ccName', 'shortCode',
        'shortCodeName', 'gLCode', 'codeID')
    list_display = ('financialYear', 'costCentre', 'account', 'service', 'activity', 'ccName')
    list_filter = ('financialYear', 'division', 'regionBranch', 'costCentre')
    actions = [
        export_as_csv_action(
            translations=[
                'id', 'financialYear', 'Download Period', 'CC', 'Account', 'Service',
                'Activity', 'Resource', 'Project', 'Job', 'Shortcode', 'Shortcode_Name', 'GL_Code',
                'PTD_Actual', 'PTD_Budget', 'YTD_Actual', 'YTD_Budget', 'FY_Budget', 'YTD_Variance',
                'CC_Name', 'Service Name', 'Activity_Name', 'Resource_Name', 'Project_Name', 'Job_Name',
                'Code identifier', 'ResNmNo', 'ActNmNo', 'ProjNmNo', 'Region/Branch', 'Division',
                'Resource Category', 'Wildfire', 'Exp_Rev', 'Fire Activities', 'MPRA Category'],
            fields=[
                'id', 'financialYear', 'downloadPeriod', 'costCentre', 'account', 'service',
                'activity', 'resource', 'project', 'job', 'shortCode', 'shortCodeName', 'gLCode',
                'ptdActual', 'ptdBudget', 'ytdActual', 'ytdBudget', 'fybudget', 'ytdVariance',
                'ccName', 'serviceName', 'activityName', 'resourceName', 'projectName', 'jobName',
                'codeID', 'resNameNo', 'actNameNo', 'projNameNo', 'regionBranch', 'division',
                'resourceCategory', 'wildfire', 'expenseRevenue', 'fireActivities', 'mPRACategory'])]


@register(CorporateStrategy)
class CorporateStrategyAdmin(ModelAdmin):
    list_display = ['financialYear', 'corporateStrategyNo', 'description1']
    list_filter = ['financialYear']
    actions = [
        export_as_csv_action(
            fields=[
                'id',
                'financialYear',
                'corporateStrategyNo',
                'description1',
                'description2'],
            translations=['id', 'financialYear', 'IBMSCSNo', 'IBMSCSDesc1', 'IBMSCSDesc2'])]


@register(GeneralServicePriority)
class GeneralServicePriorityAdmin(ModelAdmin):
    list_display = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    list_filter = ['financialYear']
    search_fields = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    actions = [
        export_as_csv_action(
            translations=['id', 'financialYear', 'CategoryID', 'SerPriNo', 'StratPlanNo',
                          'IBMCS', 'Description 1', 'Description 2'],
            fields=[
                'id', 'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo',
                'corporateStrategyNo', 'description', 'description2'])]


@register(NCServicePriority)
class NCServicePriorityAdmin(ModelAdmin):
    list_display = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    list_filter = ['financialYear', 'categoryID']
    search_fields = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo',
        'description', 'target', 'action', 'milestone']
    actions = [
        export_as_csv_action(
            translations=[
                'id', 'financialYear', 'CategoryID', 'SerPriNo', 'StratPlanNo',
                'IBMCS', 'AssetNo',
                'Asset', 'TargetNo', 'Target', 'ActionNo', 'Action', 'MileNo', 'Milestone'],
            fields=[
                'id', 'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo',
                'corporateStrategyNo', 'assetNo',
                'asset', 'targetNo', 'target', 'actionNo', 'action', 'mileNo', 'milestone'])]


@register(PVSServicePriority)
class PVSServicePriorityAdmin(ModelAdmin):
    list_display = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    list_filter = ['financialYear']
    search_fields = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    actions = [
        export_as_csv_action(
            translations=[
                'id', 'financialYear', 'CategoryID', 'SerPriNo', 'StratPlanNo',
                'IBMCS', 'SerPri1', 'SerPri', 'PVSExampleAnnWP',
                'PVSExampleActNo'],
            fields=[
                'id', 'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo',
                'corporateStrategyNo', 'description', 'pvsExampleAnnWP', 'pvsExampleActNo',
                'servicePriority1'])]


@register(SFMServicePriority)
class SFMServicePriorityAdmin(ModelAdmin):
    list_display = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    list_filter = ['financialYear']
    actions = [
        export_as_csv_action(
            translations=[
                'id', 'financialYear', 'CategoryID', 'Region', 'SerPriNo', 'StratPlanNo',
                'IBMCS', 'SerPri1', 'SerPri2'],
            fields=[
                'id', 'financialYear', 'categoryID', 'regionBranch', 'servicePriorityNo', 'strategicPlanNo',
                'corporateStrategyNo', 'description', 'description2'])]


@register(ERServicePriority)
class ERServicePriorityAdmin(ModelAdmin):
    list_display = [
        'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo', 'corporateStrategyNo']
    list_filter = ['financialYear']
    actions = [
        export_as_csv_action(
            translations=[
                'id', 'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo',
                'corporateStrategyNo', 'description', 'pvsExampleAnnWP', 'pvsExampleActNo',
                'classification'],
            fields=[
                'id', 'financialYear', 'categoryID', 'servicePriorityNo', 'strategicPlanNo',
                'corporateStrategyNo', 'description', 'pvsExampleAnnWP', 'pvsExampleActNo',
                'classification'])]


@register(NCStrategicPlan)
class NCStrategicPlanAdmin(ModelAdmin):
    list_filter = ['financialYear']
    list_display = [
        'financialYear',
        'strategicPlanNo',
        'directionNo',
        'direction']
    actions = [
        export_as_csv_action(
            translations=[
                'id', 'financialYear', 'StratPlanNo', 'StratDirNo', 'StratDir', 'AimNo', 'Aim1',
                'Aim2', 'ActNo', 'Action'],
            fields=[
                'id', 'financialYear', 'strategicPlanNo', 'directionNo', 'direction', 'AimNo', 'Aim1',
                'Aim2', 'ActionNo', 'Action'])]


@register(Outcomes)
class OutcomesAdmin(ModelAdmin):
    list_display = ('financialYear', 'q1Input')
    list_filter = ('financialYear',)
    actions = [
        export_as_csv_action(
            translations=[
                'id',
                'financialYear',
                'q1Input',
                'q2Input',
                'q3Input',
                'q4Input'],
            fields=['id', 'financialYear', 'q1Input', 'q2Input', 'q3Input', 'q4Input'])]

@register(ServicePriorityMappings)
class ServicePriorityMappings(ModelAdmin):
    list_display = ('costCentreNo', 'financialYear')
    list_filter = ('financialYear',)
    actions = [
        export_as_csv_action(
            translations=[
                'financialYear',
                'costCentreNo',
                'wildlifeManagement',
                'parksManagement',
                'forestManagement'],
            fields =['financialYear','costCentreNo', 'wildlifeManagement', 'parksManagement', 'forestManagement'])]
