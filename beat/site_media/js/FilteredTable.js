//local variables that define what the contents of the select-elements are in the filter
var name_filterStyle = '<option value="equal">Equal to</option><option value="contains">Contains</option><option value="beginswith">Begins with</option><option value="endswith">Ends with</option>';
var date_filterStyle = '<option value="on">On</option><option value="before">Before</option><option value="after">After</option>';
var memory_filterStyle = '<option value="equal">Equal to</option><option value="greaterthan">Greater than</option><option value="lessthan">Less than</option>';
var runtime_filterStyle = '<option value="equal">Equal to</option><option value="greaterthan">Greater than</option><option value="lessthan">Less than</option>';
var states_filterStyle = '<option value="equal">Equal to</option><option value="greaterthan">Greater than</option><option value="lessthan">Less than</option>';
var transitions_filterStyle = '<option value="equal">Equal to</option><option value="greaterthan">Greater than</option><option value="lessthan">Less than</option>';
var options_filterStyle = '<option value="0">Options (hover)</option>';
var empty_filterStyle = '<option value="empty">&lt;empty&gt;</option>';

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
					<option value="name">Name</option>\n\
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
	//get the class, so we can see what has changed
	var filterclass = elem.className;
	//if the element changed is a filterAt-element, the filterWith must be changed
	if (filterclass == 'filterType'){
		//get the value, so we can identify what the filterAt is
		var value = elem.value;
		
		switch(value){
			case "empty":
				//set the text
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html('<option value="empty">&lt;empty&gt;</option>');
				//remove the hover-div if it exists
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				//show the filterOn-textinput if it was hidden
				$(elem).siblings('input.filterValue').show();
			break;
			case "name":
				//set the text
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(name_filterStyle);
				//remove the hover-div if it exists
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				//show the filterOn-textinput if it was hidden
				$(elem).siblings('input.filterValue').show();
			break;
			case "date":
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(date_filterStyle);
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				$(elem).siblings('input.filterValue').show();
			break;
			case "memory":
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(memory_filterStyle);
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				$(elem).siblings('input.filterValue').show();
			break;
			case "runtime":
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(runtime_filterStyle);
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				$(elem).siblings('input.filterValue').show();
			break;
			case "states":
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(states_filterStyle);
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				$(elem).siblings('input.filterValue').show();
			break;
			case "transitions":
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(transitions_filterStyle);
				$(elem).siblings('ul.mega').children('li.mega').children('div').remove();
				$(elem).siblings('input.filterValue').show();
			break;
			case "options":
				$(elem).siblings('ul.mega').children('li.mega').children('select.filterStyle').html(options_filterStyle);
				//hide the filterOn-textinput
				$(elem).siblings('input.filterValue').hide();
				//insert the hover-div
				$(elem).siblings('ul.mega').children('li.mega').children('select').after('\
					<div>\n\
						<input type="checkbox" value="cache" class="optionName">cache<input type="text" class="optionValue"><br>\n\
						<input type="checkbox" value="option 7" class="optionName">Option 7 <input type="text" class="optionValue"><br>\n\
						<input type="checkbox" value="option 6" class="optionName">Option 6 <input type="text" class="optionValue"><br>\n\
						<input type="checkbox" value="option 5" class="optionName">Option 5 <input type="text" class="optionValue"><br>\n\
						<input type="checkbox" value="option 4" class="optionName">Option 4 <input type="text" class="optionValue"><br>\n\
						<input type="checkbox" value="option 3" class="optionName">Option 3 <input type="text" class="optionValue"><br>\n\
						<input type="checkbox" value="option 2" class="optionName">Option 2 <input type="text" class="optionValue"><br>\n\
					</div>');
			break;
		}
	}
}

function filter(){
	var d = collectData();
	alert(d);
	if (d!=""){
		$.ajax({
			url: 'ajax/filter/',
			data: d,
			beforeSend: function(){
							$("#ajaxload").append('<img src="/site_media/img/ajaxload.gif" />');
						},
			success: function(a){
						/*var headers = '<tr>\n\
											<th>&nbsp;</th>\n\
											<th>Model</th>\n\
											<th>States</th>\n\
											<th>Runtime</th>\n\
											<th>VSize</th>\n\
											<th>Finished</th>\n\
										</tr>';
						$("table.benchmarks").empty();
						$("table.benchmarks").append(headers);
						$(a).each(function(i,json){
							$("table.benchmarks").append('<tr>\n\
								<td><input type="checkbox" name="benchmarks" value="'+json.pk+'" /></td>\n\
								<td>'+json.fields.model_ID[0]+'.'+json.fields.model_ID[1]+'</td>\n\
								<td>'+json.fields.states_count+'</td>\n\
								<td>'+json.fields.elapsed_time+'</td>\n\
								<td>'+json.fields.memory_VSIZE+'</td>\n\
								<td>true</td></tr>');
						});*/
						alert(a);
					},
			error: function(XMLHttpRequest,textStatus,errorThrown){
						alert("Error: "+textStatus);
					},
			complete: function(){
							$("#ajaxload").empty();
						},
			dataType: 'json'
		});
	}
}

function collectData(){
	var res = "";
	var count = 0;
	var filterrows = $('#filters tr');
	
	for (var i=0;i<filterrows.length;i++){
		//get the type
		var type = $("#filterrow_"+i+" .filterType").attr('value');
		if (type!="empty"){
			if (type=="options"){
				var checkboxes = $("#filterrow_"+i+" .optionName");
				var values = $("#filterrow_"+i+" .optionValue");
				for (var j=0;j<checkboxes.length;j++){
					if (checkboxes[j].checked==true){
						res+="filter"+count+"=options,"+checkboxes[j].value+","+values[j].value+"&";
						count++;
					}
				}
			}else{
				res+="filter"+count+"="+type+","+$("#filterrow_"+i+" .filterStyle").attr('value')+","+$("#filterrow_"+i+" .filterValue").attr('value')+"&";
				count++;
			}
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
});