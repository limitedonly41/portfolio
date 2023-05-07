from django import forms
from .models import Prediction

class PredictForm(forms.ModelForm):
	class Meta:
		model = Prediction
		fields = ['url']