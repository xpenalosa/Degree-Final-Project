from django import forms
from django.core.validators import RegexValidator

class CreateTournamentForm(forms.Form):
	name = forms.CharField(
		label="Nom del torneig",
		max_length=32,
		validators=[
			RegexValidator(regex=r"[\w\d\s]+")
		]
	)
	pass1 = forms.CharField(
		label="Contrassenya",
		max_length=32,
		validators=[
			RegexValidator(regex=r"[\w\d\s]+")
		],
		widget=forms.PasswordInput()
	)
	pass2 = forms.CharField(
		label="Repeteix la contrassenya",
		max_length=32,
		validators=[
			RegexValidator(regex=r"[\w\d\s]+")
		],
		widget=forms.PasswordInput()
	)
	players = forms.CharField(
		label="Noms dels participants",
		validators=[
			RegexValidator(regex=r"(\s?([\w\d]{1,16})[,\n]){1,15}\s?[\w\d]{1,16}")
		],
		widget=forms.PasswordInput()
	)

	def clean(self):
		clean_data = super(CreateTournamentForm, self).clean()
		p1 = clean_data.get('pass1')
		p2 = clean_data.get('pass2')
		
		if p1 and p2 and p1 != p2:
			self._errors['pass2'] = self.error_class([
				"Les contrassenyes no coincideixen"])
			del self.cleaned_data['pass1']
		return clean_data
