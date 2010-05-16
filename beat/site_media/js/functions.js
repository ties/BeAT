$(document).ready(function(){
	return;
	$("#CheckAll").click(function(){//Als je op checkall clicked checkt/unchekced hij alle checkboxes in de benchmark lijst
		if($("#CheckAll").attr("value") == "All"){
			$(".benchmarks input[type=checkbox]").not(":checked").click();
			$("#CheckAll").attr("value", "None");	
		} else {
			$(".benchmarks input[type=checkbox]:checked").click();
			$("#CheckAll").attr("value", "All");
		}
	});
	
	$(".benchmarks input[type=checkbox]").live('click', function(){
		if($(".benchmarks input[type=checkbox]").not(":checked").size() == 0){
			$("#CheckAll").attr("value", "None");	
		} else {
			$("#CheckAll").attr("value", "All");
		}
	});
	
	$("#InvertAll").click(function(){
		$(".benchmarks input[type=checkbox]").click();
	});
});

function invertAll(field) {
	for (i = 0; i < field.length; i++)
		field[i].checked = !field[i].checked;

}
