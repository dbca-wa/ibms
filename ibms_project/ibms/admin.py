import csv
from ibms import models
from django.contrib import admin
from django.http import HttpResponse


def export_as_csv_action(fields=None, translations=None, exclude=None,
                         header=True, description='Export selected objects to CSV'):
    '''
    This function add an "Export as CSV" action to a model in the Django admin site.
    Register the action using the ModelAdmin ``action`` option.
    ``fields`` and ``exclude`` work the same as those Django ModelForm options (use one or the other).
    ``header`` defines whether or not the column names are output as the first row.

    Example usage::
        class ReferralAdmin(admin.ModelAdmin):
            list_display = ('id', 'region', 'type', 'reference')
            date_hierarchy = 'created'
            actions = [export_as_csv_action(fields=['id','reference'], header=False),]

        admin.site.register(Referral, ReferralAdmin)

    Adapted from::
        http://djangosnippets.org/snippets/2020/
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
            writer.writerow([unicode(getattr(obj, field))
                             for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv


class IBMDataAdmin(admin.ModelAdmin):
    search_fields = (
        'financialYear',
        'ibmIdentifier',
        'budgetArea',
        'corporatePlanNo',
        'strategicPlanNo')
    list_display = (
        'financialYear',
        'ibmIdentifier',
        'budgetArea',
        'corporatePlanNo',
        'strategicPlanNo')
    list_filter = (
        'financialYear',
        'costCentre',
        'budgetArea',
        'service',
        'corporatePlanNo')
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


class GLPivDownloadAdmin(admin.ModelAdmin):
    search_fields = (
        'financialYear', 'costCentre', 'account', 'service', 'activity', 'ccName', 'shortCode',
        'shortCodeName', 'gLCode', 'codeID')
    list_display = (
        'financialYear',
        'costCentre',
        'account',
        'service',
        'activity',
        'ccName')
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


class CorporateStrategyAdmin(admin.ModelAdmin):
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


class GeneralServicePriorityAdmin(admin.ModelAdmin):
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


class NCServicePriorityAdmin(admin.ModelAdmin):
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


class PVSServicePriorityAdmin(admin.ModelAdmin):
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


class SFMServicePriorityAdmin(admin.ModelAdmin):
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


class ERServicePriorityAdmin(admin.ModelAdmin):
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


class NCStrategicPlanAdmin(admin.ModelAdmin):
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


class OutcomesAdmin(admin.ModelAdmin):
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


admin.site.register(models.IBMData, IBMDataAdmin)
admin.site.register(models.GLPivDownload, GLPivDownloadAdmin)
admin.site.register(models.CorporateStrategy, CorporateStrategyAdmin)
admin.site.register(models.GeneralServicePriority, GeneralServicePriorityAdmin)
admin.site.register(models.NCServicePriority, NCServicePriorityAdmin)
admin.site.register(models.PVSServicePriority, PVSServicePriorityAdmin)
admin.site.register(models.SFMServicePriority, SFMServicePriorityAdmin)
admin.site.register(models.ERServicePriority, ERServicePriorityAdmin)
admin.site.register(models.NCStrategicPlan, NCStrategicPlanAdmin)
admin.site.register(models.Outcomes, OutcomesAdmin)
