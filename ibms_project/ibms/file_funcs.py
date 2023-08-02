import csv
from ibms import db_funcs


COLS_GLPIVOT = 34
COLS_CORPORATE_PLAN_DATA = 3
COLS_ER_SERVICE_PRIORITY = 6
COLS_SFM_SERVICE_PRIORITY = 7
COLS_PVS_SERVICE_PRIORITY = 8
COLS_GENERAL_SERVICE_PRIORITY = 6
COLS_NC_SERVICE_PRIORITY = 12
COLS_NC_STRATEGIC_PLAN = 8
COLS_SET_SERVICE_PRIORITY = 4


def process_upload_file(fileName, fileType, fy):
    if fileType == 'GLPivotDownload':
        db_funcs.import_to_glpivotdownload(fileName, fy)
    elif fileType == 'IBMData':
        db_funcs.import_to_ibmdata(fileName, fy)
    elif fileType == 'CorporateStrategyData':
        db_funcs.import_to_corporate_strategy(fileName, fy)
    elif fileType == 'ERServicePriorityData':
        db_funcs.import_to_er_service_priority(fileName, fy)
    elif fileType == 'PVSServicePriorityData':
        db_funcs.import_to_pvs_service_priority(fileName, fy)
    elif fileType == 'SFMServicePriorityData':
        db_funcs.import_to_sfm_service_priority(fileName, fy)
    elif fileType == 'NCStrategyData':
        db_funcs.import_to_nc_strategic_plan(fileName, fy)
    elif fileType == 'GeneralServicePriorityData':
        db_funcs.import_to_general_service_priority(fileName, fy)
    elif fileType == 'NCServicePriorityData':
        db_funcs.import_to_nc_service_priority(fileName, fy)
    elif fileType == 'ServicePriorityMappings':
        db_funcs.import_to_service_priority_mappings(fileName, fy)
    else:
        raise Exception('process_upload_file : file type {} unknown'.format(fileType))


def validate_file(file, fileType):
    """Utility function called by the Upload view to validate uploaded files.
    Should return True or raise an Exception.
    """
    reader = csv.reader(file, dialect='excel')
    if fileType == 'GLPivotDownload':
        return validate_glpivotdownload_headers(reader)
    elif fileType == 'IBMData':
        return validate_ibmdata_headers(reader)
    elif fileType == 'NCStrategyData':
        return validate_nc_strategicplan_headers(reader)
    elif fileType == 'CorporateStrategyData':
        return validate_corporatestrategydata_headers(reader)
    elif fileType == 'ERServicePriorityData':
        return validate_er_servicepriority_headers(reader)
    elif fileType == 'PVSServicePriorityData':
        return validate_pvs_servicepriority_headers(reader)
    elif fileType == 'SFMServicePriorityData':
        return validate_sfm_servicepriority_headers(reader)
    elif fileType == 'GeneralServicePriorityData':
        return validate_general_servicepriority_headers(reader)
    elif fileType == 'NCServicePriorityData':
        return validate_nc_servicepriority_headers(reader)
    elif fileType == 'ServicePriorityMappings':
        return validate_settings_service_priority_headers(reader)
    else:
        raise Exception('validate_file: unknown file type {}'.format(fileType))


def validate_corporatestrategydata_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_CORPORATE_PLAN_DATA:
        bad_headings = ''
        if row[0].strip() != 'IBMSCSNo':
            bad_headings += row[0] + ' : ' + 'IBMSCSNo\n'
        if row[1].strip() != 'IBMSCSDesc1':
            bad_headings += row[1] + ' : ' + 'IBMSCSDesc1\n'
        if row[2].strip() != 'IBMSCSDesc2':
            bad_headings += row[2] + ' : ' + 'IBMSCSDesc2\n'
        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_CORPORATE_PLAN_DATA) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_ibmdata_headers(reader):
    """Function to validate an uploaded CSV of IBMData records.
    """
    row = next(reader)  # Get the first (header) row.
    valid_count = 19
    column_count = len(row)

    if column_count == valid_count:  # Correct number of columns.
        # Check column headings.
        bad_headings = ''
        headings = [
            'ibmIdentifier',
            'costCentre',
            'account',
            'service',
            'activity',
            'project',
            'job',
            'budgetArea',
            'projectSponsor',
            'corporatePlanNo',
            'strategicPlanNo',
            'regionalSpecificInfo',
            'servicePriorityID',
            'annualWPInfo',
            'priorityActionNo',
            'priorityLevel',
            'marineKPI',
            'regionProject',
            'regionDescription',
        ]
        for k, heading in enumerate(headings):
            if row[k].strip() != heading:
                bad_headings += f'{row[k]}: {heading}\n'

        if bad_headings:
            raise Exception(f'The column headings in the CSV file do not match the required headings\n{bad_headings}')
    else:  # Incorrect number of columns
        raise Exception(f'The number of columns in the CSV file do not match the required column count:\nExpects {valid_count}, met {column_count}')

    return True


