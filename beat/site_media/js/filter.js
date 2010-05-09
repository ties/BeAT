/** Some constants for the filtersystem: **/
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

/** global constant which contains the filterStyle of the DATE filter **/
var DATEFILTERSTYLE = '<option value="on">On</option><option value="before">Before</option><option value="after">After</option>';
/** global constant which contains the filterStyle of the VALUE filters **/
var VALUEFILTERSTYLE = '<option value="equal">Equal to</option><option value="greaterthan">Greater than</option><option value="lessthan">Less than</option>';
/** global constant which contains the filterStyle of the OPTIONS filters **/
var OPTIONSFILTERSTYLE = '<option value="0">Options (hover)</option>';
/** global constant which contains the filterStyle of the EMPTY filter **/
var EMPTYFILTERSTYLE = '<option value="empty">&lt;empty&gt;</option>';
/** global constant which contains the filterStyle of the FINISHED filter **/
var FINISHEDFILTERSTYLE = '<option value="true">True</option><option value="false">False</option>';

/** global constant array which contains the filterStyles of the LIST filters **/
var LISTFILTERSTYLES = new Array(
	'<option value="0">Model (hover)</option>',
	'<option value="0">Algorithm (hover)</option>',
	'<option value="0">Tool (hover)</option>');

/** global constant which contains the class of the EMPTY filter **/
var EMPTYFILTER = '({"type" : "","row" : -1,"value" : ""})';
/** global constant which contains the class of the LIST filters **/
var LISTFILTER = '({"type" : "","row" : -1,"list" : []})';
/** global constant which contains the class of the VALUE filters **/
var VALUEFILTER = '({"type" : "","row" : -1,"style" : "","value": -1})';
/** global constant which contains the class of the DATE filter **/
var DATEFILTER = '({"type" : "","row" : -1,"style" : "","value": -1})';
/** global constant which contains the class of the OPTIONS filters **/
var OPTIONSFILTER = '({"type" : "","row" : -1,"options" : [],"values": []})';
/** global constant which contains the class of the FINISHED filter **/
var FINISHEDFILTER = '({"type" : "","row" : -1,"value" : []})';

/** global array ORDERS which keeps all the possible orders in it **/
var ORDERS = new Array('id','model','states','runtime','memory_rss','finished');

var DEFAULTCOLUMNS = new Array('model__name','states_count','total_time','memory_RSS','finished');

/** global array filters which keeps all the stored filters in it **/
var filters = new Array();
/** global array possible_options which keeps all possible options in it **/
var possible_options = new Array();
/** global array possible_lists which keeps all the possible models, algorithms and tools in it (in that order) **/
var possible_lists = new Array(new Array(), new Array(), new Array());

/** global variable current_order which keeps the current order in it **/
var current_sort = ORDERS[0];
/** global variable current_order which keeps the current order in it **/
var current_sort_order = "ASC";
/** global variable possible_colums which keeps the possible extra columns in it, which are derived from table extra_values in the database **/
var possible_columns = new Array();
var checked_columns = DEFAULTCOLUMNS;
var checked_benchmarks = new Array();


/**
 * Function that adds a filterrow after the filter with filter.row=row
 * @require		row>=0
 * @ensure		A new EMPTY filter is added to filters after the filter with row = row
 * @ensure		The filter-objects in filters are ordered by rownumber
 */
function addFilterRow(row){
	storeValues();
	row = parseInt(row);
	
	$(filters).each(function(i,filter){
		if (filter.row > row){
			filter.row = filter.row+1;
		}
	});
	
	var newf = eval(EMPTYFILTER);
	newf.type = EMPTY;
	newf.row = (row+1);
	filters.push(newf);
	
	sortFilters();
	
	//console.log('Added a new filterrow, current filters: '+filterstring());
	
	renewFilters();
}

/**
 * Function that removes the filterrow with rownumber row
 * @require		row>=0 /\ filters.length>1
 * @ensure		The filterrow with rownumber row is removed from filters
 * @ensure		The filter-objects in filters are ordered by rownumber
 */
