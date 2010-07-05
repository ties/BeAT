/** Constant for ascending/descending sortorder **/
var ASCENDING = "ASC";
var DESCENDING = "DESC";

var DELAY = 2000;

/** Global variable where id's of checked benchmarks are stored **/
var checked_benchmarks = [];

/** Global variable which is true when the table is updating and false otherwise **/
var updating = false;
var updateagain = false;

/** Global variable that keeps the benchmarks of the current page **/
var benchmarks = [];

/** Global variable that keeps all the benchmark_ids **/
var benchmark_ids = [];

/** All possible columns **/
var columns;

var data =	{
				sort:				[],
				columns:			['model__name','states_count','total_time','memory_RSS','finished'], //This is for the first request
				page:				0,
				pagesize:			25,
				filters:			[],
				subset:				[],
			};

var table;
var timeout;

var previousRequest;
var previousSucceededRequest;

/**
 * Function that sends a request to the server
 * @param d object The data to be send with the request (a JSON object)
 * @require d != 'undefined'
 * @ensure	The reply of the filter is send to handleResponse 
 *			Errors are handled by giving an alert of the errordescription
 *			An ajax load image is visible on the page while a request is being made
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

//function that will start the makerequest
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
		else							timeout = setTimeout(function(){makeRequest(data);},0);
		
	}
}

/**
 * Function that handles the response from the server
 * @param json object The contents of the servers' reply (a JSON object)
 * @require 	json!='undefined'
 *				json is in JSON-format
 *				json contains the variables options, models, algorithms, tools, columns and benchmarks
 * @ensure 		possible_options == json.options
 *				possible_lists == new Array(json.models,json.algorithms,json.tools)
 *				benchmarks == json.benchmarks
 *				benchmark_ids == json.benchmark_ids
 *				The checked_benchmarks variable is updated so that it does not contain id's that are not in the current QuerySet
 *				The benchmarktable is updated with the newest values
 *				The filters on the page are renewed
 */
function handleResponse(json){
	$(table).updateContext(json);
	
	benchmarks = json.benchmarks;
	benchmark_ids = json.benchmark_ids;
	
	columns = json.columns;
	showMultisort();
	
	updateCheckedBenchmarks();
	
	updateColumns();
	showResults();
}

function updateColumns(){
	$('#columns').empty();
	for (var i = 0; i < columns.length; i++){
		var col = $('<input type="checkbox" value="'+columns[i].dbname+'" />')
					.change(function(){
						if ($(this).attr('checked'))
							data.columns.push($(this).val());
						else
							data.columns.splice(data.columns.indexOf($(this).val()), 1);
					})
					.attr('checked',(data.columns.indexOf(columns[i].dbname)!=-1));
		$('#columns').append(col).append(' '+columns[i].name+'<br />');
	}
}

/**
 * Function that shows the results of a request in the benchmarktable
 * @require benchmarks!='undefined'
 * @ensure 	The benchmarkresults contained in benchmarks are shown in the benchmarktable
 *			The pagingtable (the small table under the benchmarktable showing the current resperpage etc.) is updated (updatePagingTable is called)
 *			The headers are configured with sorting-functionality (configureSorting is called)
 *			The checkboxes are configured with the click-event (configureCheckboxes is called)
 **/
function showResults(){
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
	$("table.benchmarks").html(getTableHeaders()+table);
	
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
	
	updatePagingTable();
	configureCheckboxes();
}

/**
 * Function that returns the headers to be added to the top of the table
 * @require 	sort!='undefined'
 *				columns!='undefined'
 * @ensure 	The result contains a header for model__name and the headers for all checked columns
 */
function getTableHeaders(){
	var res = '<tr><th>&nbsp;</th>';
	for (var i = 0; i < columns.length; i++){
		if (data.columns.indexOf(columns[i].dbname)!=-1)
			res+= '<th id="'+columns[i].dbname+'"><span class="">'+columns[i].name+'</span></th>';
	}
	res+='</tr>';
	return res;
}

/**
 * Function that updates the paging table (small table under the benchmarktable containing the previous/next page buttons etc.)
 * @require 	paging != 'undefined'
 *				benchmark_ids != 'undefined'
 * @ensure		The paging table (with id=paginginfo) is updated
 **/
function updatePagingTable(){
	var start = (data.page * data.pagesize + 1);
	var end = (benchmark_ids.length < ((data.page + 1) * data.pagesize) ? benchmark_ids.length : ((data.page + 1) * data.pagesize));
	var txt = 'Showing results '+start+'-'+end+' of '+(benchmark_ids.length)+
		' results with <form id="pagesizeform" style="display:inline;"><input type="text" name="pagesize" id="pagesize" value="'+data.pagesize+'" size="3" /></form> results per page';
	$("#paginginfo").html(txt);
	configurePagesize();
}

/**
 * Function to update the global variable checked_benchmarks
 * @require 	checked_benchmarks != 'undefined'
 *				benchmark_ids != 'undefined'
 * @ensure		checked_benchmarks contains all elements of old.checked_benchmarks that are also in benchmark_ids
 **/
function updateCheckedBenchmarks(){
	var len = checked_benchmarks.length;
	var newarr = [];
	
	for (var i=0;i<benchmark_ids.length;i++){
		if (checked_benchmarks.indexOf(benchmark_ids[i])!=-1)	newarr.push(benchmark_ids[i]);
	}
	checked_benchmarks = newarr;
}

