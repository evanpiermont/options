

var option_len = 7

document.addEventListener("DOMContentLoaded", function(event) {
var api = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+$symbol+'&apikey=TDO6ET6NSGZF1MZ5';

  togChart();

  fetch(api)
     .then(function(response) { return response.json(); })
     .then(function(data) { 

      var parsedData = parseData(data)
      drawChart(parsedData);

     })
});

function togChart() {
  d3.select('#graph_tog')
      .on("click", function() { 
        gw = d3.select('#graph_wrap')
        cp = d3.select('#cp')  
        disp = gw.style("display")
        if (disp == "none"){
          gw.style("display", 'block')
          cp.style("display", 'none')
        }else{
          gw.style("display", 'none')
          cp.style("display", 'block')
        }
      });

};

function parseData(data) {
  ts = data['Time Series (Daily)']

   arr0 = []
   arr1 = []
   arr2 = []
   arr3 = []

  for (key in ts){
      ycoord = ts[key]['4. close'];
      xcoord = new Date(key + 'T20:00:00Z');
     arr0.unshift(ycoord); // closing price
     arr1.unshift(xcoord); //date
  }

  for (i = 0; i < arr0.length; i++){
    arr2.push([arr0[i],arr1[i]]); //vectors
    if (i > option_len){
      arr3.push([arr0[i],arr1[i-option_len]]);
    }
   }
  return [arr0, arr1, arr2, arr3]
}


function drawChart(data){

  // define dimensions of graph
    var m = [80, 80, 80, 100]; // margins
    var w = window.innerWidth*.9 - m[1] - m[3]; // width
    var h = window.innerHeight*.8 - m[0] - m[2]; // height

    bisectDate = d3.bisector(function(d) { return d[1]; }).left,
    formatValue = d3.format(",.2f");
    formatCurrency = function(d) { return "$" + formatValue(d); };


  // Add an SVG element with the desired dimensions and margin.
  var graph = d3.select("#graph").append("svg:svg")
        .attr("width", w + m[1] + m[3] + "%")
        .attr("height", h + m[0] + m[2])
      .append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");

    var focus = graph.append("g")
      .attr("class", "focus")
      .style("display", "none");

      focus.append("circle")
      .attr("r", 4.5);

    var focus_op = graph.append("g")
      .attr("class", "focus")
      .style("display", "none");

      focus_op.append("circle")
      .attr("r", 4.5);

    var profit = graph.append("rect")
      .attr("class", "profit")
      .attr("width", w + "px")
      .attr("opacity", ".3");

    d3.select('.profit').raise()
    d3.select('#profit_text').style("display", "none")


    // X scale will fit all values from data[] within pixels 0-w
    //var x = d3.scale.linear().domain([0, data[0].length]).range([0, w]);
    var x = d3.scaleTime().domain([data[1][0], data[1][data[1].length -1]]).range([0, w]);
    // Y scale will fit values from 0-10 within pixels h-0 (Note the inverted domain for the y-scale: bigger is up!)
    // automatically determining max range can work something like this
    var y = d3.scaleLinear().domain([d3.min(data[0]), d3.max(data[0])]).range([h, 0]);

    // create a line function that can convert data[] into x and y points
    var line = d3.line().curve(d3.curveCardinal)
      // assign the X function to plot our line as we wish
      .x(function(d) { 
        //console.log('Plotting X value for data point: ' + d + ' using index: ' + i + ' to be at: ' + x(i) + ' using our xScale.');
        // return the X coordinate where we want to plot this datapoint
        return x(d[1]); 
      })
      .y(function(d) { 
        //console.log('Plotting Y value for data point: ' + d + ' to be at: ' + y(d) + " using our yScale.");
        // return the Y coordinate where we want to plot this datapoint
        return y(d[0]); 
      })


      // create yAxis
      var xAxis = d3.axisBottom().scale(x).tickSize(10);
      // Add the x-axis.
      graph.append("svg:g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + h + ")")
            .call(xAxis);


      // create left yAxis
      var yAxisLeft = d3.axisLeft().scale(y).ticks(4);
      // Add the y-axis to the left
      graph.append("svg:g")
            .attr("class", "y axis")
            .attr("transform", "translate(-25,0)")
            .call(yAxisLeft);
      
        // Add the line by appending an svg:path element with the data line we created above
      // do this AFTER the axes above so that the line is above the tick-lines
        graph.append("svg:path").attr("d", line(data[2]))
        //graph.append("svg:path").attr("d", line(data[3])).attr("class", 'price');

      graph.append("rect")
      .attr("class", "overlay")
      .attr("width", w)
      .attr("height", h)
      .on("mouseover", function() { 
        focus.style("display", null);
        focus_op.style("display", null);
        profit.style("display", null);
        d3.select('#profit_text').style("display", null);
       })
      .on("mouseout", function() { 
        focus.style("display", "none"); 
        focus_op.style("display", "none");
        profit.style("display", "none");
        d3.select('#profit_text').style("display", "none");
      })
      .on("mousemove", mousemove);

    function mousemove() {
    var x0 = x.invert(d3.mouse(this)[0]);
    var i = bisectDate(data[2], x0, 1);
    var d0 = data[2][i - 1];
    var d1 = data[2][i];
    var i_star = x0 - d0[1] > d1[1] - x0 ? i : i-1;
    var i_op = i_star + option_len
    var profit_height = y(data[2][i_star][0]) - y(data[2][i_op][0]) //option profit
    focus.attr("transform", "translate(" + x(data[2][i_star][1]) + "," + y(data[2][i_star][0]) + ")")
    .transition()
    .duration(50);
    focus_op.attr("transform", "translate(" + x(data[2][i_op][1]) + "," + y(data[2][i_op][0]) + ")")
    .transition()
    .duration(50);

    if (profit_height > 0){
      profit.attr("height", profit_height)
      .transition()
      .attr("transform", "translate(" + 0 + "," + y(data[2][i_op][0]) + ")")
      .attr("fill", "#00B233")
      .duration(50);
      d3.select('#o_value').text(formatCurrency(data[2][i_op][0] - data[2][i_star][0]))
      .style('color', "#00B233");
    } else {
      profit.attr("height", -profit_height)
      .transition()
      .attr("transform", "translate(" + 0 + "," + y(data[2][i_star][0]) + ")")
      .attr("fill", "#B20000")
      .duration(50);
      d3.select('#o_value').text(formatCurrency(0))
      .style('color', "#B20000");
    }
    d3.select('.overlay').raise()
    d3.select('#open').text(formatCurrency(data[2][i_star][0]));
    d3.select('#close').text(formatCurrency(data[2][i_op][0]));

    

    //focus.select("text").text(formatCurrency(d[0]));
  }

}