//local variables that define what the contents of the select-elements are in the filter
var date_filterStyle = '<option value="on">On</option><option value="before">Before</option><option value="after">After</option>';
var text_filterStyle = '<option value="equal">Equal to</option><option value="contains">Contains</option><option value="beginswith">Begins with</option><option value="endswith">Ends with</option>';;
var number_filterStyle = '<option value="equal">Equal to</option><option value="greaterthan">Greater than</option><option value="lessthan">Less than</option>';
var options_filterStyle = '<option value="0">Options (hover)</option>';
var modelname_filterStyle = '<option value="0">Model (hover)</option>';
var algorithmname_filterStyle = '<option value="0">Algorithm (hover)</option>';
var toolname_filterStyle = '<option value="0">Tool (hover)</option>';
var empty_filterStyle = '<option value="empty">&lt;empty&gt;</option>';

var LISTFILTERS = new Array(
	'modelname',
	'toolname',
	'algorithmname');
var LISTFILTERSTYLES = new Array(
	'<option value="0">Model (hover)</option>', 
	'<option value="0">Tool (hover)</option>', 
	'<option value="0">Algorithm (hover)</option>');
var OPTIONFILTERS = new Array('options');
var VALUEFILTERS = new Array('memory','runtime','states','transitions');
var DATEFILTERS = new Array('date');

var options;
/*var tools;
var algorithms;
var models;*/
var lists;
var order = "id";

var TABLEHEADERS = '<tr>\n\
	<th>&nbsp;</th>\n\
	<th>Model</th>\n\
	<th>States</th>\n\
	<th>Runtime</th>\n\
	<th>Memory (RSS)</th>\n\
	<th>Finished</th>\n\
</tr>';

/*
 * Function to add a filterrow to the filtertable, will be placed after the caller
 */
function addFilter(caller){
	//get the id of the caller (this equals the row number)
	var callerid = parseInt(caller.id.substr(4));
	//rename all of the id's that come after the caller
	var filterrows = $('#filters tr');
	var i;

	for (i=filterrows.length;i>callerid;i--){
		$("#filterrow_"+i).attr('id','filterrow_'+(i+1));
		$('#rem_'+i).attr('id','rem_'+(i+1));
		$('#add_'+i).attr('id','add_'+(i+1));
	}

	//insert new filter
	$("#filterrow_"+callerid).after(
		'<tr id="filterrow_'+(callerid+1)+'">\n\
			<td width="320" align="left">\n\
				<select size="1" class="filterType" onchange="changedFilter(this);">\n\
					<option value="empty">&lt;empty&gt;</option>\n\
					<option value="modelname">Model</option>\n\
					<option value="algorithmname">Algorithm</option>\n\
					<option value="toolname">Tool</option>\n\
					<option value="date">Date</option>\n\
					<option value="memory">Memory</option>\n\
					<option value="runtime">Runtime</option>\n\
					<option value="states">states</option>\n\
					<option value="transitions">transitions</option>\n\
					<option value="options">Options</option>\n\
				</select>\n\
				<ul class="mega">\n\
					<li class="mega">\n\
						<select size="1" class="filterStyle" onchange="changedFilter(this);">\n\
							<option value="empty">&lt;empty&gt;</option>\n\
						</select>\n\
					</li>\n\
				</ul>\n\
				<input type="text" class="filterValue" onchange="changedFilter(this);">\n\
			</td>\n\
			<td align="right" style="width:160px">\n\
				<a class="remove" id="rem_'+(callerid+1)+'">\n\
					<img src="/site_media/img/remove_filter.png" alt="remove">\n\
				</a>\n\
				<a class="add" id="add_'+(callerid+1)+'">\n\
					<img src="/site_media/img/add_filter.png" alt="add">\n\
				</a>\n\
			</td>\n\
		</tr>');

	//set click actions
	$("#rem_"+(callerid+1)).click(function(){
		removeFilter(this);
		return false;
	});
	$("#add_"+(callerid+1)).click(function(){
		addFilter(this);
		return false;
	});
	//set hover action
	$("li.mega").hover(
		function(){
			addMega($(this));
		},
		function(){
			removeMega($(this));
		}
	);

}

/*
 * Function to remove a filter from the list
 */
function removeFilter(caller){
	//get the id of the filter
	var callerid = parseInt(caller.id.substr(4));
	//remove specified filter
	$('#filterrow_'+callerid).remove();
	
	//rename all filter id's afther the caller
	var filterrows = $('#filters tr');
	var i;
	
	for (i=callerid;i<filterrows.length;i++){
		var row_id = parseInt(filterrows[i].id.substr(10));
		$("#filterrow_"+row_id).attr('id','filterrow_'+(row_id-1));
		$('#rem_'+row_id).attr('id','rem_'+(row_id-1));
		$('#add_'+row_id).attr('id','add_'+(row_id-1));
	}
}

/*
 * Function called when a mega drop-down menu must be shown
 */
function addMega(elem){
	$(elem).addClass("hovering");
}

