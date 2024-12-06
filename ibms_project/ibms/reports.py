import csv
from copy import copy

from django.conf import settings
from django.db.models import Sum
from xlrd import cellname
from xlwt import Formula, XFStyle, easyxf

from ibms.models import (
    CorporateStrategy,
    ERServicePriority,
    GeneralServicePriority,
    IBMData,
    NCServicePriority,
    NCStrategicPlan,
    PVSServicePriority,
    SFMServicePriority,
)


def service_priority_report(workbook, gl, ibm, nc_sp, pvs_sp, fm_sp):
    # Sheet 1
    sheet = workbook.get_sheet(0)

    # Download hyperlink:
    bigfont = easyxf("font: bold 1,height 360;")  # Font height is in "twips" (1/20 of a point)
    sheet.write(1, 0, Formula('HYPERLINK("{}")'.format(settings.IBM_SERVICE_PRIORITY_URI)), bigfont)

    # Padded zeroes number format
    pad2, pad3, pad4 = XFStyle(), XFStyle(), XFStyle()
    pad2.num_format_str = "00"
    pad3.num_format_str = "000"
    pad4.num_format_str = "0000"

    current_row = 3
    code_id = ""
    for _, data in enumerate(gl, current_row):
        # Only insert GLPivDownload objects with a matching IBMData object.
        if ibm.filter(ibmIdentifier=data.codeID):
            # We have to aggregate all the GLPivotDownload objects with
            # matching codeID values, and insert one row with total
            # ytdActual and fyBudget values.
            if code_id != data.codeID:  # Reached the next codeID value.
                code_id = data.codeID
                i = ibm.get(ibmIdentifier=data.codeID)
                current_row += 1  # Advance one row.
                sheet.write(current_row, 0, data.codeID)
                sheet.write(current_row, 1, int(data.costCentre), pad3)
                sheet.write(current_row, 2, data.account, pad2)
                sheet.write(current_row, 3, data.service, pad2)
                sheet.write(current_row, 4, data.activity)
                try:
                    sheet.write(current_row, 5, int(data.project), pad4)
                except ValueError:
                    sheet.write(current_row, 5, data.project, pad4)
                try:
                    sheet.write(current_row, 6, int(data.job), pad3)
                except ValueError:
                    sheet.write(current_row, 6, data.job, pad3)
                sheet.write(current_row, 7, data.jobName)
                sheet.write(current_row, 8, data.activityName)
                sheet.write(current_row, 9, data.projNameNo)
                sheet.write(current_row, 10, i.budgetArea)
                sheet.write(current_row, 11, i.projectSponsor)
                sheet.write(current_row, 12, i.regionalSpecificInfo)
                sheet.write(current_row, 13, i.servicePriorityID)
                sheet.write(current_row, 14, i.annualWPInfo)
                sheet.write(current_row, 15, data.mPRACategory)
                ytd = gl.filter(codeID=code_id).aggregate(Sum("ytdActual"))
                fy = gl.filter(codeID=code_id).aggregate(Sum("fybudget"))
                sheet.write(current_row, 16, ytd["ytdActual__sum"])
                sheet.write(current_row, 17, fy["fybudget__sum"])

    # Insert the footer row formulae and '#END OF INPUT'
    sheet.write(current_row + 2, 0, "#END OF INPUT")
    sheet.write(current_row + 2, 16, Formula("SUM({}:{})".format(cellname(4, 16), cellname(current_row, 16))))
    sheet.write(current_row + 2, 17, Formula("SUM({}:{})".format(cellname(4, 17), cellname(current_row, 17))))

    # Sheet 2 - Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)


