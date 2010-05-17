//new data
var lastData; //Temporary string
var lastRequestString; //String of last succeeded request

/** Global variables and constants for filtering: **/
	/** Constants containing possible filters: **/
	var EMPTY = 'empty';
	var MODEL = 'model';
	var ALGORITHM = 'algorithm';
	var TOOL = 'tool';
	var MEMORY = 'memory';
	var RUNTIME ='runtime';
	var STATES ='states';
	var TRANSITIONS ='transitions';
	var DATE ='date';
	var OPTIONS = 'options';
	var FINISHED = 'finished';

	/** global constant array LISTFILTERS which keeps the names of all the listfilters in it **/
	var LISTFILTERS = new Array(MODEL,ALGORITHM,TOOL);
	/** global constant array VALUEFILTERS which keeps the names of all the valuefilters in it **/
	var VALUEFILTERS = new Array(MEMORY,RUNTIME,STATES,TRANSITIONS);
	/** global constant which contains the class of the EMPTY filter **/
	var EMPTYFILTER = '{"type" : "","row" : -1,"value" : ""}';
	/** global constant which contains the class of the LIST filters **/
	var LISTFILTER = '{"type" : "","row" : -1,"list" : []}';
	/** global constant which contains the class of the VALUE filters **/
	var VALUEFILTER = '{"type" : "","row" : -1,"style" : "","value": -1}';
	/** global constant which contains the class of the DATE filter **/
	var DATEFILTER = '{"type" : "","row" : -1,"style" : "","value": ""}';
	/** global constant which contains the class of the OPTIONS filters **/
	var OPTIONSFILTER = '{"type" : "","row" : -1,"options" : [],"values": []}';
	/** global constant which contains the class of the FINISHED filter **/
	var FINISHEDFILTER = '{"type" : "","row" : -1,"value" : []}';
	
	/** global array filters which keeps all the stored filters in it **/
	var filters = new Array();
	/** global array possible_options which keeps all possible options in it **/
	var possible_options = new Array();
	/** global array possible_lists which keeps all the possible models, algorithms and tools in it (in that order) **/
	var possible_lists = new Array(new Array(), new Array(), new Array());
	
/** End of global variables and constants for filtering **/

/** Global variables and constants for sorting: **/
	
	/** global array ORDERS which keeps all the possible orders in it **/
	var ORDERS = new Array('id','model','states','runtime','memory_rss','finished');
	var ASCENDING = "ASC";
	var DESCENDING = "DESC";
	/** global variable current_order which keeps the current order in it **/
	var current_sort = ORDERS[0];
	/** global variable current_order which keeps the current order in it **/
	var current_sort_order = "ASC";
	var sort = JSON.parse('{"sort":"id","sortorder":"ASC"}');
	
	var previousfilter = "";
	
/** End of global variables and constants for sorting **/

/** Global variables and constants for columns: **/
	var columns = JSON.parse('{"column_names":["States","Transitions","Runtime","Memory (RSS)","Memory (VSIZE)","Tool","Algorithm","Finished"],\
							"column_db_names":["states_count","transition_count","total_time","memory_RSS","memory_VSIZE","algorithm_tool__tool__name","algorithm_tool__algorithm__name","finished"],\
							"column_checked":[true,false,true,true,false,false,false,true]}');
	/** global variable extra_colums which keeps the possible extra columns in it, which are derived from table extra_values in the database **/
	var extra_columns;

/** End of global variables and constants for columns **/

/** Global variable where id's of checked benchmarks are stored **/
var checked_benchmarks = new Array();

/** Global variable which is true when the table is updating and false otherwise **/
var updating = false;

/** Global variable that keeps the benchmarks of the current page **/
var benchmarks = new Array();
/** Global variable that keeps all the benchmark_ids **/
var benchmark_ids = new Array();

/** Global variable that keeps the paging settings, defaults to page 0 and 200 results per page **/
var paging = JSON.parse('{"page":0,"resperpage":200}');

/**
 * Function that gets a filter-object from filters
 * @require		row>=0
 * @ensure		result.row = row
 */
function getFilter(row){
	if (row>=filters.length)	return -1;
	return filters[row];
}

/**
 * Function that sorts the stored filters on their rownumber
 * @ensure The filter-objects in filters are sorted by rownumber
 */
