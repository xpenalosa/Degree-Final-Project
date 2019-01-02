function updateSearch() {
	var input, filter, list, tournaments, tournament_name, txtValue;
	input = document.getElementById("searchBar");
	filter = input.value.toUpperCase();

	list = document.getElementById("list");
	tournaments = list.getElementsByTagName("li");
	for (i = 0; i < tournaments.length; i++){
		console.log(i);
		tournament_name = tournaments[i].getElementsByClassName("name");

		txtValue = tournament_name[0].textContent;
		console.log(txtValue);

		if (txtValue.toUpperCase().indexOf(filter) > -1) {
			tournaments[i].style.display = "";
		} else {
			tournaments[i].style.display = "none";
		}
	}
}
