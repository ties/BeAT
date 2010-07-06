/** Constant for ascending/descending sortorder **/
var ASCENDING = "ASC";
var DESCENDING = "DESC";

/** Constant DELAY which specifies the delay between a change and an update **/
var DELAY = 2000;

/** Global variable where id's of checked benchmarks are stored **/
var checked_benchmarks = [];

/** Global variable which is true when the table is updating and false otherwise **/
var updating = false;
/** Global variable which specifies whether there needs to be another update when a running update is finished **/
var updateagain = false;

/** Global variable that keeps the benchmarks of the current page **/
var benchmarks = [];

/** Global variable that keeps all the benchmark_ids **/
var benchmark_ids = [];

/** All possible columns **/
var columns;

/** Global variable data, which contains all data to be sent to the server **/
var data =	{
				sort:				[],
				columns:			['model__name','states_count','total_time','memory_RSS','finished'], //This is for the first request
				page:				0,
				pagesize:			25,
				filters:			[],
				subset:				[],
			};

/** Global variable table, contains the filter table **/
var table;
/** Global variable timeout, contains the result of a setTimeout call which is used to update the benchmark table **/
var timeout;

/** Global variable previousRequest, which contains the JSON.strinify value of data when makeRequest is called. **/
var previousRequest;
/** Global variable previousSucceededRequest, which contains the value of the last previousRequest after a succeeded request to the server. **/
var previousSucceededRequest;

/**
 * Function that sends a request to the server
 * @param d object The data to be send with the request (a JSON object)
 * @require d != undefined
 * @ensure	The reply of the filter is send to handleResponse 
 *			Errors are handled by giving an alert of the error description
 *			An AJAX load image is visible on the page while a request is being made
 **/
function makeRequest(d){
	if (updating){
		updateagain = true;
		return;
	}
	updating = true;
	updateagain = false;
	
	var str = JSON.stringify(d);
	previousRequest = str;
	
	$.ajax({
		url: 			'ajax/benchmarks/',
		type: 			'POST',
		data: 			"data=" + str,
		beforeSend: 	function(){
							$("#ajaxload").append('<img src="/site_media/img/ajaxload.gif" />');
						},
		success: 		function(json){
							handleResponse(json);
							previousSucceededRequest = previousRequest;
						},
		error: 			function(XMLHttpRequest,textStatus,errorThrown){
							alert("Error with getting results: "+textStatus);
						},
		complete: 		function(){
							updating = false;
							$("#ajaxload").html('');
							if (updateagain)	update(true);
						},
		dataType: 		'json'
	});
}

/**
 * Function that is called to make a request
 * @require table!=undefined
 * @param direct If this value is true, makeRequest is called directly, else, a setTimeout with DELAY is called
 **/
function update(direct){
	var filters = $(table).filters();
	
	//strip all filters that have an error:
	var filters2 = [];
	for (var i = 0; i<filters.length; i++){
		if (!filters[i].error)	filters2.push(filters[i]);
	}
	
	data.filters = filters2;
	var str = JSON.stringify(data);
	
	if ((!updating && previousSucceededRequest != str) ||
		(updating && previousRequest != str)){
		
		clearTimeout(timeout);
		if (!direct && !updating)		timeout = setTimeout(function(){makeRequest(data);},DELAY);
		else							makeRequest(data);
		
	}
}

/**
 * Function that handles the response from the server
 * @param json 	The contents of the servers' reply (a JSON object)
 * @require 	json!=undefined
 *				json is in JSON-format
 * @ensure 		benchmarks == json.benchmarks
 *				benchmark_ids == json.benchmark_ids
 *				columns == json.columns
 *				The checked_benchmarks variable is updated so that it does not contain id's that are not in the current QuerySet
 *				The benchmarktable is updated with the newest values
 *				The filters on the page are renewed
 *				The possible columns are updated
 *				The sort table is renewed
 **/
function handleResponse(json){
	//update local variables
	benchmarks = json.benchmarks;
	benchmark_ids = json.benchmark_ids;
	columns = json.columns;
	
	//update context of the filter table
	$(table).updateContext(json);
	
	//update the sort table
	showMultisort();
	
	//remove all identifiers in checked_benchmarks that aren't in the QuerySet anymore
	var newarr = [];
	for (var i=0;i<benchmark_ids.length;i++){
		if (checked_benchmarks.indexOf(benchmark_ids[i])!=-1)	newarr.push(benchmark_ids[i]);
	}
	checked_benchmarks = newarr;
	
	//show the new columns
	showColumns();
	//show results
	showResults();
}

/**
 * Function to show all possible columns so the user can check or uncheck which columns he wants to see in the benchmark table
 **/
