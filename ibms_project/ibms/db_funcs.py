import csv
from datetime import datetime
from django.db import transaction
import xlwt

from ibms.models import (
    IBMData, GLPivDownload, CorporateStrategy, NCStrategicPlan, NCServicePriority,
    ERServicePriority, GeneralServicePriority, PVSServicePriority, SFMServicePriority,
    ServicePriorityMappings)

CSV_FILE_LIMIT = 100000000


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
    csvfile = open(fileName, 'r')
    csv.field_size_limit(CSV_FILE_LIMIT)
    rdr = csv.reader(csvfile, dialect='excel', quotechar=str('"'))
    if not csv.Sniffer().has_header(csvfile.readline()):
        rdr.seek(0)
    return rdr, csvfile, fileName


def saverow(model, data, query):
    # Query the database for an existing object based on ``query``, and update it with ``data``.
    # Alternatively, just create a new object with ``data``.
    if model.objects.filter(**query).exists():
        # We won't bother raising an exception if there are multiple rows returned by the filter().
        # We'll rely on any natural keys defined on the model to maintain
        # database integrity.
        obj = model.objects.filter(**query).update(**data)
        return
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
                "annualWPInfo": str(row[13])
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
        except:
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
    try:
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
    except:
        file.close()
        raise


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
    try:
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
    except:
        file.close()
        raise


def import_to_sfm_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    try:
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

    except:
        file.close()
        raise


def import_to_er_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    try:
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

    except:
        file.close()
        raise


def import_to_general_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:
            try:
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

            except:
                raise

        file.close()
    except:
        file.close()
        raise


def import_to_nc_service_priority(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    try:
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
    except:
        file.close()
        raise


def import_to_service_priority_mappings(fileName, fy):
    rdr, file, fileName = csvload(fileName)
    try:
        query = {
            "fy": fy
        }
        query_results = ServicePriorityMappings.objects.filter(**query)
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
    except:
        file.close()
        raise


def validateCharField(fieldName, fieldLen, data):
    if (len(data.strip()) > fieldLen):
        raise Exception('Field ' + fieldName + ' cannot be truncated')
    return data.strip()


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
        except:
            pass
        try:
            xlrow[9] = int(xlrow[9])  # job
        except:
            pass

        for col, cell in enumerate(xlrow):
            sheet.write(row_num, col, cell)

    return book
