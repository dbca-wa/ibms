import codecs
import csv
from datetime import datetime
from django.conf import settings
from django.db import transaction
import xlwt

from ibms.models import (
    IBMData, GLPivDownload, CorporateStrategy, NCStrategicPlan, NCServicePriority,
    ERServicePriority, GeneralServicePriority, PVSServicePriority, SFMServicePriority,
    ServicePriorityMappings)


def get_download_period():
    """Return the 'newest' download_period date value for all the GLPivDownload objects.
    """
    if not GLPivDownload.objects.exists():
        return datetime.today()
    elif not GLPivDownload.objects.filter(download_period__isnull=False).exists():
        return datetime.today()
    return GLPivDownload.objects.order_by('-download_period').first().download_period


def validateCharField(fieldName, fieldLen, data):
    if (len(data.strip()) > fieldLen):
        raise Exception('Field ' + fieldName + ' cannot be truncated')
    return data.strip()


def export_ibms_data(response, fy):
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    glrows = GLPivDownload.objects.filter(fy=fy).order_by('codeID')
    writer.writerow([
        "IBM ID", "Financial year", "DownloadPeriod", "CostCentre", "Account", "Service",
        "Activity", "Resource", "Project", "Job", "ShortCode", "ShortCodeName", "GLCode",
        "ptdActual", "ptdBudget", "ytdActual", "ytdBudget", "fybudget", "ytdVariance",
        "ccName", "serviceName", "activityName", "resourceName", "jobName", "codeIdentifier",
        "resNameNo", "actNameNo", "projNameNo", "regionBranch", "division", "resourceCategory",
        "wildfire", "expenseRevenue", "fireActivities", "mPRACategory", "budgetArea",
        "projectSponsor", "corporatePlanNo", "strategicPlanNo", "regionalSpecificInfo",
        "servicePriorityID", "annualWPInfo", "CS Description1", "CS Description2",
        "Strategic Direction No", "Strategic Direction", "Aim No", "Aim 1", "Aim 2",
        "Action No", "Action Description", "SP Description1", "SP Description2"
    ])

    for r in glrows.iterator():
        if IBMData.objects.filter(ibmIdentifier=r.codeID, fy=fy).exists():
            ibm = IBMData.objects.get(ibmIdentifier=r.codeID, fy=fy)
        else:
            ibm = IBMData()

        if CorporateStrategy.objects.filter(corporateStrategyNo=ibm.corporatePlanNo, fy=fy).exists():
            cs = CorporateStrategy.objects.get(corporateStrategyNo=ibm.corporatePlanNo, fy=fy)
        else:
            cs = CorporateStrategy()

        if NCStrategicPlan.objects.filter(strategicPlanNo=ibm.strategicPlanNo, fy=fy).exists():
            nc = NCStrategicPlan.objects.get(strategicPlanNo=ibm.strategicPlanNo, fy=fy)
        else:
            nc = NCStrategicPlan()

        sp = NCServicePriority()
        d1 = ""
        d2 = ""
        if ERServicePriority.objects.filter(servicePriorityNo=ibm.servicePriorityID, fy=fy).exists():
            sp = ERServicePriority.objects.get(servicePriorityNo=ibm.servicePriorityID, fy=fy)
            d1 = sp.classification
            d2 = sp.description
        if GeneralServicePriority.objects.filter(servicePriorityNo=ibm.servicePriorityID, fy=fy).exists():
            sp = GeneralServicePriority.objects.get(servicePriorityNo=ibm.servicePriorityID, fy=fy)
            d1 = sp.description
            d2 = sp.description2
        if PVSServicePriority.objects.filter(servicePriorityNo=ibm.servicePriorityID, fy=fy).exists():
            sp = PVSServicePriority.objects.get(servicePriorityNo=ibm.servicePriorityID, fy=fy)
            d1 = sp.servicePriority1
            d2 = sp.description
        if SFMServicePriority.objects.filter(servicePriorityNo=ibm.servicePriorityID, fy=fy).exists():
            sp = SFMServicePriority.objects.get(servicePriorityNo=ibm.servicePriorityID, fy=fy)
            d1 = sp.description
            d2 = sp.description2
        if NCServicePriority.objects.filter(servicePriorityNo=ibm.servicePriorityID, fy=fy).exists():
            sp = NCServicePriority.objects.get(servicePriorityNo=ibm.servicePriorityID, fy=fy)
            d1 = sp.action
            d2 = sp.milestone

        writer.writerow([ibm.ibmIdentifier,
                         fy,
                         r.downloadPeriod,
                         r.costCentre,
                         r.account,
                         r.service,
                         r.activity,
                         r.resource,
                         r.project,
                         r.job,
                         r.shortCode,
                         r.shortCodeName,
                         r.gLCode,
                         r.ptdActual,
                         r.ptdBudget,
                         r.ytdActual,
                         r.ytdBudget,
                         r.fybudget,
                         r.ytdVariance,
                         r.ccName,
                         r.serviceName,
                         r.jobName,
                         r.resNameNo,
                         r.actNameNo,
                         r.projNameNo,
                         r.regionBranch,
                         r.division,
                         r.resourceCategory,
                         r.wildfire,
                         r.expenseRevenue,
                         r.fireActivities,
                         r.mPRACategory,
                         ibm.budgetArea,
                         ibm.projectSponsor,
                         ibm.corporatePlanNo,
                         ibm.strategicPlanNo,
                         ibm.regionalSpecificInfo,
                         ibm.servicePriorityID,
                         ibm.annualWPInfo,
                         cs.description1,
                         cs.description2,
                         nc.directionNo,
                         nc.direction,
                         nc.AimNo,
                         nc.Aim1,
                         nc.Aim2,
                         nc.ActionNo,
                         nc.Action,
                         d1,
                         d2])
    return response