function sortFilters(){
	var f = new Array();
	$(filters).each(function(i,filter){
		f[filter.row] = filter;
	});
	filters = f;
	console.log('Sorted filters');
}

/**
 * Function used to get the contents of the filter in a string, for testing purposes
 */
function filterstring(){
	var print = "";
	for (var i=0;i<filters.length;i++){
		var filter = filters[i];
		
		if (filter.type==EMPTY)						print+=filter.type+":("+filter.row+","+filter.value+")\n";
		if (LISTFILTERS.indexOf(filter.type)!=-1)	print+=filter.type+":("+filter.row+",("+filter.list.toString()+'))\n';
		if (VALUEFILTERS.indexOf(filter.type)!=-1)	print+=filter.type+":("+filter.row+","+filter.style+','+filter.value+")\n";
		if (filter.type==DATE)						print+=filter.type+":("+filter.row+","+filter.style+','+filter.value+")\n";
		if (filter.type==OPTIONS)					print+=filter.type+":("+filter.row+",("+filter.options.toString()+'),('+filter.values.toString()+'))\n';
		if (filter.type==FINISHED)					print+=filter.type+":("+filter.row+","+filter.value+")\n";
	}
	return print;
}

/** 
 * Function that checks whether a filter of type type is set
 * @ensure result=true when a filter f has f.type==type
 **/
function hasFilter(type){
	for (var i=0;i<filters.length;i++){
		if (filters[i].type==type) return true;
	}
	return false;
}

/**
 * Function that takes 
 **/
function makeData(f,s,c,p){
	var data = JSON.parse('{"filters":[],"sort":{},"columns":{},"paging":{}}');
	data.filters = f;
	data.sort = s;
	data.columns = c;
	data.paging = p;
	return data;
}

function checkRequest(req){
	var str = JSON.stringify(req);
	var res = (str!=lastRequestString);
	if (!res)	console.log("Same request as last time!");
	return res;
}

//new function to make request!
function makeRequest(d){
	if (!checkRequest(d)){
		return;
	}
	var str = JSON.stringify(d);
	
	console.log("Making a request! Using data: "+str);
	lastData = str;
	
	$.ajax({
		url: 'ajax/benchmarks/',
		type: 'POST',
		data: "data="+str,
		beforeSend: function(){
						$("#ajaxload").append('<img src="/site_media/img/ajaxload.gif" />');
					},
		success: function(json){
					lastRequestString = lastData;//update last request!
					handleResponse(json);
				},
		error: function(XMLHttpRequest,textStatus,errorThrown){
					alert("Error with getting results: "+textStatus);
				},
		complete: function(){
					updating = false;
					$("#ajaxload").html('');
					console.log("Done!");
				},
		dataType: 'json'
	});
}

/**
 * Function that handles the response from the server
 * @require 	json!='undefined'
 *				json is in JSON-format
 *				json contains the variables options, models, algorithms, tools, columns and benchmarks
 * @ensure The page is updated with the newly received values
 */
function handleResponse(json){
	//set received values
	possible_options = json.options;
	possible_lists = new Array(json.models,json.algorithms,json.tools);
	extra_columns = json.columns
	benchmarks = json.benchmarks;
	benchmark_ids = json.benchmark_ids;
	console.log("Received "+benchmarks.length+" benchmarks!");
	
	//update checked benchmarks
	updateCheckedBenchmarks();
	
	//show results
	showResults();
	renewFilters();
}

function showResults(){
	var table = "";
	for (var i = 0; i<benchmarks.length; i++){
		var benchmark = benchmarks[i];
		var check = (checked_benchmarks.indexOf(benchmark.id)!=-1);
		
		table+='<tr><td><input type="checkbox"'+(check ? ' checked' : '')+' name="benchmarks" value="' + benchmark.id + '" /></td>\n\
			<td><label for="{{ ' + benchmark.id + ' }}">' + benchmark.model__name + '</label></td>';
		
		for (var j=0; j<columns.column_db_names.length;j++){
			if (columns.column_checked[j])		table+='<td>'+benchmark[columns.column_db_names[j]]+'</td>';
		}
		table+='</tr>';
	}
	$("table.benchmarks").html(getTableHeaders()+table);
	updatePagingTable();
	configureSorting();
	configureCheckboxes();
}

