import csv
from django.db import transaction
import xlwt

from ibms.models import (IBMData, GLPivDownload, CorporateStrategy,
                     NCStrategicPlan, NCServicePriority, ERServicePriority,
                     GeneralServicePriority, PVSServicePriority,
                     SFMServicePriority)

CSV_FILE_LIMIT = 100000000


def export_ibms_data(response, fy):
    writer = csv.writer(response, quoting=csv.QUOTE_ALL)
    glrows = GLPivDownload.objects.filter(financialYear=fy).order_by('codeID')
    writer.writerow(["IBM ID",
                     "FinancialYear",
                     "DownloadPeriod",
                     "CostCentre",
                     "Account",
                     "Service",
                     "Activity",
                     "Resource",
                     "Project",
                     "Job",
                     "ShortCode",
                     "ShortCodeName",
                     "GLCode",
                     "ptdActual",
                     "ptdBudget",
                     "ytdActual",
                     "ytdBudget",
                     "fybudget",
                     "ytdVariance",
                     "ccName",
                     "serviceName",
                     "activityName",
                     "resourceName"
                     "jobName",
                     "codeIdentifier",
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
                     "CS Description1",
                     "CS Description2",
                     "Strategic Direction No",
                     "Strategic Direction",
                     "Aim No",
                     "Aim 1",
                     "Aim 2",
                     "Action No",
                     "Action Description",
                     "SP Description1",
                     "SP Description2"])

    for r in glrows.iterator():
        if IBMData.objects.filter(
                ibmIdentifier=r.codeID, financialYear=fy).exists():
            ibm = IBMData.objects.get(ibmIdentifier=r.codeID, financialYear=fy)
        else:
            ibm = IBMData()

        if CorporateStrategy.objects.filter(
                corporateStrategyNo=ibm.corporatePlanNo,
                financialYear=fy).exists():
            cs = CorporateStrategy.objects.get(
                corporateStrategyNo=ibm.corporatePlanNo,
                financialYear=fy)
        else:
            cs = CorporateStrategy()

        if NCStrategicPlan.objects.filter(
                strategicPlanNo=ibm.strategicPlanNo,
                financialYear=fy).exists():
            nc = NCStrategicPlan.objects.get(
                strategicPlanNo=ibm.strategicPlanNo,
                financialYear=fy)
        else:
            nc = NCStrategicPlan()

        sp = NCServicePriority()
        d1 = ""
        d2 = ""
        if ERServicePriority.objects.filter(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy).exists():
            sp = ERServicePriority.objects.get(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy)
            d1 = sp.classification
            d2 = sp.description
        if GeneralServicePriority.objects.filter(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy).exists():
            sp = GeneralServicePriority.objects.get(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy)
            d1 = sp.description
            d2 = sp.description2
        if PVSServicePriority.objects.filter(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy).exists():
            sp = PVSServicePriority.objects.get(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy)
            d1 = sp.servicePriority1
            d2 = sp.description
        if SFMServicePriority.objects.filter(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy).exists():
            sp = SFMServicePriority.objects.get(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy)
            d1 = sp.description
            d2 = sp.description2
        if NCServicePriority.objects.filter(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy).exists():
            sp = NCServicePriority.objects.get(
                servicePriorityNo=ibm.servicePriorityID,
                financialYear=fy)
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
    csvfile = open(fileName, "rb")
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


def import_to_ibmdata(fileName, finyear):
    rdr, csvfile, fileName = csvload(fileName)
    i = 2
    try:
        for row in rdr:
            data = {
                "financialYear": finyear,
                "ibmIdentifier": validateCharField("ibmsIdentifier", 50, row[0]),
                "costCentre": validateCharField('costCentre', 4, row[1]),
                "account": row[2],
                "service": row[3],
                "activity": validateCharField('activity', 4, row[4]),
                "project": validateCharField('project', 6, row[5]),
                "job": validateCharField('job', 6, row[6]),
                "budgetArea": validateCharField('budgetArea', 50, row[7]),
                "projectSponsor": validateCharField('projectSponsor', 50, unicode(str(row[8]), errors='ignore')),
                "corporatePlanNo": validateCharField('corporatePlanNo', 20, row[9]),
                "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[10]),
                "regionalSpecificInfo": row[11],
                "servicePriorityID": validateCharField('servicePriorityID', 100, row[12]),
                "annualWPInfo": unicode(str(row[13]), errors='ignore')
            }
            query = {
                "financialYear": finyear,
                "ibmIdentifier": str(row[0])
            }
            saverow(IBMData, data, query)
            i += 1
        csvfile.close()
    except Exception as e:
        csvfile.close()
        raise Exception(e)
        #raise Exception('Row {0} has ill formed data. please remedy and retry'.format(i))