function showColumns(){
	$('#columns').empty();
	for (var i = 0; i < columns.length; i++){
		var col = $('<input type="checkbox" value="'+columns[i].dbname+'" />')
					.change(function(){
						if ($(this).attr('checked')){
							data.columns.push($(this).val());
							var newcols = [];
							for (var j = 0; j < columns.length; j++){
								if (data.columns.indexOf(columns[j].dbname)!=-1)
									newcols.push(columns[j].dbname);
							}
							data.columns = newcols;
						}else
							data.columns.splice(data.columns.indexOf($(this).val()), 1);
					})
					.attr('checked',(data.columns.indexOf(columns[i].dbname)!=-1));
		$('#columns').append(col).append(' '+columns[i].name+'<br />');
	}
}

/**
 * Function that shows the results of a request in the benchmarktable
 * @require benchmarks != undefined
 **/
function showResults(){
	//create benchmark table
	var table = "";
	if (benchmarks.length){
		for (var i = 0; i<benchmarks.length; i++){
			
			var b = benchmarks[i];
			var check = (checked_benchmarks.indexOf(b.id)!=-1);
			
			table+='<tr id="row' + b.id + '"><td><input type="checkbox"'+(check ? ' checked' : '')+' name="benchmarks" value="' + b.id + '" /></td>';
			
			for (var j = 0; j < data.columns.length; j++){
				table+= '<td>' + b[data.columns[j]] + '</td>';
			}
			table+='</tr>';
			
		}
	}
	
	var headers = '<tr><th>&nbsp;</th>';
	for (var i = 0; i < columns.length; i++){
		if (data.columns.indexOf(columns[i].dbname)!=-1)
			headers+= '<th id="'+columns[i].dbname+'"><span class="">'+columns[i].name+'</span></th>';
	}
	headers+='</tr>';
	
	$("table.benchmarks").html(headers+table);
	
	//make rows clickable to view benchmark
	$("table.benchmarks tr td:nth-child(n+2)").click(function(){
		var id = $(this).parent().attr('id').substr(3);
		window.open('/benchmarks/'+id);
	});
	
	//right align all numbers
	if (benchmarks.length){
		var i = 2;
		for (var j=0; j<columns.length;j++){
			if (data.columns.indexOf(columns[j].dbname)!=-1){
				if (typeof benchmarks[0][columns[j].dbname] == "number"){
					$(".benchmarks tr td:nth-child(" + i + ")").css('text-align','right');
				}
				i++;
			}
		}
	}
	
	//update paging table
	var start = (data.page * data.pagesize + 1);
	var end = (benchmark_ids.length < ((data.page + 1) * data.pagesize) ? benchmark_ids.length : ((data.page + 1) * data.pagesize));
	var txt = start+'-'+end+' of '+(benchmark_ids.length);
	$("#pagingnumbers").html(txt);
	
	//configure clicking of checkbox
	$("table.benchmarks input").click(function(){
		var id = parseInt($(this).attr('value'));
		var index = checked_benchmarks.indexOf(id);
		
		if ($(this).attr('checked')){
			if (index==-1)		checked_benchmarks.push(id);
		}else{
			if (index!=-1)		checked_benchmarks.splice(index,1);
		}
	});
}

/**
 * Function that updates all checkboxes to checked or unchecked
 * @require 	checked_benchmarks != undefined
 * @ensure 		All checkboxes where checkbox.value is in checked_benchmarks are checked, all others are unchecked
 **/
function updateCheckboxes(){
	$("table.benchmarks input").each(function(i,obj){
		$(obj).attr('checked',(checked_benchmarks.indexOf(obj.value)!=-1));
	});
}

/**
 * Function that is called when the document has finished loading.
 * @ensure	The Array,indefOf function is registered
 *			Some basic events like "All".click are registered
 *			Mega drop down menu's are configured
 *			The filter table is added
 *			update(true) is called
 */
