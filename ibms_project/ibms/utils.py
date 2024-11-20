import codecs
import csv
from datetime import datetime

import xlwt
from django.conf import settings
from django.db import transaction

from ibms.models import (
    CorporateStrategy,
    ERServicePriority,
    GeneralServicePriority,
    GLPivDownload,
    IBMData,
    NCServicePriority,
    NCStrategicPlan,
    PVSServicePriority,
    ServicePriorityMappings,
    SFMServicePriority,
)


def get_download_period():
    """Return the 'newest' download_period date value for all the GLPivDownload objects."""
    if not GLPivDownload.objects.exists():
        return datetime.today()
    elif not GLPivDownload.objects.filter(download_period__isnull=False).exists():
        return datetime.today()
    return GLPivDownload.objects.order_by("-download_period").first().download_period


def validate_char_field(field_name, max_length, data):
    """For a passed-in string value, validate it doesn't exceed a maximum length."""
    if len(data.strip()) > max_length:
        raise Exception(f"Field {field_name} exceeds maximum length of {max_length}")
    return data.strip()


def csvload(file_name):
    csvfile = codecs.open(file_name, encoding="utf-8", errors="ignore")
    csv.field_size_limit(settings.CSV_FILE_LIMIT)
    reader = csv.reader(csvfile, dialect="excel", quotechar=str('"'))
    if not csv.Sniffer().has_header(csvfile.readline()):
        reader.seek(0)
    return reader, csvfile, file_name


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


def import_to_ibmdata(file_name, fy):
    """Utility function to import data from the uploaded CSV to the IBMData table."""
    reader, csvfile, file_name = csvload(file_name)

    for row in reader:
        data = {
            "fy": fy,
            "ibmIdentifier": validate_char_field("ibmIdentifier", 50, row[0]),
            "costCentre": validate_char_field("costCentre", 4, row[1]),
            "account": row[2],
            "service": row[3],
            "activity": validate_char_field("activity", 4, row[4]),
            "project": validate_char_field("project", 6, row[5]),
            "job": validate_char_field("job", 6, row[6]),
            "budgetArea": validate_char_field("budgetArea", 50, row[7]),
            "projectSponsor": validate_char_field("projectSponsor", 50, str(row[8])),
            "regionalSpecificInfo": row[9],
            "servicePriorityID": validate_char_field("servicePriorityID", 100, row[10]),
            "annualWPInfo": str(row[11]),
            "priorityActionNo": str(row[12]),
            "priorityLevel": str(row[13]),
            "marineKPI": str(row[14]),
            "regionProject": str(row[15]),
            "regionDescription": str(row[16]),
        }
        query = {"fy": fy, "ibmIdentifier": str(row[0])}
        saverow(IBMData, data, query)

    csvfile.close()


@transaction.atomic
def import_to_glpivotdownload(file_name, fy):
    reader, file, file_name = csvload(file_name)
    glpiv = []
    for row in reader:
        try:
            download_period = datetime.strptime(row[0], "%d/%m/%Y")
        except ValueError:
            download_period = None
        glpiv.append(
            GLPivDownload(
                fy=fy,
                download_period=download_period,
                downloadPeriod=row[0],
                costCentre=row[1],
                account=row[2],
                service=row[3],
                activity=row[4],
                resource=row[5],
                project=row[6],
                job=row[7],
                shortCode=row[8],
                shortCodeName=row[9],
                gLCode=row[10],
                ptdActual=row[11],
                ptdBudget=row[12],
                ytdActual=row[13],
                ytdBudget=row[14],
                fybudget=row[15],
                ytdVariance=row[16],
                ccName=row[17],
                serviceName=row[18],
                activityName=row[19],
                resourceName=row[20],
                projectName=row[21],
                jobName=row[22],
                codeID=row[23],
                resNameNo=row[24],
                actNameNo=row[25],
                projNameNo=row[26],
                regionBranch=row[27],
                division=row[28],
                resourceCategory=row[29],
                wildfire=row[30],
                expenseRevenue=row[31],
                fireActivities=row[32],
                mPRACategory=row[33],
            )
        )
    GLPivDownload.objects.bulk_create(glpiv)


def import_to_corporate_strategy(file_name, fy):
    reader, file, file_name = csvload(file_name)
    for row in reader:
        data = {
            "fy": fy,
            "corporateStrategyNo": validate_char_field("corporateStrategyNo", 10, row[0]),
            "description1": str(row[1]),
            "description2": str(row[2]),
        }
        query = {"fy": fy, "corporateStrategyNo": str(row[0])}
        saverow(CorporateStrategy, data, query)
    file.close()