def data_amend_report(workbook, gl, ibm, nc_sp, pvs_sp, fm_sp, ibm_filtered):
    # Sheet 1
    sheet = workbook.get_sheet(0)

    # Download hyperlink:
    bigfont = easyxf("font: bold 1,height 360;")  # Font height is in "twips" (1/20 of a point)
    sheet.write(1, 0, Formula('HYPERLINK("{}")'.format(settings.IBM_DATA_AMEND_URI)), bigfont)

    # Padded zeroes number format
    pad2, pad3, pad4 = XFStyle(), XFStyle(), XFStyle()
    pad2.num_format_str = "00"
    pad3.num_format_str = "000"
    pad4.num_format_str = "0000"

    current_row = 3
    code_id = ""
    for _, data in enumerate(gl, current_row):
        # Only insert GLPivDownload objects with a matching IBMData object.
        if ibm.filter(ibmIdentifier=data.codeID).exists():
            # We have to aggregate all the GLPivotDownload objects with
            # matching codeID values, and insert one row with total
            # ytdActual and fyBudget values.
            if code_id != data.codeID:  # Reached the next codeID value.
                current_row += 1  # Advance one row.
                code_id = data.codeID
                i = ibm.get(ibmIdentifier=data.codeID)
                sheet.write(current_row, 0, data.codeID)
                sheet.write(current_row, 1, int(data.costCentre), pad3)
                sheet.write(current_row, 2, data.account, pad2)
                sheet.write(current_row, 3, data.service, pad2)
                sheet.write(current_row, 4, data.activity, pad3)
                try:
                    sheet.write(current_row, 5, int(data.project), pad4)
                except ValueError:
                    sheet.write(current_row, 5, data.project, pad4)
                try:
                    sheet.write(current_row, 6, int(data.job), pad3)
                except ValueError:
                    sheet.write(current_row, 6, data.job, pad3)
                sheet.write(current_row, 7, data.jobName)
                sheet.write(current_row, 8, data.activityName)
                sheet.write(current_row, 9, data.projNameNo)
                sheet.write(current_row, 10, i.budgetArea)
                sheet.write(current_row, 11, i.projectSponsor)
                sheet.write(current_row, 14, i.regionalSpecificInfo)
                sheet.write(current_row, 15, i.servicePriorityID)
                sheet.write(current_row, 18, i.annualWPInfo)
                sheet.write(current_row, 19, data.mPRACategory)
                ytd = gl.filter(codeID=code_id).aggregate(Sum("ytdActual"))
                fy = gl.filter(codeID=code_id).aggregate(Sum("fybudget"))
                sheet.write(current_row, 20, ytd["ytdActual__sum"])
                sheet.write(current_row, 21, fy["fybudget__sum"])

    # Insert the footer row formulae and '#END OF INPUT'
    sheet.write(current_row + 2, 0, "#END OF INPUT")
    sheet.write(current_row + 2, 20, Formula("SUM({}:{})".format(cellname(4, 20), cellname(current_row, 20))))
    sheet.write(current_row + 2, 21, Formula("SUM({}:{})".format(cellname(4, 21), cellname(current_row, 21))))

    # Sheet 2 - Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)

    # Sheet 3: Budget area & project sponsor lookup data.
    # This is a list of unique budgetArea and projectSponsor values, written in
    # as reference data for macros.
    sheet = workbook.get_sheet(2)
    write_budget_areas(sheet, ibm_filtered)
    write_project_sponsors(sheet, ibm_filtered)
    write_regional_spec_info(sheet, ibm_filtered)

    # Select the first sheet.
    sheet = workbook.get_sheet(0)


