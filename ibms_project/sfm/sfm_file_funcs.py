import csv

COLS_SFM_METRICS = 4
COLS_COSTCENTRES = 1


def process_upload_file(fileName, fileType, fy):
    from sfm import sfm_db_funcs
    if fileType == 'sfmmetrics':
        sfm_db_funcs.import_to_sfmmetrics(fileName, fy)
    elif fileType == 'costcentres':
        sfm_db_funcs.import_to_costcentres(fileName, fy)
    else:
        raise Exception('func: process_upload_file : file type ' + fileType + ' unknown')


def validate_file(file, fileType):
    rdr = csv.reader(file, dialect='excel')
    if fileType == 'sfmmetrics':
        return validate_sfmmetrics_hdr(rdr)
    if fileType == 'costcentres':
        return validate_costcentre_hdr(rdr)
    else:
        raise Exception("Attempting to validate and unknown file type of " + fileType)


def validate_sfmmetrics_hdr(rdr):
    row = next(rdr)
    if len(row) == COLS_SFM_METRICS:
        sBad = ''
        if row[0].strip() != 'servicePriorityNo':
            sBad += row[0] + ' : ' + 'servicePriorityNo\n'
        if row[1].strip() != 'metricID':
            sBad += row[1] + ' : ' + 'metricID\n'
        if row[2].strip() != 'descriptor':
            sBad += row[2] + ' : ' + 'descriptor\n'
        retVal = sBad == ''

        if not retVal:
            raise Exception('The column headings in the CSV file do not match the required headings\n' + sBad)
    else:
        raise Exception('The number of columns in the CSV file do not match the required column count :\nExpects ' + str(COLS_SFM_METRICS) + ' met ' + str(len(row)))

    return retVal


def validate_costcentre_hdr(rdr):
    row = next(rdr)
    if len(row) == COLS_COSTCENTRES:
        sBad = ''
        if row[0].strip() != 'costCentre':
            sBad += row[0] + ' : ' + 'costCentre\n'
        retVal = sBad == ''

        if not retVal:
            raise Exception('The column headings in the CSV file do not match the required headings\n' + sBad)
    else:
        raise Exception('The number of columns in the CSV file do not match the required column count :\nExpects ' + str(COLS_COSTCENTRES) + ' met ' + str(len(row)))

    return retVal
