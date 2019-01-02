from django import forms
from django.core.validators import RegexValidator

import re

class CreateTournamentForm(forms.Form):
	name = forms.CharField(
		label="Nom del torneig",
		max_length=32
	)
	pass1 = forms.CharField(
		label="Contrassenya",
		max_length=32,
		widget=forms.PasswordInput()
	)
	pass2 = forms.CharField(
		label="Repeteix la contrassenya",
		max_length=32,
		widget=forms.PasswordInput()
	)
	players = forms.CharField(
		label="Noms dels participants",
		widget=forms.Textarea({
			'cols' : '72',
			'rows' : '8'
		})
	)

	def clean(self):
		clean_data = super(CreateTournamentForm, self).clean()
		n = clean_data.get('name')
		if not re.match(r"^[\w\d\s]{1,32}$", n):
			self._errors['name'] = self.error_class([
				" ".join([
					"El nom del torneig ha de contenir",
					"entre 1 i 32 caràcters",
					"alfanumèrics."])
			])
			del self.cleaned_data['name']


		p1 = clean_data.get('pass1')
		p2 = clean_data.get('pass2')
		
		if p1 != p2:
			self._errors['pass1'] = self.error_class([
				"Les contrassenyes no coincideixen"])
			self._errors['pass2'] = self.error_class([
				"Les contrassenyes no coincideixen"])
			del self.cleaned_data['pass1']
			del self.cleaned_data['pass2']

		players = clean_data.get('players')

		player_errors = []
		player_characters_rgx = re.compile("^[A-Za-z\d,;:\s\n]+$")
		if not player_characters_rgx.match(players):
			player_errors.append(" ".join([
				"Els identificadors dels participants només",
				"poden ser caràcters alfanumèrics."]))

		player_names = re.split("[,;:\s\n]+", players)
		if len(player_names) < 2:	
			player_errors.append("".join([
				"Es requereixen un mínim de 2 participants."])
			)
		elif len(player_names) > 16:
			player_errors.append("".join([
				"S'accepten un màxim de 16 participants."])
			)
		elif len(player_names) not in [2,4,8,16]:
			player_errors.append(" ".join([
				"Només es poden registrar 2, 4, 8 o 16",
				"participants"])
			)
		else:
			for p_name in player_names:
				if len(p_name) < 1 or len(p_name) > 16:
					player_errors.append(" ".join([
						"El nom d'un participant",
						"excedeix els 16 caràcters."])
					)
					break

		if player_errors:
			self._errors['players'] = self.error_class(
				player_errors)

		return clean_data


class UpdateTournamentForm(forms.Form):

	version = forms.IntegerField(
		label="Version",
		widget=forms.HiddenInput()
	)

	password = forms.CharField(
		help_text = "Contrassenya", 
		max_length=32,
		widget=forms.PasswordInput(
			attrs={
				'placeholder': "Contrassenya"
			}
		)
	)

	classification = forms.CharField(
		max_length=15,
		widget=forms.HiddenInput()
	)

	def clean(self):
		clean_data = super(UpdateTournamentForm, self).clean()

		v = clean_data.get('version', None)
		if v < 0:
			self._errors['version'] = self.error_class([
				"La versió no pot ser negativa"])
			del self.cleaned_data['version']

		c = clean_data.get('classification', None)
		if len(c) not in [1, 3, 7, 15]:
			self._errors['classification'] = self.error_class([
				"Classificació invàlida"])
			del self.cleaned_data['classification']
		else:
			for match in c:
				if match not in ['U', '1', '2']:
					self._errors['classification'] = \
						self.error_class([
							"Classificació \
							invàlida"])
					del self.cleaned_data['classification']
					break
		return clean_data
