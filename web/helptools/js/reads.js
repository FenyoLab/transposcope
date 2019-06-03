/*jslint browser: true*/
/*global $, d3, data, console, buildTable, loadJSON*/
console.log("READS VIEWER");
var datas = "",
    g_layers = "",
    l_layers = "",
    data = "",
    L1_start = 0,
    t_genome_offset = -70,
    t_L1_offset = 20,
    Zero_estimate = 0,
    initialized = false
l_reads = 0,
g_reads = 0,
g_reads_sorted = '',
l_reads_sorted = '';
var margin = {
    top: 30,
    right: 30,
    bottom: 30,
    left: 60
},

width = window.innerWidth - margin.left - margin.right - 20,
height = window.innerHeight - margin.top - margin.bottom - 170,
plotheight = height + 60;
var x = d3.scale.linear()
    .range([0, width])
    .domain([-200, 200]);

var dom_dist = (x.domain()[1] - x.domain()[0]);
var barWidth = width / dom_dist;

var y = d3.scale.linear()
    .domain([0, 2*1.15])
    .range([plotheight, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .tickSize(-plotheight)
//                .tickPadding(3)
    .ticks(Math.max(width / 50, 2))
    .orient("bottom");
var yAxis = d3.svg.axis()
    .scale(y)
    .tickFormat(d3.format("d"))
    .tickPadding(3)
    .tickSize(-width)
    .ticks(2)
    .orient("left");

var svg = d3.select("#reads").append("svg")
    .attr("width",  width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom + 50)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
var drag = d3.behavior.drag()
    .origin(function(d) { return d; })
    .on("drag", dragmove);

function dragmove(d) {
    var dx = d3.event.dx;
    $( "#slider-rangeRead1" ).slider( "values", 0, rd1[0] + dx/(width/dom_dist));
    $( "#slider-rangeRead1" ).slider( "values", 1, rd1[1] + dx/(width/dom_dist) );

    redraw([rd1[0] + dx/(width/dom_dist), rd1[1] + dx/(width/dom_dist)], rd2);
}

var drag2 = d3.behavior.drag()
    .origin(function(d) { return d; })
    .on("drag", dragmove2);

function dragmove2(d) {
    var dx = d3.event.dx;
    $( "#slider-rangeRead2" ).slider( "values", 0, rd2[0] + dx/(width/dom_dist));
    $( "#slider-rangeRead2" ).slider( "values", 1,  rd2[1] + dx/(width/dom_dist));
    redraw(rd1, [rd2[0] + dx/(width/dom_dist), rd2[1] + dx/(width/dom_dist)]);
}

function getMax(DPP) {
    'use strict';
    return function (d, i, a) {
        return i % Math.ceil(DPP) === 0;
    };
}

function inRange(d, i, a) {
    'use strict';
    var dom = x.domain();
    if (dom[0] - 1 <= d.x && d.x <= dom[1] + 1) {
        return d;
    }
}

function calcX(d) {
    'use strict';
    return x(d.x - 0.5);
}

function calcY(plot_idx) {
    'use strict';
    return function (d) {
        return y[plot_idx](d.y);
    };
}

function calcHeight(plot_idx) {
    'use strict';
    return function (d) {
        return ((plot_idx + 1) * plotheight / 4) - 5 - y[plot_idx](d.y);
    };
}

function startHeight(plot_idx) {
    'use strict';
    return function (d) {
        return y[plot_idx](d.y) + ((plot_idx + 1) * plotheight / 4) - 5 - y[plot_idx](d.y);
    };
};


var rd1 = 0,
    rd2 = 0;
function redraw(r1, r2) {
    'use strict';
    rd1 = r1,
    rd2 = r2;
    var table = {
        0: {'colorCode': ['NN', 'NN'], 'text': '-/-'},
        2: {'colorCode': ['LLN', 'LLN'], 'text': 'L/-'},
        1: {'colorCode': ['GGN', 'GGN'], 'text': 'G/-'},
        3: {'colorCode': ['JN', 'JN'], 'text': 'J/-'},
        8: {'colorCode': ['LLN','LLN'], 'text': 'L/-'},
        10: {'colorCode': ['LLL', 'LLL'], 'text': 'L/L'},
        6: {'colorCode': ['LGL', 'GGL'], 'text': 'G/L'},
        11: {'colorCode': ['JL', 'JL'], 'text': 'J/L'},
        4: {'colorCode': ['GGN', 'GGN'], 'text': 'G/-'},
        9: {'colorCode': ['GGL', 'LGL'], 'text': 'G/L'},
        5: {'colorCode': ['GGG', 'GGG'], 'text': 'G/G'},
        7: {'colorCode': ['JG', 'JG'], 'text': 'J/G'},
        12: {'colorCode': ['JN', 'JN'], 'text': 'J/-'},
        14: {'colorCode': ['JL', 'JL'], 'text': 'J/L'},
        13: {'colorCode': ['JG', 'JG'], 'text': 'J/G'},
        15: {'colorCode': ['JJ', 'JJ'], 'text': 'J/J'}
    };
    var counter = "",
        plot_idx = "",
        origin = "",
        bars = "",
        dom = "",
        dataPerPixel = "",
        cuts = "",
        currentDomain = x.domain();
    //if (r2[0] < r1[0]) {
    //    var temp = r1;
    //    r1 = r2;
    //    temp = r2 = temp;
    //};
    var read1 = [];
    for (var i = r1[0];i < r1[1];++i) {
        if ( i < r2[0] || i > r2[1] )
            read1.push({'x':i, 'y':1});
        else
            read1.push({'x':i, 'y':2});
    }
    var read2 = [];
    for (var i = r2[0];i < r2[1];++i)
        if (i > r1[1] - 0.9 || i < r1[0])
            read2.push({'x':i, 'y':1});
    var barWidth = width / dom_dist;

    var r1Plot = "",
        r2Plot = "",
        reads = [
            r1[0] == r1[1] ? 0 : r1[0] <= 0,
            r1[0] == r1[1] ? 0 : r1[1] >= 0,
            r2[0] == r2[1] ? 0 : r2[0] <= 0,
            r2[0] == r2[1] ? 0 : r2[1] >= 0
    ];
    var idx = reads[0] << 3 | reads[1] << 2 | reads[2] << 1 | reads[3];
    r1Plot = table[idx].colorCode[1];
    r2Plot = table[idx].colorCode[0];
    svg.select("text.axis-label.gg").text(table[idx].text);
    document.getElementById(table[idx].text).checked = true;
    //if ((r1[0] <= 0 && r1[1] >= 0 && r2[0] === r2[1]) || (r1[0] === r1[1] && r2[0] <= 0 && r2[1] >= 0)) { r1Plot = "JN"; r2Plot = "JN";svg.select("text.axis-label.gg").text('J/-');}
    //else if ((r1[1] < 0 && r2[0] <= 0 && r2[1] >= 0) || (r1[0] <= 0 && r1[1] >=0 && r2[1] < 0)) { r1Plot = "JG"; r2Plot = "JG";svg.select("text.axis-label.gg").text('G/J');}
    //else if (r1[0] <= 0 && r1[1] >= 0 && r2[0] > 0) { r1Plot = "JL"; r2Plot = "JL";svg.select("text.axis-label.gg").text('J/L');}
    //else if (r1[0] <= 0 && r1[1] >= 0 && r2[0] <= 0 && r2[1] >= 0) { r1Plot = "JJ"; r2Plot = "JJ";svg.select("text.axis-label.gg").text('J/J');}
    //else if (r1[1] < 0 && r2[0] === r2[1]) { r1Plot = "GGN"; r2Plot = "";svg.select("text.axis-label.gg").text('G/-');}
    //else if (r1[0] === r1[1] && r2[0] > 0) { r1Plot = ""; r2Plot = "LLN";svg.select("text.axis-label.gg").text('L/-');}
    //else if (r1[1] < 0 && r2[1] < 0) { r1Plot = r2Plot = "GGG";svg.select("text.axis-label.gg").text('G/G');}
    //else if (r1[0] > 0 && r2[0] > 0) { r1Plot = r2Plot = "LLL";svg.select("text.axis-label.gg").text('L/L');}
    //else if (r1[1] < 0 && r2[0] > 0) { r1Plot = "GGL"; r2Plot = "LGL"; svg.select("text.axis-label.gg").text('G/L');}



    var plot_classes = ['GGG', 'LLL', 'GGL', 'LGL', 'JJG', 'JJL']
    var bars = svg.select("g.rekt").selectAll(".read1")
        .data(read1);
    bars.exit()
        .attr("y", function (d) { return y(d.y);})
        .attr("height", 0)
        .remove();
    bars.enter()
        .append("rect")
        .attr("class", "read1 bar" + r1Plot)
        .attr("clip-path", "url(#clip)")
        .attr("x", function(d) {return x(d.x);})
        .attr("width", barWidth)
    //pre animation height
        .attr("y", function (d) { return y(d.y);})
        .attr("height", 2)
        .call(drag);
    bars
        .attr("class", "read1 bar" + r1Plot)
        .attr("x", function(d) {return x(d.x);})
        .attr("width", barWidth)
        .attr("y", function (d) { return y(d.y);})
        .attr("height", function (d) { return y(0) - y(d.y); });

    bars = svg.select("g.rekt").selectAll(".read2")
        .data(read2);
    bars.exit()
        .attr("y", function (d) { return y(d.y);})
        .attr("height", 0)
        .remove();
    bars.enter()
        .append("rect")
        .attr("class", "read2 bar" + r2Plot)
        .attr("clip-path", "url(#clip)")
        .attr("x", function(d) {return x(d.x);})
        .attr("width", barWidth)
    //pre animation height
        .attr("y", function (d) { return y(d.y);})
        .attr("height", y(0) - y(1))
        .call(drag2);
    bars
        .attr("class", "read2 bar" + r2Plot)
        .attr("x", function(d) {return x(d.x);})
        .attr("width", barWidth)
        .attr("y", function (d) { return y(d.y);})
        .attr("height", y(0) - y(1));

}







svg.append("g")
    .attr("class", "plot");

svg.select("g.plot")
    .append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + plotheight + ")")
    .call(xAxis);

svg.select("g.plot")
    .append("g")
    .attr("class", "x axis genome")
    .append("text")
    .attr("class", "axis-label-genome")
    .attr("y", (-2))
    .attr("x", x(0) - 60 )
    .style("font-weight", "bold")
    .style("text-rendering", "geometricprecision")
    .text('LINE-1');

svg.select("g.plot")
    .append("g")
    .attr("class", "x axis l1")
    .append("text")
    .attr("class", "axis-label-l1")
    .attr("y", -2)
    .attr("x", x(0) + 15)
    .style("font-weight", "bold")
    .text('hg19');

svg.select("g.plot")
    .append("g")
    .attr("class", "sequence_g");

svg.select("g.plot")
    .append("g")
    .attr("class", "sequence_l");

svg.select("g.plot")
    .append("g")
    .attr("class", "y axis");

svg.select("g.y.axis")
    .append("g")
    .attr("class", "y1 axis")
    .call(yAxis);



svg.append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("class", "clip")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", width)
    .attr("height", height + margin.bottom + 120);









svg.select("g.y.axis")
    .attr("class", "y axis")
    .append("text")
    .attr("class", "axis-label gg")
    .attr("y", (-margin.left + 20))
    .attr("x", -plotheight / 2)
    .attr("transform", "rotate(-90)")
    .text('g/g');



svg.select("g.guide")
    .append("line")
    .attr("class", "chart_start")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "#49d198") // colour the line
    .style("stroke-width", "2") // thicken the line
    .attr("x1", x(0)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(0)) // x position of the second end of the line
    .attr("y2", plotheight); // y position of the second end of the line