$(document).ready(function(){
	//make Array.indexOf function
	Array.prototype.indexOf = function (element,offset) {
		if (typeof offset==undefined){
			offset=0;
		}
		for (var i = offset; i < this.length; i++) {
			if (this[i] == element) {
				return i;
			}
		}
		return -1;
	}
	
	//configure mega drop down menu's
	$("li.mega").each(function(i,elem){
		var config = {
			sensitivity: 1,
			interval: 100,
			over: function(){addMega(elem)},
			timeout: 500,
			out: function(){removeMega(elem)}
		};
		
		$(elem).hoverIntent(config);
	});
	
	//configure changing of pagesize
	$("#pagesizeform").submit(function(){
		if (/(^-?\d\d*$)/.test($("#pagesize").val())){
			data.pagesize = parseInt($("#pagesize").val());
			data.page = 0;
			update(true);
		}
		return false;
	});
	
	//configure next button
	$("#next").click(function(){
		var check = benchmark_ids.length > ((data.page+1) * data.pagesize);
		if (check){
			data.page++;
			update(true);
		}
	});
	
	//configure previous button
	$("#previous").click(function(){
		if (data.page>0){
			data.page--;
			update(true);
		}
	});
	
	//configure last button
	$("#last").click(function(){
		data.page = Math.ceil(benchmark_ids.length / data.pagesize) - 1
		update(true);
	});
	
	//configure first button
	$("#first").click(function(){
		data.page = 0;
		update(true);
	});
	
	//configure check all button
	$("#checkall").click(function(){
		if ($(this).val() == "All"){
			checked_benchmarks = benchmark_ids.slice();
			$(this).val("None");
			updateCheckboxes();
		}
		else{
			checked_benchmarks = [];
			$("#checkall").val("All");
			updateCheckboxes();
		}
	});
	
	//configure invert button
	$("#invert").click(function(){
		var newarr = [];
		for (var i=0;i<benchmark_ids.length;i++){
			if (checked_benchmarks.indexOf(benchmark_ids[i])==-1)	newarr.push(benchmark_ids[i]);
		}
		checked_benchmarks = newarr;
		updateCheckboxes();
	});
	
	//configure filter selected button
	$("#checkedfilter").click(function(){
		data.subset = checked_benchmarks;
		update(true);
	});
	
	//configure export button
	$("#csvform").submit(function(){
		var ids = JSON.stringify(checked_benchmarks);
		$("#ids").val(ids);
	});
	
	//make filter table
	table = $("#filters").filtertable([], {});
	
	//bind triggercode to an update funtion
	$(document).bind($(table).triggercode(),function(){
		data.page = 0;
		update();
	});
	
	update(true);
	
});

/**
 * Function called when a mega drop-down menu must be shown
 * @ensure	$(elem).hasClass("hovering")==True
 */
function addMega(elem){
	$(elem).addClass("hovering");
}

/**
 * Function called when a mega drop-down menu must be hidden
 * @ensure	$(elem).hasClass("hovering")==False
 *			The benchmarktable is updated if needed
 */
function removeMega(elem){
	$(elem).removeClass("hovering");
	data.page = 0;
	update();
}

/**
 * Function that manages the sort table
 * @require data.sort != undefined
 **/
function showMultisort(){
	//empty multisort to draw again
	$('#multisort').empty();
	
	$(data.sort).each(function(i,s){
		//make column selection
		var sel = $('<select />');
		$(sel).append('<option value="-1">-----</option>')
				.change(function(){
					//on change, update data.sort
					var val = $(this).val();
					if (val == "-1"){
						data.sort.splice(i,1);
						showMultisort();
					}else{
						data.sort[i][0] = val;
					}
					//update
					update();
				});
		
		//add column names to select-element
		$(columns).each(function(j,col){
			if (data.columns.indexOf(col.dbname)!=-1){
				var opt = $('<option value="'+col.dbname+'">'+col.name+'</option>');
				if (s[0] == col.dbname)  $(opt).attr('selected',true);
				$(sel).append(opt);
			}
		});
		
		//add sortorder selection
		var order = $('<select />');
		var order_asc = $('<option value="'+ASCENDING+'">Asc</option>').attr('selected',s[1]==ASCENDING);
		var order_desc = $('<option value="'+DESCENDING+'">Desc</option>').attr('selected',s[1]==DESCENDING);
		$(order).append(order_asc)
				.append(order_desc)
				.change(function(){
					//update data.sort
					var val = $(this).val();
					data.sort[i][1] = val;
					//update table
					update();
				});
		
		//add to multisort table
		var leftcol = $('<td />')
						.append(sel)
						.addClass('columnname');
		var rightcol = $('<td />')
						.append(order)
						.addClass('sortorder');
		var row = $('<tr />').append(leftcol).append(rightcol);
		$('#multisort').append(row);
	});
	
	//add empty sort to the end of the table
	var sel = $('<select />');
	$(sel).append('<option value="-1">-----</option>')
			.change(function(){
				data.sort[data.sort.length] = [$(this).val(),ASCENDING];
				showMultisort();
				update();
			});
	$(columns).each(function(j,col){
		if (data.columns.indexOf(col.dbname)!=-1){
			var opt = $('<option value="'+col.dbname+'">'+col.name+'</option>');
			$(sel).append(opt);
		}
	});

	var order = $('<select />');
	var order_asc = $('<option value="'+ASCENDING+'">Asc</option>');
	var order_desc = $('<option value="'+DESCENDING+'">Desc</option>');
	$(order).append(order_asc)
			.append(order_desc);
	
	var leftcol = $('<td />')
					.append(sel)
					.addClass('columnname');
	var rightcol = $('<td />')
					.append(order)
					.addClass('sortorder');
	var row = $('<tr />').append(leftcol).append(rightcol);
	$('#multisort').append(row);
}