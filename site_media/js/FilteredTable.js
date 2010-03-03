//local variables that define what the contents of the select-elements are in the filter
var text_filterWith = '<option value="0">Equal to</option><option value="1">Contains</option><option value="2">Begins with</option><option value="3">Ends with</option>';
var date_filterWith = '<option value="0">On</option><option value="1">Before</option><option value="2">After</option>';
var number_filterWith = '<option value="0">Equal to</option><option value="1">Greater than</option><option value="2">Smaller than</option>';
var options_filterWith = '<option value="0">Options (hover)</option>';

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
                <select size="1" class="filterAt" onchange="changedFilter(this);">\n\
                    <option value="-1">&lt;empty&gt;</option>\n\
                    <option value="0">Name</option>\n\
                    <option value="1">Date</option>\n\
                    <option value="2">Memory</option>\n\
                    <option value="3">Runtime</option>\n\
                    <option value="4">Options</option>\n\
                </select>\n\
                <ul class="mega">\n\
                    <li class="mega">\n\
                        <select size="1" class="filterWith" onchange="changedFilter(this);">\n\
                            <option value="-1">&lt;empty&gt;</option>\n\
                        </select>\n\
                    </li>\n\
                </ul>\n\
                <input type="text" class="filterOn" onchange="changedFilter(this);">\n\
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
    if (filterclass == 'filterAt'){
        //get the value, so we can identify what the filterAt is
        var value = parseInt(elem.value);
        
        switch(value){
            //The name filter
            case 0:
                //set the text
                $(elem).siblings('ul.mega').children('li.mega').children('select.filterWith').html(text_filterWith);
                //remove the hover-div if it exists
                $(elem).siblings('ul.mega').children('li.mega').children('div').remove();
                //show the filterOn-textinput if it was hidden
                $(elem).siblings('input.filterOn').show(0);
            break;
            //The date filter
            case 1:
                $(elem).siblings('ul.mega').children('li.mega').children('select.filterWith').html(date_filterWith);
                $(elem).siblings('ul.mega').children('li.mega').children('div').remove();
                $(elem).siblings('input.filterOn').show(0);
            break;
            //The memory filter
            case 2:
                $(elem).siblings('ul.mega').children('li.mega').children('select.filterWith').html(number_filterWith);
                $(elem).siblings('ul.mega').children('li.mega').children('div').remove();
                $(elem).siblings('input.filterOn').show(0);
            break;
            //The runtime filter
            case 3:
                $(elem).siblings('ul.mega').children('li.mega').children('select.filterWith').html(number_filterWith);
                $(elem).siblings('ul.mega').children('li.mega').children('div').remove();
                $(elem).siblings('input.filterOn').show(0);
            break;
            //The options filter
            case 4:
                $(elem).siblings('ul.mega').children('li.mega').children('select.filterWith').html(options_filterWith);
                //hide the filterOn-textinput
                $(elem).siblings('input.filterOn').hide();
                //insert the hover-div
                $(elem).siblings('ul.mega').children('li.mega').children('select').after('\
                    <div>\n\
                        <input type="checkbox">Option 1<br>\n\
                        <input type="checkbox">Option 7<br>\n\
                        <input type="checkbox">Option 6<br>\n\
                        <input type="checkbox">Option 5<br>\n\
                        <input type="checkbox">Option 4<br>\n\
                        <input type="checkbox">Option 3<br>\n\
                        <input type="checkbox">Option 2<br>\n\
                    </div>');
            break;
        }
    }
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