@transaction.atomic
def import_to_glpivotdownload(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    i = 0
    try:
        for row in rdr:
            data = {
                'financialYear': finyear,
                'downloadPeriod': validateCharField('downloadPeriod', 10, row[0]),
                'costCentre': validateCharField('costCentre', 4, row[1]),
                'account': row[2],
                'service': row[3],
                'activity': validateCharField('activity', 4, row[4]),
                'resource': row[5],
                'project': validateCharField('project', 6, row[6]),
                'job': validateCharField('job', 6, row[7]),
                'shortCode': validateCharField('shortCode', 20, row[8]),
                'shortCodeName': validateCharField('shortCodeName', 200, row[9]),
                'gLCode': validateCharField('gLCode', 30, row[10]),
                'ptdActual': row[11],
                'ptdBudget': row[12],
                'ytdActual': row[13],
                'ytdBudget': row[14],
                'fybudget': row[15],
                'ytdVariance': row[16],
                'ccName': validateCharField('ccName', 100, row[17]),
                'serviceName': validateCharField('serviceName', 100, row[18]),
                'activityName': validateCharField('activityName', 100, row[19]),
                'resourceName': validateCharField('resourceName', 100, row[20]),
                'projectName': validateCharField('projectName', 100, row[21]),
                'jobName': validateCharField('jobName', 100, row[22]),
                'codeID': validateCharField('codeID', 30, row[23]),
                'resNameNo': validateCharField('resNameNo', 100, row[24]),
                'actNameNo': validateCharField('actNameNo', 100, row[25]),
                'projNameNo': validateCharField('projNameNo', 100, row[26]),
                'regionBranch': validateCharField('regionBranch', 100, row[27]),
                'division': validateCharField('division', 100, row[28]),
                'resourceCategory': validateCharField('resourceCategory', 100, row[29]),
                'wildfire': validateCharField('wildfire', 30, row[30]),
                'expenseRevenue': validateCharField('expenseRevenue', 7, row[31]),
                'fireActivities': validateCharField('fireActivities', 50, row[32]),
                'mPRACategory': validateCharField('mPRACategory', 100, row[33])}

            query = {
                'financialYear': finyear,
                'gLCode': str(row[10])
            }
            i += 1
            saverow(GLPivDownload, data, query)
        file.close()
    except:
        file.close()
        raise Exception(
            'An error occured populating table:\nRow {0}\n{1}'.format(i, ','.join(row)))


def import_to_corporate_strategy(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:
            data = {
                "financialYear": finyear,
                "corporateStrategyNo": validateCharField('corporateStrategyNo', 10, row[0]),
                "description1": unicode(str(row[1]), errors='ignore'),
                "description2": unicode(str(row[2]), errors='ignore')
            }
            query = {
                "financialYear": finyear,
                "corporateStrategyNo": str(row[0])
            }
            saverow(CorporateStrategy, data, query)
        file.close()
    except:
        file.close()
        raise


def import_to_nc_strategic_plan(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in rdr:
            data = {
                "financialYear": finyear,
                "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[0]),
                "directionNo": validateCharField('directionNo', 20, row[1]),
                "direction": unicode(str(row[2]), errors='ignore'),
                "AimNo": validateCharField('directionNo', 20, row[3]),
                "Aim1": unicode(str(row[4]), errors='ignore'),
                "Aim2": unicode(str(row[5]), errors='ignore'),
                "ActionNo": validateCharField('directionNo', 20, row[6]),
                "Action": unicode(str(row[7]), errors='ignore')
            }
            query = {
                "financialYear": finyear,
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


def import_to_pvs_service_priority(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:

            data = {
                "financialYear": validateCharField('financialYear', 7, finyear),
                "categoryID": validateCharField('categoryID', 30, row[0]),
                "servicePriorityNo": validateCharField('servicePriorityNo', 100, row[1]),
                "strategicPlanNo": validateCharField('strategicPlanNo', 100, row[2]),
                "corporateStrategyNo": row[3],
                "servicePriority1": unicode(str(row[4]), errors='ignore'),
                "description": unicode(str(row[5]), errors='ignore'),
                "pvsExampleAnnWP": unicode(str(row[6]), errors='ignore'),
                "pvsExampleActNo": unicode(str(row[7]))
            }

            query = {
                "financialYear": finyear,
                "servicePriorityNo": str(row[1])
            }
            saverow(PVSServicePriority, data, query)

        file.close()
    except:
        file.close()
        raise


def import_to_sfm_service_priority(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:
            data = {
                "financialYear": finyear,
                "categoryID": validateCharField('categoryID', 30, row[0]),
                "regionBranch": validateCharField('regionBranch', 20, row[1]),
                "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[2]),
                "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[3]),
                "corporateStrategyNo": row[4],
                "description": unicode(str(row[5]), errors='ignore'),
                "description2": unicode(str(row[6]), errors='ignore')
            }
            query = {
                "financialYear": finyear,
                "servicePriorityNo": validateCharField(
                    'servicePriorityNo',
                    20,
                    row[2])}
            saverow(SFMServicePriority, data, query)

        file.close()

    except:
        file.close()
        raise


def import_to_er_service_priority(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:
            data = {
                "financialYear": validateCharField('financialYear', 7, finyear),
                "categoryID": validateCharField('categoryID', 30, row[0]),
                "servicePriorityNo": validateCharField('servicePriorityNo', 10, row[1]),
                "strategicPlanNo": validateCharField('strategicPlanNo', 10, row[2]),
                "corporateStrategyNo": row[3],
                "classification": unicode(str(row[4]), errors='ignore'),
                "description": unicode(str(row[5]), errors='ignore')
            }
            query = {
                "financialYear": finyear,
                "servicePriorityNo": str(row[1])
            }
            saverow(ERServicePriority, data, query)

        file.close()

    except:
        file.close()
        raise


def import_to_general_service_priority(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:
            try:
                data = {
                    "financialYear": finyear,
                    "categoryID": validateCharField('categoryID', 30, row[0]),
                    "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[1]),
                    "strategicPlanNo": validateCharField('strategicPlanNo', 20, row[2]),
                    "corporateStrategyNo": row[3],
                    "description": unicode(str(row[4]), errors='ignore'),
                    "description2": unicode(str(row[5]), errors='ignore')
                }
                query = {
                    "financialYear": finyear,
                    "servicePriorityNo": str(row[1])
                }

                saverow(GeneralServicePriority, data, query)

            except:
                raise

        file.close()
    except:
        file.close()
        raise


def import_to_nc_service_priority(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        for row in rdr:
            data = {
                "financialYear": finyear,
                "categoryID": validateCharField('categoryID', 30, row[0]),
                "servicePriorityNo": validateCharField('servicePriorityNo', 100, row[1]),
                "strategicPlanNo": validateCharField('strategicPlanNo', 100, row[2]),
                "corporateStrategyNo": validateCharField('corporateStrategyNo', 100, row[3]),
                "assetNo": validateCharField('AssetNo', 5, row[4]),
                "asset": unicode(str(row[5]), errors='ignore'),
                "targetNo": validateCharField('Asset', 30, row[6]),
                "target": unicode(str(row[7]), errors='ignore'),
                "actionNo": unicode(str(row[8]), errors='ignore'),
                "action": unicode(str(row[9]), errors='ignore'),
                "mileNo": validateCharField('MileNo', 30, row[10]),
                "milestone": unicode(str(row[11]), errors='ignore')
            }
            query = {
                "financialYear": finyear,
                "servicePriorityNo": str(row[1])
            }
            saverow(NCServicePriority, data, query)

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
        "financialYear",
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
        "financialYear",
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
          r["financialYear"],
            r) for r in ibmrows))

    csrows = CorporateStrategy.objects.values(
        "corporateStrategyNo",
        "financialYear",
        "description1",
        "description2")
    csdict = dict(
        ((r["corporateStrategyNo"] +
          "_" +
          r["financialYear"],
            r) for r in csrows))

    ncrows = NCStrategicPlan.objects.values(
        "strategicPlanNo",
        "financialYear",
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
          r["financialYear"],
            r) for r in ncrows))

    spdict = dict()
    ncsprows = NCServicePriority.objects.values_list(
        "servicePriorityNo", "financialYear", "action", "milestone")
    sfmsprows = SFMServicePriority.objects.values_list(
        "servicePriorityNo", "financialYear", "description", "description2")
    pvssprows = PVSServicePriority.objects.values_list(
        "servicePriorityNo",
        "financialYear",
        "servicePriority1",
        "description")
    gensprows = GeneralServicePriority.objects.values_list(
        "servicePriorityNo", "financialYear", "description", "description2")
    ersprows = ERServicePriority.objects.values_list(
        "servicePriorityNo", "financialYear", "classification", "description")

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
                row["financialYear"],
                dict()))
        if "corporatePlanNo" in outputdict.keys():
            outputdict.update(
                csdict.get(
                    outputdict["corporatePlanNo"] +
                    "_" +
                    row["financialYear"],
                    dict()))
        if "strategicPlanNo" in outputdict.keys():
            outputdict.update(
                ncdict.get(
                    outputdict["strategicPlanNo"] +
                    "_" +
                    row["financialYear"],
                    dict()))
        if "servicePriorityID" in outputdict.keys():
            d1, d2 = spdict.get(
                outputdict["servicePriorityID"] + "_" + row["financialYear"], ("", "", "", ""))[2:]
            outputdict.update({"d1": d1, "d2": d2})
        xlrow = list()
        for key in [
                "codeID",
                "financialYear",
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
