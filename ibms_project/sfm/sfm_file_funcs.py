import csv
from ibms.db_funcs import csvload, saverow, validateCharField
from sfm.models import CostCentre, SFMMetric, MeasurementValue, Quarter

COLS_SFM_METRICS = 5
COLS_COSTCENTRES = 1


def import_to_sfmmetrics(fileName, fy):
    reader, file, fileName = csvload(fileName)

    try:
        i = 1
        for row in reader:
            data = {
                "fy": fy,
                "region": validateCharField('region', 30, row[0]),
                "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[1]),
                "metricID": validateCharField('metricID', 20, row[2]),
                "descriptor": str(row[3]),
                "example": str(row[4])
            }
            query = {
                "fy": fy,
                "servicePriorityNo": str(row[1]),
                "metricID": str(row[2])
            }
            saverow(SFMMetric, data, query)
            i += 1
    except SFMMetric.DoesNotExist:
        raise Exception('Row {}:{}\nPlease import servicePriorityNo into IBMData before proceeding, otherwise database integrity will be compromised.'.format(i, row[0]))

    return


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
    except CostCentre.DoesNotExist:
        raise Exception('Row {}:{}\nhas invalid data. Unable to import.'.format(i, row))

    return


def import_measurementvalues(fileName, fy):
    reader, file, fileName = csvload(fileName)

    try:
        i = 1
        for row in reader:
            # Assumes Quarter is in the format "2020/21 Q1 (Jul - Sep)"
            try:
                quarter = Quarter.objects.get(fy=fy, description=row[0].split(maxsplit=1)[1])
            except Quarter.DoesNotExist:
                raise Exception('Quarter in row {}:{}\nnot found, unable to import.'.format(i, row))

            try:
                cc = CostCentre.objects.get(costCentre=row[1].split("-")[0].strip())
            except CostCentre.DoesNotExist:
                raise Exception('CostCentre in row {}:{}\nnot found, unable to import.'.format(i, row))

            try:
                metric = SFMMetric.objects.get(fy=fy, metricID=row[2])
            except SFMMetric.DoesNotExist:
                raise Exception('SFMMetric in row {}:{}\nnot found, unable to import.'.format(i, row))

            query = {
                "quarter": quarter,
                "costCentre": cc,
                "sfmMetric": metric,
            }
            data = {
                "quarter": quarter,
                "costCentre": cc,
                "sfmMetric": metric,
                "planned": row[3] == 'TRUE' if row[3] else None,
                "status": row[4].lower(),
                "comment": row[5],
            }
            saverow(MeasurementValue, data, query)
            i += 1

    except Exception as e:
        raise Exception('Row {}:{}\nhas invalid data. Unable to import.\n{}'.format(i, row, e.message))

    return


def process_upload_file(file_name, fileType, fy):
    if fileType == 'sfmmetrics':
        import_to_sfmmetrics(file_name, fy)
    elif fileType == 'costcentres':
        import_to_costcentres(file_name, fy)
    elif fileType == 'measurementvalues':
        import_measurementvalues(file_name, fy)


def validate_file(file, fileType):
    reader = csv.reader(file, dialect='excel')
    if fileType == 'sfmmetrics':
        return validate_sfmmetrics_header(reader)
    if fileType == 'costcentres':
        return validate_costcentre_header(reader)
    if fileType == 'measurementvalues':
        return validate_measurementvalues_header(reader)

    return False


def validate_sfmmetrics_header(reader):
    row = next(reader)
    if len(row) == COLS_SFM_METRICS:
        sBad = ''
        if row[0].strip() != 'region':
            sBad += row[0] + ' : ' + 'region\n'
        if row[1].strip() != 'servicePriorityNo':
            sBad += row[1] + ' : ' + 'servicePriorityNo\n'
        if row[2].strip() != 'metricID':
            sBad += row[2] + ' : ' + 'metricID\n'
        if row[3].strip() != 'descriptor':
            sBad += row[3] + ' : ' + 'descriptor\n'
        retVal = sBad == ''

        if not retVal:
            raise Exception('The column headings in the CSV file do not match the required headings\n{}'.format(sBad))
    else:
        raise Exception('The number of columns in the CSV file do not match the required column count :\nExpects {}, met {}'.format(COLS_SFM_METRICS, len(row)))

    return retVal


def validate_costcentre_header(reader):
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


def validate_measurementvalues_header(reader):
    row = next(reader)
    sBad = ''
    if row[0].strip() != 'quarter':
        sBad += row[0] + ' : ' + 'quarter\n'
    if row[1].strip() != 'costCentre':
        sBad += row[1] + ' : ' + 'costCentre\n'
    if row[2].strip() != 'sfmMetric':
        sBad += row[2] + ' : ' + 'sfmMetric\n'
    if row[3].strip() != 'planned':
        sBad += row[3] + ' : ' + 'planned\n'
    if row[4].strip() != 'status':
        sBad += row[4] + ' : ' + 'status\n'
    if row[5].strip() != 'comment':
        sBad += row[5] + ' : ' + 'comment\n'
    retVal = sBad == ''

    if not retVal:
        raise Exception('The column headings in the CSV file do not match the required headings\n' + sBad)

    return retVal