function removeFilterRow(row){
	if (filters.length==1){
		alert('cannot remove last filter');
		return;
	}
	
	storeValues();
	var f = new Array();
	row = parseInt(row);
	
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
	
	//console.log('Removed a filterrow, current filters: '+filterstring());
	
	renewFilters();
}

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
 * Function that changes the type of a filter-object
 * @require		elem!='undefined' /\row>=0
 * @ensure		getFilter(row).type = $(elem).attr('value')
 */
function changeFilterType(elem,row){
	storeValues();
	var f;
	type = $(elem).attr('value');
	$('#filterValue'+row).attr('value','');
	
	if (type==EMPTY){
		f = eval(EMPTYFILTER);
	}else if (LISTFILTERS.indexOf(type)!=-1){
		f = eval(LISTFILTER);
	}else if (VALUEFILTERS.indexOf(type)!=-1){
		f = eval(VALUEFILTER);
	}else if (type==DATE){
		f = eval(DATEFILTER);
	}else if (type==OPTIONS){
		f = eval(OPTIONSFILTER);
	}else if (type==FINISHED){
		f = eval(FINISHEDFILTER);
	}
	f.type = type;
	f.row = row;
	filters[row] = f;
	renewFilters();
	//console.log('Changed a filterrow, current filters: '+filterstring());
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
	//console.log('Sorted filters');
}

function storeSelectedIDs(){
	checked_benchmarks = new Array();
	var checkboxes = $("table.benchmarks tr td input");
	$(checkboxes).each(function(i,obj){
		if (obj.checked){
			checked_benchmarks.push(parseInt($(obj).attr('value')));
		}
	});
	//console.log('Stored selected benchmarks: '+checked_benchmarks.toString());
}

/**
 * Function that stores the values of each filterrow
 * @ensure All necessary data needed to recreate the filtertable is stored
 */
function storeValues(){
	$(filters).each(function(i,filter){
		if (filter.type==EMPTY)							storeEmptyFilter(filter);
		else if (LISTFILTERS.indexOf(filter.type)!=-1)	storeListFilter(filter);
		else if (VALUEFILTERS.indexOf(filter.type)!=-1)	storeValueFilter(filter);
		else if (filter.type==DATE)						storeDateFilter(filter);
		else if (filter.type==OPTIONS)					storeOptionsFilter(filter);
		else if (filter.type==FINISHED)					storeFinishedFilter(filter);
	});
	//console.log('Stored filter values');
}

/**
 * Function that stores the values of a filterrow of type EMPTY
 * This filter only needs to store its value
 */
function storeEmptyFilter(filter){
	filter.value = $("#filterValue"+filter.row).attr('value');
}

/**
 * Function that stores the values of a filterrow which has a type specified in LISTFILTERS
 * This filter needs to store which id's are selected
 */
function storeListFilter(filter){
	var selected = $("#filterrow"+filter.row+" select.list option");
	var ids = new Array();
	$(selected).each(function(j,opt){
		if (opt.selected){
			ids.push(opt.value);
		}
	});
	filter.list = ids;
}

/**
 * Function that stores the values of a filterrow which has a type specified in VALUEFILTERS
 */
function storeValueFilter(filter){
	filter.style = $("#filterStyle"+filter.row).attr('value');
	filter.value = $("#filterValue"+filter.row).attr('value');
}

/**
 * Function that stores the values of a filterrow of type DATE
 */
function storeDateFilter(filter){
	filter.style = $("#filterStyle"+filter.row).attr('value');
	filter.value = $("#filterValue"+filter.row).attr('value');
}

