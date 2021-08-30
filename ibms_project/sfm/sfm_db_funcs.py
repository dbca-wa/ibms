import os
from ibms.db_funcs import csvload, saverow, validateCharField
from sfm.models import Quarter, CostCentre, SFMMetric, FinancialYear, MeasurementValue, MeasurementType


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