svg.select("g.guide")
    .append("line")
    .attr("class", "chart_end")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "#49d198") // colour the line
    .style("stroke-width", "2") // thicken the line
    .attr("x1", x(0)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(0)) // x position of the second end of the line
    .attr("y2", plotheight); // y position of the second end of the line

svg.select("g.plot")
    .append("g")
    .attr("class", "guide");

svg.select("g.plot")
    .append("g")
    .attr("class", "enzyme_cs");

svg.select("g.plot")
    .append("g")
    .attr("class", "rekt");

svg.select("g.plot")
    .append("g")
    .attr("class", "rektangle");

svg.append("g")
    .attr("class", "bg");

svg.select("g.plot")
    .append("g")
    .attr("class", "each_seq");

svg.append("g")
    .attr("class", "loader");

svg.select("g.loader")
    .append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", width)
    .attr("height", plotheight)
    .style("fill", "none")
    .style("stroke", "black")
    .style("stroke-width", 1);




svg.select("g.guide")
    .append("line")
    .attr("class", "zero_line")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "blue") // colour the line
    .attr("x1", x(0)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(0)) // x position of the second end of the line
    .attr("y2", plotheight); // y position of the second end of the line

svg.select("g.guide")
    .append("rect")
    .attr("class", "junction")
    .attr("clip-path", "url(#clip)")
    .attr("x", x(0))
    .attr("y", 0)
    .attr("width", 0)
    .attr("height", plotheight);

redraw([-150, -50], [50, 150]);
