function getAlgorithms(d){
	$.ajax({
		url: '/benchmarks/ajax/modelcompare/',
		type: 'POST',
		data: d,
		success: function(json){
					handleResults(json);
				},
		error: function(XMLHttpRequest,textStatus,errorThrown){
					alert("Error with getting results: "+textStatus);
				},
		dataType: 'json'
	});
}

function handleResults(json){
	alert(json);
}

$(document).ready(function() {
	$('#id_tool').change(function(){
		alert(this.value);
		var data = 'tool='+this.id;
		getAlgorithms(data);
	});
});