/**
 * Function that stores the values of a filterrow of type OPTIONS
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

function storeFinishedFilter(filter){
	filter.value = $("#filterStyle"+filter.row).attr('value');
}

/**
 * Function used to get the contents of the filter in a string
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
	//console.log('Renewed filters');
}

function EmptyFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty" selected>&lt;empty&gt;</option>\n\
						<option value="model">Model</option>\n\
						<option value="algorithm">Algorithm</option>\n\
						<option value="tool">Tool</option>\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						<option value="options">Options</option>\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<ul class="mega">\n\
						<li class="mega">\n\
							<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
								'+EMPTYFILTERSTYLE+'\n\
							</select>\n\
						</li>\n\
					</ul>\n\
					<input type="text" class="filterValue" id="filterValue'+filter.row+'" value="'+filter.value+'">\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

function DateFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						<option value="model">Model</option>\n\
						<option value="algorithm">Algorithm</option>\n\
						<option value="tool">Tool</option>\n\
						<option value="date" selected>Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						<option value="options">Options</option>\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<ul class="mega">\n\
						<li class="mega">\n\
							<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
								<option value="on"'+(filter.style=='on' ? ' selected' : '')+'>On</option>\n\
								<option value="before"'+(filter.style=='before' ? ' selected' : '')+'>Before</option>\n\
								<option value="after"'+(filter.style=='after' ? ' selected' : '')+'>After</option>\n\
							</select>\n\
						</li>\n\
					</ul>\n\
					<input type="text" class="filterValue" id="filterValue'+filter.row+'" value="'+filter.value+'">\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

function ValueFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						<option value="model">Model</option>\n\
						<option value="algorithm">Algorithm</option>\n\
						<option value="tool">Tool</option>\n\
						<option value="date">Date</option>\n\
						<option value="memory"'+(filter.type==MEMORY ? ' selected' : '')+'>Memory</option>\n\
						<option value="runtime"'+(filter.type==RUNTIME ? ' selected' : '')+'>Runtime</option>\n\
						<option value="states"'+(filter.type==STATES ? ' selected' : '')+'>states</option>\n\
						<option value="transitions"'+(filter.type==TRANSITIONS ? ' selected' : '')+'>transitions</option>\n\
						<option value="options">Options</option>\n\
						<option value="finished">Finished</option>\n\
					</select>\n\
					<ul class="mega">\n\
						<li class="mega">\n\
							<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
								<option value="equal"'+(filter.style=='equal' ? ' selected' : '')+'>Equal to</option>\n\
								<option value="greaterthan"'+(filter.style=='greaterthan' ? ' selected' : '')+'>Greater than</option>\n\
								<option value="lessthan"'+(filter.style=='lessthan' ? ' selected' : '')+'>Less than</option>\n\
							</select>\n\
						</li>\n\
					</ul>\n\
					<input type="text" class="filterValue" id="filterValue'+filter.row+'" value="'+filter.value+'">\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

function FinishedFilterRow(filter){
	return '<tr id="filterrow'+filter.row+'">\n\
				<td width="320" align="left">\n\
					<select size="1" class="filterType" id="filterType'+filter.row+'" onchange="changeFilterType(this,'+filter.row+');">\n\
						<option value="empty">&lt;empty&gt;</option>\n\
						<option value="model">Model</option>\n\
						<option value="algorithm">Algorithm</option>\n\
						<option value="tool">Tool</option>\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						<option value="options">Options</option>\n\
						<option value="finished" selected>Finished</option>\n\
					</select>\n\
					<ul class="mega">\n\
						<li class="mega">\n\
							<select size="1" class="filterStyle" id="filterStyle'+filter.row+'">\n\
								<option value="true"'+(filter.value=='true' ? ' selected' : '')+'>True</option>\n\
								<option value="false"'+(filter.value=='false' ? ' selected' : '')+'>False</option>\n\
							</select>\n\
						</li>\n\
					</ul>\n\
				</td>\n\
				<td align="right" style="width:160px">\n\
					<a class="remove" onclick="removeFilterRow('+filter.row+');"><img src="/site_media/img/remove_filter.png" alt="remove"></a>\n\
					<a class="add" onclick="addFilterRow('+filter.row+');"><img src="/site_media/img/add_filter.png" alt="add"></a>\n\
				</td>\n\
			</tr>';
}

function ListFilterRow(filter){
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
						<option value="model"'+(filter.type==MODEL ? ' selected' : '')+'>Model</option>\n\
						<option value="algorithm"'+(filter.type==ALGORITHM ? ' selected' : '')+'>Algorithm</option>\n\
						<option value="tool"'+(filter.type==TOOL ? ' selected' : '')+'>Tool</option>\n\
						<option value="date">Date</option>\n\
						<option value="memory">Memory</option>\n\
						<option value="runtime">Runtime</option>\n\
						<option value="states">states</option>\n\
						<option value="transitions">transitions</option>\n\
						<option value="options">Options</option>\n\
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
						<option value="model">Model</option>\n\
						<option value="algorithm">Algorithm</option>\n\
						<option value="tool">Tool</option>\n\
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
								'+OPTIONSFILTERSTYLE+'\n\
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
 * Function called when a mega drop-down menu must be shown
 * @ensure	$(elem).hassClass("hovering")==True
 */