def import_to_nc_strategic_plan(file_name, fy):
    reader, file, file_name = csvload(file_name)
    i = 1
    try:
        for row in reader:
            data = {
                "fy": fy,
                "strategicPlanNo": validate_char_field("strategicPlanNo", 20, row[0]),
                "directionNo": validate_char_field("directionNo", 20, row[1]),
                "direction": str(row[2]),
                "aimNo": validate_char_field("directionNo", 20, row[3]),
                "aim1": str(row[4]),
                "aim2": str(row[5]),
                "actionNo": validate_char_field("directionNo", 20, row[6]),
                "action": str(row[7]),
            }
            query = {"fy": fy, "strategicPlanNo": str(row[0])}
            saverow(NCStrategicPlan, data, query)
            i += 1

        file.close()
    except NCServicePriority.DoesNotExist:
        file.close()
        raise Exception(
            "Row {}:{}\nPlease import NC Service Priority data before proceeding, otherwise database integrity will be compromised.".format(
                i, row[0]
            )
        )


def import_to_pvs_service_priority(file_name, fy):
    reader, file, file_name = csvload(file_name)
    for row in reader:
        data = {
            "fy": fy,
            "categoryID": validate_char_field("categoryID", 30, row[0]),
            "servicePriorityNo": validate_char_field("servicePriorityNo", 100, row[1]),
            "strategicPlanNo": validate_char_field("strategicPlanNo", 100, row[2]),
            "corporateStrategyNo": row[3],
            "servicePriority1": str(row[4]),
            "description": str(row[5]),
            "pvsExampleAnnWP": str(row[6]),
            "pvsExampleActNo": str(row[7]),
        }

        query = {"fy": fy, "servicePriorityNo": str(row[1])}
        saverow(PVSServicePriority, data, query)

    file.close()


def import_to_sfm_service_priority(file_name, fy):
    reader, file, file_name = csvload(file_name)
    for row in reader:
        data = {
            "fy": fy,
            "categoryID": validate_char_field("categoryID", 30, row[0]),
            "regionBranch": validate_char_field("regionBranch", 20, row[1]),
            "servicePriorityNo": validate_char_field("servicePriorityNo", 20, row[2]),
            "strategicPlanNo": validate_char_field("strategicPlanNo", 20, row[3]),
            "corporateStrategyNo": row[4],
            "description": str(row[5]),
            "description2": str(row[6]),
        }
        query = {"fy": fy, "servicePriorityNo": validate_char_field("servicePriorityNo", 20, row[2])}
        saverow(SFMServicePriority, data, query)

    file.close()


def import_to_er_service_priority(file_name, fy):
    reader, file, file_name = csvload(file_name)
    for row in reader:
        data = {
            "fy": fy,
            "categoryID": validate_char_field("categoryID", 30, row[0]),
            "servicePriorityNo": validate_char_field("servicePriorityNo", 10, row[1]),
            "strategicPlanNo": validate_char_field("strategicPlanNo", 10, row[2]),
            "corporateStrategyNo": row[3],
            "classification": str(row[4]),
            "description": str(row[5]),
        }
        query = {"fy": fy, "servicePriorityNo": str(row[1])}
        saverow(ERServicePriority, data, query)

    file.close()


def import_to_general_service_priority(file_name, fy):
    reader, file, file_name = csvload(file_name)
    for row in reader:
        data = {
            "fy": fy,
            "categoryID": validate_char_field("categoryID", 30, row[0]),
            "servicePriorityNo": validate_char_field("servicePriorityNo", 20, row[1]),
            "strategicPlanNo": validate_char_field("strategicPlanNo", 20, row[2]),
            "corporateStrategyNo": row[3],
            "description": str(row[4]),
            "description2": str(row[5]),
        }
        query = {"fy": fy, "servicePriorityNo": str(row[1])}

        saverow(GeneralServicePriority, data, query)

    file.close()


def import_to_nc_service_priority(file_name, fy):
    reader, file, file_name = csvload(file_name)
    for row in reader:
        data = {
            "fy": fy,
            "categoryID": validate_char_field("categoryID", 30, row[0]),
            "servicePriorityNo": validate_char_field("servicePriorityNo", 100, row[1]),
            "strategicPlanNo": validate_char_field("strategicPlanNo", 100, row[2]),
            "corporateStrategyNo": validate_char_field("corporateStrategyNo", 100, row[3]),
            "assetNo": validate_char_field("AssetNo", 5, row[4]),
            "asset": str(row[5]),
            "targetNo": validate_char_field("Asset", 30, row[6]),
            "target": str(row[7]),
            "actionNo": str(row[8]),
            "action": str(row[9]),
            "mileNo": validate_char_field("MileNo", 30, row[10]),
            "milestone": str(row[11]),
        }
        query = {"fy": fy, "servicePriorityNo": str(row[1])}
        saverow(NCServicePriority, data, query)

    file.close()