/**
 * Function to check all benchmarks in the current QuerySet
 * @require 	benchmark_ids != 'undefined'
 * @ensure 		checked_benchmarks = benchmark_ids.slice()
 *				The checkboxes are updated (updateCheckboxes is called)
 **/
function checkAll(){
	checked_benchmarks = benchmark_ids.slice();
	$("#CheckAll").attr("value","None");
	updateCheckboxes();
}

/**
 * Function to change current selection to an empty list
 * @ensure 		checked_benchmarks.length==0
 *				The checkboxes are updated (updateCheckboxes is called)
 **/
function checkNone(){
	checked_benchmarks = [];
	$("#CheckAll").attr("value","All");
	updateCheckboxes();
}

/**
 * Function to invert te current selection
 * @require 	checked_benchmarks != 'undefined'
 *				benchmark_ids != 'undefined'
 * @ensure 		checked_benchmarks = benchmark_ids - old.checked_benchmarks
 *				The checkboxes are updated (updateCheckboxes is called)
 **/
function checkInvert(){
	var newarr = [];
	for (var i=0;i<benchmark_ids.length;i++){
		if (checked_benchmarks.indexOf(benchmark_ids[i])==-1)	newarr.push(benchmark_ids[i]);
	}
	checked_benchmarks = newarr;
	updateCheckboxes();
}

/**
 * Function that updates all checkboxes to checked or unchecked
 * @require 	checked_benchmarks != 'undefined'
 * @ensure 		All checkboxes where checkbox.value is in checked_benchmarks are checked, all others are unchecked
 **/
function updateCheckboxes(){
	$("table.benchmarks input").each(function(i,obj){
		$(obj).attr('checked',(checked_benchmarks.indexOf(obj.value)!=-1));
	});
}

function setSubset(){
	data.subset = checked_benchmarks;
	update(true);
}

/**
 * Function that is called when the document has finished loading.
 * @ensure	showColumnOptions is called
 *			registerFunctionsAndEvents is called
 *			The first filter f is added to filters with f.type=EMPTY and f.row=0
 *			makeRequest is called with a makeData over getFilters(), getSort(), getColumns() and getPaing()
 */
$(document).ready(function(){
	showMultisort();
	registerFunctionsAndEvents();
	var temporarycontext = 	{
								models: 	[],
								algorithms: [],
								tools: 		[],
								options: 	[]
							};
	
	table = $("#filters").filtertable([], temporarycontext);
	
	$(document).bind($(table).triggercode(),function(){
		data.page = 0;
		update();
	});
	
	update(true);
	
});

/** ------------------ Functions for events etc! -------------------------- **/

/**
 * Function that registers some functions and events
 * @ensure 	Array.index is defined
 *			configureHover is called
 *			configureLiveUpdate is called
 *			configureColumnSelection is called
 *			Functionality for clicking the next-button, previous-button, check all/none-button and invert-button is added
 **/
function registerFunctionsAndEvents(){
	
	Array.prototype.indexOf = function (element,offset) {
		if (typeof offset=='undefined'){
			offset=0;
		}
		for (var i = offset; i < this.length; i++) {
			if (this[i] == element) {
				return i;
			}
		}
		return -1;
	}
	
	configureHover();
	configurePagesize();
	
	$("#next").click(function(){
		nextPage();
	});
	
	$("#previous").click(function(){
		previousPage();
	});
	
	$("#last").click(function(){
		lastPage();
	});
	
	$("#first").click(function(){
		firstPage();
	});
	
	$("#CheckAll").click(function(){
		if ($(this).attr('value') == "All" )	checkAll();
		else									checkNone();
	});
	
	$("#InvertAll").click(function(){
		checkInvert();
	});
	$("#checkedfilter").click(function(){
		setSubset();
	});
	
	$("#csvform").submit(function(){
		var ids = JSON.stringify(checked_benchmarks);
		$("#ids").val(ids);
	});
}

function configurePagesize(){
	$("#pagesizeform").submit(function(){
		if (/(^-?\d\d*$)/.test($("#pagesize").val())){
			data.pagesize = parseInt($("#pagesize").val());
			data.page = 0;
			update();
		}
		return false;
	});
}

/**
 * Function that configures the click-event for the checkboxes in the benchmarktable (for selecting benchmarks)
 * @ensure When clicking on a checkbox, it's value is either added or removed from checked_benchmarks
 **/
function configureCheckboxes(){
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
 * Function that adds hoverIntent to all <li>-elements with class "mega"
 * @ensure	Every <li>-element with the class "mega" has the hoverIntent configured with addMega as mouseover function and removeMega as mouseoutfunction
 */
function configureHover(){
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
}

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
 * Function to go to the next page of the benchmarktable, if there is one
 * @ensure paging.page = old.paging.page + 1 and makeRequest is called if there is a next page and the filters don't contain an error
 **/
function nextPage(){
	var check = benchmark_ids.length > ((data.page+1) * data.pagesize);
	if (check){
		data.page++;
		update();
	}
}

/**
 * Function to go to the previous page of the benchmarktable, if there is one
 * @ensure paging.page = old.paging.page - 1 and makeRequest is called if there is a previous page and the filters don't contain an error
 **/
function previousPage(){
	if (data.page>0){
		data.page--;
		update();
	}
}

function lastPage(){
	data.page = Math.ceil(benchmark_ids.length / data.pagesize) - 1
	update();
}

function firstPage(){
	data.page = 0;
	update();
}

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