def code_update_report(workbook_ro, workbook, gl, gl_codeids, nc_sp, pvs_sp, fm_sp, ibm):
    """This report reads from the readonly workbook in order to perform some cell processing."""
    # Sheet 1
    sheet = workbook.get_sheet(0)
    sheet_ro = workbook_ro.get_sheet(0)

    # Download hyperlink:
    bigfont = easyxf("font: bold 1,height 360;")  # Font height is in "twips" (1/20 of a point)
    url = Formula('HYPERLINK("{}")'.format(settings.IBM_CODE_UPDATER_URI))
    sheet.write(1, 0, url, bigfont)

    # Padded zeroes number format
    pad2, pad3, pad4 = XFStyle(), XFStyle(), XFStyle()
    pad2.num_format_str = "00"
    pad3.num_format_str = "000"
    pad4.num_format_str = "0000"

    # Find the maximum column index in the template headers (row 4).
    max_col_idx = 21  # Start at column V.
    blank_cell = False
    while not blank_cell:
        if not sheet_ro.cell_value(3, max_col_idx):  # Blank cell
            blank_cell = True
        else:
            max_col_idx += 1

    # Create a dict of the resource column headings and their column numbers by reading in
    # row 3 of the output spreadsheet.
    resource_column_indexes = {}
    resource_column_start = 21  # Column V, '0000'
    for i in range(resource_column_start, max_col_idx + 1):
        if sheet_ro.cell_value(3, i):
            resource_column_indexes[int(sheet_ro.cell_value(3, i))] = i

    # Start inserting GL codes at row 4.
    row = 4

    for _, codeID in enumerate(gl_codeids, start=1):
        # For each of the GL code IDs, take a subset of the query and insert values as required.
        gl_pivs = gl.filter(codeID=codeID)
        g = gl_pivs.first()  # Use the first GL code to write common values.

        # Fill the non-resource columns.
        sheet.write(row, 0, g.codeID)
        sheet.write(row, 1, int(g.costCentre), pad3)
        sheet.write(row, 2, g.account, pad2)
        sheet.write(row, 3, g.service, pad2)
        sheet.write(row, 4, g.activity, pad3)
        try:
            sheet.write(row, 5, int(g.project), pad4)
        except ValueError:
            sheet.write(row, 5, g.project, pad4)
        try:
            sheet.write(row, 6, int(g.job), pad3)
        except ValueError:
            sheet.write(row, 6, g.job, pad3)
        sheet.write(row, 7, g.jobName)
        sheet.write(row, 8, g.activityName)
        sheet.write(row, 9, g.projNameNo)
        sheet.write(row, 19, g.mPRACategory)

        # Write the SUM formula.
        sheet.write(row, 20, Formula("ROUND(SUM(V{}:GP{}), 0)".format(row + 1, row + 1)))

        # Write ytdActual values for matching resource columns (use the dict created earlier).
        # Use the column index of a matching resource code.
        # If no match found, use the '0000' column (the first).
        for gl_piv in gl_pivs:
            if gl_piv.resource in resource_column_indexes:
                sheet.write(row, resource_column_indexes[gl_piv.resource], gl_piv.ytdActual)
            else:
                sheet.write(row, resource_column_start, gl_piv.ytdActual)

        row += 1  # Advance one row, to the next Code ID.

    row += 1
    # Insert the footer row formulae and '#END OF INPUT'
    sheet.write(row, 0, "#END OF INPUT")
    sheet.write(row, 20, Formula("ROUND(SUM(V{}:GP{}), 0)".format(row + 1, row + 1)))
    for i in range(21, max_col_idx):
        # For cell V:<end> in the footer row, insert a SUM formula.
        sheet.write(row, i, Formula("ROUND(SUM({}:{}), 0)".format(cellname(4, i), cellname(row - 1, i))))

    # Sheet 2: Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)

    # Sheet 3: Budget area & project sponsor lookup data.
    # This is a list of unique budgetArea and projectSponsor values, written in
    # as reference data for macros.
    sheet = workbook.get_sheet(2)
    write_budget_areas(sheet, ibm)
    write_project_sponsors(sheet, ibm)
    write_regional_spec_info(sheet, ibm)

    # Select the first sheet.
    sheet = workbook.get_sheet(0)