def import_to_service_priority_mappings(file_name, fy):
    reader, file, file_name = csvload(file_name)
    query_results = ServicePriorityMappings.objects.filter(fy=fy)
    if query_results.exists():
        query_results.delete()
    for row in reader:
        data = {
            "fy": fy,
            "costCentreNo": validate_char_field("costCentreNo", 4, row[0]),
            "wildlifeManagement": validate_char_field("wildlifeManagement", 100, row[1]),
            "parksManagement": validate_char_field("parksManagement", 100, row[2]),
            "forestManagement": validate_char_field("forestManagement", 100, row[3]),
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
        "mPRACategory",
    )

    ibmrows = IBMData.objects.values(
        "ibmIdentifier",
        "fy",
        "budgetArea",
        "projectSponsor",
        # "corporatePlanNo",
        # "strategicPlanNo",
        "regionalSpecificInfo",
        "servicePriorityID",
        "annualWPInfo",
    )
    ibmdict = dict(((r["ibmIdentifier"] + "_" + r["fy"], r) for r in ibmrows))

    csrows = CorporateStrategy.objects.values("corporateStrategyNo", "fy", "description1", "description2")
    csdict = dict(((r["corporateStrategyNo"] + "_" + r["fy"], r) for r in csrows))

    ncrows = NCStrategicPlan.objects.values(
        "strategicPlanNo", "fy", "directionNo", "direction", "aimNo", "aim1", "aim2", "actionNo", "action"
    )
    ncdict = dict(((r["strategicPlanNo"] + "_" + r["fy"], r) for r in ncrows))

    spdict = dict()
    ncsprows = NCServicePriority.objects.values_list("servicePriorityNo", "fy", "action", "milestone")
    sfmsprows = SFMServicePriority.objects.values_list("servicePriorityNo", "fy", "description", "description2")
    pvssprows = PVSServicePriority.objects.values_list("servicePriorityNo", "fy", "servicePriority1", "description")
    gensprows = GeneralServicePriority.objects.values_list("servicePriorityNo", "fy", "description", "description2")
    ersprows = ERServicePriority.objects.values_list("servicePriorityNo", "fy", "classification", "description")

    # order important
    for sprows in [ncsprows, sfmsprows, pvssprows, gensprows, ersprows]:
        spdict.update(dict(((r[0] + "_" + r[1], r) for r in sprows)))

    book = xlwt.Workbook()
    sheet = book.add_sheet("Sheet 1")
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
        "Service Priority Description 2",
    ]

    for col, h in enumerate(headers):
        sheet.write(0, col, h)

    for row_num, row in enumerate(rows, 1):
        outputdict = row
        outputdict.update(ibmdict.get(row["codeID"] + "_" + row["fy"], dict()))
        # if "corporatePlanNo" in outputdict.keys():
        #     outputdict.update(
        #         csdict.get(
        #             outputdict["corporatePlanNo"] +
        #             "_" +
        #             row["fy"],
        #             dict()))
        # if "strategicPlanNo" in outputdict.keys():
        #     outputdict.update(
        #         ncdict.get(
        #             outputdict["strategicPlanNo"] +
        #             "_" +
        #             row["fy"],
        #             dict()))
        if "servicePriorityID" in outputdict.keys():
            d1, d2 = spdict.get(outputdict["servicePriorityID"] + "_" + row["fy"], ("", "", "", ""))[2:]
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
            # "corporatePlanNo",
            # "strategicPlanNo",
            "regionalSpecificInfo",
            "servicePriorityID",
            "annualWPInfo",
            "description1",
            "description2",
            "directionNo",
            "direction",
            "aimNo",
            "aim1",
            "aim2",
            "actionNo",
            "action",
            "d1",
            "d2",
        ]:
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


def process_upload_file(file_name, file_type, fy):
    """Utility function to process an uploaded CSV file."""
    if file_type == "GLPivotDownload":
        import_to_glpivotdownload(file_name, fy)
    elif file_type == "IBMData":
        import_to_ibmdata(file_name, fy)
    elif file_type == "CorporateStrategyData":
        import_to_corporate_strategy(file_name, fy)
    elif file_type == "ERServicePriorityData":
        import_to_er_service_priority(file_name, fy)
    elif file_type == "PVSServicePriorityData":
        import_to_pvs_service_priority(file_name, fy)
    elif file_type == "SFMServicePriorityData":
        import_to_sfm_service_priority(file_name, fy)
    elif file_type == "NCStrategyData":
        import_to_nc_strategic_plan(file_name, fy)
    elif file_type == "GeneralServicePriorityData":
        import_to_general_service_priority(file_name, fy)
    elif file_type == "NCServicePriorityData":
        import_to_nc_service_priority(file_name, fy)
    elif file_type == "ServicePriorityMappings":
        import_to_service_priority_mappings(file_name, fy)
    else:
        raise Exception("process_upload_file : file type {} unknown".format(file_type))


