import csv
from ibms import db_funcs


COLS_IBMDATA = 14
COLS_GLPIVOT = 34
COLS_CORPORATE_PLAN_DATA = 3
COLS_ER_SERVICE_PRIORITY = 6
COLS_SFM_SERVICE_PRIORITY = 7
COLS_PVS_SERVICE_PRIORITY = 8
COLS_GENERAL_SERVICE_PRIORITY = 6
COLS_NC_SERVICE_PRIORITY = 12
COLS_NC_STRATEGIC_PLAN = 8


def process_upload_file(fileName, fileType, fy):
    if fileType == "Staging":
        db_funcs.import_to_staging(fileName)
    elif fileType == "GLPivotDownload":
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
    else:
        raise Exception(
            'func: process_upload_file : file type ' +
            fileType +
            ' unknown')


def validate_file(file, fileType):
    rdr = csv.reader(file, dialect='excel')
    if fileType == 'GLPivotDownload':
        return validate_glpivotdownload_hdr(rdr)
    elif fileType == 'IBMData':
        return validate_ibmdata_hdr(rdr)
    elif fileType == 'NCStrategyData':
        return validate_nc_strategicplan_hdr(rdr)
    elif fileType == 'CorporateStrategyData':
        return validate_corporatestrategydata_hdr(rdr)
    elif fileType == 'ERServicePriorityData':
        return validate_er_servicepriority_hdr(rdr)
    elif fileType == 'PVSServicePriorityData':
        return validate_pvs_servicepriority_hdr(rdr)
    elif fileType == 'SFMServicePriorityData':
        return validate_sfm_servicepriority_hdr(rdr)
    elif fileType == 'GeneralServicePriorityData':
        return validate_general_servicepriority_hdr(rdr)
    elif fileType == 'NCServicePriorityData':
        return validate_nc_servicepriority_hdr(rdr)
    else:
        raise Exception("Attempting to validate and unknown file type of " + fileType)