/**
 * Function that returns the headers to be added to the top of the table
 */
function getTableHeaders(){
	var res = '<tr><th>&nbsp;</th>';
	//contains model by default
	var c = '';
	if (sort.sort == 'model__name')		c = (sort.sortorder==ASCENDING ? 'ascending' : 'descending');
	res+='<th id="model__name"><span class="'+c+'">Model</span></th>';
	
	for (var i=0;i<columns.column_names.length;i++){
		if (columns.column_checked[i]){
			var c = '';
			if (columns.column_db_names[i]==sort.sort){
				c = (sort.sortorder==ASCENDING ? 'ascending' : 'descending');
			}
			res+='<th id="'+columns.column_db_names[i]+'"><span class="'+c+'">'+columns.column_names[i]+'</span></th>';
		}
	}
	res+='</tr>';
	return res;
}

function updatePagingTable(){
	var begin = (paging.page*paging.resperpage+1);
	var end = (benchmark_ids.length < ((paging.page+1)*paging.resperpage) ? benchmark_ids.length : ((paging.page+1)*paging.resperpage));
	var txt = 'Showing results '+begin+'-'+end+' of '+(benchmark_ids.length)+
		' results with <input type="text" name="resperpage" id="resperpage" value="'+paging.resperpage+'" size="3" /> results per page';
	$("#paginginfo").html(txt);
}

function updateCheckedBenchmarks(){
	var len = checked_benchmarks.length;
	var newarr = new Array();
	
	for (var i=0;i<benchmark_ids.length;i++){
		if (checked_benchmarks.indexOf(benchmark_ids[i])!=-1)	newarr.push(benchmark_ids[i]);
	}
	checked_benchmarks = newarr;
	console.log("Updated checked benchmarks: "+checked_benchmarks.toString()+", previous length: "+len+", new length: "+checked_benchmarks.length);
}

function checkAll(){
	checked_benchmarks = benchmark_ids.slice();
	$("#CheckAll").attr("value","None");
	console.log("Checked all "+checked_benchmarks.length+" benchmarks");
	updateCheckboxes();
}

function checkNone(){
	console.log("Check none");
	checked_benchmarks = new Array();
	$("#CheckAll").attr("value","All");
	updateCheckboxes();
}

function checkInvert(){
	console.log("Invert selection");
	var newarr = new Array();
	for (var i=0;i<benchmark_ids.length;i++){
		if (checked_benchmarks.indexOf(benchmark_ids[i])==-1)	newarr.push(benchmark_ids[i]);
	}
	checked_benchmarks = newarr;
	updateCheckboxes();
}

function updateCheckboxes(){
	$("table.benchmarks input").each(function(i,obj){
		if (checked_benchmarks.indexOf(obj.value)!=-1){
			$(obj).attr('checked',true);
		}else{
			$(obj).attr('checked',false);
		}
	});
}

/**
 * Function that returns the current filter
 * @ensure 	result!='undefined'
 *			result is in JSON-format, containing an array of objects
 */
function getFilters(){
	storeFilters();
	//special case of only one empty filter:
	if (filters.length==1){
		if (getFilter(0).type==EMPTY){
			return new Array();
		}
	}
	for (var i=0;i<filters.length;i++){
		if (!checkFilter(filters[i]))	return "error";
	}
	return filters;
}

function checkFilter(f){
	if (f.type == EMPTY){
		console.log("ERROR: EMPTY FILTER");
		return false;
	}else if(f.type == DATE){
		if (f.style.length==0){
			console.log("ERROR: DATE FILTER STYLE HAS NO CONTENT");
			return false;
		}else if(f.value.length==0){
			console.log("ERROR: DATE FILTER VALUE HAS NO CONTENT");
			return false;
		}else if(!f.value.match(/^[0-9]{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])/)){
			console.log("ERROR: DATE FILTER VALUE DOES NOT MATCH DATE!");
			return false;
		}
	}else if(f.type == OPTIONS){
		if (f.options.length==0){
			console.log("ERROR: OPTIONS FILTER HAS NO CHECKS");
			return false;
		}
	}else if(f.type == FINISHED){
		if (f.value.length==0){
			console.log("ERROR: FINISHED FILTER VALUE HAS NO CONTENT");
			return false;
		}
	}else if(LISTFILTERS.indexOf(f.type)!=-1){
		if (f.list.length==0){
			console.log("ERROR: LIST FILTER ("+f.type+"): LIST IS EMPTY");
			return false;
		}
	}else if(VALUEFILTERS.indexOf(f.type)!=-1){
		if (f.style.length==0){
			console.log("ERROR: VALUE FILTER ("+f.type+") STYLE HAS NO CONTENT");
			return false;
		}else if(f.value.length==0){
			console.log("ERROR: VALUE FILTER ("+f.type+") VALUE HAS NO CONTENT");
			return false;
		}else if((parseInt(f.value)+"")!=f.value){
			console.log("ERROR: VALUE FILTER ("+f.type+") VALUE IS NOT AN INT");
			return false;
		}
	}
	return true;
}