def csvload(fileName):
    csvfile = codecs.open(fileName, encoding="utf-8", errors="ignore")
    csv.field_size_limit(settings.CSV_FILE_LIMIT)
    rdr = csv.reader(csvfile, dialect='excel', quotechar=str('"'))
    if not csv.Sniffer().has_header(csvfile.readline()):
        rdr.seek(0)
    return rdr, csvfile, fileName


def saverow(model, data, query):
    # Query the database for an existing object based on ``query``, and update it with ``data``.
    # Alternatively, just create a new object with ``data``.
    if model.objects.filter(**query).exists():
        # We won't bother raising an exception if there are multiple rows returned by the filter().
        # We'll rely on any natural keys defined on the model to maintain database integrity.
        obj = model.objects.filter(**query).update(**data)
    else:
        obj = model(**data)
        obj.save()


def import_to_ibmdata(fileName, fy):
    rdr, csvfile, fileName = csvload(fileName)
    i = 2
    try:
        for row in rdr:
            data = {
                "fy": fy,
                "ibmIdentifier": validateCharField("ibmsIdentifier", 50, row[0]),
                "costCentre": validateCharField('costCentre', 4, row[1]),
                "account": row[2],
                "service": row[3],
                "activity": validateCharField('activity', 4, row[4]),
                "project": validateCharField('project', 6, row[5]),
                "job": validateCharField('job', 6, row[6]),
                "budgetArea": validateCharField('budgetArea', 50, row[7]),
                "projectSponsor": validateCharField('projectSponsor', 50, str(row[8])),
                "corporatePlanNo": validateCharField('corporatePlanNo', 20, row[9]),
                "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[10]),
                "regionalSpecificInfo": row[11],
                "servicePriorityID": validateCharField('servicePriorityID', 100, row[12]),
                "annualWPInfo": str(row[13]),
                "priorityActionNo": str(row[14]),
                "priorityLevel": str(row[15]),
                "marineKPI": str(row[16]),
                "regionProject": str(row[17]),
                "regionDescription": str(row[18]),
            }
            query = {
                "fy": fy,
                "ibmIdentifier": str(row[0])
            }
            saverow(IBMData, data, query)
            i += 1
        csvfile.close()
    except Exception as e:
        csvfile.close()
        raise Exception(e)


