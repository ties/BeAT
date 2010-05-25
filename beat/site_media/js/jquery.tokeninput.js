/**
 * This is an edited version of the following jQuery plugin:
 * jQuery Plugin: Tokenizing Autocomplete Text Entry
 * Version 1.1
 *
 * Copyright (c) 2009 James Smith (http://loopj.com)
 * Licensed jointly under the GPL and MIT licenses,
 * choose which one suits your project best!
 * ----------------------------------------------------------------
 * This plugin has been edited so that it does not connect to the server, but looks in locally stored results.
 * Also, some functionality (caching, requesting results from server, etc.) have been removed
 */

(function($) {

$.fn.tokenInput = function (searcharray,numberofresults,prepop) {
	var prepopulate = new Array();
	
	if (prepop && prepop.length){
		for (var i=0;i<searcharray.length;i++){
			var index = prepop.indexOf(searcharray[i].id);
			if (index!=-1){
				prepopulate.push(searcharray[i]);
			}
		}
	}
	
	var settings = {
		hintText: "Type in a search term",
		noResultsText: "No results",
		searchingText: "Searching...",
		searchDelay: 300,
		minChars: 1,
		tokenLimit: null,
		jsonContainer: null,
		contentType: "json",
		onResult: null,
		searcharray: searcharray,
		numberofresults: numberofresults
	};
	
	if (prepopulate && prepopulate.length)	settings.prePopulate = prepopulate;

	settings.classes = {
		tokenList: "token-input-list",
		token: "token-input-token",
		tokenDelete: "token-input-delete-token",
		selectedToken: "token-input-selected-token",
		highlightedToken: "token-input-highlighted-token",
		dropdown: "token-input-dropdown",
		dropdownItem: "token-input-dropdown-item",
		dropdownItem2: "token-input-dropdown-item2",
		selectedDropdownItem: "token-input-selected-dropdown-item",
		inputToken: "token-input-input-token"
	}

	return this.each(function () {
		var list = new $.TokenList(this, settings);
	});
};

$.TokenList = function (input, settings) {
	var POSITION = {
		BEFORE: 0,
		AFTER: 1,
		END: 2
	};
	
	var KEY = {
		BACKSPACE: 8,
		TAB: 9,
		RETURN: 13,
		ESC: 27,
		LEFT: 37,
		UP: 38,
		RIGHT: 39,
		DOWN: 40,
		COMMA: 188
	};
	var saved_tokens = [];
	var token_count = 0;
	var timeout;
	var input_box = $("<input type=\"text\">")
		.css({
			outline: "none"
		})
		.focus(function () {
			if (settings.tokenLimit == null || settings.tokenLimit != token_count) {
				show_dropdown_hint();
			}
		})
		.blur(function () {
			hide_dropdown();
		})
		.keydown(function (event) {
			var previous_token;
			var next_token;

			switch(event.keyCode) {
				case KEY.LEFT:
				case KEY.RIGHT:
				case KEY.UP:
				case KEY.DOWN:
					if(!$(this).val()) {
						previous_token = input_token.prev();
						next_token = input_token.next();

						if((previous_token.length && previous_token.get(0) === selected_token) || (next_token.length && next_token.get(0) === selected_token)) {
							if(event.keyCode == KEY.LEFT || event.keyCode == KEY.UP) {
								deselect_token($(selected_token), POSITION.BEFORE);
							} else {
								deselect_token($(selected_token), POSITION.AFTER);
							}
						} else if((event.keyCode == KEY.LEFT || event.keyCode == KEY.UP) && previous_token.length) {
							select_token($(previous_token.get(0)));
						} else if((event.keyCode == KEY.RIGHT || event.keyCode == KEY.DOWN) && next_token.length) {
							select_token($(next_token.get(0)));
						}
					} else {
						var dropdown_item = null;

						if(event.keyCode == KEY.DOWN || event.keyCode == KEY.RIGHT) {
							dropdown_item = $(selected_dropdown_item).next();
						} else {
							dropdown_item = $(selected_dropdown_item).prev();
						}

						if(dropdown_item.length) {
							select_dropdown_item(dropdown_item);
						}
						return false;
					}
					break;

				case KEY.BACKSPACE:
					previous_token = input_token.prev();

					if(!$(this).val().length) {
						if(selected_token) {
							delete_token($(selected_token));
						} else if(previous_token.length) {
							select_token($(previous_token.get(0)));
						}

						return false;
					} else if($(this).val().length == 1) {
						hide_dropdown();
					} else {
						setTimeout(function(){do_search(false);}, 5);
					}
					break;

				case KEY.TAB:
				case KEY.RETURN:
				case KEY.COMMA:
				  if(selected_dropdown_item) {
					add_token($(selected_dropdown_item));
					return false;
				  }
				  break;

				case KEY.ESC:
				  hide_dropdown();
				  return true;

				default:
					if(is_printable_character(event.keyCode)) {
					  setTimeout(function(){do_search(false);}, 5);
					}
					break;
			}
		});

	var hidden_input = $(input)
							.hide()
							.focus(function () {
								input_box.focus();
							})
							.blur(function () {
								input_box.blur();
							});

	var selected_token = null;
	var selected_dropdown_item = null;

	var token_list = $("<ul />")
		.addClass(settings.classes.tokenList)
		.insertAfter(hidden_input)
		.click(function (event) {
			var li = get_element_from_event(event, "li");
			if(li && li.get(0) != input_token.get(0)) {
				toggle_select_token(li);
				return false;
			} else {
				input_box.focus();

				if(selected_token) {
					deselect_token($(selected_token), POSITION.END);
				}
			}
		})
		.mouseover(function (event) {
			var li = get_element_from_event(event, "li");
			if(li && selected_token !== this) {
				li.addClass(settings.classes.highlightedToken);
			}
		})
		.mouseout(function (event) {
			var li = get_element_from_event(event, "li");
			if(li && selected_token !== this) {
				li.removeClass(settings.classes.highlightedToken);
			}
		})
		.mousedown(function (event) {
			var li = get_element_from_event(event, "li");
			if(li){
				return false;
			}
		});

	var dropdown = $("<div>")
		.addClass(settings.classes.dropdown)
		.insertAfter(token_list)
		.hide();

	var input_token = $("<li />")
		.addClass(settings.classes.inputToken)
		.appendTo(token_list)
		.append(input_box);

	init_list();

	function init_list () {
		li_data = settings.prePopulate;
		if(li_data && li_data.length) {
			for(var i in li_data) {
				var this_token = $("<li><p>"+li_data[i].name+"</p> </li>")
					.addClass(settings.classes.token)
					.insertBefore(input_token);

				$("<span>x</span>")
					.addClass(settings.classes.tokenDelete)
					.appendTo(this_token)
					.click(function () {
						delete_token($(this).parent());
						return false;
					});

				$.data(this_token.get(0), "tokeninput", {"id": li_data[i].id, "name": li_data[i].name});

				input_box.val("");

				hide_dropdown();

				var id_string = li_data[i].id + ","
				hidden_input.val(hidden_input.val() + id_string);
			}
		}
	}

	function is_printable_character(keycode) {
		return ((keycode >= 48 && keycode <= 90) ||
					(keycode >= 96 && keycode <= 111) ||
					(keycode >= 186 && keycode <= 192) ||
					(keycode >= 219 && keycode <= 222)
				)
	}

	function get_element_from_event (event, element_type) {
		var target = $(event.target);
		var element = null;

		if(target.is(element_type)) {
			element = target;
		} else if(target.parent(element_type).length) {
			element = target.parent(element_type+":first");
		}

		return element;
	}

	function insert_token(id, value) {
	  var this_token = $("<li><p>"+ value +"</p> </li>")
	  .addClass(settings.classes.token)
	  .insertBefore(input_token);

	  $("<span>x</span>")
		  .addClass(settings.classes.tokenDelete)
		  .appendTo(this_token)
		  .click(function () {
			  delete_token($(this).parent());
			  return false;
		  });

	  $.data(this_token.get(0), "tokeninput", {"id": id, "name": value});

	  return this_token;
	}

	function add_token (item) {
		var li_data = $.data(item.get(0), "tokeninput");
		var this_token = insert_token(li_data.id, li_data.name);

		input_box
			.val("")
			.focus();

		hide_dropdown();

		var id_string = li_data.id + ","
		hidden_input.val(hidden_input.val() + id_string);
		
		token_count++;
		
		if(settings.tokenLimit != null && settings.tokenLimit >= token_count) {
			input_box.hide();
			hide_dropdown();
		}
	}

	function select_token (token) {
		token.addClass(settings.classes.selectedToken);
		selected_token = token.get(0);

		input_box.val("");

		hide_dropdown();
	}

	function deselect_token (token, position) {
		token.removeClass(settings.classes.selectedToken);
		selected_token = null;

		if(position == POSITION.BEFORE) {
			input_token.insertBefore(token);
		} else if(position == POSITION.AFTER) {
			input_token.insertAfter(token);
		} else {
			input_token.appendTo(token_list);
		}

		input_box.focus();
	}

	function toggle_select_token (token) {
		if(selected_token == token.get(0)) {
			deselect_token(token, POSITION.END);
		} else {
			if(selected_token) {
				deselect_token($(selected_token), POSITION.END);
			}
			select_token(token);
		}
	}

	function delete_token (token) {
		var token_data = $.data(token.get(0), "tokeninput");

		token.remove();
		selected_token = null;

		input_box.focus();

		var str = hidden_input.val()
		var start = str.indexOf(token_data.id+",");
		var end = str.indexOf(",", start) + 1;

		if(end >= str.length) {
			hidden_input.val(str.slice(0, start));
		} else {
			hidden_input.val(str.slice(0, start) + str.slice(end, str.length));
		}
		
		token_count--;
		
		if (settings.tokenLimit != null) {
			input_box
				.show()
				.val("")
				.focus();
		}
	}

	function hide_dropdown () {
		dropdown.hide().empty();
		selected_dropdown_item = null;
	}

	function show_dropdown_searching () {
		dropdown
			.html("<p>"+settings.searchingText+"</p>")
			.show();
	}

	function show_dropdown_hint () {
		dropdown
			.html("<p>"+settings.hintText+"</p>")
			.show();
	}

	function highlight_term(value, term) {
		return value.replace(new RegExp("(?![^&;]+;)(?!<[^<>]*)(" + term + ")(?![^<>]*>)(?![^&;]+;)", "gi"), "<b>$1</b>");
	}

	function populate_dropdown (query, results) {
		if(results.length) {
			dropdown.empty();
			var dropdown_ul = $("<ul>")
				.appendTo(dropdown)
				.mouseover(function (event) {
					select_dropdown_item(get_element_from_event(event, "li"));
				})
				.mousedown(function (event) {
					add_token(get_element_from_event(event, "li"));
					return false;
				})
				.hide();

			for(var i in results) {
				if (results.hasOwnProperty(i)) {
					var this_li = $("<li>"+highlight_term(results[i].name, query)+"</li>")
									  .appendTo(dropdown_ul);

					if(i%2) {
						this_li.addClass(settings.classes.dropdownItem);
					} else {
						this_li.addClass(settings.classes.dropdownItem2);
					}

					if(i == 0) {
						select_dropdown_item(this_li);
					}

					$.data(this_li.get(0), "tokeninput", {"id": results[i].id, "name": results[i].name});
				}
			}

			dropdown.show();
			dropdown_ul.slideDown("fast");

		} else {
			dropdown
				.html("<p>"+settings.noResultsText+"</p>")
				.show();
		}
	}

	function select_dropdown_item (item) {
		if(item) {
			if(selected_dropdown_item) {
				deselect_dropdown_item($(selected_dropdown_item));
			}

			item.addClass(settings.classes.selectedDropdownItem);
			selected_dropdown_item = item.get(0);
		}
	}

	function deselect_dropdown_item (item) {
		item.removeClass(settings.classes.selectedDropdownItem);
		selected_dropdown_item = null;
	}

	function do_search(immediate) {
		var query = input_box.val().toLowerCase();

		if (query && query.length) {
			if(selected_token) {
				deselect_token($(selected_token), POSITION.AFTER);
			}
			if (query.length >= settings.minChars) {
				show_dropdown_searching();
				if (immediate) {
					run_search(query);
				} else {
					clearTimeout(timeout);
					timeout = setTimeout(function(){run_search(query);}, settings.searchDelay);
				}
			} else {
				hide_dropdown();
			}
		}
	}

	function run_search(query) {
		results = search_for_results(query,settings.searcharray,settings.numberofresults);
		if($.isFunction(settings.onResult)) {
			results = settings.onResult.call(this, results);
		}
		populate_dropdown(query, results);
	}
	
	function search_for_results(query,searcharray,numberofresults){
		var i=0;
		var res = new Array();
		while (i<searcharray.length && res.length<numberofresults){
			if (searcharray[i].name.indexOf(query)!=-1)
				res.push(searcharray[i]);
			i++;
		}
		return res;
	}
};

})(jQuery);