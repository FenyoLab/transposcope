/**
 * Created by markgrivainis on 8/11/16.
 */


var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

/*
 * value accessor - returns the value to encode for a given data object.
 * scale - maps value to a visual display encoding, such as a pixel position.
 * map function - maps from data value to display value
 * axis - sets up axis
 */

// setup x
var xValue = function(d) {return d["H28_Uniq"];}; // data -> value
xScale = d3.scaleLinear().range([0, width]).domain([0, 100]); // value -> display
xMap = function(d) { return xScale(xValue(d));}; // data -> display
xAxis = d3.axisBottom(xScale);

// setup y
var yValue = function(d) { return d.H29_Prop;}, // data -> value
    yScale = d3.scaleLinear().range([height, 0]).domain([0, 100]), // value -> display
    yMap = function(d) { return yScale(yValue(d));}, // data -> display
    yAxis = d3.axisLeft(yScale);

// setup fill color
// var cValue = function(d) { return d.H1_ClipChr;},
//     color = d3.scale.category10();

// add the graph canvas to the body of the webpage
var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// add the tooltip area to the webpage
var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

// load data
d3.tsv("csv_uniq_prop/ovarian/ACAGTG.wsize100.regwsize1.minreads1.clip1.clipflk5.mindis150.FP.uniqgs.bed.csinfo.lm.l1hs.pred.txt.repred", function(error, data) {

    // change string (from CSV) into number format
    var count = 0;
    var points = data.filter(function(d) { if (d["H17_IfGS"] != "N/A") return true;});
//     data.forEach(function(d) {
//         if (d.H17_IfGS != "N/A") {
//             count++;
//             // console.log(d.H17_IfGS);
//             d.H28_Uniq = +d.H28_Uniq;
//             d.H29_Prop = +d.H29_Prop;
//             points.push(d);
//         }
//         // console.log(d);
// //    console.log(d);
//     });
//     console.log(count);

    // don't want dots overlapping axis, so add in buffer to data domain
    // xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
    // yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);

    // x-axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "label")
        .attr("x", width)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text("H28_Uniq");

    // y-axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("H29_Prop");

    // draw dots
    svg.selectAll(".dot")
        .data(points)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr("cx", xMap)
        .attr("cy", yMap)
        // .style("fill", function(d) { return color(cValue(d));})
        .on("mouseover", function(d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(d["H1_ClipChr"] + "<br/> (" + xValue(d)
                + ", " + yValue(d) + ")")
                .style("left", (d3.event.pageX + 5) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function(d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

// draw legend
// var legend = svg.selectAll(".legend")
//     .data(color.domain())
//     .enter().append("g")
//     .attr("class", "legend")
//     .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

// draw legend colored rectangles
// legend.append("rect")
//     .attr("x", width - 18)
//     .attr("width", 18)
//     .attr("height", 18);
//     // .style("fill", color);
//
// // draw legend text
// legend.append("text")
//     .attr("x", width - 24)
//     .attr("y", 9)
//     .attr("dy", ".35em")
//     .style("text-anchor", "end")
//     .text(function(d) { return d;})
});

function switchPlot() {
    var myselect = document.getElementById("selectOpt");
    // alert(myselect.options[myselect.selectedIndex].value);

    d3.tsv(myselect.options[myselect.selectedIndex].value, function(error, data) {

        // change string (from CSV) into number format
        var count = 0;
        var points = data.filter(function(d) { if (d["H17_IfGS"] != "N/A") return true;});
//     data.forEach(function(d) {
//         if (d.H17_IfGS != "N/A") {
//             count++;
//             // console.log(d.H17_IfGS);
//             d.H28_Uniq = +d.H28_Uniq;
//             d.H29_Prop = +d.H29_Prop;
//             points.push(d);
//         }
//         // console.log(d);
// //    console.log(d);
//     });
//     console.log(count);

        // don't want dots overlapping axis, so add in buffer to data domain
        // xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
        // yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);


        svg.selectAll("g.x.axis").call(xAxis);
        svg.selectAll("g.y.axis").call(yAxis);

        // draw dots
        var pnts = svg.selectAll(".dot")
            .data(points);

        pnts.enter().append("circle")
            .attr("class", "dot");

        pnts.exit().remove();

        pnts.attr("r", 3.5)
            .attr("cx", xMap)
            .attr("cy", yMap)
            // .style("fill", function(d) { return color(cValue(d));})
            .on('mouseover', function(d) {
                tooltip.transition()
                    .duration(200)
                    .style("opacity", .9);
                tooltip.html(d["H1_ClipChr"] + "<br/> (" + xValue(d)
                    + ", " + yValue(d) + ")")
                    .style("left", (d3.event.pageX + 5) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            })
            .on('mouseout', function(d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });
    });
}
