import csv

from sfm.models import CostCentre, MeasurementValue, Quarter, SFMMetric

from ibms.utils import csvload, save_record

COLS_SFM_METRICS = 5
COLS_COSTCENTRES = 3


def import_to_sfmmetrics(fileName, fy):
    reader, file, fileName = csvload(fileName)

    try:
        i = 1
        for row in reader:
            metric, created = SFMMetric.objects.get_or_create(
                fy=fy,
                servicePriorityNo=row[1],
                metricID=row[2],
            )
            metric.region = row[0]
            metric.descriptor = row[3]
            metric.example = row[4]
            metric.save()
            i += 1
    except SFMMetric.DoesNotExist:
        raise Exception(
            "Row {}:{}\nPlease import servicePriorityNo into IBMData before proceeding, otherwise database integrity will be compromised.".format(
                i, row[0]
            )
        )

    return


def import_to_costcentres(fileName):
    reader, file, fileName = csvload(fileName)

    try:
        i = 1
        for row in reader:
            if CostCentre.objects.filter(costCentre=row[0]):
                cc = CostCentre.objects.get(costCentre=row[0])
                cc.name = row[1]
                cc.region = row[2]
                cc.save()
            else:
                CostCentre.objects.create(
                    costCentre=row[0],
                    name=row[1],
                    region=row[2],
                )
            i += 1
    except:
        raise Exception("Row {}:{}\nhas invalid data. Unable to import.".format(i, row))

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
                raise Exception("Quarter in row {}:{}\nnot found, unable to import.".format(i, row))

            try:
                metric = SFMMetric.objects.get(fy=fy, metricID=row[2])
            except SFMMetric.DoesNotExist:
                raise Exception("SFMMetric in row {}:{}\nnot found, unable to import.".format(i, row))

            query = {
                "quarter": quarter,
                "region": row[1],
                "sfmMetric": metric,
            }
            data = {
                "quarter": quarter,
                "region": row[1],
                "sfmMetric": metric,
                "planned": row[3] == "TRUE" if row[3] else None,
                "status": row[4].lower(),
                "comment": row[5],
            }
            save_record(MeasurementValue, data, query)
            i += 1

    except Exception as e:
        raise Exception("Row {}:{}\nhas invalid data. Unable to import.\n{}".format(i, row, e.message))

    return


def process_upload_file(file_name, fileType, fy):
    if fileType == "sfmmetrics":
        import_to_sfmmetrics(file_name, fy)
    elif fileType == "costcentres":
        import_to_costcentres(file_name)
    elif fileType == "measurementvalues":
        import_measurementvalues(file_name, fy)


def validate_file(file, fileType):
    reader = csv.reader(file, dialect="excel")
    if fileType == "sfmmetrics":
        return validate_sfmmetrics_header(reader)
    if fileType == "costcentres":
        return validate_costcentre_header(reader)
    if fileType == "measurementvalues":
        return validate_measurementvalues_header(reader)

    return False


def validate_sfmmetrics_header(reader):
    row = next(reader)
    if len(row) == COLS_SFM_METRICS:
        sBad = ""
        if row[0].strip() != "region":
            sBad += row[0] + " : " + "region\n"
        if row[1].strip() != "servicePriorityNo":
            sBad += row[1] + " : " + "servicePriorityNo\n"
        if row[2].strip() != "metricID":
            sBad += row[2] + " : " + "metricID\n"
        if row[3].strip() != "descriptor":
            sBad += row[3] + " : " + "descriptor\n"
        retVal = sBad == ""

        if not retVal:
            raise Exception("The column headings in the CSV file do not match the required headings\n{}".format(sBad))
    else:
        raise Exception(
            "The number of columns in the CSV file do not match the required column count :\nExpects {}, found {}".format(
                COLS_SFM_METRICS, len(row)
            )
        )

    return retVal


def validate_costcentre_header(reader):
    row = next(reader)
    if len(row) == COLS_COSTCENTRES:
        sBad = ""
        if row[0].strip() != "costCentre":
            sBad += row[0] + " : " + "costCentre\n"
        if row[1].strip() != "name":
            sBad += row[1] + " : " + "name\n"
        if row[2].strip() != "region":
            sBad += row[2] + " : " + "region\n"
        retVal = sBad == ""

        if not retVal:
            raise Exception("The column headings in the CSV file do not match the required headings\n{}".format(sBad))
    else:
        raise Exception(
            "The number of columns in the CSV file do not match the required column count :\nExpects {}, found {}".format(
                COLS_COSTCENTRES, len(row)
            )
        )

    return retVal


def validate_measurementvalues_header(reader):
    row = next(reader)
    sBad = ""
    if row[0].strip() != "quarter":
        sBad += row[0] + " : " + "quarter\n"
    if row[1].strip() != "region":
        sBad += row[1] + " : " + "region\n"
    if row[2].strip() != "sfmMetric":
        sBad += row[2] + " : " + "sfmMetric\n"
    if row[3].strip() != "planned":
        sBad += row[3] + " : " + "planned\n"
    if row[4].strip() != "status":
        sBad += row[4] + " : " + "status\n"
    if row[5].strip() != "comment":
        sBad += row[5] + " : " + "comment\n"
    retVal = sBad == ""

    if not retVal:
        raise Exception("The column headings in the CSV file do not match the required headings\n" + sBad)

    return retVal