def reload_report(workbook, ibm, nc_sp, pvs_sp, fm_sp, gl):
    # IBMData sheet
    sheet = workbook.get_sheet(0)
    # Define cell styles
    data_xf = easyxf("border: left thin, right thin, top thin, bottom thin;")
    pad2 = copy(data_xf)
    pad2.num_format_str = "00"
    pad3 = copy(data_xf)
    pad3.num_format_str = "000"
    pad4 = copy(data_xf)
    pad4.num_format_str = "0000"
    # Download hyperlink:
    sheet.write(1, 0, Formula('HYPERLINK("{}")'.format(settings.IBM_RELOAD_URI)))
    # Insert data:
    for row, data in enumerate(ibm, 3):
        sheet.write(row, 0, int(data.costCentre), pad3)
        sheet.write(row, 1, data.account, pad2)
        sheet.write(row, 2, data.service, pad2)
        sheet.write(row, 3, data.activity, pad3)
        try:
            sheet.write(row, 4, int(data.project), pad4)
        except ValueError:
            sheet.write(row, 4, data.project, pad4)
        try:
            sheet.write(row, 5, int(data.job), pad3)
        except ValueError:
            sheet.write(row, 5, data.job, pad3)
        sheet.write(row, 6, data.budgetArea, data_xf)
        sheet.write(row, 7, data.projectSponsor, data_xf)
        sheet.write(row, 8, data.regionalSpecificInfo, data_xf)
        sheet.write(row, 9, data.servicePriorityID, data_xf)
        sheet.write(row, 10, data.annualWPInfo, data_xf)
    # Make some columns wider
    sheet.col(6).width = 5000
    sheet.col(7).width = 5000
    sheet.col(8).width = 5000
    sheet.col(9).width = 5000
    sheet.col(10).width = 30000

    # Sheet 2 - Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)

    # Sheet 3 - GL Codes sheet
    sheet = workbook.get_sheet(2)

    for row, data in enumerate(gl):
        sheet.write(row, 0, data.gLCode)
        sheet.write(row, 1, data.shortCode)
        sheet.write(row, 2, data.shortCodeName)

    sheet.col(0).width = 7500
    sheet.col(2).width = 12500

    # Sheet 4 - Job and Job name
    sheet = workbook.get_sheet(3)

    jobs = []
    jobNames = []
    jobDict = {}
    jobNoNumDict = {}
    current_row = 0
    for row, data in enumerate(gl):
        if data.job not in jobs or data.jobName not in jobNames:
            # sheet.write(current_row, 0, data.job)
            # sheet.write(current_row, 1, data.jobName)
            if data.job.isdigit():
                job = {"job": int(data.job), "jobName": data.jobName}
                jobDict[current_row] = job
            else:
                job = {"job": data.job, "jobName": data.jobName}
                jobNoNumDict[current_row] = job
            jobs.append(data.job)
            jobNames.append(data.jobName)
            current_row += 1
        else:
            pass
    current_row = 0
    for s in sorted(jobDict.items(), key=lambda k_v: k_v[1]["job"]):
        sheet.write(current_row, 0, str(s[1]["job"]))
        sheet.write(current_row, 1, s[1]["jobName"])
        current_row += 1

    for s in sorted(jobNoNumDict.items(), key=lambda k_v: k_v[1]["job"]):
        sheet.write(current_row, 0, s[1]["job"])
        sheet.write(current_row, 1, s[1]["jobName"])
        current_row += 1

    sheet.col(1).width = 10000
    workbook.active_sheet = 0


def write_budget_areas(sheet, ibm):
    """From a queryset of IBMData objects, write unique budgetArea values
    to the passed-in worksheet.
    """
    row = 1  # Skip the header row
    budget_areas = sorted(set(ibm.values_list("budgetArea", "costCentre")))
    for i in budget_areas:
        if i[0]:  # Non-blank only.
            sheet.write(row, 0, i[0])
            sheet.write(row, 1, i[1])
            row += 1


def write_project_sponsors(sheet, ibm):
    """From a queryset of IBMData objects, write unique projectSponsor values
    to the passed-in worksheet.
    """
    row = 1  # Skip the header row
    sponsors = sorted(set(ibm.values_list("projectSponsor", "costCentre")))
    for i in sponsors:
        if i[0]:  # Non-blank only.
            sheet.write(row, 2, i[0])
            sheet.write(row, 3, i[1])
            row += 1


def write_regional_spec_info(sheet, ibm):
    """From a queryset of IBMData objects, write unique regionalSpecificInfo values
    to the passed-in worksheet.
    """
    row = 1  # Skip the header row
    reg_info = sorted(set(ibm.values_list("regionalSpecificInfo", "costCentre")))
    for i in reg_info:
        if i[0]:  # Non-blank only.
            sheet.write(row, 4, i[0])
            sheet.write(row, 5, i[1])
            row += 1