def validate_glpivotdownload_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_GLPIVOT:
        bad_headings = ''
        if row[0].strip() != 'Download Period':
            bad_headings += row[0] + ' : ' + 'Download Period\n'
        if row[1].strip() != 'CC':
            bad_headings += row[1] + ' : ' + 'CC\n'
        if row[2].strip() != 'Account':
            bad_headings += row[2] + ' : ' + 'Account\n'
        if row[3].strip() != 'Service':
            bad_headings += row[3] + ' : ' + 'Service\n'
        if row[4].strip() != 'Activity':
            bad_headings += row[4] + ' : ' + 'Activity\n'
        if row[5].strip() != 'Resource':
            bad_headings += row[5] + ' : ' + 'Resource\n'
        if row[6].strip() != 'Project':
            bad_headings += row[6] + ' : ' + 'Project\n'
        if row[7].strip() != 'Job':
            bad_headings += row[7] + ' : ' + 'Job\n'
        if row[8].strip() != 'Shortcode':
            bad_headings += row[8] + ' : ' + 'Shortcode\n'
        if row[9].strip() != 'Shortcode_Name':
            bad_headings += row[9] + ' : ' + 'Shortcode_Name\n'
        if row[10].strip() != 'GL_Code':
            bad_headings += row[10] + ' : ' + 'GL_Code\n'
        if row[11].strip() != 'PTD_Actual':
            bad_headings += row[11] + ' : ' + 'PTD_Actual\n'
        if row[12].strip() != 'PTD_Budget':
            bad_headings += row[12] + ' : ' + 'PTD_Budget\n'
        if row[13].strip() != 'YTD_Actual':
            bad_headings += row[13] + ' : ' + 'YTD_Actual\n'
        if row[14].strip() != 'YTD_Budget':
            bad_headings += row[14] + ' : ' + 'YTD_Budget\n'
        if row[15].strip() != 'FY_Budget':
            bad_headings += row[15] + ' : ' + 'FY_Budget\n'
        if row[16].strip() != 'YTD_Variance':
            bad_headings += row[16] + ' : ' + 'YTD_Variance\n'
        if row[17].strip() != 'CC_Name':
            bad_headings += row[17] + ' : ' + 'CC_Name\n'
        if row[18].strip() != 'Service Name':
            bad_headings += row[18] + ' : ' + 'Service Name\n'
        if row[19].strip() != 'Activity_Name':
            bad_headings += row[19] + ' : ' + 'Activity_Name\n'
        if row[20].strip() != 'Resource_Name':
            bad_headings += row[20] + ' : ' + 'Resource_Name\n'
        if row[21].strip() != 'Project_Name':
            bad_headings += row[21] + ' : ' + 'Project_Name\n'
        if row[22].strip() != 'Job_Name':
            bad_headings += row[22] + ' : ' + 'Job_Name\n'
        if row[23].strip() != 'Code identifier':
            bad_headings += row[23] + ' : ' + 'Code identifier\n'
        if row[24].strip() != 'ResNmNo':
            bad_headings += row[24] + ' : ' + 'ResNmNo\n'
        if row[25].strip() != 'ActNmNo':
            bad_headings += row[25] + ' : ' + 'ActNmNo\n'
        if row[26].strip() != 'ProjNmNo':
            bad_headings += row[26] + ' : ' + 'ProjNmNo\n'
        if row[27].strip() != 'Region/Branch':
            bad_headings += row[27] + ' : ' + 'Region/Branch\n'
        if row[28].strip() != 'Division':
            bad_headings += row[28] + ' : ' + 'Division\n'
        if row[29].strip() != 'Resource Category':
            bad_headings += row[29] + ' : ' + 'Resource Category\n'
        if row[30].strip() != 'Wildfire':
            bad_headings += row[30] + ' : ' + 'Wildfire\n'
        if row[31].strip() != 'Exp_Rev':
            bad_headings += row[31] + ' : ' + 'Exp_Rev\n'
        if row[32].strip() != 'Fire Activities':
            bad_headings += row[32] + ' : ' + 'Fire Activities\n'
        if row[33].strip() != 'MPRA Category':
            bad_headings += row[33] + ' : ' + 'MPRA Category'

        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings \n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_GLPIVOT) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_general_servicepriority_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_GENERAL_SERVICE_PRIORITY:
        bad_headings = ''
        if row[0].strip() != 'CategoryID':
            bad_headings += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            bad_headings += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            bad_headings += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            bad_headings += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'Description 1':
            bad_headings += row[4] + ' : ' + 'Description 1\n'
        if row[5].strip() != 'Description 2':
            bad_headings += row[5] + ' : ' + 'Description 2\n'
        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_GENERAL_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_er_servicepriority_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_ER_SERVICE_PRIORITY:
        bad_headings = ''
        if row[0].strip() != 'CategoryID':
            bad_headings += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            bad_headings += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            bad_headings += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            bad_headings += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'Env Regs Specific Classification':
            bad_headings += row[4] + ' : ' + 'Env Regs Specific Classification\n'
        if row[5].strip() != 'Env Regs Specific Description':
            bad_headings += row[5] + ' : ' + 'Env Regs Specific Description\n'

        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_ER_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_sfm_servicepriority_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_SFM_SERVICE_PRIORITY:
        bad_headings = ''
        if row[0].strip() != 'CategoryID':
            bad_headings += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'Region':
            bad_headings += row[1] + ' : ' + 'Region\n'
        if row[2].strip() != 'SerPriNo':
            bad_headings += row[2] + ' : ' + 'SerPriNo\n'
        if row[3].strip() != 'StratPlanNo':
            bad_headings += row[3] + ' : ' + 'StratPlanNo\n'
        if row[4].strip() != 'IBMCS':
            bad_headings += row[4] + ' : ' + 'IBMCS\n'
        if row[5].strip() != 'SerPri1':
            bad_headings += row[5] + ' : ' + 'SerPri1\n'
        if row[6].strip() != 'SerPri2':
            bad_headings += row[6] + ' : ' + 'SerPri2\n'

        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_SFM_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_pvs_servicepriority_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_PVS_SERVICE_PRIORITY:
        bad_headings = ''
        if row[0].strip() != 'CategoryID':
            bad_headings += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            bad_headings += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            bad_headings += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            bad_headings += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'SerPri1':
            bad_headings += row[4] + ' : ' + 'SerPri1\n'
        if row[5].strip() != 'SerPri':
            bad_headings += row[5] + ' : ' + 'SerPri\n'
        if row[6].strip() != 'PVSExampleAnnWP':
            bad_headings += row[6] + ' : ' + 'PVSExampleAnnWP\n'
        if row[7].strip() != 'PVSExampleActNo':
            bad_headings += row[7] + ' : ' + 'PVSExampleActNo\n'

        return_value = (bad_headings.strip() == '')

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_PVS_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_nc_servicepriority_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_NC_SERVICE_PRIORITY:
        bad_headings = ''
        if row[0].strip() != 'CategoryID':
            bad_headings += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            bad_headings += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            bad_headings += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            bad_headings += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'AssetNo':
            bad_headings += row[4] + ' : ' + 'AssetNo\n'
        if row[5].strip() != 'Asset':
            bad_headings += row[5] + ' : ' + 'Asset\n'
        if row[6].strip() != 'TargetNo':
            bad_headings += row[6] + ' : ' + 'TargetNo\n'
        if row[7].strip() != 'Target':
            bad_headings += row[7] + ' : ' + 'Target\n'
        if row[8].strip() != 'ActionNo':
            bad_headings += row[8] + ' : ' + 'ActionNo\n'
        if row[9].strip() != 'Action':
            bad_headings += row[9] + ' : ' + 'Action\n'
        if row[10].strip() != 'MileNo':
            bad_headings += row[10] + ' : ' + 'MileNo\n'
        if row[11].strip() != 'Milestone':
            bad_headings += row[11] + ' : ' + 'Milestone\n'
        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_NC_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_nc_strategicplan_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_NC_STRATEGIC_PLAN:
        bad_headings = ''
        if row[0].strip() != 'StratPlanNo':
            bad_headings += row[0] + ' : ' + 'StratPlanNo\n'
        if row[1].strip() != 'StratDirNo':
            bad_headings += row[1] + ' : ' + 'StratDirNo\n'
        if row[2].strip() != 'StratDir':
            bad_headings += row[2] + ' : ' + 'StratDir\n'
        if row[3].strip() != 'AimNo':
            bad_headings += row[3] + ' : ' + 'AimNo\n'
        if row[4].strip() != 'Aim1':
            bad_headings += row[4] + ' : ' + 'Aim1\n'
        if row[5].strip() != 'Aim2':
            bad_headings += row[5] + ' : ' + 'Aim2\n'
        if row[6].strip() != 'ActNo':
            bad_headings += row[6] + ' : ' + 'ActNo\n'
        if row[7].strip() != 'Action':
            bad_headings += row[7] + ' : ' + 'Action\n'

        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_NC_STRATEGIC_PLAN) +
            ' met ' +
            str(
                len(row)))

    return return_value


def validate_settings_service_priority_headers(reader):
    return_value = False
    row = next(reader)
    if len(row) == COLS_SET_SERVICE_PRIORITY:
        bad_headings = ''
        if row[0].strip() != 'CC No.':
            bad_headings += row[0] + ' : ' + 'CC No.\n'
        if row[1].strip() != 'Wildlife Management':
            bad_headings += row[1] + ' : ' + 'Wildlife Management\n'
        if row[2].strip() != 'Parks Management':
            bad_headings += row[2] + ' : ' + 'Parks Management\n'
        if row[3].strip() != 'Forest Management':
            bad_headings += row[3] + ' : ' + 'Forest Management\n'

        return_value = bad_headings == ''

        if not return_value:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                bad_headings)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_SET_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return return_value
