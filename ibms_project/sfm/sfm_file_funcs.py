import csv
import os
from ibms.db_funcs import csvload, saverow, validateCharField
from sfm.models import CostCentre, SFMMetric

COLS_SFM_METRICS = 4
COLS_COSTCENTRES = 1


def import_to_sfmmetrics(fileName, fy):
    reader, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in reader:
            data = {
                "fy": fy,
                "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[0]),
                "metricID": validateCharField('metricID', 20, row[1]),
                "descriptor": str(row[2]),
                "example": str(row[3])
            }
            query = {
                "fy": fy,
                "servicePriorityNo": str(row[0]),
                "metricID": str(row[1])
            }
            saverow(SFMMetric, data, query)
            i += 1
        file.close()
        os.remove(fileName)
    except SFMMetric.DoesNotExist:
        file.close()
        os.remove(fileName)
        raise Exception('Row {}:{}\nPlease import servicePriorityNo into IBMData before proceeding, otherwise database integrity will be compromised.'.format(i, row[0]))


def import_to_costcentres(fileName, fy):
    reader, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in reader:
            data = {
                "costCentre": validateCharField('servicePriorityNo', 4, row[0]),
            }
            query = {
                "costCentre": str(row[0]),
            }
            saverow(CostCentre, data, query)
            i += 1
        file.close()
        os.remove(fileName)
    except CostCentre.DoesNotExist:
        file.close()
        os.remove(fileName)
        raise Exception('Row {}:{}\nhas invalid data. Unable to import.'.format(i, row[0]))


def import_measurementvalues(fileName, fy):
    # TODO: placeholder function only.
    reader, file, fileName = csvload(fileName)
    return


def process_upload_file(file_name, fileType, fy):
    if fileType == 'sfmmetrics':
        import_to_sfmmetrics(file_name, fy)
    elif fileType == 'costcentres':
        import_to_costcentres(file_name, fy)
    elif fileType == 'measurementvalues':
        # TODO: this import function is not complete yet.
        import_measurementvalues(file_name, fy)
    else:
        raise Exception('func: process_upload_file : file type ' + fileType + ' unknown')


def validate_file(file, fileType):
    reader = csv.reader(file, dialect='excel')
    if fileType == 'sfmmetrics':
        return validate_sfmmetrics_hdr(reader)
    if fileType == 'costcentres':
        return validate_costcentre_hdr(reader)
    if fileType == 'measurementvalues':
        return validate_measurementvalues_hdr(reader)
    else:
        raise Exception("Attempting to validate and unknown file type of " + fileType)


def validate_sfmmetrics_hdr(reader):
    row = next(reader)
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


def validate_costcentre_hdr(reader):
    row = next(reader)
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


def validate_measurementvalues_hdr(reader):
    # TODO: placeholder function only.
    return True
