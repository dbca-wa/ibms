import os
from ibms.db_funcs import csvload, saverow, validateCharField
from sfm.models import Quarter, CostCentre, SFMMetric, FinancialYear, MeasurementValue, MeasurementType


def import_to_sfmmetrics(fileName, finyear):
    rdr, file, fileName = csvload(fileName)
    try:
        i = 1
        for row in rdr:
            data = {
                "fy": finyear,
                "servicePriorityNo": validateCharField('servicePriorityNo', 20, row[0]),
                "metricID": validateCharField('metricID', 20, row[1]),
                "descriptor": str(row[2]),
                "example": str(row[3])
            }
            query = {
                "fy": finyear,
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
    metric = SFMMetric.objects.get(fy=str(sfmdata['financialYear']), metricID=str(sfmdata['metricID']))
    quarter = Quarter.objects.get(fy=str(sfmdata['financialYear']), id=str(sfmdata['quarter']))
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