function getPaging(){
	return paging;
}

/**
 * Function that returns the current sorting
 * @ensure 	result!='undefined'
 *			result is in JSON-format, containing an object with a variable sort and a variable sortorder
 */
function getSort(){
	return sort;
}

/**
 * Function that returns the selected columns
 * @ensure 	result!='undefined'
 *			result is in JSON-format, containing an object with an array "columns", containing all selected column-names
 */
function getColumns(){
	var res = new Array('id','model__name');
	for (var i=0;i<columns.column_checked.length;i++){
		if (columns.column_checked[i])	res.push(columns.column_db_names[i]);
	}
	return res;
}

function setSorting(id){
	$("table.benchmarks tr th span").removeClass();
	if (sort.sort == id){
		if(sort.sortorder==ASCENDING){
			sort.sortorder=DESCENDING;
			$("#"+id+" span").addClass('descending');
		}else{
			sort.sortorder=ASCENDING;
			$("#"+id+" span").addClass('ascending');
		}
	}else{
		sort.sort = id;
		sort.sortorder = ASCENDING;
		$("#"+id+" span").addClass('ascending');
	}
	console.log("Sending request after sorting (with page 0)");
	paging.page = 0;
	makeRequest(makeData(getFilters(),getSort(),getColumns(),getPaging()));
}

/**
 * Function that is called when the document has finished loading.
 * @ensure	The Array.indexOf function is made /\
 *			The first filter f is added to filters with f.type=EMPTY and f.row=0 /\
 *			configureHover is called
 */
$(document).ready(function(){
	showColumnOptions();
	registerFunctionsAndEvents();
	
	makeRequest(makeData(getFilters(),getSort(),getColumns(),getPaging()));
	
	var f = JSON.parse(EMPTYFILTER);
	f.row = 0;
	f.type = EMPTY;
	filters = new Array();
	filters.push(f);
	
});

/** ------------------ Functions for events etc! -------------------------- **/

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
	configureLiveUpdate();
	configureColumnSelection();
	
	$("#next").click(function(){
		nextPage();
	});
	
	$("#previous").click(function(){
		previousPage();
	});
	
	$("#CheckAll").click(function(){
		console.log('starting function, value = '+$(this).attr('value'));
		if ($(this).attr('value') == "All" )	checkAll();
		else									checkNone();
	});
	$("#InvertAll").click(function(){
		checkInvert();
	});
}

function configureColumnSelection(){
	$("#columns input").click(function(){
		var val = $(this).attr('value');
		var index = columns.column_db_names.indexOf(val);
		if (index!=-1){
			if (this.checked){
				columns.column_checked[index] = true;
				console.log('Set column '+val+' to true');
			}else{
				columns.column_checked[index] = false;
				console.log('Set column '+val+' to false');
			}
		}
	});
}

function configureLiveUpdate(){
	$(".filterStyle").focusout(function(){
		var f = getFilters();
		if (f!="error"){
			var d = makeData(f,getSort(),getColumns(),getPaging());
			var c = checkRequest(d);
			if (c){
				paging.page = 0;
				makeRequest(makeData(f,getSort(),getColumns(),getPaging()));
			}
		}else{
			console.log("Error in filters, not updating");
		}
	});
	$(".filterValue").focusout(function(){
		var f = getFilters();
		if (f!="error"){
			var d = makeData(f,getSort(),getColumns(),getPaging());
			var c = checkRequest(d);
			if (c){
				paging.page = 0;
				makeRequest(makeData(f,getSort(),getColumns(),getPaging()));
			}
		}else{
			console.log("Error in filters, not updating");
		}
	});
}

