
var current_pane=1


document.addEventListener("DOMContentLoaded", function(e) { //we need to re aqquire the window sizes
d3.select("#next").on("click", function() {

	var pane_len = d3.selectAll(".inst").size();

		if (current_pane < pane_len) {

      d3.select('#pane-'+current_pane).style("display", "none");
      d3.select('#pane-'+(current_pane+1)).style("display", 'block');
      d3.select('#prev').style("display", 'block');

      current_pane+=1; 

  	} else {
  		window.location.replace("/compquiz/"+$subject);
  	}
});

d3.select("#prev").on("click", function() {


      d3.select('#pane-'+current_pane).style("display", "none");
      d3.select('#pane-'+(current_pane-1)).style("display", 'block');

      current_pane+=(-1); 

  	if (current_pane == 1) {
  		d3.select('#prev').style("display", "none");
  	}
});

});