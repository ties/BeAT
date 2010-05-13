function getBenchmarks(d){
	//console.log('Getting benchmarks: '+d);
	$.ajax({
		url: 'ajax/benchmarks/',
		type: 'POST',
		data: d,
		beforeSend: function(){
						$("#ajaxload").append('<img src="/site_media/img/ajaxload.gif" />');
					},
		success: function(json){
					handleResponse(json);
				},
		error: function(XMLHttpRequest,textStatus,errorThrown){
					alert("Error with getting results: "+textStatus);
				},
		complete: function(){
					$("#ajaxload").html('');
				},
		dataType: 'json'
	});
}

function handleResponse(json){
	/** Add response-specific code here, e.g.: saving possible options, models, algorithms and tool **/
	possible_options = json.options;
	possible_lists = new Array(json.models,json.algorithms,json.tools);
	possible_columns = json.columns
	$(possible_columns).each(function(i,obj){
		alert(obj.header);
	});
	var table = '';
	
	$(json.benchmarks).each(function(i,benchmark){
		table+='<tr>\n\
			<td><input type="checkbox" name="benchmarks" value="' + benchmark.id + '" /></td>\n\
			<td><label for="{{ ' + benchmark.id + ' }}">' + benchmark.model + '</label></td>\n\
			<td>' + benchmark.states + '</td>\n\
			<td>' + (Math.round(benchmark.runtime*100)/100) + '</td>\n\
			<td>' + benchmark.memory + '</td>\n\
			<td>' + benchmark.finished + '</td></tr>';
	});
	$("table.benchmarks").html(getTableHeaders()+table);
	
	renewFilters();
	storeValues();
	showColumnOptions();
}

function getTableHeaders(){
	var res = '<tr><th>&nbsp;</th>';
	for (var i=0;i<DEFAULTCOLUMNS.length;i++){
		res+= '<th id="'+DEFAULTCOLUMNS[i]+'_sort">'+DEFAULTCOLUMNS[i]+'</th>';
	}
	res+='</tr>';
	return res;
}
