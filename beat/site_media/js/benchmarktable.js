/** Constant for ascending sortorder **/
var ASCENDING = "ASC";
/** Constant for descending sortorder **/
var DESCENDING = "DESC";

var DELAY = 600;

/** Global variable which keeps default column names, the names of these columns in the database and whether they are checked or not **/
var columns =	[
					{
						name: 		"States",
						db_name: 	"states_count",
						checked: 	true
					},
					{
						name: 		"Transitions",
						db_name: 	"transition_count",
						checked: 	false
					},
					{
						name: 		"Runtime",
						db_name: 	"total_time",
						checked: 	true
					},
					{
						name: 		"Memory (RSS)",
						db_name: 	"memory_RSS",
						checked: 	true
					},
					{
						name: 		"Memory (VSIZE)",
						db_name: 	"memory_VSIZE",
						checked: 	false
					},
					{
						name: 		"Tool",
						db_name: 	"algorithm_tool__tool__name",
						checked: 	false
					},
					{
						name: 		"Algorithm",
						db_name: 	"algorithm_tool__algorithm__name",
						checked: 	false
					},
					{
						name: 		"Date",
						db_name: 	"date_time",
						checked: 	false
					},
					{
						name: 		"Finished",
						db_name: 	"finished",
						checked: 	true
					}
				];

/** Global variable where id's of checked benchmarks are stored **/
var checked_benchmarks = [];

/** Global variable which is true when the table is updating and false otherwise **/
var updating = false;
var updateagain = false;

/** Global variable that keeps the benchmarks of the current page **/
var benchmarks = [];

/** Global variable that keeps all the benchmark_ids **/
var benchmark_ids = [];

var data =	{
				sort:			"id",
				sortorder:		ASCENDING,
				columns:		getColumns(),
				extracolumns:	[],
				page:			0,
				pagesize:		200,
				filters:		[],
				subset:			[]
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
		
	}else{
		console.log('skipping');
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
	console.log("Received "+benchmarks.length+" benchmarks!");
	
	updateCheckedBenchmarks();
	
	showResults();
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
			
			var benchmark = benchmarks[i];
			var check = (checked_benchmarks.indexOf(benchmark.id)!=-1);
			
			table+='<tr><td><input type="checkbox"'+(check ? ' checked' : '')+' name="benchmarks" value="' + benchmark.id + '" /></td>\n\
				<td><label for="{{ ' + benchmark.id + ' }}">' + benchmark.model__name + '</label></td>';
			
			for (var j=0; j<columns.length;j++){
				if (columns[j].checked)		table+='<td>'+benchmark[columns[j].db_name]+'</td>';
			}
			table+='</tr>';
			
		}
	}
	$("table.benchmarks").html(getTableHeaders()+table);
	
	//right align all numbers
	if (benchmarks.length){
		var i = 3;
		for (var j=0; j<columns.length;j++){
			if (columns[j].checked){
				if (typeof benchmarks[0][columns[j].db_name] == "number"){
					$(".benchmarks tr td:nth-child(" + i + ")").css('text-align','right');
					i++;
				}
			}
		}
	}
	
	updatePagingTable();
	configureSorting();
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
	//contains model by default
	var c = '';
	if (data.sort == 'model__name')		c = (data.sortorder==ASCENDING ? 'ascending' : 'descending');
	res+='<th id="model__name"><span class="'+c+'">Model</span></th>';
	
	for (var i=0;i<columns.length;i++){
		if (columns[i].checked){
			var c = '';
			if (columns[i].db_name == data.sort){
				c = (data.sortorder == ASCENDING ? 'ascending' : 'descending');
			}
			res+='<th id="'+columns[i].db_name+'"><span class="'+c+'">'+columns[i].name+'</span></th>';
		}
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
	var newarr = new Array();
	
	for (var i=0;i<benchmark_ids.length;i++){
		if (checked_benchmarks.indexOf(benchmark_ids[i])!=-1)	newarr.push(benchmark_ids[i]);
	}
	checked_benchmarks = newarr;
	//console.log("Updated checked benchmarks: "+checked_benchmarks.toString()+", previous length: "+len+", new length: "+checked_benchmarks.length);
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
	//console.log("Checked all "+checked_benchmarks.length+" benchmarks");
	updateCheckboxes();
}

