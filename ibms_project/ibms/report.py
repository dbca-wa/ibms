from copy import copy
import csv
from django.conf import settings
from django.db.models import Sum
from xlrd import cellname
from xlwt import easyxf, Formula, XFStyle

from ibms.models import (
    IBMData, CorporateStrategy, NCStrategicPlan, NCServicePriority,
    ERServicePriority, GeneralServicePriority, PVSServicePriority,
    SFMServicePriority)


def service_priority_report(workbook, gl, ibm, nc_sp, pvs_sp, fm_sp):
    # Sheet 1
    sheet = workbook.get_sheet(0)

    # Download hyperlink:
    bigfont = easyxf('font: bold 1,height 360;')  # Font height is in "twips" (1/20 of a point)
    sheet.write(1, 0, Formula('HYPERLINK("{}")'.format(settings.IBM_SERVICE_PRIORITY_URI)), bigfont)

    # Padded zeroes number format
    pad2, pad3, pad4 = XFStyle(), XFStyle(), XFStyle()
    pad2.num_format_str = '00'
    pad3.num_format_str = '000'
    pad4.num_format_str = '0000'

    current_row = 3
    code_id = ''
    for row, data in enumerate(gl, current_row):
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
                ytd = gl.filter(codeID=code_id).aggregate(Sum('ytdActual'))
                fy = gl.filter(codeID=code_id).aggregate(Sum('fybudget'))
                sheet.write(current_row, 16, ytd['ytdActual__sum'])
                sheet.write(current_row, 17, fy['fybudget__sum'])

    # Insert the footer row formulae and '#END OF INPUT'
    sheet.write(current_row+2, 0, '#END OF INPUT')
    sheet.write(current_row+2, 16, Formula('SUM({}:{})'.format(cellname(4, 16), cellname(current_row, 16))))
    sheet.write(current_row+2, 17, Formula('SUM({}:{})'.format(cellname(4, 17), cellname(current_row, 17))))

    # Sheet 2 - Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)


def data_amend_report(workbook, gl, ibm, nc_sp, pvs_sp, fm_sp, ibm_filtered):
    # Sheet 1
    sheet = workbook.get_sheet(0)

    # Download hyperlink:
    bigfont = easyxf('font: bold 1,height 360;')  # Font height is in "twips" (1/20 of a point)
    sheet.write(1, 0, Formula('HYPERLINK("{}")'.format(settings.IBM_DATA_AMEND_URI)), bigfont)

    # Padded zeroes number format
    pad2, pad3, pad4 = XFStyle(), XFStyle(), XFStyle()
    pad2.num_format_str = '00'
    pad3.num_format_str = '000'
    pad4.num_format_str = '0000'

    current_row = 3
    code_id = ''
    for row, data in enumerate(gl, current_row):
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
                ytd = gl.filter(codeID=code_id).aggregate(Sum('ytdActual'))
                fy = gl.filter(codeID=code_id).aggregate(Sum('fybudget'))
                sheet.write(current_row, 20, ytd['ytdActual__sum'])
                sheet.write(current_row, 21, fy['fybudget__sum'])

    # Insert the footer row formulae and '#END OF INPUT'
    sheet.write(current_row+2, 0, '#END OF INPUT')
    sheet.write(current_row+2, 20, Formula('SUM({}:{})'.format(cellname(4, 20), cellname(current_row, 20))))
    sheet.write(current_row+2, 21, Formula('SUM({}:{})'.format(cellname(4, 21), cellname(current_row, 21))))

    # Sheet 2 - Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)

    # Sheet 3: Budget area & project sponsor lookup data.
    # This is a list of unique budgetArea and projectSponsor values, written in
    # as reference data for macros.
    sheet = workbook.get_sheet(2)
    write_budget_areas(sheet, ibm_filtered)
    write_project_sponsors(sheet, ibm_filtered)

    # Select the first sheet.
    sheet = workbook.get_sheet(0)


