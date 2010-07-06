/**
 * jQuery plugin for the filtertable
 **/
(function($) {
	
	/** Constants containing the names of the filters **/
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
	
	/** Constant containing the number of results shown when typing in a tokenInput element **/
	var LISTFILTERSIZE 	= 10;
	
	/**
	 * Function that returns the name of a filter to be displayed
	 **/
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
	
	/** Array containing all filternames **/
	var ALLFILTERS = [EMPTY,MODEL,ALGORITHM,TOOL,VERSION,MEMORY_RSS,MEMORY_VSIZE,RUNTIME,STATES,TRANSITIONS,DATE,OPTIONS,FINISHED,CPU,RAM,COMPUTERNAME,KERNELVERSION,DISKSPACE];
	
	/** Array containing the names of all list filters **/
	var LISTFILTERS = [MODEL,ALGORITHM,TOOL,COMPUTERNAME,CPU,VERSION,KERNELVERSION];
	
	/** Array containing the names of all value filters **/
	var VALUEFILTERS = [MEMORY_RSS,MEMORY_VSIZE,RUNTIME,STATES,TRANSITIONS,RAM,DISKSPACE];
	
	/** Array containing the names of all filters of which at most one instance should be added **/
	var UNIQUEFILTERS = [MODEL,ALGORITHM,TOOL,VERSION,OPTIONS,COMPUTERNAME,CPU,KERNELVERSION];
	
	/** Constant containing the template for a filter **/
	var FILTERTEMPLATE = '{"type" : "", "row" : -1, "style":"", "value" : "", "error" : true}';
	
	/** Color used to show an error **/
	var ERRORCOLOR = "#FF9999";
	
	/** Triggercode send to notify the filter table has changed **/
	var TRIGGERCODE = 'filterupdate';
	
	/**
	 * Function which makes it possible to do $(table).filtertable(...) to make a filtertable of table
	 **/
	$.fn.filtertable = function (filterarray, context) {
		return this.each(function () {
			var list = new $.startfiltertable(this, filterarray, context);
		});
	};
	
	/**
	 * Specification for the filtertable
	 **/
	$.startfiltertable = function (table, filterarray, context){
		
		/** The first thing to do is to initialize the table **/
		initTable(filterarray);
		
		/**
		 * Function which returns the filterobjects of the filter table
		 * Can be used by the benchmark table
		 **/
		$.fn.filters = function(){
			var res = [];
			for (var i=0; i < filterarray.length; i++){
				res.push($.extend({},filterarray[i]));
			}
			return res;
		}
		
		/**
		 * Function which returns the TRIGGERCODE
		 * Can be used by the benchmark table
		 **/
		$.fn.triggercode = function(){
			return TRIGGERCODE;
		}
		
		/**
		 * Function which updates the context with the new context
		 * Can be used by the benchmark table
		 * @ newcontext Contains the new context
		 **/
		$.fn.updateContext = function(newcontext){
			//overwrite the stored context
			context = newcontext;
			
			//update all list filters and option filters
			$(filterarray).each(function(i,filterobj){
				if (filterobj.type == OPTIONS){
					//create the new value for the option filter
					var newval = [[],[]];
					for (var j=0;j<filterobj.value[0].length;j++){
						if (indexOfId(context.options,filterobj.value[0][j])!=-1){
							newval[0].push(filterobj.value[0][j]);
							newval[1].push(filterobj.value[1][j]);
						}
					}
					//overwrite filterobj.value
					filterobj.value = newval;
					//rewrite the row of filterobj
					rewriteRow(filterobj,filterarray);
				}else if(LISTFILTERS.indexOf(filterobj.type)!=-1){
					//create new value
					var newval = [];
					for (var j=0;j<filterobj.value.length;j++){
						if (context[filterobj.type].indexOf(filterobj.value[j])!=-1)		newval.push(filterobj.value[j]);
					}
					//overwrite filterobj.value
					filterobj.value = newval;
					//rewrite row of filterobj
					rewriteRow(filterobj,filterarray);
				}
			});
		}
		
		/**
		 * Function that initializes the filtertable
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
			//show the table
			showTable(farr);
		}
		
		/**
		 * Function that shows the table
		 * @param farr The filterobject array
		 **/
		function showTable(farr){
			//empty table
			$(table).empty();
			
			$(farr).each(function(i,obj){
				//make the contents of the row
				var contents = makeRowContents(obj,farr);
				var row = $('<tr id="filterrow'+obj.row+'"></tr>');
				
				$(contents).each(function(j,col){
					$(row).append(col);
				});
				//append the row to the table
				$(table).append($(row));
				//if it is a list filter, it must be made into an inputToken-element
				if (LISTFILTERS.indexOf(obj.type)!=-1)	$("#filterValue"+obj.row).tokenInput(context[obj.type], LISTFILTERSIZE, obj.value);
				
				setErrorCSS(obj);
			});
		}
		
		/**
		 * Function that makes the contents of a row in the filter table
		 * Also makes sure events are handled correctly
		 * @param filterobj The filterobject of which the rowcontents should be made
		 * @param farr The filterobject array
		 **/
		function makeRowContents(filterobj,farr){
			var rowcontent = [];
			
			//make filtertype select-element
			var ftype = $('<select size="1" class="filterType" id="filterType'+(filterobj.row)+'"></select>')
								.change(function(){
									//set new type value, set style and value to empty
									filterobj.type = $(this).val();
									filterobj.style = "";
									filterobj.value = "";
									
									//if it is set to a finished filter, set error to false and value to the initial true
									//else, set error to true
									if (filterobj.type==FINISHED){
										filterobj.error = false;
										filterobj.value = true;
									}else
										filterobj.error = true;
									
									//rewrite the changed filter
									rewriteRow(filterobj,farr);
								});
			
			//for every filter type, add it to the select-element
			$(ALLFILTERS).each(function (i,val){
				//check for uniqueness
				if(!(UNIQUEFILTERS.indexOf(val)!=-1 && hasFilterType(val,farr) && filterobj.type!=val)){
					
					var option = $('<option value="'+val+'" class="'+val+'">' + filtername(val) + '</option>');
					if (filterobj.type==val)
						$(option).attr('selected',true);
					
					$(ftype).append(option);
					
				}
				
			});
			//add it to a new td-element
			var td = $('<td></td>');
			$(td).append(ftype);
			//add the td-element to the result
			rowcontent.push($(td));
			
			//case EMPTY
			if (filterobj.type == EMPTY){
				filterobj.style = "empty";
				
				//make filter style selection and filter value element
				var fstyle = $('<select size="1" class="filterStyle" id="filterStyle'+filterobj.row+'"><option value="empty">&lt;empty&gt;</option></select>');
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" value="'+filterobj.value+'" />')
								.change(function(){
									filterobj.value = $(this).val();
									filterobj.error = true;
								});
				$(fvalue).addClass("filterValue");
				
				//add style and value to td-elements
				var td1 = $('<td></td>');
				$(td1).append(fstyle);
				var td2 = $('<td></td>');
				$(td2).append(fvalue);
				
				//add td-elements to the result
				rowcontent.push($(td1));
				rowcontent.push($(td2));
			//case VALUEFILTER
			}else if(VALUEFILTERS.indexOf(filterobj.type)!=-1){
				//set style to equal if it is empty
				if (filterobj.style == "")	filterobj.style = "equal";
				
				//make style
				var fstyle = $('<select size="1" class="filterStyle" id="filterStyle'+filterobj.row+'"></select>')
								.change(function(){
									//change style and send trigger
									filterobj.style = $(this).val();
									sendTrigger();
								});
				//append options to filterstyle
				$(fstyle).append('<option value="equal"'+(filterobj.style=='equal' ? ' selected' : '')+'>=</option>');
				$(fstyle).append('<option value="greaterthan"'+(filterobj.style=='greaterthan' ? ' selected' : '')+'>&gt;=</option>');
				$(fstyle).append('<option value="lessthan"'+(filterobj.style=='lessthan' ? ' selected' : '')+'>&lt;=</option>');
				
				//make value element
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" value="'+filterobj.value+'" />')
									.keyup(function(){
										//when a keyup happens, set the new value and error and update the view for the error
										filterobj.value = $(this).val();
										filterobj.error = !(is_float(filterobj.value));
										setErrorCSS(filterobj);
										//send trigger
										sendTrigger();
									});
				$(fvalue).addClass("filterValue");
				
				//add filter style and value to td-elements
				var td1 = $('<td></td>');
				$(td1).append(fstyle);
				var td2 = $('<td></td>');
				$(td2).append(fvalue);
				
				//add td-elements to result
				rowcontent.push($(td1));
				rowcontent.push($(td2));
			//case LISTFILTERS
			}else if(LISTFILTERS.indexOf(filterobj.type)!=-1){
				//style is not needed: set it to empty
				filterobj.style = "";
				//make value element, this element will later be changed into a tokenInput-element
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" />')
								.change(function(){
									//set the new value
									filterobj.value = $(this).val().split(',');
									//set the error state
									filterobj.error = (filterobj.value.length==0);
									setErrorCSS(filterobj);
									//send trigger
									sendTrigger();
								});
				$(fvalue).addClass("filterValue");
				
				//add value to a td-element
				var td1 = $('<td></td>');
				$(td1).attr('colspan',2);
				$(td1).append(fvalue);
				
				//add td-element to result
				rowcontent.push($(td1));
				
			//case DATE
			}else if(filterobj.type == DATE){
				//set the style to on if it is empty
				if (!filterobj.style)	filterobj.style = "on";
				//make style selection
				var fstyle = $('<select size="1" class="filterStyle" id="filterStyle'+filterobj.row+'"></select>')
								.change(function(){
									//set the new style
									filterobj.style = $(this).val();
									//send trigger
									sendTrigger();
								});
				//add options to style selector
				$(fstyle).append('<option value="on"'+(filterobj.style=='on' ? ' selected' : '')+'>On</option>');
				$(fstyle).append('<option value="before"'+(filterobj.style=='before' ? ' selected' : '')+'>Before or on</option>');
				$(fstyle).append('<option value="after"'+(filterobj.style=='after' ? ' selected' : '')+'>After or on</option>');
				
				//make value element
				var fvalue = $('<input type="text" id="filterValue'+filterobj.row+'" value="'+filterobj.value+'" />')
								.change(function(){
									//store new value
									filterobj.value = $(this).val();
									//set error
									filterobj.error = !(is_date($(this).val()));
									setErrorCSS(filterobj);
									//send trigger
									sendTrigger();
								});
				$(fvalue).addClass("filterValue");
				
				//add style and value to td-elements
				var td1 = $('<td></td>');
				$(td1).append(fstyle);
				var td2 = $('<td></td>');
				$(td2).append(fvalue);
				
				//add td-elements to result
				rowcontent.push($(td1));
				rowcontent.push($(td2));
			//case OPTIONS
			}else if (filterobj.type == OPTIONS){
				//set value to an array with two empty arrays if it is empty
				if(!filterobj.value.length){
					filterobj.value = [[],[]];
				}
				
				//make hover table; this will be shown when hovering over the correct element in the filter table
				var hovertbl = $('<table cellspacing="1" cellpadding="0"></table>');
				
				//add each available option to the hover table
				$(context.options).each(function(i,option){
					//make a tr and three td-elements for each option
					var row = $('<tr></tr>'); 
					var td1 = $('<td></td>'); 
					var td2 = $('<td></td>'); 
					var td3 = $('<td></td>');
					//search for the index of the option.id in the value
					var index = filterobj.value[0].indexOf(option.id);
					
					//make checkbox element
					var checkbox = $('<input type="checkbox" value="'+option.id+'" class="optionId" id="optionId'+option.id+'" />')
						.change(function(){
							//on change, make an id out of the string value
							var id = parseInt($(this).val());
							//if it is checked, add it to the value
							if ($(this).attr('checked')){
								filterobj.value[0].push(id);
								filterobj.value[1].push($("#optionValue"+id).val());
							//if not, remove it from the value
							}else{
								var remindex = filterobj.value[0].indexOf(id);
								if (remindex!=-1){
									filterobj.value[0].splice(remindex,1);
									filterobj.value[1].splice(remindex,1);
								}
							}
							//set the error value
							filterobj.error = (filterobj.value[0].length==0);
							setErrorCSS(filterobj);
						});
					//set the checked attribute
					$(checkbox).attr('checked',(index!=-1));
					//append the checkbox and option name
					$(td1).append($(checkbox));
					$(td2).append(option.name);
					
					//make the value element, which is hidden and set to "True" when the option does not require an argument, and is an textinput element if it does
					var value;
					if (option.takes_argument){
						value = $('<input type="text" id="optionValue'+option.id+'" class="optionValue">')
									.keyup(function(){
										//set the value
										filterobj.value[1][filterobj.value[0].indexOf(option.id)] = $(this).val();
									});
						if (index!=-1)	$(value).val(filterobj.value[1][index]);
					}else{
						value = $('<input type="hidden" id="optionValue'+option.id+'" value="True" class="optionValue">');
					}
					//append value to td3
					$(td3).append(value);
					
					//append td's to row
					$(row).append(td1);
					$(row).append(td2);
					$(row).append(td3);
					//append row to hovertbl
					$(hovertbl).append(row);
				});
				
				//add mega drop down manu
				var hover = $('<div></div>');
				$(hover).append(hovertbl);
				
				var megaul = $('<ul class="mega"></ul>');
				var megali = $('<li class="mega">(hover)</li>').css('padding-right',100);
				//user hoverIntent
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
				//add to result
				rowcontent.push($(td1));
			}else if (filterobj.type == FINISHED){
				//always false
				filterobj.error = false;
				var fvalue = $('<select size="1" class="filterValue" id="filterValue'+filterobj.row+'"></select>')
								.change(function(){
									//set value
									filterobj.value = $(this).val();
									//set error
									filterobj.error = false;
									//send trigger
									sendTrigger();
								});
				//append options
				$(fvalue).append('<option value="true">True</option><option value="false">False</option>');
				
				var td1 = $('<td></td>');
				$(td1).append(fvalue);
				//add to result
				rowcontent.push($(td1));
			}			
			
			//make remove button
			var rem = $('<a class="remove"></a>')
						.click(function(){
							removeFilter(filterobj,farr);
						});
			$(rem).append($('<img src="/site_media/img/remove_filter.png" alt="- " />'));
			
			//make add button
			var add = $('<a class="add"></a>')
						.click(function(){
							addFilter(filterobj,farr);
						});
			$(add).append($('<img src="/site_media/img/add_filter.png" alt=" +" />'));
			
			//add buttons to the result
			var span = $('<span></span>');
			$(span).append(rem).append(add);
			rowcontent.push(span);
			var td1 = $('<td></td>');
			$(td1).append(span);
			
			rowcontent.push($(td1));
			//return result
			return rowcontent;
		}
		
		/**
		 * Function to rewrite one of the rows in the table
		 * @param filterobj Filterobject to be rewritten
		 * @param farr The filterobject array
		 **/
		function rewriteRow(filterobj,farr){
			//make row contents
			var contents = makeRowContents(filterobj,farr);
			//get the row in the table
			var row = $('#filterrow'+filterobj.row);
			$(row).empty();
			//write row to table
			$(contents).each(function(j,col){
				$(row).append(col);
			});
			//If it is a listfilter, it must be called with the tokenInput plugin
			if (LISTFILTERS.indexOf(filterobj.type)!=-1)	$("#filterValue"+filterobj.row).tokenInput(context[filterobj.type], LISTFILTERSIZE, filterobj.value);
			//set errror css
			setErrorCSS(filterobj);
		}
		
		/**
		 * Sets the style of a row in the table to show whether or not a filterobject has an error
		 * @param filterobj The filterobject
		 **/
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
		
		/**
		 * Function to add a filter to the filter table
		 * @param filterobj_caller The filterobject from which the + button is clicked
		 * @param farr The filterobject array
		 **/
		function addFilter(filterobj_caller,farr){
			//make a new filter from the FILTERTEMPLATE
			var newfilter 	= $.parseJSON(FILTERTEMPLATE);
			newfilter.type 	= EMPTY;
			newfilter.row 	= filterobj_caller.row+1;
			newfilter.style = "empty";
			
			//set the row values of all filterobjects in farr correctly
			for (var i=farr.length-1; i>=0; i--){
				
				if (i>=newfilter.row){
						farr[i+1] = farr[i];
						farr[i+1].row++;
				}
				else	break;
				
			}
			//add new filter
			farr[newfilter.row] = newfilter;
			//rewrite table
			showTable(farr);
		}
		
		/**
		 * Function that removes a filter
		 * @param filterobj_caller The filterobject to be removed
		 * @param farr The filterobject array
		 **/
		function removeFilter(filterobj_caller,farr){
			//if this is the only filter, make an empty filter out of it
			if (farr.length==1){
				farr[0].type = EMPTY;
				farr[0].style = "empty";
				farr[0].value = "";
				showTable(farr);
			}else{
				//make sure farr contains the correct filters
				for (var i=0;i<farr.length;i++){
					if (i>filterobj_caller.row){
						farr[i-1] = farr[i];
						farr[i-1].row--;
					}
				}
				//after the for-loop above, the filterobject to be removed is at the end of farr, so farr.pop() is called
				farr.pop();
				//rewrite table
				showTable(farr);
			}
			//send a trigger
			sendTrigger();
		}
		
		/**
		 * Function to send a trigger so the benchmark table knows there has been a change in the filter table
		 **/
		function sendTrigger(){
			$(document).trigger(TRIGGERCODE);
		}
		
		/**
		 * Function that checks if a filterobject array contains a filter of the specified type
		 * @param type The type to be checked on
		 * @param farr The filterobject array
		 **/
		function hasFilterType(type,farr){
			for (var i=0; i<farr.length; i++){
				if (type==farr[i].type)	return true;
			}
			return false;
		}
		
		/**
		 * Checks if a string is a date (yyyy-mm-dd)
		 **/
		function is_date(str){
			var objRegExp = /^[0-9]{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])/;
			return objRegExp.test(str);
		}
		
		/**
		 * Checks if a string contains an integer or float
		 **/
		function is_float(str){
			var objRegExp  = /^[-+]?\d+(\.\d+)?$/;
			return objRegExp.test(str);
		}
		
		/**
		 * Used by the options filter to get the position of a option id
		 **/
		function indexOfId(haystack,needle){
			for (var i = 0; i < haystack.length; i++) {
				if (haystack[i].id == needle) {
					return i;
				}
			}
			return -1;
		}
		
		/**
		 * Registers Array.indexOf
		 **/
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