/**
 * Function to change current selection to an empty list
 * @ensure 		checked_benchmarks.length==0
 *				The checkboxes are updated (updateCheckboxes is called)
 **/
function checkNone(){
	//console.log("Check none");
	checked_benchmarks = new Array();
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
	//console.log("Invert selection");
	var newarr = new Array();
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

/**
 * Function that returns the selected columns
 * @ensure 	result!='undefined'
 *			result is in JSON-format, containing an object with an array "columns", containing all selected column-names
 */
function getColumns(){
	var res = new Array('id','model__name');
	for (var i=0;i<columns.length;i++){
		if (columns[i].checked)		res.push(columns[i].db_name);
	}
	return res;
}

/**
 * Function to change the current sorting
 * @require 	sort != 'undefined'
 *				id != 'undefined'
 * @ensure 		If sort.sort == id then sort.sortorder is changed to the other possible value
 *				If sort.sort != id then sort.sort = id
 *				The headers of the benchmarktable are updated to the new sorting
 *				paging.page is set to 0 and the benchmarktable is updated
 **/
function setSorting(id){
	$("table.benchmarks tr th span").removeClass();
	if (data.sort == id){
		if(data.sortorder == ASCENDING){
			data.sortorder = DESCENDING;
			$("#"+id+" span").addClass('descending');
		}else{
			data.sortorder = ASCENDING;
			$("#"+id+" span").addClass('ascending');
		}
	}else{
		data.sort = id;
		data.sortorder = ASCENDING;
		$("#"+id+" span").addClass('ascending');
	}
	//console.log("Sending request after sorting (with page 0)");
	data.page = 0;
	update();
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
	showColumnOptions();
	registerFunctionsAndEvents();
	var temporarycontext = 	{
								models: 	[],
								algorithms: [],
								tools: 		[],
								options: 	[]
							};
	table = $("#filters").filtertable([], temporarycontext);
	$(document).bind($(table).triggercode(),function(){
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
	configureColumnSelection();
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
		//console.log('starting function, value = '+$(this).attr('value'));
		if ($(this).attr('value') == "All" )	checkAll();
		else									checkNone();
	});
	$("#InvertAll").click(function(){
		checkInvert();
	});
	$("#checkedfilter").click(function(){
		setSubset();
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
 * Function to configure the selecting of a column
 * @ensure When clicking on a column checkbox, the corresponding value in columns.checked_columns is set to the value of the checkbox
 **/
function configureColumnSelection(){
	$("#columns input").click(function(){
		var val = $(this).attr('value');
		for (var i = 0; i<columns.length;i++){
			if (columns[i].db_name == val)	columns[i].checked = this.checked;
		}
		
		data.columns = getColumns();
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
		//console.log("Currently checked benchmarks: "+checked_benchmarks.toString());
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
 * Function that sets the inner html of the columns-element
 **/
function showColumnOptions(){
	
	var html = '';
	for (var i=0;i<columns.length;i++){
		html+= '<input type="checkbox" value="'+columns[i].db_name+'"'+(columns[i].checked ? ' checked' : '')+'>'+columns[i].name+'<br />';
	}
	$("#columns").html(html);
	
}

/**
 * Function called when a mega drop-down menu must be shown
 * @ensure	$(elem).hasClass("hovering")==True
 */
function addMega(elem){
	$(elem).addClass("hovering");
	//console.log('Add megadropdownmenu: '+elem.id);
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
 * Function that configures the click-event of the headers of the benchmarktable
 * @ensure When clicking a header, the function setSorting is called
 **/
function configureSorting(){
	var headers = $("table.benchmarks tr th");
	$(headers).each(function(i,h){
		var header = $(h);
		if (header.attr('id')!='' ){
			header.click(function(){
				setSorting(this.id);
			});
		}
	});
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