def write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp):
    """Convenience function to write Service Priorites to a passed-in sheet."""
    # Note that we can't just concat the three querysets together, because we
    # are using different models (with different field names).
    row = 0
    # NC service priorities.
    for sp in nc_sp:
        sheet.write(row, 0, sp.categoryID)
        sheet.write(row, 1, sp.servicePriorityNo)
        sheet.write(row, 2, sp.strategicPlanNo)
        sheet.write(row, 3, sp.corporateStrategyNo)
        sheet.write(row, 4, sp.assetNo)
        sheet.write(row, 5, sp.asset)
        sheet.write(row, 6, sp.targetNo)
        sheet.write(row, 7, sp.target)
        sheet.write(row, 8, sp.actionNo)
        sheet.write(row, 9, sp.action)
        sheet.write(row, 10, sp.mileNo)
        sheet.write(row, 11, sp.milestone)
        row += 1
    # PVS service priorities.
    for sp in pvs_sp:
        sheet.write(row, 0, sp.categoryID)
        sheet.write(row, 1, sp.servicePriorityNo)
        sheet.write(row, 2, sp.strategicPlanNo)
        sheet.write(row, 3, sp.corporateStrategyNo)
        sheet.write(row, 4, "")
        sheet.write(row, 5, "")
        sheet.write(row, 6, "")
        sheet.write(row, 7, "")
        sheet.write(row, 8, "")
        sheet.write(row, 9, sp.servicePriority1)
        sheet.write(row, 10, "")
        sheet.write(row, 11, sp.description)
        sheet.write(row, 12, sp.pvsExampleAnnWP)
        sheet.write(row, 13, sp.pvsExampleActNo)
        row += 1
    # FM service priorities.
    for sp in fm_sp:
        sheet.write(row, 0, sp.categoryID)
        sheet.write(row, 1, sp.servicePriorityNo)
        sheet.write(row, 2, sp.strategicPlanNo)
        sheet.write(row, 3, sp.corporateStrategyNo)
        sheet.write(row, 4, "")
        sheet.write(row, 5, "")
        sheet.write(row, 6, "")
        sheet.write(row, 7, "")
        sheet.write(row, 8, "")
        sheet.write(row, 9, sp.description)
        sheet.write(row, 10, "")
        sheet.write(row, 11, sp.description2)
        row += 1