function configureCheckboxes(){
	$("table.benchmarks input").click(function(){
		//alert($(this).attr('value') + $(this).attr('checked'));
		var id = parseInt($(this).attr('value'));
		var index = checked_benchmarks.indexOf(id);
		
		if ($(this).attr('checked')){
			if (index==-1)		checked_benchmarks.push(id);
		}else{
			if (index!=-1)		checked_benchmarks.splice(index,1);
		}
		console.log("Currently checked benchmarks: "+checked_benchmarks.toString());
	});
}

/**
 * Function that adds hoverIntent to all <li>-elements with class="mega"
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

function showColumnOptions(){
	
	var html = '';
	for (var i=0;i<columns.column_db_names.length;i++){
		html+= '<input type="checkbox" value="'+columns.column_db_names[i]+'"'+(columns.column_checked[i] ? ' checked' : '')+'>'+columns.column_names[i]+'<br />';
	}
	$("#columns").html(html);
	
}

/**
 * Function called when a mega drop-down menu must be shown
 * @ensure	$(elem).hassClass("hovering")==True
 */
function addMega(elem){
	$(elem).addClass("hovering");
	console.log('Add megadropdownmenu: '+elem.id);
}

/**
 * Function called when a mega drop-down menu must be hidden
 * @ensure	$(elem).hassClass("hovering")==False
 */
function removeMega(elem){
	$(elem).removeClass("hovering");
	console.log('Remove megadropdownmenu: '+elem.id+', updating table!');
	var f = getFilters();
	if (f!="error"){
		var d = makeData(f,getSort(),getColumns(),getPaging());
		var c = checkRequest(d);
		if (c){
			paging.page = 0;
			makeRequest(makeData(f,getSort(),getColumns(),getPaging()));
		}
	}else{
		console.log("Error in filters, not updating");
	}
}

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

function nextPage(){
	var check = benchmark_ids.length > ((paging.page+1)*paging.resperpage);
	if (check){
		paging.page++;
		var f = getFilters();
		if (f!="error"){
			makeRequest(makeData(f,getSort(),getColumns(),getPaging()));
		}else{
			console.log("Error in filters, not updating");
		}
	}
}

function previousPage(){
	if (paging.page>0){
		paging.page--;
		var f = getFilters();
		if (f!="error"){
			makeRequest(makeData(f,getSort(),getColumns(),getPaging()));
		}else{
			console.log("Error in filters, not updating");
		}
	}
}

/** ------------------- Functions for filterrows! ------------------------ **/

/**
 * Function that changes the type of a filter-object
 * @require		elem!='undefined' /\ row>=0
 * @ensure		getFilter(row).type = $(elem).attr('value')
 */
function changeFilterType(elem,row){
	storeFilters();
	var f;
	type = $(elem).attr('value');
	$('#filterValue'+row).attr('value','');
	
	if (type==EMPTY){
		f = JSON.parse(EMPTYFILTER);
	}else if (LISTFILTERS.indexOf(type)!=-1){
		f = JSON.parse(LISTFILTER);
	}else if (VALUEFILTERS.indexOf(type)!=-1){
		f = JSON.parse(VALUEFILTER);
	}else if (type==DATE){
		f = JSON.parse(DATEFILTER);
	}else if (type==OPTIONS){
		f = JSON.parse(OPTIONSFILTER);
	}else if (type==FINISHED){
		f = JSON.parse(FINISHEDFILTER);
	}
	f.type = type;
	f.row = row;
	filters[row] = f;
	
	renewFilters();
	console.log('Changed a filterrow, current filters: '+filterstring());
}

/**
 * Function that adds a filterrow after the filter with filter.row=row
 * @require		row>=0
 * @ensure		A new EMPTY filter is added to filters after the filter with row = row
 * 				The filter-objects in filters are ordered by rownumber
 */
function addFilterRow(row){
	storeFilters();
	row = parseInt(row);
	
	$(filters).each(function(i,filter){
		if (filter.row > row){
			filter.row = filter.row+1;
		}
	});
	
	var newf = JSON.parse(EMPTYFILTER);
	newf.type = EMPTY;
	newf.row = (row+1);
	filters.push(newf);
	
	sortFilters();
	
	console.log('Added a new filterrow, current filters: '+filterstring());
	
	renewFilters();
}

