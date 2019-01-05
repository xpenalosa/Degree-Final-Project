function replaceAt(string, index, replace) {
	if (index == string.length){
		index = index - 1;
	}
	return string.substring(0, index) + replace + string.substring(index + 1);
}

function update_classification(p) {
	var player = arguments[0];
	var p_id = player.id;
	
	if (p_id.split(" ")[1] == "empty" || player.firstElementChild.innerHTML == ""){
		return;
	}
	
	var row = player.parentElement;
	var r_id = row.id.split(" ")[1];
	var classif = document.getElementsByName("classification")[0];
	var matches = parseInt(classif.value.length);
	var num_rows = Math.log2(matches + 1) + 1;
	if (r_id == "base"){
		r_id = num_rows - 1;
	}
	r_id = parseInt(r_id);
	var position = 0;
	for (var i = num_rows - 1; i > r_id; i--){
		var positions_in_row = 2 ** (i-1);
		position = position + positions_in_row;
	}
	position = position + Math.floor(parseInt(p_id) / 2);
	var new_classif;
	if (parseInt(p_id) % 2 == 0) {
		new_classif = replaceAt(classif.value, position, "1");
	}
	else {
		new_classif = replaceAt(classif.value, position, "2");
	}
	classif.value = new_classif;

	update_brackets();
}


function filter_spacers(e) {
	var elems = arguments[0].children;

	unfiltered_elems = [];
	for (var i = 0; i < elems.length; i++){
		if (elems[i].id == "spacer" || elems[i].className == "spacer"){
			continue;
		}
		unfiltered_elems.push(elems[i]);
	}
	return unfiltered_elems;
	
}

function update_brackets() {
	var classif = document.getElementsByName("classification")[0];
	var classif_values = classif.value.split("");

	var rows = filter_spacers(document.getElementById("canvas").children[0]);
	// Start from the base
	rows.reverse();

	var next_row_players = filter_spacers(rows[0]);
	for (var r = 0; r < rows.length - 1; r++){

		var players = next_row_players;
		next_row_players = filter_spacers(rows[r+1]);

		for (var p = 0; p < players.length; p = p+2){
			var match = classif_values.shift();
			if (match == "U"){
				continue;
			}

			var player_slot = next_row_players[Math.floor(p/2)];
			var new_name = player_slot.children[0];

			if (match == "1"){
				new_name.innerHTML = players[p].children[0].innerHTML;
			}
			else if (match == "2"){
				new_name.innerHTML = players[p+1].children[0].innerHTML;
			}
		}
	}
}

window.onload = update_brackets;