def download_report(glpiv_qs, response):
    """Convenience function to write a CSV to a passed-in HTTPResponse.
    This is an extremely obtuse function (as originally written), so here is a summary:
    The ibms app models contain almost no FK link between each other due to their regularly being
    replaced from external data (Oracle Financials), however they do generally have natural keys
    of <Identier> + <Financial year>. Subsequently, this function constructs a dictionary for
    each object class having the keys being that constructed natural key.
    Starting from a passed-in queryset of GLPivDownload objects (filtered to a single FY), the
    function
    """
    # Initial validation check: glpiv_qs may contain a maximum of one FY value.
    fys = set(glpiv_qs.values_list("fy", flat=True))
    if len(fys) > 1:
        raise ValueError("GLPivDownload queryset contains >1 financial year value")

    glpiv_qs = glpiv_qs.values(
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

    # Get a values queryset of all IBMData objects.
    ibmdata_qs = IBMData.objects.values(
        "ibmIdentifier",
        "fy",
        "budgetArea",
        "projectSponsor",
        "regionalSpecificInfo",
        "servicePriorityID",
        "annualWPInfo",
    )
    # Construct a dict of the IBMData queryset, keys being a natural key of <ibmIdentifier>_<fy>
    ibmdict = dict([(r["ibmIdentifier"] + "_" + r["fy"], r) for r in ibmdata_qs])

    # Do the same for CorporateStrategy objects.
    corpstrat_qs = CorporateStrategy.objects.values(
        "corporateStrategyNo",
        "fy",
        "description1",
        "description2",
    )
    csdict = dict([(r["corporateStrategyNo"] + "_" + r["fy"], r) for r in corpstrat_qs])

    # Do the same for NCStrategicPlan objects.
    ncstratplan_qs = NCStrategicPlan.objects.values(
        "strategicPlanNo",
        "fy",
        "directionNo",
        "direction",
        "aimNo",
        "aim1",
        "aim2",
        "actionNo",
        "action",
    )
    ncdict = dict([(r["strategicPlanNo"] + "_" + r["fy"], r) for r in ncstratplan_qs])

    # Construct a dict of the various service priority class objects as value lists.
    ncsprows = NCServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "action", "milestone"
    )
    sfmsprows = SFMServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "description", "description2"
    )
    pvssprows = PVSServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "servicePriority1", "description"
    )
    gensprows = GeneralServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "description", "description2"
    )
    ersprows = ERServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "classification", "description"
    )

    # Collapse the multiple querysets into a single dictionary.
    spdict = {}
    # NOTE: Order is important here.
    for sprows in [ncsprows, sfmsprows, pvssprows, gensprows, ersprows]:
        for row in sprows:
            key = f"{row[0]}_{row[1]}"
            spdict.update({key: row})

    # Now that we've constructed our dictionaries, begin writing the CSV output
    # to the passed-in HTTP Response object.
    writer = csv.writer(response)
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
    writer.writerow(headers)

    for row in glpiv_qs:
        # outputdict will be used to generate each row in the final CSV output.
        outputdict = row

        # Find the matching IBMData object natural key (codeID_fy == ibmIdentifier_fy)
        ibmdata_key = row["codeID"] + "_" + row["fy"]
        if ibmdata_key in ibmdict:
            ibmdata_obj = ibmdict[ibmdata_key]
            # Enrich the dict with the IBMData object values.
            outputdict.update(ibmdata_obj)

        # The output row won't necessarily contain 'link' field values but if it does,
        # enrich the dict with the matching object values.
        if "servicePriorityID" in outputdict.keys():
            sp_key = outputdict["servicePriorityID"] + "_" + row["fy"]
            # Service priorities are handled slightly differently, each having been flattened
            # into lists (instead of dictionaries).
            if sp_key in spdict:
                service_priority = spdict[sp_key]
                strategic_plan_no = service_priority[2]
                corporate_strategy_no = service_priority[3]
                d1 = service_priority[4]
                d2 = service_priority[5]
            else:
                strategic_plan_no = ""
                corporate_strategy_no = ""
                d1 = ""
                d2 = ""

            outputdict.update(
                {"corporatePlanNo": corporate_strategy_no, "strategicPlanNo": strategic_plan_no, "d1": d1, "d2": d2}
            )

        # If corporatePlanNo and/or strategicPlanNo values are present in the dict,
        # they came from the service priorities above. Hence, this part needs to
        # come afterwards.
        if "corporatePlanNo" in outputdict.keys():
            corp_plan_key = outputdict["corporatePlanNo"] + "_" + row["fy"]
            if corp_plan_key in csdict:
                outputdict.update(csdict[corp_plan_key])

        if "strategicPlanNo" in outputdict.keys():
            strat_plan_key = outputdict["strategicPlanNo"] + "_" + row["fy"]
            if strat_plan_key in ncdict:
                outputdict.update(ncdict[strat_plan_key])

        csvrow = []
        # For each of the following list of keys, append EITHER the matching dict value
        # OR an empty string into the csvrow list.
        # The final output will be a sparsely-filled list of values.
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
            "aimNo",
            "aim1",
            "aim2",
            "actionNo",
            "action",
            "d1",
            "d2",
        ]:
            csvrow.append(outputdict.get(key, ""))

        # Conditionally cast some string values as integers.
        if csvrow[3] and csvrow[3].isdigit():
            csvrow[3] = int(csvrow[3])  # costCentre
        if csvrow[8] and csvrow[8].isdigit():
            csvrow[8] = int(csvrow[8])  # project
        if csvrow[9] and csvrow[9].isdigit():
            csvrow[9] = int(csvrow[9])  # job

        # Finally, write the row to the CSV output.
        writer.writerow(csvrow)

    return response