def code_update_report(workbook_ro, workbook, gl, gl_codeids, nc_sp, pvs_sp, fm_sp, ibm):
    """This report reads from the readonly workbook in order to perform some
    cell processing.
    """
    # Sheet 1
    sheet = workbook.get_sheet(0)
    sheet_ro = workbook_ro.get_sheet(0)

    # Download hyperlink:
    bigfont = easyxf('font: bold 1,height 360;')  # Font height is in "twips" (1/20 of a point)
    sheet.write(1, 0, Formula('HYPERLINK("{}")'.format(settings.IBM_CODE_UPDATER_URI)), bigfont)

    # Padded zeroes number format
    pad2, pad3, pad4 = XFStyle(), XFStyle(), XFStyle()
    pad2.num_format_str = '00'
    pad3.num_format_str = '000'
    pad4.num_format_str = '0000'

    # For each of the GL code IDs, take a subset of the query
    # and insert values as required.
    row = 4
    max_col_idx = 21  # Start at column V.
    for codeID in gl_codeids:
        gl_pivs = gl.filter(codeID=codeID)
        g = gl_pivs[0]
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
        sheet.write(row, 20, Formula('ROUND(SUM(V{}:GP{}), 0)'.format(row+1, row+1)))

        # First, find the maximum column index in the template headers (row 4).
        blank_cell = False
        while not blank_cell:
            if not sheet_ro.cell_value(3, max_col_idx):  # Blank cell
                blank_cell = True
            else:
                max_col_idx += 1

        # Write ytdActual values for matching resource columns.
        # Find the correct cell index of a matching resource code.
        # If no match found, use the '0000' column (the first).
        for gl_piv in gl_pivs:
            resource_idx = 21  # Column V, '0000'
            match_resource_code = False
            for i in range(resource_idx, max_col_idx + 1):
                if sheet_ro.cell_value(3, i) and int(sheet_ro.cell_value(3, i)) == gl_piv.resource:
                    match_resource_code = True
                    break
                resource_idx += 1

            if not match_resource_code:  # No match was found.
                resource_idx = 21  # Insert the ytdActual into column V.
            # Write the ytdActual to the sheet.
            sheet.write(row, resource_idx, gl_piv.ytdActual)

        row += 1  # Advance one row, to the next Code ID.

    row += 1
    # Insert the footer row formulae and '#END OF INPUT'
    sheet.write(row, 0, '#END OF INPUT')
    sheet.write(row, 20, Formula('ROUND(SUM(V{}:GP{}), 0)'.format(row+1, row+1)))
    for i in range(21, max_col_idx):
        # For cell V:<end> in the footer row, insert a SUM formula.
        sheet.write(row, i, Formula('ROUND(SUM({}:{}), 0)'.format(cellname(4, i), cellname(row-1, i))))

    # Sheet 2: Service priority checkboxes.
    sheet = workbook.get_sheet(1)
    write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp)

    # Sheet 3: Budget area & project sponsor lookup data.
    # This is a list of unique budgetArea and projectSponsor values, written in
    # as reference data for macros.
    sheet = workbook.get_sheet(2)
    write_budget_areas(sheet, ibm)
    write_project_sponsors(sheet, ibm)

    # Select the first sheet.
    sheet = workbook.get_sheet(0)


def reload_report(workbook, ibm, nc_sp, pvs_sp, fm_sp, gl):
    # IBMData sheet
    sheet = workbook.get_sheet(0)
    # Define cell styles
    data_xf = easyxf('border: left thin, right thin, top thin, bottom thin;')
    pad2 = copy(data_xf)
    pad2.num_format_str = '00'
    pad3 = copy(data_xf)
    pad3.num_format_str = '000'
    pad4 = copy(data_xf)
    pad4.num_format_str = '0000'
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


def write_budget_areas(sheet, ibm):
    """From a queryset of IBMData objects, write unique budgetArea values
    to the passed-in worksheet.
    """
    row = 1  # Skip the header row
    budget_areas = sorted(set(ibm.values_list('budgetArea', 'costCentre')))
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
    sponsors = sorted(set(ibm.values_list('projectSponsor', 'costCentre')))
    for i in sponsors:
        if i[0]:  # Non-blank only.
            sheet.write(row, 2, i[0])
            sheet.write(row, 3, i[1])
            row += 1


def write_service_priorities(sheet, nc_sp, pvs_sp, fm_sp):
    """Convenience function to write Service Priorites to a passed-in sheet.
    """
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
        sheet.write(row, 4, '')
        sheet.write(row, 5, '')
        sheet.write(row, 6, '')
        sheet.write(row, 7, '')
        sheet.write(row, 8, '')
        sheet.write(row, 9, sp.servicePriority1)
        sheet.write(row, 10, '')
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
        sheet.write(row, 4, '')
        sheet.write(row, 5, '')
        sheet.write(row, 6, '')
        sheet.write(row, 7, '')
        sheet.write(row, 8, '')
        sheet.write(row, 9, sp.description)
        sheet.write(row, 10, '')
        sheet.write(row, 11, sp.description2)
        row += 1


def download_report(glrows, response):
    """Convenience function to write a CSV to a passed-in HTTPResponse.
    """
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
        "Service Priority Description 2"]

    writer.writerow(headers)

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

        writer.writerow(xlrow)

    return response