/**
 * Function that removes the filterrow with rownumber row
 * @require		row>=0 /\ filters.length>1
 * @ensure		The filterrow with rownumber row is removed from filters
 * 				The filter-objects in filters are ordered by rownumber
 */
function removeFilterRow(row){
	row = parseInt(row);
	if (filters.length==1){
		alert('cannot remove last filter');
		return;
	}
	
	storeFilters();
	var f = new Array();
	
	$(filters).each(function(i,filter){
		if (filter.row!=row){
			if (filter.row>row){
				filter.row--;
			}
			f[filter.row] = filter;
		}
	});
	
	filters = f;
	sortFilters();
	
	console.log('Removed a filterrow, current filters: '+filterstring());
	
	renewFilters();
	var f = getFilters();
	if (f!="error"){
		var d = makeData(f,getSort(),getColumns(),getPaging());
		var c = checkRequest(d);
		if (c){
			paging.page = 0;
			makeRequest(makeData(f,getSort(),getColumns(),getPaging()));
		}
	}else{
		console.log("Error in filters, not updating");
	}
}

/**
 * Function that renews the filtertable according to the contents of filters
 */
function renewFilters(){
	sortFilters();
	rows = "";
	for (var i=0;i<filters.length;i++){
		var filter = filters[i];
		if (filter.type==EMPTY)							rows+= EmptyFilterRow(filter);
		else if (LISTFILTERS.indexOf(filter.type)!=-1)	rows+= ListFilterRow(filter);
		else if (VALUEFILTERS.indexOf(filter.type)!=-1)	rows+= ValueFilterRow(filter);
		else if (filter.type==DATE)						rows+= DateFilterRow(filter);
		else if (filter.type==OPTIONS)					rows+= OptionsFilterRow(filter);
		else if (filter.type==FINISHED)					rows+= FinishedFilterRow(filter);
	}
	$('#filters').html(rows);
	configureHover();
	configureLiveUpdate();
	console.log('Renewed filters');
}

/**
 * Function that returns the HTML-code of a filterrow of type EMPTY
 * @require filter!='undefined'
 */
function EmptyFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty" selected>&lt;empty&gt;</option>\n\
						'+(hasFilter(MODEL) ? '' : '<option value="model">Model</option>')+'\n\
						'+(hasFilter(ALGORITHM) ? '' : '<option value="algorithm">Algorithm</option>')+'\n\
						'+(hasFilter(TOOL) ? '' : '<option value="tool">Tool</option>')+'\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						'+(hasFilter(OPTIONS) ? '' : '<option value="options">Options</option>')+'\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
					</select>\n\
					<input type="text" class="filterValue" id="filterValue'+filter.row+'" value="'+filter.value+'">\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

/**
 * Function that returns the HTML-code of a filterrow of type DATE
 * @require filter!='undefined'
 */
function DateFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						'+(hasFilter(MODEL) ? '' : '<option value="model">Model</option>')+'\n\
						'+(hasFilter(ALGORITHM) ? '' : '<option value="algorithm">Algorithm</option>')+'\n\
						'+(hasFilter(TOOL) ? '' : '<option value="tool">Tool</option>')+'\n\
						<option value="date" selected>Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						'+(hasFilter(OPTIONS) ? '' : '<option value="options">Options</option>')+'\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
						<option value="on"'+(filter.style=='on' ? ' selected' : '')+'>On</option>\n\
						<option value="before"'+(filter.style=='before' ? ' selected' : '')+'>Before</option>\n\
						<option value="after"'+(filter.style=='after' ? ' selected' : '')+'>After</option>\n\
					</select>\n\
					<input type="text" class="filterValue" id="filterValue'+filter.row+'" value="'+filter.value+'">\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

/**
 * Function that returns the HTML-code of a filterrow of one of the types in VALUEFILTERS
 * @require filter!='undefined'
 */
function ValueFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						'+(hasFilter(MODEL) ? '' : '<option value="model">Model</option>')+'\n\
						'+(hasFilter(ALGORITHM) ? '' : '<option value="algorithm">Algorithm</option>')+'\n\
						'+(hasFilter(TOOL) ? '' : '<option value="tool">Tool</option>')+'\n\
						<option value="date">Date</option>\n\
						<option value="memory"'+(filter.type==MEMORY ? ' selected' : '')+'>Memory</option>\n\
						<option value="runtime"'+(filter.type==RUNTIME ? ' selected' : '')+'>Runtime</option>\n\
						<option value="states"'+(filter.type==STATES ? ' selected' : '')+'>states</option>\n\
						<option value="transitions"'+(filter.type==TRANSITIONS ? ' selected' : '')+'>transitions</option>\n\
						'+(hasFilter(OPTIONS) ? '' : '<option value="options">Options</option>')+'\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
						<option value="equal"'+(filter.style=='equal' ? ' selected' : '')+'>Equal to</option>\n\
						<option value="greaterthan"'+(filter.style=='greaterthan' ? ' selected' : '')+'>Greater than</option>\n\
						<option value="lessthan"'+(filter.style=='lessthan' ? ' selected' : '')+'>Less than</option>\n\
					</select>\n\
					<input type="text" class="filterValue" id="filterValue'+filter.row+'" value="'+(filter.value<0 ? '' : filter.value)+'">\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

/**
 * Function that returns the HTML-code of a filterrow of type FINISHED
 * @require filter!='undefined'
 */
function FinishedFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						'+(hasFilter(MODEL) ? '' : '<option value="model">Model</option>')+'\n\
						'+(hasFilter(ALGORITHM) ? '' : '<option value="algorithm">Algorithm</option>')+'\n\
						'+(hasFilter(TOOL) ? '' : '<option value="tool">Tool</option>')+'\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						'+(hasFilter(OPTIONS) ? '' : '<option value="options">Options</option>')+'\n\
						<option value="finished" selected>Finished</option>\n\
					</select>\n\
					<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
						<option value="true"'+(filter.value=='true' ? ' selected' : '')+'>True</option>\n\
						<option value="false"'+(filter.value=='false' ? ' selected' : '')+'>False</option>\n\
					</select>\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

/**
 * Function that returns the HTML-code of a filterrow of one of the types in LISTFILTERS
 * @require filter!='undefined'
 */
function ListFilterRow(filter){
	
	/** array which contains the filterStyles of the LIST filters **/
	var LISTFILTERSTYLES = new Array(
		'<option value="0">Model (hover)</option>',
		'<option value="0">Algorithm (hover)</option>',
		'<option value="0">Tool (hover)</option>');
	
	var index = LISTFILTERS.indexOf(filter.type);
	var hover = '<div><select multiple size="7" class="list">';
	$(possible_lists[index]).each(function(i,opt){
		hover+='<option value="'+opt.id+'"'+(filter.list.indexOf(opt.id)!=-1 ? ' selected' : '')+'>'+opt.name+(opt.version!=undefined ? ':'+opt.version : '')+'</option>';
	});
	hover+='</select></div>';
	
	var res ='<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						'+(filter.type!=MODEL && hasFilter(MODEL) ? '' : '<option value="model"'+(filter.type==MODEL ? ' selected' : '')+'>Model</option>')+'\n\
						'+(filter.type!=ALGORITHM && hasFilter(ALGORITHM) ? '' : '<option value="algorithm"'+(filter.type==ALGORITHM ? ' selected' : '')+'>Algorithm</option>')+'\n\
						'+(filter.type!=TOOL && hasFilter(TOOL) ? '' : '<option value="tool"'+(filter.type==TOOL ? ' selected' : '')+'>Tool</option>')+'\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						'+(hasFilter(OPTIONS) ? '' : '<option value="options">Options</option>')+'\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<ul class="mega">\n\
						<li class="mega">\n\
							<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
								'+LISTFILTERSTYLES[index]+'\n\
							</select>\n\
							'+hover+'\n\
							\n\
						</li>\n\
					</ul>\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
			return res;
}

/**
 * Function that returns the HTML-code of a filterrow of one type OPTIONS
 * @require filter!='undefined'
 */