def download_enhanced_report(glpiv_qs, response):
    """Convenience function to write a CSV to a passed-in HTTPResponse."""
    glpiv_qs = glpiv_qs.values(
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
        "ytdActual",
        "ytdBudget",
        "fybudget",
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

    # Get a queryset of all IBMData objects.
    ibmrows = IBMData.objects.values(
        "ibmIdentifier",
        "fy",
        "budgetArea",
        "projectSponsor",
        "regionalSpecificInfo",
        "servicePriorityID",
        "annualWPInfo",
        # These are the additional columns in the "Enhanced" download.
        "priorityActionNo",
        "priorityLevel",
        "marineKPI",
        "regionProject",
        "regionDescription",
    )

    # Construct a dict of IBMData objects, keys being a natural key of <ibmIdentifier>_<fy>
    ibmdict = dict([(r["ibmIdentifier"] + "_" + r["fy"], r) for r in ibmrows])

    corpstrat_qs = CorporateStrategy.objects.values(
        "corporateStrategyNo",
        "fy",
        "description1",
        "description2",
    )
    csdict = dict([(r["corporateStrategyNo"] + "_" + r["fy"], r) for r in corpstrat_qs])

    ncstratplan_qs = NCStrategicPlan.objects.values(
        "strategicPlanNo",
        "fy",
        "directionNo",
        "direction",
        "aimNo",
        "aim1",
        "aim2",
        "actionNo",
        "action",
    )
    ncdict = dict([(r["strategicPlanNo"] + "_" + r["fy"], r) for r in ncstratplan_qs])

    # Construct a dict of the various service priority class objects as value lists.
    ncsprows = NCServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "action", "milestone"
    )
    sfmsprows = SFMServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "description", "description2"
    )
    pvssprows = PVSServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "servicePriority1", "description"
    )
    gensprows = GeneralServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "description", "description2"
    )
    ersprows = ERServicePriority.objects.values_list(
        "servicePriorityNo", "fy", "strategicPlanNo", "corporateStrategyNo", "classification", "description"
    )

    # Collapse the multiple querysets into a single dictionary.
    spdict = {}
    # NOTE: Order is important here.
    for sprows in [ncsprows, sfmsprows, pvssprows, gensprows, ersprows]:
        for row in sprows:
            key = f"{row[0]}_{row[1]}"
            spdict.update({key: row})

    # Now that we've constructed our dictionaries, begin writing the CSV output
    # to the passed-in HTTP Response object.
    writer = csv.writer(response)
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
        "ytd Actual",
        "ytd Budget",
        "fy Budget",
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
        # Extra columns in the enhanced report
        "Priority Action No",
        "Priority Level",
        "Marine KPI",
        "Region Project",
        "Region Description",
    ]

    writer.writerow(headers)

    for row in glpiv_qs:
        # outputdict will be used to generate each row in the final CSV output.
        outputdict = row

        # Find the matching IBMData object natural key (codeID_fy == ibmIdentifier_fy)
        ibmdata_key = row["codeID"] + "_" + row["fy"]
        if ibmdata_key in ibmdict:
            ibmdata_obj = ibmdict[ibmdata_key]
            # Enrich the dict with the IBMData object values.
            outputdict.update(ibmdata_obj)

        # The output row won't necessarily contain 'link' field values but if it does,
        # enrich the dict with the matching object values.
        if "servicePriorityID" in outputdict.keys():
            sp_key = outputdict["servicePriorityID"] + "_" + row["fy"]
            # Service priorities are handled slightly differently, each having been flattened
            # into lists (instead of dictionaries).
            if sp_key in spdict:
                service_priority = spdict[sp_key]
                strategic_plan_no = service_priority[2]
                corporate_strategy_no = service_priority[3]
                d1 = service_priority[4]
                d2 = service_priority[5]
            else:
                strategic_plan_no = ""
                corporate_strategy_no = ""
                d1 = ""
                d2 = ""

            outputdict.update(
                {"corporatePlanNo": corporate_strategy_no, "strategicPlanNo": strategic_plan_no, "d1": d1, "d2": d2}
            )

        # If corporatePlanNo and/or strategicPlanNo values are present in the dict,
        # they came from the service priorities above. Hence, this part needs to
        # come afterwards.
        if "corporatePlanNo" in outputdict.keys():
            corp_plan_key = outputdict["corporatePlanNo"] + "_" + row["fy"]
            if corp_plan_key in csdict:
                outputdict.update(csdict[corp_plan_key])

        if "strategicPlanNo" in outputdict.keys():
            strat_plan_key = outputdict["strategicPlanNo"] + "_" + row["fy"]
            if strat_plan_key in ncdict:
                outputdict.update(ncdict[strat_plan_key])

        csvrow = list()
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
            "ytdActual",
            "ytdBudget",
            "fybudget",
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
            "aimNo",
            "aim1",
            "aim2",
            "actionNo",
            "action",
            "d1",
            "d2",
            "priorityActionNo",
            "priorityLevel",
            "marineKPI",
            "regionProject",
            "regionDescription",
        ]:
            csvrow.append(outputdict.get(key, ""))

        # Conditionally cast some string values as ints.
        csvrow[3] = int(csvrow[3])  # costCentre
        try:
            csvrow[8] = int(csvrow[8])  # project
        except:
            pass
        try:
            csvrow[9] = int(csvrow[9])  # job
        except:
            pass

        # Finally, write the row to the CSV output.
        writer.writerow(csvrow)

    return response