/*
 * Function called when a mega drop-down menu must be hidden
 */
function removeMega(elem){
	$(elem).removeClass("hovering");
}

/*
 * Function called when an element (elem) in a filter has been changed
 */
function changedFilter(elem){
	
	if (elem.className=='filterType'){
		var type = elem.value;
		if(LISTFILTERS.indexOf(type)!=-1){
			var index = LISTFILTERS.indexOf(type);
			
			$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(LISTFILTERSTYLES[index]);
			$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
			$(elem).siblings('input.filterValue').hide();
			
			var hover = '<div><select multiple size="7" class="list">';
			$(lists[index]).each(function(i,opt){
				hover+='<option value="'+opt.id+'">'+opt.name+'</option>';
			});
			hover+='</select></div>';
			$(elem).siblings('ul.mega').children('li.mega').children('select').after(hover);
		}else if(OPTIONFILTERS.indexOf(type)!=-1){
			$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(options_filterStyle);
			$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
			$(elem).siblings('input.filterValue').hide();
			var hover = '<div>';
			$(options).each(
				function(i,option){
					hover+='<input type="checkbox" value="'+option.id+'" class="optionID">'+option.name;
					if (option.takes_argument)	hover+=' <input type="text" class="optionValue">';
					else						hover+=' <input type="hidden" value="True" class="optionValue">';
					hover+='<br>';
				}
			);
			hover+='</div>';
			$(elem).siblings('ul.mega').children('li.mega').children('select').after(hover);
		}else if(VALUEFILTERS.indexOf(type)!=-1){
			$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(number_filterStyle);
			$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
			$(elem).siblings('input.filterValue').show();
		}else if(DATEFILTERS.indexOf(type)!=-1){
			$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(date_filterStyle);
			$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
			$(elem).siblings('input.filterValue').show();
		}else if(type=='empty'){
			$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html('<option value="empty">&lt;empty&gt;</option>');
			$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
			$(elem).siblings('input.filterValue').show();
		}
	}
}

function filter(){
	d = getFilter();
	if (d.substr(0,5).toLowerCase()=='error'){
		alert(d);
	}else{
		getBenchmarks(d);
	}
}

function getBenchmarks(d){
	$.ajax({
		url: 'ajax/benchmarks/',
		type: 'POST',
		data: d,
		beforeSend: function(){
						$("#ajaxload").append('<img src="/site_media/img/ajaxload.gif" />');
					},
		success: function(json){
					handleBenchmarks(json);
				},
		error: function(XMLHttpRequest,textStatus,errorThrown){
					alert("Error with getting results: "+textStatus);
				},
		complete: function(){
					$("#ajaxload").empty();
				},
		dataType: 'json'
	});
}

function handleBenchmarks(json){
	options = json.options;
	lists = new Array(json.models,json.tools,json.algorithms);
	
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
	$("table.benchmarks").empty();
	$("table.benchmarks").append(TABLEHEADERS+table);
}

function getFilter(){
	res = "";
	var filterrows = $('#filters tr');
	for (var i=0;i<filterrows.length;i++){
		var type = $("#filterrow_"+i+" .filterType").attr('value');
		if (type!="empty"){
			res+="filter"+i+"="+type+"&";
			if (LISTFILTERS.indexOf(type)!=-1){
				var selected = $("#filterrow_"+i+" select.list option");
				$(selected).each(function(j,opt){
					if (opt.selected){
						res+="filter"+i+"="+opt.value+"&";
					}
				});
			}else if(OPTIONFILTERS.indexOf(type)!=-1){
				var checkboxes = $("#filterrow_"+i+" .optionID");
				var values = $("#filterrow_"+i+" .optionValue");
				
				for (var j=0;j<checkboxes.length;j++){
					if (checkboxes[j].checked==true){
						res+="filter"+i+"="+checkboxes[j].value+","+values[j].value+"&";
					}
				}
			}else if(VALUEFILTERS.indexOf(type)!=-1){
				res+="filter"+i+"="+$("#filterrow_"+i+" .filterStyle").attr('value')+"&";
				res+="filter"+i+"="+$("#filterrow_"+i+" .filterValue").attr('value')+"&";
			}else if(DATEFILTERS.indexOf(type)!=-1){
				res+="filter"+i+"="+$("#filterrow_"+i+" .filterStyle").attr('value')+"&";
				res+="filter"+i+"="+$("#filterrow_"+i+" .filterValue").attr('value')+"&";
			}
		}else{
			return "Error: empty row detected";
		}
	}
	
	return res;
}

/*
 * Function called when the document is loaded
 */
$(document).ready(function() {
	//set hover action
	$("li.mega").hover(
		function(){
			addMega($(this));
		},
		function(){
			removeMega($(this));
		}
	);
	//set click actions
	$("a.add").click(function(){
		addFilter(this);
		return false;
	});

	$("a.remove").click(function(){
		removeFilter(this);
		return false;
	});
	
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
	
	getBenchmarks('');
});