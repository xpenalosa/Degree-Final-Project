function validate_form() {

	var form = document.forms["create-tournament"];

	var nameField = form["name"];
	if (nameField.value == ""){
		alert("El nom del torneig no pot estar en blanc.")
		nameField.style.borderColor = "red";
		return false;
	}
	else {
		nameField.style.borderColor = "green";
	}


	var pass1Field = form["pass1"];
	var pass2Field = form["pass2"];
	if (pass1Field.value == ""){
		alert("La contrassenya no pot estar en blanc")
		pass1Field.style.borderColor = "red";
		return false;
	}
	pass1Field.style.borderColor = "green";

	if (pass2Field.value == ""){
		alert("Confirma la contrassenya al camp indicat")
		pass2Field.style.borderColor = "red";
		return false;
	}
	pass2Field.style.borderColor = "green";
	
	if (pass1Field.value != pass2Field.value) {
		alert("Les contrassenyes no coincideixen!")
		pass1Field.style.borderColor = "red";
		pass2Field.style.borderColor = "red";
		return false;
	}


	var playersField = form["players"];
	if (playersField.value == ""){
		alert("No s'ha entrat cap participant")
		playersField.style.borderColor = "red";
		return false;
	} else {
		var players = playersField.value.split(/[,\n\s]+/)
		if (players.length < 2 || players.length > 16){
			alert("La quantitat de participants del torneig ha d'estar entre 2 i 16 (inclosos)")
			playersField.style.borderColor = "red";
			return false;
		}
	}
	playersField.style.borderColor = "green";	
	return true;
}