function addMega(elem){
	$(elem).addClass("hovering");
	//console.log('Add megadropdownmenu: '+elem.id);
}

/**
 * Function called when a mega drop-down menu must be hidden
 * @ensure	$(elem).hassClass("hovering")==False
 */
function removeMega(elem){
	$(elem).removeClass("hovering");
	//console.log('Remove megadropdownmenu: '+elem.id);
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

function filter(){
	storeValues();
	storeSelectedIDs();
	storeSelectedColumns();
	d = 'filters='+getFilter()+'&sort='+getSort()+'&columns='+getColumns();
	//console.log('Sending request to server: '+d);
	getBenchmarks(d);
}

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
					handleJSONResponse(json);
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

function handleJSONResponse(json){
	
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

function getFilter(){
	var json = '[';
	for (var i=0; i<filters.length;i++){
		json+=JSON.stringify(filters[i]);
		if (i<(filters.length-1))	json += ',';
	}
	json += ']';
	return json;
}

function showSortOptions(){
	var txt = "";
	for (var i=0;i<ORDERS.length;i++){
		txt+= '<option value="'+ORDERS[i]+'">'+ORDERS[i]+'</option>';
	}
	$("#sort").html(txt);
}

function changeSort(val){
	current_sort = val;
	//console.log('Change Sorting: '+val);
	storeValues();
	d = 'filters='+getFilter()+'&sort='+getSort();
	getBenchmarks(d);
}

function changeSortOrder(val){
	current_sort_order = val;
	//console.log('Change Sorting Order: '+val);
	storeValues();
	d = 'filters='+getFilter()+'&sort='+getSort();
	getBenchmarks(d);
}

function getSort(){
	var json = '{"sort": "'+current_sort+'", "sortorder": "'+current_sort_order+'"}';
	return json;
}

function showColumnOptions(){
	var txt = "";
	for (var i=0; i<possible_columns.length; i++){
		var b = (checked_columns.indexOf(possible_columns[i].value)!=-1)
		txt+= '<input type="checkbox" name="column" id="'+possible_columns[i].value+'"'+(b ? ' checked' : '')+'>'+possible_columns[i].header+'<br />';
	}
	alert(txt);
	$("#columns").html(txt);
}

function storeSelectedColumns(){
	checked_columns = new Array();
	$("#columns :checked").each(function (i,obj){
		alert(i+','+obj.id);
		checked_columns.push(obj.id);
	});
}

function getColumns(){
	var json = '{"columns":[';
	for (var i=0;i<checked_columns.length;i++){
		json+='"'+checked_columns[i]+'"'+(i<(checked_columns.length-1) ? ',' : '');
	}
	json+=']}';
	alert(json);
	return json;
}

/**
 * Function that is called when the document has finished loading.
 * @ensure	The Array.indexOf function is made /\
 *			The first filter f is added to filters with f.type=EMPTY and f.row=0 /\
 *			configureHover is called
 */
$(document).ready(function(){
	
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
	
	var f = eval(EMPTYFILTER);
	f.row = 0;
	f.type = EMPTY;
	filters = new Array();
	filters.push(f);
	
	configureHover();
	
	getBenchmarks('');
	
	showSortOptions();
	//showColumnOptions();
});