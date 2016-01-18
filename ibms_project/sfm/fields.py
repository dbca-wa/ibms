#fields.py
from django import forms

class QtrModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.description

class SFMMetricModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.metricID

class SFMCostCentreModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj)
