import csv
import os
from sfm.models import Quarter, CostCentre, SFMMetric, FinancialYear, MeasurementValue, MeasurementType

CSV_FILE_LIMIT = 100000000
choices = []


def getQuarterChoices():
    choices = [('', '--------')]
    obj = Quarter.objects.order_by('quarter').all().values('quarter', 'description')
    for o in obj:
        choices.append((o['quarter'], o['description']))
    return choices


def getCostCentreChoices():
    choices = [('', '--------')]
    obj = CostCentre.objects.order_by('costCentre')
    for o in obj:
        choices.append((o['costCentre'], str(o)))
    choices.sort()
    return choices


def getMetricChoices():
    choices = [('', '--------')]
    obj = SFMMetric.objects.order_by('metricID').all().values('descriptor', 'metricID', 'example')
    for o in obj:
        choices.append((o['descriptor'], o['metricID']))
    return choices


def getFYChoices():
    choices = [('', '--------')]
    obj = FinancialYear.objects.all().values('financialYear').distinct('financialYear')
    for o in obj:
        choices.append((o['financialYear'], o['financialYear']))
    choices.sort()
    return choices


def csvload(fileName):
    file = open(fileName, "rb")
    csv.field_size_limit(CSV_FILE_LIMIT)
    try:
        rdr = csv.reader(file, dialect='excel', quotechar='"')
    except:
        file.close()
        os.remove(fileName)
    try:
        if not csv.Sniffer().has_header(file.readline()):
            rdr.seek(0)
    except:
        file.close()
        os.remove(fileName)
    return rdr, file, fileName


def saverow(model, data, query):
    # Query the database for an existing object based on ``query``, and update it with ``data``.
    # Alternatively, just create a new object with ``data``.
    if model.objects.filter(**query).exists():
        # We won't bother raising an exception if there are multiple rows returned by the filter().
        # We'll rely on any natural keys defined on the model to maintain database integrity.
        obj = model.objects.filter(**query).update(**data)
        return
    else:
        obj = model(**data)
        obj.save()


def validateCharField(fieldName, fieldLen, data):
    if (len(data.strip()) > fieldLen):
        raise Exception('Field ' + fieldName + ' cannot be truncated')
    return data.strip()


def import_to_sfmmetrics(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in rdr:
            data = {
                "financialYear": finyear,
                "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[0]),
                "metricID": validateCharField('metricID', 20, row[1]),
                "descriptor": str(row[2]),
                "example": str(row[3])
            }
            query = {
                "financialYear": finyear,
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
        raise Exception('Row {0}:{1}\nPlease import servicePriorityNo into IBMData before proceeding, otherwise database integrity will be compromised.'.format(i, row[0]))


def import_to_costcentres(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in rdr:
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
        raise Exception('Row {0}:{1}\nhas invalid data. Unable to import - '.format(i, row[0]))


def import_to_measurement_value(sfmdata, sfmvals):
    metric = SFMMetric.objects.get(financialYear=str(sfmdata['financialYear']), metricID=str(sfmdata['metricID']))
    quarter = Quarter.objects.get(financialYear=str(sfmdata['financialYear']),
                                  id=str(sfmdata['quarter']))
    cc = CostCentre.objects.get(pk=sfmdata['costCentre'].pk)

    if len(sfmvals.keys()):
        for key, val in sfmvals.iteritems():
            mt = MeasurementType.objects.get(unit=str(key))
            data = {
                "quarter": quarter,
                "sfmMetric": metric,
                "measurementType": mt,
                "costCentre": cc,
                "value": val,
                "comment": str(sfmdata['comment'])
            }
            query = {
                "quarter": quarter.id,
                "sfmMetric": metric.id,
                "measurementType": mt.id,
                "costCentre": cc.id,
            }
            saverow(MeasurementValue, data, query)
    else:
        # this is stupid :( :( :(
        saverow(MeasurementValue, {
            "quarter": quarter,
            "sfmMetric": metric,
            "measurementType": None,
            "costCentre": cc,
            "value": None,
            "comment": str(sfmdata['comment'])
        }, {
            "quarter": quarter.id,
            "sfmMetric": metric.id,
            "costCentre": cc.id,
            "measurementType": None,
            "comment": str(sfmdata['comment'])
        })