function OptionsFilterRow(filter){
	var hover = '<div>';
	$(possible_options).each(
		function(i,option){
			var index = filter.options.indexOf(option.id);
			hover+='<input type="checkbox" value="'+option.id+'" class="optionID"'+(index!=-1 ? ' checked' : '')+'>'+option.name;
			if (option.takes_argument)	hover+=' <input type="text" class="optionValue"'+(index!=-1 ? ' value="'+filter.values[index]+'"' : '')+'>';
			else						hover+=' <input type="hidden" value="True" class="optionValue">';
			hover+='<br>';
		}
	);
	hover+='</div>';
	
	var res ='<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						'+(hasFilter(MODEL) ? '' : '<option value="model">Model</option>')+'\n\
						'+(hasFilter(ALGORITHM) ? '' : '<option value="algorithm">Algorithm</option>')+'\n\
						'+(hasFilter(TOOL) ? '' : '<option value="tool">Tool</option>')+'\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						<option value="options" selected>Options</option>\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<ul class="mega">\n\
						<li class="mega">\n\
							<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
								<option value="0">Options (hover)</option>\n\
							</select>\n\
							'+hover+'\n\
							\n\
						</li>\n\
					</ul>\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
			return res;
}

/**
 * Function that stores the values of each filterrow
 * @ensure All necessary data needed to recreate the filtertable is stored
 */
function storeFilters(){
	$(filters).each(function(i,filter){
		if (filter.type==EMPTY)							storeEmptyFilter(filter);
		else if (LISTFILTERS.indexOf(filter.type)!=-1)	storeListFilter(filter);
		else if (VALUEFILTERS.indexOf(filter.type)!=-1)	storeValueFilter(filter);
		else if (filter.type==DATE)						storeDateFilter(filter);
		else if (filter.type==OPTIONS)					storeOptionsFilter(filter);
		else if (filter.type==FINISHED)					storeFinishedFilter(filter);
	});
	console.log('Stored filter values');
}

/**
 * Function that stores the values of a filterrow of type EMPTY
 * @require filter!='undefined'
 * @ensure filter.value==$("#filterValue"+filter.row).attr('value');
 */
function storeEmptyFilter(filter){
	filter.value = $("#filterValue"+filter.row).attr('value');
}

/**
 * Function that stores the values of a filterrow of one of the types in LISTFILTERS
 * @require filter!='undefined'
 * @ensure Every checked option's id is stored inside filter.list
 */
function storeListFilter(filter){
	var selected = $("#filterrow"+filter.row+" select.list option");
	var ids = new Array();
	$(selected).each(function(j,opt){
		if (opt.selected){
			ids.push(parseInt(opt.value));
		}
	});
	filter.list = ids;
}

/**
 * Function that stores the values of a filterrow of one of the types in VALUEFILTERS
 * @require filter!='undefined'
 * @ensure 	filter.style == $("#filterStyle"+filter.row).attr('value')
 * 			filter.value == $("#filterValue"+filter.row).attr('value')
 */
function storeValueFilter(filter){
	filter.style = $("#filterStyle"+filter.row).attr('value');
	filter.value = $("#filterValue"+filter.row).attr('value');
}

/**
 * Function that stores the values of a filterrow of type DATE
 * @require filter!='undefined'
 * @ensure 	filter.style == $("#filterStyle"+filter.row).attr('value')
 * 			filter.value == $("#filterValue"+filter.row).attr('value')
 */
function storeDateFilter(filter){
	filter.style = $("#filterStyle"+filter.row).attr('value');
	filter.value = $("#filterValue"+filter.row).attr('value');
}

/**
 * Function that stores the values of a filterrow of type OPTIONS
 * @require filter!='undefined'
 * @ensure 	Of every checked option, the id and value are stored in filter.options and filter.values. 
 * 			If the option does not require an argument, the value is set to "True"
 */
function storeOptionsFilter(filter){
	var checkboxes = $("#filterrow"+filter.row+" .optionID");
	var values = $("#filterrow"+filter.row+" .optionValue");
	
	var optionids = new Array();
	var optionvalues = new Array();
	
	for (var j=0;j<checkboxes.length;j++){
		if (checkboxes[j].checked==true){
			optionids.push(checkboxes[j].value)
			optionvalues.push(values[j].value);
		}
	}
	filter.options = optionids;
	filter.values = optionvalues;
}

/**
 * Function that stores the values of a filterrow of type OPTIONS
 * @require filter!='undefined'
 * @ensure 	filter.value == $("#filterStyle"+filter.row).attr('value')
 */
function storeFinishedFilter(filter){
	filter.value = $("#filterStyle"+filter.row).attr('value');
}