def validate_headers(row, valid_count, headings):
    """For a passed-in CSV row, validate the count and content of each column."""
    column_count = len(row)
    if column_count == valid_count:  # Correct number of columns.
        # Check column headings.
        bad_headings = ""
        for k, heading in enumerate(headings):
            # If the given heading value doesn't match, append it to the error message.
            if row[k].strip() != heading:
                bad_headings += f"{row[k]} does not match {heading}\n"

        if bad_headings:
            raise Exception(f"""The column headings in the CSV file do not match the required headings:\n
                            {bad_headings}""")

    else:  # Incorrect number of columns
        raise Exception(f"""The number of columns in the CSV file do not match the required column count:\n
                        expected {valid_count}, received {column_count}""")

    return True


def validate_upload_file(file, file_type):
    """Utility function called by the Upload view to validate uploaded files.
    Should return True or raise an Exception.
    """
    reader = csv.reader(file, dialect="excel")
    row = next(reader)  # Get the first (header) row.

    if file_type == "GLPivotDownload":
        return validate_headers(
            row,
            valid_count=34,
            headings=[
                "Download Period",
                "CC",
                "Account",
                "Service",
                "Activity",
                "Resource",
                "Project",
                "Job",
                "Shortcode",
                "Shortcode_Name",
                "GL_Code",
                "PTD_Actual",
                "PTD_Budget",
                "YTD_Actual",
                "YTD_Budget",
                "FY_Budget",
                "YTD_Variance",
                "CC_Name",
                "Service Name",
                "Activity_Name",
                "Resource_Name",
                "Project_Name",
                "Job_Name",
                "Code identifier",
                "ResNmNo",
                "ActNmNo",
                "ProjNmNo",
                "Region/Branch",
                "Division",
                "Resource Category",
                "Wildfire",
                "Exp_Rev",
                "Fire Activities",
                "MPRA Category",
            ],
        )
    elif file_type == "IBMData":
        return validate_headers(
            row,
            valid_count=17,
            headings=[
                "ibmIdentifier",
                "costCentre",
                "account",
                "service",
                "activity",
                "project",
                "job",
                "budgetArea",
                "projectSponsor",
                "regionalSpecificInfo",
                "servicePriorityID",
                "annualWPInfo",
                "priorityActionNo",
                "priorityLevel",
                "marineKPI",
                "regionProject",
                "regionDescription",
            ],
        )
    elif file_type == "CorporateStrategyData":
        return validate_headers(
            row,
            valid_count=3,
            headings=["IBMSCSNo", "IBMSCSDesc1", "IBMSCSDesc2"],
        )
    elif file_type == "NCStrategyData":
        return validate_headers(
            row,
            valid_count=8,
            headings=[
                "StratPlanNo",
                "StratDirNo",
                "StratDir",
                "aimNo",
                "aim1",
                "aim2",
                "actNo",
                "action",
            ],
        )
    elif file_type == "ERServicePriorityData":
        return validate_headers(
            row,
            valid_count=6,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Env Regs Specific Classification",
                "Env Regs Specific Description",
            ],
        )
    elif file_type == "PVSServicePriorityData":
        return validate_headers(
            row,
            valid_count=8,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri",
                "PVSExampleAnnWP",
                "PVSExampleActNo",
            ],
        )
    elif file_type == "SFMServicePriorityData":
        return validate_headers(
            row,
            valid_count=7,
            headings=[
                "CategoryID",
                "Region",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "SerPri1",
                "SerPri2",
            ],
        )
    elif file_type == "GeneralServicePriorityData":
        return validate_headers(
            row,
            valid_count=6,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "Description 1",
                "Description 2",
            ],
        )
    elif file_type == "NCServicePriorityData":
        return validate_headers(
            row,
            valid_count=12,
            headings=[
                "CategoryID",
                "SerPriNo",
                "StratPlanNo",
                "IBMCS",
                "AssetNo",
                "Asset",
                "TargetNo",
                "Target",
                "ActionNo",
                "Action",
                "MileNo",
                "Milestone",
            ],
        )
    elif file_type == "ServicePriorityMappings":
        return validate_headers(
            row,
            valid_count=4,
            headings=[
                "CC No.",
                "Wildlife Management",
                "Parks Management",
                "Forest Management",
            ],
        )

    else:
        raise Exception("Unknown file type {}".format(file_type))