@transaction.atomic
def import_to_glpivotdownload(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    glpiv = []
    for row in rdr:
        try:
            download_period = datetime.strptime(row[0], "%d/%m/%Y")
        except ValueError:
            download_period = None
        glpiv.append(
            GLPivDownload(
                fy=fy, download_period=download_period, downloadPeriod=row[0], costCentre=row[1],
                account=row[2], service=row[3], activity=row[4], resource=row[5],
                project=row[6], job=row[7], shortCode=row[8], shortCodeName=row[9],
                gLCode=row[10], ptdActual=row[11], ptdBudget=row[12], ytdActual=row[13],
                ytdBudget=row[14], fybudget=row[15], ytdVariance=row[16], ccName=row[17],
                serviceName=row[18], activityName=row[19], resourceName=row[20],
                projectName=row[21], jobName=row[22], codeID=row[23], resNameNo=row[24],
                actNameNo=row[25], projNameNo=row[26], regionBranch=row[27],
                division=row[28], resourceCategory=row[29], wildfire=row[30],
                expenseRevenue=row[31], fireActivities=row[32], mPRACategory=row[33]
            )
        )
    GLPivDownload.objects.bulk_create(glpiv)


def import_to_corporate_strategy(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    for row in rdr:
        data = {
            "fy": fy,
            "corporateStrategyNo": validateCharField('corporateStrategyNo', 10, row[0]),
            "description1": str(row[1]),
            "description2": str(row[2])
        }
        query = {
            "fy": fy,
            "corporateStrategyNo": str(row[0])
        }
        saverow(CorporateStrategy, data, query)
    file.close()


def import_to_nc_strategic_plan(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in rdr:
            data = {
                "fy": fy,
                "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[0]),
                "directionNo": validateCharField('directionNo', 20, row[1]),
                "direction": str(row[2]),
                "AimNo": validateCharField('directionNo', 20, row[3]),
                "Aim1": str(row[4]),
                "Aim2": str(row[5]),
                "ActionNo": validateCharField('directionNo', 20, row[6]),
                "Action": str(row[7])
            }
            query = {
                "fy": fy,
                "strategicPlanNo": str(row[0])
            }
            saverow(NCStrategicPlan, data, query)
            i + i + 1

        file.close()
    except NCServicePriority.DoesNotExist:
        file.close()
        raise Exception(
            'Row {0}:{1}\nPlease import NC Service Priority data before proceeding, otherwise database integrity will be compromised.'.format(
                i,
                row[0]))


def import_to_pvs_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    for row in rdr:

        data = {
            "fy": fy,
            "categoryID": validateCharField('categoryID', 30, row[0]),
            "servicePriorityNo": validateCharField('servicePriorityNo', 100, row[1]),
            "strategicPlanNo": validateCharField('strategicPlanNo', 100, row[2]),
            "corporateStrategyNo": row[3],
            "servicePriority1": str(row[4]),
            "description": str(row[5]),
            "pvsExampleAnnWP": str(row[6]),
            "pvsExampleActNo": str(row[7])
        }

        query = {
            "fy": fy,
            "servicePriorityNo": str(row[1])
        }
        saverow(PVSServicePriority, data, query)

    file.close()


def import_to_sfm_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    for row in rdr:
        data = {
            "fy": fy,
            "categoryID": validateCharField('categoryID', 30, row[0]),
            "regionBranch": validateCharField('regionBranch', 20, row[1]),
            "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[2]),
            "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[3]),
            "corporateStrategyNo": row[4],
            "description": str(row[5]),
            "description2": str(row[6])
        }
        query = {
            "fy": fy,
            "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[2])}
        saverow(SFMServicePriority, data, query)

    file.close()


def import_to_er_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    for row in rdr:
        data = {
            "fy": fy,
            "categoryID": validateCharField('categoryID', 30, row[0]),
            "servicePriorityNo": validateCharField('servicePriorityNo', 10, row[1]),
            "strategicPlanNo": validateCharField('strategicPlanNo', 10, row[2]),
            "corporateStrategyNo": row[3],
            "classification": str(row[4]),
            "description": str(row[5])
        }
        query = {
            "fy": fy,
            "servicePriorityNo": str(row[1])
        }
        saverow(ERServicePriority, data, query)

    file.close()


def import_to_general_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    for row in rdr:
        data = {
            "fy": fy,
            "categoryID": validateCharField('categoryID', 30, row[0]),
            "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[1]),
            "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[2]),
            "corporateStrategyNo": row[3],
            "description": str(row[4]),
            "description2": str(row[5])
        }
        query = {
            "fy": fy,
            "servicePriorityNo": str(row[1])
        }

        saverow(GeneralServicePriority, data, query)

    file.close()


def import_to_nc_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    for row in rdr:
        data = {
            "fy": fy,
            "categoryID": validateCharField('categoryID', 30, row[0]),
            "servicePriorityNo": validateCharField('servicePriorityNo', 100, row[1]),
            "strategicPlanNo": validateCharField('strategicPlanNo', 100, row[2]),
            "corporateStrategyNo": validateCharField('corporateStrategyNo', 100, row[3]),
            "assetNo": validateCharField('AssetNo', 5, row[4]),
            "asset": str(row[5]),
            "targetNo": validateCharField('Asset', 30, row[6]),
            "target": str(row[7]),
            "actionNo": str(row[8]),
            "action": str(row[9]),
            "mileNo": validateCharField('MileNo', 30, row[10]),
            "milestone": str(row[11])
        }
        query = {
            "fy": fy,
            "servicePriorityNo": str(row[1])
        }
        saverow(NCServicePriority, data, query)

    file.close()


def import_to_service_priority_mappings(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    query_results = ServicePriorityMappings.objects.filter(fy=fy)
    if query_results.exists():
        query_results.delete()
    for row in rdr:
        data = {
            "fy": fy,
            "costCentreNo": validateCharField('costCentreNo', 4, row[0]),
            "wildlifeManagement": validateCharField('wildlifeManagement', 100, row[1]),
            "parksManagement": validateCharField('parksManagement', 100, row[2]),
            "forestManagement": validateCharField('forestManagement', 100, row[3])
        }
        obj = ServicePriorityMappings(**data)
        obj.save()
    file.close()


def download_ibms_data(glrows):
    rows = glrows.values(
        "codeID",
        "fy",
        "downloadPeriod",
        "costCentre",
        "account",
        "service",
        "activity",
        "resource",
        "project",
        "job",
        "shortCode",
        "shortCodeName",
        "gLCode",
        "ptdActual",
        "ptdBudget",
        "ytdActual",
        "ytdBudget",
        "fybudget",
        "ytdVariance",
        "ccName",
        "serviceName",
        "jobName",
        "resNameNo",
        "actNameNo",
        "projNameNo",
        "regionBranch",
        "division",
        "resourceCategory",
        "wildfire",
        "expenseRevenue",
        "fireActivities",
        "mPRACategory")

    ibmrows = IBMData.objects.values(
        "ibmIdentifier",
        "fy",
        "budgetArea",
        "projectSponsor",
        "corporatePlanNo",
        "strategicPlanNo",
        "regionalSpecificInfo",
        "servicePriorityID",
        "annualWPInfo")
    ibmdict = dict(
        ((r["ibmIdentifier"] +
          "_" +
          r["fy"],
            r) for r in ibmrows))

    csrows = CorporateStrategy.objects.values(
        "corporateStrategyNo",
        "fy",
        "description1",
        "description2")
    csdict = dict(
        ((r["corporateStrategyNo"] +
          "_" +
          r["fy"],
            r) for r in csrows))

    ncrows = NCStrategicPlan.objects.values(
        "strategicPlanNo",
        "fy",
        "directionNo",
        "direction",
        "AimNo",
        "Aim1",
        "Aim2",
        "ActionNo",
        "Action")
    ncdict = dict(
        ((r["strategicPlanNo"] +
          "_" +
          r["fy"],
            r) for r in ncrows))

    spdict = dict()
    ncsprows = NCServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "action", "milestone")
    sfmsprows = SFMServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "description", "description2")
    pvssprows = PVSServicePriority.objects.values_list(
        "servicePriorityNo",
        "fy",
        "servicePriority1",
        "description")
    gensprows = GeneralServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "description", "description2")
    ersprows = ERServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "classification", "description")

    # order important
    for sprows in [ncsprows, sfmsprows, pvssprows, gensprows, ersprows]:
        spdict.update(dict(((r[0] + "_" + r[1], r) for r in sprows)))

    book = xlwt.Workbook()
    sheet = book.add_sheet('Sheet 1')
    headers = [
        "IBMS ID",
        "Financial Year",
        "Download Period",
        "Cost Centre",
        "Account",
        "Service",
        "Activity",
        "Resource",
        "Project",
        "Job",
        "Short Code",
        "Short Code Name",
        "GL Code",
        "ptd Actual",
        "ptd Budget",
        "ytd Actual",
        "ytd Budget",
        "fy Budget",
        "ytd Variance",
        "cc Name",
        "Service Name",
        "Job Name",
        "Res Name No",
        "Act Name No",
        "Proj Name No",
        "Region/Branch",
        "Division",
        "Resource Category",
        "Wildfire",
        "Expense Revenue",
        "Fire Activities",
        "mPRACategory",
        "Budget Area",
        "Project Sponsor",
        "Corporate Strategy No",
        "Strategic Plan No",
        "Regional Specific Info",
        "Service Priority No",
        "Annual Works Plan",
        "Corp Strategy Description 1",
        "Corp Strategy Description 2",
        "Nat Cons Strategic Direction No",
        "Nat Cons Strat Direction Desc",
        "Nat Cons Strat Plan Aim No",
        "Nat Cons Strat Plan Aim Desc 1",
        "Nat Cons Strat Plan Aim Desc 2",
        "Nat Cons Strat Plan Action No",
        "Nat Cons Strat Plan Action Description",
        "Service Priority Description 1",
        "Service Priority Description 2"]

    for col, h in enumerate(headers):
        sheet.write(0, col, h)

    for row_num, row in enumerate(rows, 1):
        outputdict = row
        outputdict.update(
            ibmdict.get(
                row["codeID"] +
                "_" +
                row["fy"],
                dict()))
        if "corporatePlanNo" in outputdict.keys():
            outputdict.update(
                csdict.get(
                    outputdict["corporatePlanNo"] +
                    "_" +
                    row["fy"],
                    dict()))
        if "strategicPlanNo" in outputdict.keys():
            outputdict.update(
                ncdict.get(
                    outputdict["strategicPlanNo"] +
                    "_" +
                    row["fy"],
                    dict()))
        if "servicePriorityID" in outputdict.keys():
            d1, d2 = spdict.get(
                outputdict["servicePriorityID"] + "_" + row["fy"], ("", "", "", ""))[2:]
            outputdict.update({"d1": d1, "d2": d2})
        xlrow = list()
        for key in [
                "codeID",
                "fy",
                "downloadPeriod",
                "costCentre",
                "account",
                "service",
                "activity",
                "resource",
                "project",
                "job",
                "shortCode",
                "shortCodeName",
                "gLCode",
                "ptdActual",
                "ptdBudget",
                "ytdActual",
                "ytdBudget",
                "fybudget",
                "ytdVariance",
                "ccName",
                "serviceName",
                "jobName",
                "resNameNo",
                "actNameNo",
                "projNameNo",
                "regionBranch",
                "division",
                "resourceCategory",
                "wildfire",
                "expenseRevenue",
                "fireActivities",
                "mPRACategory",
                "budgetArea",
                "projectSponsor",
                "corporatePlanNo",
                "strategicPlanNo",
                "regionalSpecificInfo",
                "servicePriorityID",
                "annualWPInfo",
                "description1",
                "description2",
                "directionNo",
                "direction",
                "AimNo",
                "Aim1",
                "Aim2",
                "ActionNo",
                "Action",
                "d1",
                "d2"]:
            xlrow.append(outputdict.get(key, ""))

        # Conditionally cast some string values as ints.
        xlrow[3] = int(xlrow[3])  # costCentre
        try:
            xlrow[8] = int(xlrow[8])  # project
        except ValueError:
            pass
        try:
            xlrow[9] = int(xlrow[9])  # job
        except ValueError:
            pass

        for col, cell in enumerate(xlrow):
            sheet.write(row_num, col, cell)

    return book


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
        import_to_glpivotdownload(fileName, fy)
    elif fileType == 'IBMData':
        import_to_ibmdata(fileName, fy)
    elif fileType == 'CorporateStrategyData':
        import_to_corporate_strategy(fileName, fy)
    elif fileType == 'ERServicePriorityData':
        import_to_er_service_priority(fileName, fy)
    elif fileType == 'PVSServicePriorityData':
        import_to_pvs_service_priority(fileName, fy)
    elif fileType == 'SFMServicePriorityData':
        import_to_sfm_service_priority(fileName, fy)
    elif fileType == 'NCStrategyData':
        import_to_nc_strategic_plan(fileName, fy)
    elif fileType == 'GeneralServicePriorityData':
        import_to_general_service_priority(fileName, fy)
    elif fileType == 'NCServicePriorityData':
        import_to_nc_service_priority(fileName, fy)
    elif fileType == 'ServicePriorityMappings':
        import_to_service_priority_mappings(fileName, fy)
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
    """Function to validate an uploaded CSV of GLPivot records.
    """
    # TODO: refactor this insane function.
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
