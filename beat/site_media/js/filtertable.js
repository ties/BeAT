/**
 * jQuery plugin for the filtertable
 **/
(function($) {
	
	var EMPTY			= 'empty';
	var MODEL 			= 'model__name';
	var ALGORITHM 		= 'algorithm_tool__algorithm__name';
	var TOOL 			= 'algorithm_tool__tool__name';
	var MEMORY_RSS		= 'memory_RSS';
	var MEMORY_VSIZE	= 'memory_VSIZE';
	var RUNTIME 		= 'total_time';
	var STATES 			= 'states_count';
	var TRANSITIONS 	= 'transition_count';
	var DATE 			= 'date_time';
	var OPTIONS 		= 'options';
	var FINISHED 		= 'finished';
	var COMPUTERNAME 	= 'computername';
	var CPU 			= 'cpu';
	var RAM				= 'memory';
	var VERSION			= 'algorithm_tool__version';
	var KERNELVERSION	= 'kernelversion';
	var DISKSPACE		= 'disk_space';
	
	var LISTFILTERSIZE 	= 10;
	
	function filtername(type){
		switch(type){
			case EMPTY:
				return '&lt;empty&gt;';
			break;
			case MODEL:
				return 'Model name';
			break;
			case ALGORITHM:
				return 'Algorithm name';
			break;
			case TOOL:
				return 'Tool name';
			break;
			case MEMORY_RSS:
				return 'Memory (RSS)';
			break;
			case MEMORY_VSIZE:
				return 'Memory (VSIZE)';
			break;
			case RUNTIME:
				return 'Runtime';
			break;
			case STATES:
				return 'States';
			break;
			case TRANSITIONS:
				return 'Transitions';
			break;
			case DATE:
				return 'Date';
			break;
			case OPTIONS:
				return 'Options';
			break;
			case FINISHED:
				return 'Finished';
			break;
			case COMPUTERNAME:
				return 'Computername';
			break;
			case CPU:
				return 'Processor';
			break;
			case RAM:
				return 'RAM';
			break;
			case VERSION:
				return 'Version';
			break;
			case KERNELVERSION:
				return 'Kernelversion';
			break;
			case DISKSPACE:
				return 'Disk space';
			break;
		}
		return type;
	}
	
	var ALLFILTERS = [EMPTY,MODEL,ALGORITHM,TOOL,MEMORY_RSS,MEMORY_VSIZE,RUNTIME,STATES,TRANSITIONS,DATE,OPTIONS,FINISHED,CPU,RAM,COMPUTERNAME,VERSION,KERNELVERSION,DISKSPACE];
	var LISTFILTERS = [MODEL,ALGORITHM,TOOL,COMPUTERNAME,CPU,VERSION,KERNELVERSION];
	var VALUEFILTERS = [MEMORY_RSS,MEMORY_VSIZE,RUNTIME,STATES,TRANSITIONS,RAM,DISKSPACE];
	var UNIQUEFILTERS = [MODEL,ALGORITHM,TOOL,OPTIONS,COMPUTERNAME,CPU,VERSION,KERNELVERSION];

	var FILTERTEMPLATE = '{"type" : "", "row" : -1, "style":"", "value" : "", "error" : true}';
	
	var ERRORCOLOR = "#FF9999";
	var TRIGGERCODE = 'filterupdate';

	$.fn.filtertable = function (filterarray, context) {
		return this.each(function () {
			var list = new $.startfiltertable(this, filterarray, context);
		});
	};

	$.startfiltertable = function (table, filterarray, context){
		
		$.fn.filters = function(){
			var res = [];
			for (var i=0; i < filterarray.length; i++){
				res.push($.extend({},filterarray[i]));
			}
			return res;
		}
		
		$.fn.triggercode = function(){
			return TRIGGERCODE;
		}
		
		$.fn.updateContext = function(newcontext){
			context = newcontext;
			
			$(filterarray).each(function(i,filterobj){
				if (filterobj.type == OPTIONS){
					var newval = [[],[]];
					for (var j=0;j<filterobj.value[0].length;j++){
						if (indexOfId(context.options,filterobj.value[0][j])!=-1){
							newval[0].push(filterobj.value[0][j]);
							newval[1].push(filterobj.value[1][j]);
						}
					}
					filterobj.value = newval;
					rewriteRow(filterobj,filterarray,table);
				}else if(LISTFILTERS.indexOf(filterobj.type)!=-1){
					var newval = [];
					for (var j=0;j<filterobj.value.length;j++){
						if (context[filterobj.type].indexOf(filterobj.value[j])!=-1)		newval.push(filterobj.value[j]);
					}
					filterobj.value = newval;
					rewriteRow(filterobj,filterarray,table);
				}
			});
		}
		
		initTable(filterarray);
		
		/**
		 * Function that initializes the filtertable
		 * @param tbl jQuery A jQuery object representing a table in the document
		 * @param farr array An array containing all the filters to be shown in the table
		 **/
		function initTable(farr){
			//if there is no filter, add an empty one
			if (farr.length==0){
				var f = $.parseJSON(FILTERTEMPLATE);
				f.type = EMPTY;
				f.row = 0;
				f.style = "empty";
				
				farr.push(f);
			}
			showTable(table, farr);
		}
		
		/**
		 * Function that shows the table
		 **/
		function showTable(tbl,farr){
			$(tbl).empty();
			
			$(farr).each(function(i,obj){
				var contents = makeRowContents(obj,farr,tbl);
				var row = $('<tr id="filterrow'+obj.row+'"></tr>');
				
				$(contents).each(function(j,col){
					$(row).append(col);
				});
				
				$(tbl).append($(row));
				if (LISTFILTERS.indexOf(obj.type)!=-1)	$("#filterValue"+obj.row).tokenInput(context[obj.type], LISTFILTERSIZE, obj.value);
				if (obj.error){
					$("#filterrow"+obj.row+" td input").css("background",ERRORCOLOR);
					$("#filterrow"+obj.row+" td .token-input-input-token").css("background",ERRORCOLOR);
					$("#filterrow"+obj.row+" td li.mega").css("background",ERRORCOLOR);
				}
			});
		}
		
		function makeRowContents(filterobj,farr,tbl){
			var rowcontent = [];
			
			var ftype = $('<select size="1" class="filterType" id="filterType'+(filterobj.row)+'"></select>')
								.change(function(){
									filterobj.type = $(this).val();
									filterobj.style = "";
									filterobj.value = "";
									
									if (filterobj.type==FINISHED){
										filterobj.error = false;
										filterobj.value = true;
									}else
										filterobj.error = true;
									
									rewriteRow(filterobj,farr,tbl);
								});
			
			$(ALLFILTERS).each(function (i,val){
				
				if(!(UNIQUEFILTERS.indexOf(val)!=-1 && hasFilterType(val,farr) && filterobj.type!=val)){
					
					var option = $('<option value="'+val+'" class="'+val+'">' + filtername(val) + '</option>');
					if (filterobj.type==val)
						$(option).attr('selected',true);
					
					$(ftype).append(option);
					
				}
				
			});
			var td = $('<td></td>');
			$(td).append(ftype);
			rowcontent.push($(td));
			
			if (filterobj.type == EMPTY){
				filterobj.style = "empty";
				
				var fstyle = $('<select size="1" class="filterStyle" id="filterStyle'+filterobj.row+'"></select>')
								.change(function(){
									filterobj.style = $(this).val();
									sendTrigger();
								});
				$(fstyle).append('<option value="empty">&lt;empty&gt;</option>');
				
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" value="'+filterobj.value+'" />')
								.change(function(){
									filterobj.value = $(this).val();
									filterobj.error = true;
								});
				$(fvalue).addClass("filterValue");
				
				var td1 = $('<td></td>');
				$(td1).append(fstyle);
				var td2 = $('<td></td>');
				$(td2).append(fvalue);
				
				rowcontent.push($(td1));
				rowcontent.push($(td2));
			}else if(VALUEFILTERS.indexOf(filterobj.type)!=-1){
				if (filterobj.style == "")	filterobj.style = "equal";
				var fstyle = $('<select size="1" class="filterStyle" id="filterStyle'+filterobj.row+'"></select>')
								.change(function(){
									filterobj.style = $(this).val();
									sendTrigger();
								});
				$(fstyle).append('<option value="equal"'+(filterobj.style=='equal' ? ' selected' : '')+'>=</option>');
				$(fstyle).append('<option value="greaterthan"'+(filterobj.style=='greaterthan' ? ' selected' : '')+'>&gt;=</option>');
				$(fstyle).append('<option value="lessthan"'+(filterobj.style=='lessthan' ? ' selected' : '')+'>&lt;=</option>');
				
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" value="'+filterobj.value+'" />')
									.keyup(function(){
										filterobj.value = $(this).val();
										filterobj.error = !(is_float(filterobj.value));
										setErrorCSS(filterobj);
										sendTrigger();
									});
				$(fvalue).addClass("filterValue");
				
				var td1 = $('<td></td>');
				$(td1).append(fstyle);
				var td2 = $('<td></td>');
				$(td2).append(fvalue);
				
				rowcontent.push($(td1));
				rowcontent.push($(td2));
			}else if(LISTFILTERS.indexOf(filterobj.type)!=-1){
				filterobj.style = "";
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" />')
								.change(function(){
									//var arr = [];
									//$($(this).val().split(',')).each(function(i,str){
									//	if (str.length)		arr.push(str);
									//});
									filterobj.value = $(this).val().split(',');
									filterobj.error = (filterobj.value.length==0);
									setErrorCSS(filterobj);
									sendTrigger();
								});
				$(fvalue).addClass("filterValue");
				
				var td1 = $('<td></td>');
				$(td1).attr('colspan',2);
				$(td1).append(fvalue);
				
				rowcontent.push($(td1));
			}else if(filterobj.type == DATE){
				if (!filterobj.style)	filterobj.style = "on";
				var fstyle = $('<select size="1" class="filterStyle" id="filterStyle'+filterobj.row+'"></select>')
								.change(function(){
									filterobj.style = $(this).val();
									sendTrigger();
								});
				$(fstyle).append('<option value="on"'+(filterobj.style=='on' ? ' selected' : '')+'>On</option>');
				$(fstyle).append('<option value="before"'+(filterobj.style=='before' ? ' selected' : '')+'>Before or on</option>');
				$(fstyle).append('<option value="after"'+(filterobj.style=='after' ? ' selected' : '')+'>After or on</option>');
				
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" value="'+filterobj.value+'" />')
								.change(function(){
									filterobj.value = $(this).val();
									filterobj.error = !(is_date($(this).val()));
									setErrorCSS(filterobj);
									sendTrigger();
								});
				$(fvalue).addClass("filterValue");
				
				var td1 = $('<td></td>');
				$(td1).append(fstyle);
				var td2 = $('<td></td>');
				$(td2).append(fvalue);
				
				rowcontent.push($(td1));
				rowcontent.push($(td2));
			}else if (filterobj.type == OPTIONS){
				if(!filterobj.value.length){
					filterobj.value = [[],[]];
				}
				var hovertbl = $('<table cellspacing="1" cellpadding="0"></table>');
				$(context.options).each(function(i,option){
					var row = $('<tr></tr>'); var td1 = $('<td></td>'); var td2 = $('<td></td>'); var td3 = $('<td></td>');
					var index = filterobj.value[0].indexOf(option.id);
					
					var checkbox = $('<input type="checkbox" value="'+option.id+'" class="optionId" id="optionId'+option.id+'" />')
						.change(function(){
							var id = parseInt($(this).val());
							if ($(this).attr('checked')){
								filterobj.value[0].push(id);
								filterobj.value[1].push($("#optionValue"+id).val());
							}else{
								var remindex = filterobj.value[0].indexOf(id);
								if (remindex!=-1){
									filterobj.value[0].splice(remindex,1);
									filterobj.value[1].splice(remindex,1);
								}
							}
							filterobj.error = (filterobj.value[0].length==0);
							setErrorCSS(filterobj);
						});
					$(checkbox).attr('checked',(index!=-1));
					$(td1).append($(checkbox));
					$(td2).append(option.name);
					
					var value;
					if (option.takes_argument){
						value = $('<input type="text" id="optionValue'+option.id+'" class="optionValue">')
									.keyup(function(){
										filterobj.value[1][filterobj.value[0].indexOf(option.id)] = $(this).val();
									});
						if (index!=-1)	$(value).val(filterobj.value[1][index]);
					}else{
						value = $('<input type="hidden" id="optionValue'+option.id+'" value="True" class="optionValue">');
					}
					$(td3).append(value);
					
					$(row).append(td1);
					$(row).append(td2);
					$(row).append(td3);
					$(hovertbl).append(row);
				});
				
				var hover = $('<div></div>');
				$(hover).append(hovertbl);
				
				var megaul = $('<ul class="mega"></ul>');
				var megali = $('<li class="mega">(hover)</li>').css('padding-right',100);
				$(megali).hoverIntent({
					sensitivity: 1,
					interval: 100,
					over: function(){$(this).addClass('hovering')},
					timeout: 500,
					out: function(){$(this).removeClass('hovering'); sendTrigger();}
				});
				
				
				$(megali).append(hover);
				$(megaul).append(megali);
				
				var td1 = $('<td></td>');
				$(td1).attr('colspan',2);
				$(td1).append(megaul);
				
				rowcontent.push($(td1));
			}else if (filterobj.type == FINISHED){
				//always false
				filterobj.error = false;
				var fvalue = $('<select size="1" class="filterValue" id="filterValue'+filterobj.row+'"></select>')
								.change(function(){
									filterobj.value = $(this).val();
									filterobj.error = false;
									sendTrigger();
								});
				$(fvalue).append('<option value="true">True</option><option value="false">False</option>');
				
				var td1 = $('<td></td>');
				$(td1).append(fvalue);
				
				rowcontent.push($(td1));
			}			
			
			var rem = $('<a class="remove"></a>')
						.click(function(){
							removeFilter(filterobj,farr,tbl);
						});
			$(rem).append($('<img src="/site_media/img/remove_filter.png" alt="- " />'));
			
			var add = $('<a class="add"></a>')
						.click(function(){
							addFilter(filterobj,farr,tbl);
						});
			$(add).append($('<img src="/site_media/img/add_filter.png" alt=" +" />'));
			
			var span = $('<span></span>');
			$(span).append(rem).append(add);
			rowcontent.push(span);
			var td1 = $('<td></td>');
			$(td1).append(span);
			
			rowcontent.push($(td1));
			
			return rowcontent;
		}
		
		function rewriteRow(filterobj,farr,tbl){
			var contents = makeRowContents(filterobj,farr,tbl);
			var row = $('#filterrow'+filterobj.row);
			$(row).empty();
			$(contents).each(function(j,col){
				$(row).append(col);
			});
			
			if (LISTFILTERS.indexOf(filterobj.type)!=-1)	$("#filterValue"+filterobj.row).tokenInput(context[filterobj.type], LISTFILTERSIZE, filterobj.value);
			if (filterobj.error){
				$("#filterrow"+filterobj.row+" td input").css("background",ERRORCOLOR);
				$("#filterrow"+filterobj.row+" td .token-input-input-token").css("background",ERRORCOLOR);
				$("#filterrow"+filterobj.row+" td li.mega").css("background",ERRORCOLOR);
			}
		}
		
		function setErrorCSS(filterobj){
			if (filterobj.error){
				$("#filterrow"+filterobj.row+" td input").css("background",ERRORCOLOR);
				$("#filterrow"+filterobj.row+" td .token-input-input-token").css("background",ERRORCOLOR);
				$("#filterrow"+filterobj.row+" td li.mega").css("background",ERRORCOLOR);
			}else{
				$("#filterrow"+filterobj.row+" td input").css("background",'');
				$("#filterrow"+filterobj.row+" td .token-input-input-token").css("background",'');
				$("#filterrow"+filterobj.row+" td li.mega").css("background",'');
			}
		}
		
		function addFilter(filterobj_caller,farr,tbl){
			var newfilter 	= $.parseJSON(FILTERTEMPLATE);
			newfilter.type 	= EMPTY;
			newfilter.row 	= filterobj_caller.row+1;
			newfilter.style = "empty";
			
			for (var i=farr.length-1; i>=0; i--){
				
				if (i>=newfilter.row){
						farr[i+1] = farr[i];
						farr[i+1].row++;
				}
				else	break;
				
			}
			farr[newfilter.row] = newfilter;
			showTable(tbl,farr);
		}
		
		function removeFilter(filterobj_caller,farr,tbl){
			if (farr.length==1){
				farr[0].type = EMPTY;
				farr[0].style = "empty";
				farr[0].value = "";
				showTable(tbl,farr);
			}else{
				for (var i=0;i<farr.length;i++){
					if (i>filterobj_caller.row){
						farr[i-1] = farr[i];
						farr[i-1].row--;
					}
				}
				farr.pop();
				showTable(tbl,farr);
			}
			sendTrigger();
		}
		
		function sendTrigger(){
			$(document).trigger(TRIGGERCODE);
		}
		
		function hasFilterType(type,farr){
			for (var i=0; i<farr.length; i++){
				if (type==farr[i].type)	return true;
			}
			return false;
		}
		
		function is_date(str){
			var objRegExp = /^[0-9]{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])/;
			return objRegExp.test(str);
		}
		
		function is_float(str){
			var objRegExp  = /^[-+]?\d+(\.\d+)?$/;
			return objRegExp.test(str);
		}
		
		function indexOfId(haystack,needle){
			for (var i = 0; i < haystack.length; i++) {
				if (haystack[i].id == needle) {
					return i;
				}
			}
			return -1;
		}
		
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
	};

})(jQuery);