def validate_corporatestrategydata_hdr(rdr):
    retval = False
    row = next(rdr)
    if len(row) == COLS_CORPORATE_PLAN_DATA:
        sBad = ''
        if row[0].strip() != 'IBMSCSNo':
            sBad += row[0] + ' : ' + 'IBMSCSNo\n'
        if row[1].strip() != 'IBMSCSDesc1':
            sBad += row[1] + ' : ' + 'IBMSCSDesc1\n'
        if row[2].strip() != 'IBMSCSDesc2':
            sBad += row[2] + ' : ' + 'IBMSCSDesc2\n'
        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_CORPORATE_PLAN_DATA) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_ibmdata_hdr(rdr):
    retVal = False
    row = next(rdr)
    if len(row) == COLS_IBMDATA:
        sBad = ''

        if row[0].strip() != 'ibmIdentifier':
            sBad += row[0] + ' : ' + 'ibmIdentifier\n'
        if row[1].strip() != 'costCentre':
            sBad += row[1] + ' : ' + 'costCentre\n'
        if row[2].strip() != 'account':
            sBad += row[2] + ' : ' + 'account\n'
        if row[3].strip() != 'service':
            sBad += row[3] + ' : ' + 'service\n'
        if row[4].strip() != 'activity':
            sBad += row[4] + ' : ' + 'activity\n'
        if row[5].strip() != 'project':
            sBad += row[5] + ' : ' + 'project\n'
        if row[6].strip() != 'job':
            sBad += row[6] + ' : ' + 'job\n'
        if row[7].strip() != 'budgetArea':
            sBad += row[7] + ' : ' + 'budgetArea\n'
        if row[8].strip() != 'projectSponsor':
            sBad += row[8] + ' : ' + 'projectSponsor\n'
        if row[9].strip() != 'corporatePlanNo':
            sBad += row[9] + ' : ' + 'corporatePlanNo\n'
        if row[10].strip() != 'strategicPlanNo':
            sBad += row[10] + ' : ' + 'strategicPlanNo\n'
        if row[11].strip() != 'regionalSpecificInfo':
            sBad += row[11] + ' : ' + 'regionalSpecificInfo\n'
        if row[12].strip() != 'servicePriorityID':
            sBad += row[12] + ' : ' + 'servicePriorityID\n'
        if row[13].strip() != 'annualWPInfo':
            sBad += row[13] + ' : ' + 'annualWPInfo\n'

        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_IBMDATA) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_glpivotdownload_hdr(rdr):
    retVal = False
    row = next(rdr)
    if len(row) == COLS_GLPIVOT:
        sBad = ''
        if row[0].strip() != 'Download Period':
            sBad += row[0] + ' : ' + 'Download Period\n'
        if row[1].strip() != 'CC':
            sBad += row[1] + ' : ' + 'CC\n'
        if row[2].strip() != 'Account':
            sBad += row[2] + ' : ' + 'Account\n'
        if row[3].strip() != 'Service':
            sBad += row[3] + ' : ' + 'Service\n'
        if row[4].strip() != 'Activity':
            sBad += row[4] + ' : ' + 'Activity\n'
        if row[5].strip() != 'Resource':
            sBad += row[5] + ' : ' + 'Resource\n'
        if row[6].strip() != 'Project':
            sBad += row[6] + ' : ' + 'Project\n'
        if row[7].strip() != 'Job':
            sBad += row[7] + ' : ' + 'Job\n'
        if row[8].strip() != 'Shortcode':
            sBad += row[8] + ' : ' + 'Shortcode\n'
        if row[9].strip() != 'Shortcode_Name':
            sBad += row[9] + ' : ' + 'Shortcode_Name\n'
        if row[10].strip() != 'GL_Code':
            sBad += row[10] + ' : ' + 'GL_Code\n'
        if row[11].strip() != 'PTD_Actual':
            sBad += row[11] + ' : ' + 'PTD_Actual\n'
        if row[12].strip() != 'PTD_Budget':
            sBad += row[12] + ' : ' + 'PTD_Budget\n'
        if row[13].strip() != 'YTD_Actual':
            sBad += row[13] + ' : ' + 'YTD_Actual\n'
        if row[14].strip() != 'YTD_Budget':
            sBad += row[14] + ' : ' + 'YTD_Budget\n'
        if row[15].strip() != 'FY_Budget':
            sBad += row[15] + ' : ' + 'FY_Budget\n'
        if row[16].strip() != 'YTD_Variance':
            sBad += row[16] + ' : ' + 'YTD_Variance\n'
        if row[17].strip() != 'CC_Name':
            sBad += row[17] + ' : ' + 'CC_Name\n'
        if row[18].strip() != 'Service Name':
            sBad += row[18] + ' : ' + 'Service Name\n'
        if row[19].strip() != 'Activity_Name':
            sBad += row[19] + ' : ' + 'Activity_Name\n'
        if row[20].strip() != 'Resource_Name':
            sBad += row[20] + ' : ' + 'Resource_Name\n'
        if row[21].strip() != 'Project_Name':
            sBad += row[21] + ' : ' + 'Project_Name\n'
        if row[22].strip() != 'Job_Name':
            sBad += row[22] + ' : ' + 'Job_Name\n'
        if row[23].strip() != 'Code identifier':
            sBad += row[23] + ' : ' + 'Code identifier\n'
        if row[24].strip() != 'ResNmNo':
            sBad += row[24] + ' : ' + 'ResNmNo\n'
        if row[25].strip() != 'ActNmNo':
            sBad += row[25] + ' : ' + 'ActNmNo\n'
        if row[26].strip() != 'ProjNmNo':
            sBad += row[26] + ' : ' + 'ProjNmNo\n'
        if row[27].strip() != 'Region/Branch':
            sBad += row[27] + ' : ' + 'Region/Branch\n'
        if row[28].strip() != 'Division':
            sBad += row[28] + ' : ' + 'Division\n'
        if row[29].strip() != 'Resource Category':
            sBad += row[29] + ' : ' + 'Resource Category\n'
        if row[30].strip() != 'Wildfire':
            sBad += row[30] + ' : ' + 'Wildfire\n'
        if row[31].strip() != 'Exp_Rev':
            sBad += row[31] + ' : ' + 'Exp_Rev\n'
        if row[32].strip() != 'Fire Activities':
            sBad += row[32] + ' : ' + 'Fire Activities\n'
        if row[33].strip() != 'MPRA Category':
            sBad += row[33] + ' : ' + 'MPRA Category'

        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings \n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_GLPIVOT) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_general_servicepriority_hdr(rdr):
    retval = False
    row = next(rdr)
    if len(row) == COLS_GENERAL_SERVICE_PRIORITY:
        sBad = ''
        if row[0].strip() != 'CategoryID':
            sBad += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            sBad += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            sBad += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            sBad += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'Description 1':
            sBad += row[4] + ' : ' + 'Description 1\n'
        if row[5].strip() != 'Description 2':
            sBad += row[5] + ' : ' + 'Description 2\n'
        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_GENERAL_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_er_servicepriority_hdr(rdr):
    retval = False
    row = next(rdr)
    if len(row) == COLS_ER_SERVICE_PRIORITY:
        sBad = ''
        if row[0].strip() != 'CategoryID':
            sBad += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            sBad += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            sBad += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            sBad += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'Env Regs Specific Classification':
            sBad += row[4] + ' : ' + 'Env Regs Specific Classification\n'
        if row[5].strip() != 'Env Regs Specific Description':
            sBad += row[5] + ' : ' + 'Env Regs Specific Description\n'

        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_ER_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_sfm_servicepriority_hdr(rdr):
    retval = False
    row = next(rdr)
    if len(row) == COLS_SFM_SERVICE_PRIORITY:
        sBad = ''
        if row[0].strip() != 'CategoryID':
            sBad += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'Region':
            sBad += row[1] + ' : ' + 'Region\n'
        if row[2].strip() != 'SerPriNo':
            sBad += row[2] + ' : ' + 'SerPriNo\n'
        if row[3].strip() != 'StratPlanNo':
            sBad += row[3] + ' : ' + 'StratPlanNo\n'
        if row[4].strip() != 'IBMCS':
            sBad += row[4] + ' : ' + 'IBMCS\n'
        if row[5].strip() != 'SerPri1':
            sBad += row[5] + ' : ' + 'SerPri1\n'
        if row[6].strip() != 'SerPri2':
            sBad += row[6] + ' : ' + 'SerPri2\n'

        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_SFM_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_pvs_servicepriority_hdr(rdr):
    retval = False
    row = next(rdr)
    if len(row) == COLS_PVS_SERVICE_PRIORITY:
        sBad = ''
        if row[0].strip() != 'CategoryID':
            sBad += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            sBad += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            sBad += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            sBad += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'SerPri1':
            sBad += row[4] + ' : ' + 'SerPri1\n'
        if row[5].strip() != 'SerPri':
            sBad += row[5] + ' : ' + 'SerPri\n'
        if row[6].strip() != 'PVSExampleAnnWP':
            sBad += row[6] + ' : ' + 'PVSExampleAnnWP\n'
        if row[7].strip() != 'PVSExampleActNo':
            sBad += row[7] + ' : ' + 'PVSExampleActNo\n'

        retVal = (sBad.strip() == '')

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_PVS_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_nc_servicepriority_hdr(rdr):
    retval = False
    row = next(rdr)
    if len(row) == COLS_NC_SERVICE_PRIORITY:
        sBad = ''
        if row[0].strip() != 'CategoryID':
            sBad += row[0] + ' : ' + 'CategoryID\n'
        if row[1].strip() != 'SerPriNo':
            sBad += row[1] + ' : ' + 'SerPriNo\n'
        if row[2].strip() != 'StratPlanNo':
            sBad += row[2] + ' : ' + 'StratPlanNo\n'
        if row[3].strip() != 'IBMCS':
            sBad += row[3] + ' : ' + 'IBMCS\n'
        if row[4].strip() != 'AssetNo':
            sBad += row[4] + ' : ' + 'AssetNo\n'
        if row[5].strip() != 'Asset':
            sBad += row[5] + ' : ' + 'Asset\n'
        if row[6].strip() != 'TargetNo':
            sBad += row[6] + ' : ' + 'TargetNo\n'
        if row[7].strip() != 'Target':
            sBad += row[7] + ' : ' + 'Target\n'
        if row[8].strip() != 'ActionNo':
            sBad += row[8] + ' : ' + 'ActionNo\n'
        if row[9].strip() != 'Action':
            sBad += row[9] + ' : ' + 'Action\n'
        if row[10].strip() != 'MileNo':
            sBad += row[10] + ' : ' + 'MileNo\n'
        if row[11].strip() != 'Milestone':
            sBad += row[11] + ' : ' + 'Milestone\n'
        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_NC_SERVICE_PRIORITY) +
            ' met ' +
            str(
                len(row)))

    return retVal


def validate_nc_strategicplan_hdr(rdr):
    retVal = False
    row = next(rdr)
    if len(row) == COLS_NC_STRATEGIC_PLAN:
        sBad = ''
        if row[0].strip() != 'StratPlanNo':
            sBad += row[0] + ' : ' + 'StratPlanNo\n'
        if row[1].strip() != 'StratDirNo':
            sBad += row[1] + ' : ' + 'StratDirNo\n'
        if row[2].strip() != 'StratDir':
            sBad += row[2] + ' : ' + 'StratDir\n'
        if row[3].strip() != 'AimNo':
            sBad += row[3] + ' : ' + 'AimNo\n'
        if row[4].strip() != 'Aim1':
            sBad += row[4] + ' : ' + 'Aim1\n'
        if row[5].strip() != 'Aim2':
            sBad += row[5] + ' : ' + 'Aim2\n'
        if row[6].strip() != 'ActNo':
            sBad += row[6] + ' : ' + 'ActNo\n'
        if row[7].strip() != 'Action':
            sBad += row[7] + ' : ' + 'Action\n'

        retVal = sBad == ''

        if not retVal:
            raise Exception(
                'The column headings in the CSV file do not match the required headings\n' +
                sBad)
    else:
        raise Exception(
            'The number of columns in the CSV file do not match the required column count :\nExpects ' +
            str(COLS_NC_STRATEGIC_PLAN) +
            ' met ' +
            str(
                len(row)))

    return retVal
