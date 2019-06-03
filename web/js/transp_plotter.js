/*jslint browser: true*/
/*global $, d3, data, console, buildTable, loadJSON*/


//$("#data_table").click(function(){
//      var theLink = $(this).text();
//      alert(theLink);
//});

//determine which folder to load information from

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value.split("#")[0];
    });
    return vars;
}

if (location.search == '') {
    window.location.replace("home.html");
}
var area = getUrlVars()["area"];
var patientFolder = getUrlVars()["patientFolder"];
var type = getUrlVars()["type"];

$(".IDtext").text(area + "-" + type);
//var area = decodeURIComponent((new RegExp('[?|&]=area' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [""])[1].replace(/\+/g, '%20')) || null;
//var folder = decodeURIComponent((new RegExp('[?|&]=patientFolder' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [""])[1].replace(/\+/g, '%20')) || null;
//var type = decodeURIComponent((new RegExp('[?|&]=type' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [""])[1].replace(/\+/g, '%20')) || null;



var datas = "",
    g_layers = "",
    l_layers = "",
    data = "",
    L1_start = 0,
    t_genome_offset = -70,
    t_L1_offset = 20,
    Zero_estimate = 0,
    enzymeCuts = "",
    initialized = false
l_reads = 0,
    g_reads = 0,
    g_reads_sorted = '',
    l_reads_sorted = '';

var margin = {
        top: 50,
        right: 30,
        bottom: 40,
        left: 60
    },

    width = parseInt(d3.select(".plot").style("width"), 10) - margin.left - margin.right,
    height = parseInt(d3.select(".plot").style("height"), 10) - margin.top - margin.bottom - 100,
    plotHeight = height + 60;

var x = d3.scale.linear()
    .range([0, width])
    .domain([-10, 10]);

var dom_dist = (x.domain()[1] - x.domain()[0]);
var maxdom = [];
var dom = [];
var barWidth = width / dom_dist;
var stack_g = d3.layout.stack().order("default");
var stack_l = d3.layout.stack().order("default");
//var stack_g = d3.layout.stack().order("inside-out");
//var stack_l = d3.layout.stack().order("inside-out");

var y = [d3.scale.linear()
            .domain([0, 1])
            .range([plotHeight / 4 - 5, 0]),
        d3.scale.linear()
            .domain([0, 1])
            .range([(2 * plotHeight / 4) - 5, (plotHeight / 4) + 5]),
        d3.scale.linear()
            .domain([0, 1])
            .range([(3 * plotHeight / 4) - 5, (2 * plotHeight / 4) + 5]),
        d3.scale.linear()
            .domain([0, 1])
            .range([(4 * plotHeight / 4), (3 * plotHeight / 4) + 5])
        ];

var seqY = d3.scale.linear()
    .domain([-100, 100])
    .range([plotHeight, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .tickSize(-plotHeight)
    //                .tickPadding(3)
    .ticks(Math.max(width / 50, 2))
    .orient("bottom");
var yAxis = [d3.svg.axis()
                .scale(y[0])
                .tickFormat(d3.format("d"))
                .tickPadding(3)
                .tickSize(-width)
                .ticks(4)
                .orient("left"),
            d3.svg.axis()
                .scale(y[1])
                .tickFormat(d3.format("d"))
                .tickPadding(3)
                .tickSize(-width)
                .ticks(4)
                .orient("left"),
            d3.svg.axis()
                .scale(y[2])
                .tickFormat(d3.format("d"))
                .tickPadding(3)
                .tickSize(-width)
                .ticks(4)
                .orient("left"),
            d3.svg.axis()
                .scale(y[3])
                .tickFormat(d3.format("d"))
                .tickPadding(3)
                .tickSize(-width)
                .ticks(4)
                .orient("left")];

var seqYAxis = d3.svg.axis()
    .scale(seqY)
    .tickFormat(d3.format("d"))
    .tickPadding(3)
    .tickSize(-width)
    .ticks(4)
    .orient("left");

var zoom = d3.behavior.zoom()
    .size([width + margin.left + margin.right, height + margin.bottom + margin.top]);

var svg = d3.select("#chart").append("svg")
    .call(zoom)
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom + 120)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var div = d3.select("#chart").append("div")
    .attr("class", "tooltip_a")
    .style("opacity", 0);

var cut_div = d3.select("#chart").append("div")
    .attr("class", "tooltip_b")
    .style("opacity", 0);

var line = d3.svg.line()
    .x(function (d) {
        return x(d.x);
    })
    .y(function (d) {
        return y[3](d.y);
    })
    .interpolate("step-after");

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
        return ((plot_idx + 1) * plotHeight / 4) - 5 - y[plot_idx](d.y);
    };
}

function startHeight(plot_idx) {
    'use strict';
    return function (d) {
        return y[plot_idx](d.y) + ((plot_idx + 1) * plotHeight / 4) - 5 - y[plot_idx](d.y);
    };
}


function mouseIn(d) {
    'use strict';
    if (d.y !== 0) {
        div.transition()
            .duration(200)
            .style("opacity", 0.9);
        div.html(
                "" + datas.stats.chromosome + ":" + d.pos + "<br/>" +
                "----------------------" + "<br/>" +
                "A: " + d.A + "\t(" + Math.round(d.A * 100 / d.y) + "%)<br/>" +
                "C: " + d.C + "\t(" + Math.round(d.C * 100 / d.y) + "%)<br/>" +
                "G: " + d.G + "\t(" + Math.round(d.G * 100 / d.y) + "%)<br/>" +
                "T: " + d.T + "\t(" + Math.round(d.T * 100 / d.y) + "%)<br/>" +
                "N: " + d.N + "\t(" + Math.round(d.N * 100 / d.y) + "%)<br/>" +
                "----------------------" + "<br/>" +
                "x: " + d.x + ", y: " + d.y

            )
            .style("left", x(d.x) - 30 + "px")
            .style("top", d3.event.pageY - 200 + "px");
    }
}

function g_total(x, v) {
    if (datas.stats.complement == 1)
        return ((g_layers[0][g_layers[0].length + x][v]) +
            (g_layers[1][g_layers[1].length + x][v]) +
            (g_layers[2][g_layers[2].length + x][v]) +
            (g_layers[3][g_layers[3].length + x][v]) +
            (g_layers[4][g_layers[4].length + x][v]) +
            (g_layers[5][g_layers[5].length + x][v]) +
            (g_layers[6][g_layers[6].length + x][v]))
    else
        return ((g_layers[0][x][v]) +
            (g_layers[1][x][v]) +
            (g_layers[2][x][v]) +
            (g_layers[3][x][v]) +
            (g_layers[4][x][v]) +
            (g_layers[5][x][v]) +
            (g_layers[6][x][v]))
}

function g_mouseInAll(d, i) {
    'use strict';
    if (d.y !== 0) {
        var y_tot = g_total(d.x, "y")
        div.transition()
            .duration(200)
            .style("opacity", 0.9);
        div.html(
                "" + datas.stats.chromosome + ":" + d.pos + "<br/>" +
                "----------------------" + "<br/>" +
                "A: " + g_total(d.x, "A") + "\t(" + Math.round(g_total(d.x, "A") * 100 / y_tot) + "%)<br/>" +
                "C: " + g_total(d.x, "C") + "\t(" + Math.round(g_total(d.x, "C") * 100 / y_tot) + "%)<br/>" +
                "G: " + g_total(d.x, "G") + "\t(" + Math.round(g_total(d.x, "G") * 100 / y_tot) + "%)<br/>" +
                "T: " + g_total(d.x, "T") + "\t(" + Math.round(g_total(d.x, "T") * 100 / y_tot) + "%)<br/>" +
                "N: " + g_total(d.x, "N") + "\t(" + Math.round(g_total(d.x, "N") * 100 / y_tot) + "%)<br/>" +
                "----------------------" + "<br/>" +
                //                "x: " + d.x + ", y: " + d.y
                "x: " + d.x + ", y: " + y_tot

            )
            .style("left", x(d.x) - 30 + "px")
            .style("top", d3.event.pageY - 200 + "px");
    }
}

function l_total(x, v) {
    //    if (datas.stats.complement == 0) {
    return ((l_layers[0][l_layers[0].length - 1 + (x - l_layers[0][l_layers[0].length - 1]['x'])][v]) +
            (l_layers[1][l_layers[1].length - 1 + (x - l_layers[0][l_layers[1].length - 1]['x'])][v]) +
            (l_layers[2][l_layers[2].length - 1 + (x - l_layers[0][l_layers[2].length - 1]['x'])][v]) +
            (l_layers[3][l_layers[3].length - 1 + (x - l_layers[0][l_layers[3].length - 1]['x'])][v]) +
            (l_layers[4][l_layers[4].length - 1 + (x - l_layers[0][l_layers[4].length - 1]['x'])][v]) +
            (l_layers[5][l_layers[5].length - 1 + (x - l_layers[0][l_layers[5].length - 1]['x'])][v]) +
            (l_layers[6][l_layers[6].length - 1 + (x - l_layers[0][l_layers[6].length - 1]['x'])][v]))
        //    } else {
        //        return ((l_layers[0][160 - (x-l_layers[0][l_layers[0].length-1]['x'])][v]) +
        //            (l_layers[1][160 - (x-l_layers[1][l_layers[1].length-1]['x'])][v]) +
        //            (l_layers[2][160 - (x-l_layers[2][l_layers[2].length-1]['x'])][v]) +
        //            (l_layers[3][160 - (x-l_layers[3][l_layers[3].length-1]['x'])][v]))
        //    }
}

function l_mouseInAll(d, i) {
    'use strict';
    if (d.y !== 0) {
        var y_tot = l_total(d.x, "y")
        div.transition()
            .duration(200)
            .style("opacity", 0.9);
        div.html(
                "" + datas.stats.chromosome + ":" + d.pos + "<br/>" +
                "----------------------" + "<br/>" +
                "A: " + l_total(d.x, "A") + "\t(" + Math.round(l_total(d.x, "A") * 100 / y_tot) + "%)<br/>" +
                "C: " + l_total(d.x, "C") + "\t(" + Math.round(l_total(d.x, "C") * 100 / y_tot) + "%)<br/>" +
                "G: " + l_total(d.x, "G") + "\t(" + Math.round(l_total(d.x, "G") * 100 / y_tot) + "%)<br/>" +
                "T: " + l_total(d.x, "T") + "\t(" + Math.round(l_total(d.x, "T") * 100 / y_tot) + "%)<br/>" +
                "N: " + l_total(d.x, "N") + "\t(" + Math.round(l_total(d.x, "N") * 100 / y_tot) + "%)<br/>" +
                "----------------------" + "<br/>" +
                //                "x: " + d.x + ", y: " + d.y
                "x: " + d.x + ", y: " + y_tot

            )
            .style("left", x(d.x) - 30 + "px")
            .style("top", d3.event.pageY - 200 + "px");
    }
}

function mouseleave(d) {
    'use strict';
    div.transition()
        .duration(500)
        .style("opacity", 0);
}

function mouseleaveEnzyme(d) {
    'use strict';
    cut_div.transition()
        .duration(500)
        .style("opacity", 0);
}

function mouseClick(d) {
    'use strict';
    //    var currentDomain = x.domain()
    //    $("#position").val(datas.stats.chromosome + ":" + Math.floor(d.pos - (d.x - currentDomain[0]-1)) + "-" + Math.floor(d.pos + (currentDomain[1] - d.x)));
}




//************************************************************
// Zoom specific updates
//************************************************************
var a = 0;

var trans = [];

function zoomReads() {

    var reads_g = g_reads_sorted;
    var reads_l = l_reads_sorted;

    var j_seq_g = svg.select('g.each_seq').selectAll('g.jg_seq')
        .data(reads_g);

    j_seq_g.enter()
        .append("g")
        .attr("class", "jg_seq")
        .attr("clip-path", "url(#clipReads)")
        .style("font", "arial")
        .style("font-size", 14)
        .style("font-weight", "bold")
        .style("shape-rendering", "optimizeSpeed")

    var j_seq_each_g = j_seq_g.selectAll("text")
        .data(function (d) {
            var domY = seqY.domain();
            return d.filter(function (c) {
                if (domY[0] - 1 <= c.y && c.y < domY[1])
                    return c;
            })
        });

    j_seq_each_g.enter()
        .append("text")
        .style("fill", function (d) {
            return d.c
        })
        .text(function (d) {
            return d.l;
        });
    j_seq_each_g
        .style("font-size", 14)
        .attr("x", function (d) {
            return x(d.x - 0.3);
        })
        .attr("y", function (d) {
            return seqY(d.y);
        }) //(plotHeight + 50))

    j_seq_each_g.exit()
        .remove()

    j_seq_g.exit()
        .remove();

    var j_seq_l = svg.select('g.each_seq').selectAll('g.jl_seq')
        .data(reads_l)

    j_seq_l.enter()
        .append("g")
        .attr("class", "jl_seq")
        .attr("clip-path", "url(#clipReads)")
        .style("font", "arial")
        .style("font-size", 14)
        .style("font-weight", "bold")
        .style("shape-rendering", "optimizeSpeed")

    var j_seq_each_l = j_seq_l.selectAll("text")
        .data(function (d) {
            var dom = seqY.domain();
            return d.filter(function (c) {
                if (dom[0] - 1 <= c.y && c.y < dom[1])
                    return c;
            })
        });

    j_seq_each_l.enter()
        .append("text")
        .style("fill", function (d) {
            return d.c
        })
        .text(function (d) {
            return d.l;
        });
    j_seq_each_l
        .attr("x", function (d) {
            return x(d.x - 0.3);
        })
        .attr("y", function (d) {
            return seqY(d.y);
        }) //(plotHeight + 50))

    j_seq_each_l.exit()
        .remove()

    j_seq_l.exit()
        .remove();


    svg.select("g.sequence_g").selectAll("rect").remove();
    svg.select("g.sequence_l").selectAll("rect").remove();
    var qwe = svg.select("g.sequence_g").selectAll("text")
        .data(datas['stats']['sequence_g'].filter(inRange));
    qwe
        .enter()
        .append("text")
        .attr("class", "yo")
        .attr("clip-path", "url(#clip)")
        .on("mouseenter", function (d) {
            svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", x(1) - x(0)).attr("height", plotHeight);
        })
        .on("mouseleave", function (d) {
            svg.selectAll(".marked").remove();
        });


    qwe
        .attr("x", calcX)
        .attr("y", plotHeight + 70) //(plotHeight + 50))
        .attr("class", function (d) {
            if (d.s !== d.c || false) {
                svg.selectAll(".marked").remove();
                svg.select("g.sequence_g")
                    .append("text")
                    .attr("clip-path", "url(#clip)")
                    .on("mouseenter", function (e) {
                        svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", x(1) - x(0)).attr("height", plotHeight);
                    })
                    .on("mouseleave", function (e) {
                        svg.selectAll(".marked").remove();
                    })
                    .attr("class", "txt " + d.c)
                    .attr("x", x(d.x - 0.5))
                    .attr("y", plotHeight + 55)
                    .text(d.c);
                return "txt " + d.s;
            } else {
                return "txt " + d.s
            }
        })
        .text(function (d) {
            return d.s;
        });

    qwe.exit()
        .remove();

    var qwe = svg.select("g.sequence_l").selectAll("text")
        .data(datas['stats']['sequence_l'].filter(inRange));
    qwe
        .enter()
        .append("text")
        .attr("class", "yo")
        .attr("clip-path", "url(#clip)")
        .on("mouseenter", function (d) {
            svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", x(1) - x(0)).attr("height", plotHeight);
        })
        .on("mouseleave", function (d) {
            svg.selectAll(".marked").remove();
        });


    qwe
        .attr("x", calcX)
        .attr("y", plotHeight + 40) //(plotHeight + 50))
        .attr("class", function (d) {
            if (d.s !== d.c || false) {
                svg.selectAll(".marked").remove();
                svg.select("g.sequence_l")
                    .append("text")
                    .attr("clip-path", "url(#clip)")
                    .on("mouseenter", function (e) {
                        svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", x(1) - x(0)).attr("height", plotHeight);
                    })
                    .on("mouseleave", function (e) {
                        svg.selectAll(".marked").remove();
                    })
                    .attr("class", "txt " + d.c)
                    .attr("x", x(d.x - 0.5))
                    .attr("y", plotHeight + 25)
                    .text(d.c);
                return "txt " + d.s;
            } else {
                return "txt " + d.s
            }
        })
        .text(function (d) {
            return d.s;
        });
    console.log(datas);
    qwe.exit()
        .remove();
    svg.select("line.zero_line").attr("x1", x(datas['stats']['ClipS'] - 0.5)).attr("x2", x(datas['stats']['ClipS'] - 0.5));
    svg.select("line.possible_line").attr("x1", x(datas['stats']['ClipE'] - 0.5)).attr("x2", x(datas['stats']['ClipE'] - 0.5));
    svg.select("rect.junction")
        .attr("x", x(datas['stats']['ClipS'] - 0.5))
        .attr("width", x(datas['stats']['ClipE']) - x(datas['stats']['ClipS']));
    svg.select(".x.axis").call(xAxis);
    svg.select('g.seqY.axis').call(seqYAxis);

    svg.select("text.axis-label-genome").attr("x", x(0) + t_genome_offset);
    svg.select("text.axis-label-L1").attr("x", x(0) + t_L1_offset);

}


function zoomed() {
    'use strict';
    var plot_idx, origin, dom, bar,
        xlowerlimit = "",
        xupperlimit = "",
        xTranslateLower = "",
        xTranslateUpper = "",
        dataPerPixel = "",
        cuts = "",
        t = zoom.translate(),
        s = zoom.scale(),
        se = zoom.scaleExtent()[1],
        currentDomain = x.domain(),
        xinterval = currentDomain[1] - currentDomain[0];

    $("#position").val(datas.stats.chromosome + ":" + Math.floor(datas.stats.bp_max - (0 - currentDomain[0] - 1)) + "-" + Math.floor(datas.stats.bp_max + currentDomain[1]));
    dom_dist = (x.domain()[1] - x.domain()[0]);
    barWidth = width / dom_dist;
    var barWidth2 = width / dom_dist;

    dataPerPixel = (dom_dist * 6) / width;
    barWidth *= Math.ceil(dataPerPixel);


    if (se >= s && dataPerPixel < 1) {
        svg.select("g.sequence_g").selectAll("rect").remove();
        svg.select("g.sequence_l").selectAll("rect").remove();
        var qwe = svg.select("g.sequence_g").selectAll("text")
            .data(datas['stats']['sequence_g'].filter(inRange));
        qwe
            .enter()
            .append("text")
            .attr("class", "yo")
            .attr("clip-path", "url(#clip)")
            .on("mouseenter", function (d) {
                svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", barWidth).attr("height", plotHeight);
            })
            .on("mouseleave", function (d) {
                svg.selectAll(".marked").remove();
            });


        qwe
            .attr("x", calcX)
            .attr("y", plotHeight + 50) //(plotHeight + 50))
            .attr("class", function (d) {
                if (d.s !== d.c || false) {
                    if (d.c === 'X') d.c = '-';
                    svg.selectAll(".marked").remove();
                    svg.select("g.sequence_g")
                        .append("text")
                        .attr("clip-path", "url(#clip)")
                        .on("mouseenter", function (e) {
                            svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", barWidth).attr("height", plotHeight);
                        })
                        .on("mouseleave", function (e) {
                            svg.selectAll(".marked").remove();
                        })
                        .attr("class", "txt " + d.c)
                        .attr("x", x(d.x - 0.5))
                        .attr("y", plotHeight + 35)
                        .text(d.c);
                    return "txt " + d.s;
                } else {
                    return "txt " + d.s
                }
            })
            .text(function (d) {
                return d.s;
            });

        qwe.exit()
            .remove();

        var qwe = svg.select("g.sequence_l").selectAll("text")
            .data(datas['stats']['sequence_l'].filter(inRange));
        qwe
            .enter()
            .append("text")
            .attr("class", "yo")
            .attr("clip-path", "url(#clip)")
            .on("mouseenter", function (d) {
                svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", barWidth).attr("height", plotHeight);
            })
            .on("mouseleave", function (d) {
                svg.selectAll(".marked").remove();
            });


        qwe
            .attr("x", calcX)
            .attr("y", plotHeight + 50) //(plotHeight + 50))
            .attr("class", function (d) {
                if (d.s !== d.c || false) {
                    if (d.c === 'X') d.c = '-';
                    svg.selectAll(".marked").remove();
                    svg.select("g.sequence_l")
                        .append("text")
                        .attr("clip-path", "url(#clip)")
                        .on("mouseenter", function (e) {
                            svg.select("g.rekt").append("rect").attr("class", "marked").attr("x", x(d.x - 0.5)).attr("y", 0).attr("width", barWidth).attr("height", plotHeight);
                        })
                        .on("mouseleave", function (e) {
                            svg.selectAll(".marked").remove();
                        })
                        .attr("class", "txt " + d.c)
                        .attr("x", x(d.x - 0.5))
                        .attr("y", plotHeight + 35)
                        .text(d.c);
                    return "txt " + d.s;
                } else {
                    return "txt " + d.s
                }
            })
            .text(function (d) {
                return d.s;
            });

        qwe.exit()
            .remove();
        //    }
        //    } else if ((se - 5) >= s && s > (se - 17)) {
    } else if (1 <= dataPerPixel && dataPerPixel < 2) {

        svg.select("g.sequence_g").selectAll("text").remove();
        var qwe = svg.select("g.sequence_g").selectAll("rect")
            .data(datas['stats']['sequence_g'].filter(inRange));
        qwe
            .enter()
            .append("rect")
            .attr("class", "txt")
            .attr("clip-path", "url(#clip)")

        qwe
            .attr("x", calcX)
            .attr("width", barWidth2)
            .attr("y", plotHeight + 40) //(plotHeight + 50))
            .attr("height", 10)
            .attr("class", function (d) {
                if (d.s !== d.c || false) {
                    svg.select("g.sequence_g")
                        .append("rect")
                        .attr("clip-path", "url(#clip)")
                        .attr("class", "txt " + d.c)
                        .attr("x", x(d.x - 0.5))
                        .attr("width", barWidth2)
                        .attr("y", plotHeight + 25)
                        .attr("height", 10)
                    return "txt " + d.s;
                } else {
                    return "txt " + d.s
                }
            })

        qwe.exit()
            .remove();

        svg.select("g.sequence_l").selectAll("text").remove();
        var qwe = svg.select("g.sequence_l").selectAll("rect")
            .data(datas['stats']['sequence_l'].filter(inRange));
        qwe
            .enter()
            .append("rect")
            .attr("class", "txt")
            .attr("clip-path", "url(#clip)")

        qwe
            .attr("x", calcX)
            .attr("width", barWidth2)
            .attr("y", plotHeight + 40) //(plotHeight + 50))
            .attr("height", 10)
            .attr("class", function (d) {
                if (d.s !== d.c || false) {
                    svg.select("g.sequence_l")
                        .append("rect")
                        .attr("clip-path", "url(#clip)")
                        .attr("class", "txt " + d.c)
                        .attr("x", x(d.x - 0.5))
                        .attr("width", barWidth2)
                        .attr("y", plotHeight + 25)
                        .attr("height", 10)
                    return "txt " + d.s;
                } else {
                    return "txt " + d.s
                }
            })

        qwe.exit()
            .remove();
    } else {
        svg.select("g.sequence_g").selectAll("text").remove();
        svg.select("g.sequence_g").selectAll("rect").remove();
        svg.select("g.sequence_l").selectAll("text").remove();
        svg.select("g.sequence_l").selectAll("rect").remove();
    }



    for (plot_idx = 0; plot_idx < 3; plot_idx += 1) {
        for (origin = 0; origin < 2; origin += 1) {
            var bar = svg.select("g.rekt").selectAll(".bar" + plot_classes[(plot_idx * 2 + origin)])
                .data(data[plot_idx * 2 + origin].filter(getMax(dataPerPixel)).filter(inRange));

            bar.enter()
                .append("rect")
                .attr("class", "bar" + plot_classes[(plot_idx * 2 + origin)])
                .attr("clip-path", "url(#clip)")
                .attr("x", calcX)
                .attr("width", barWidth)
                .attr("y", calcY(plot_idx))
                .attr("height", calcHeight(plot_idx))
                .on("mouseenter", mouseIn)
                .on("mouseleave", mouseleave)
                .on('click', mouseClick);

            bar
                .attr("x", calcX)
                .attr("width", barWidth)
                .attr("y", calcY(plot_idx))
                .attr("height", calcHeight(plot_idx));

            bar.exit()
                .on("mouseenter", null)
                .on("mouseleave", null)
                .remove();

        }
    }

    cuts = svg.select("g.enzyme_cs").selectAll(".cuts").data(enzymeCuts);
    cuts
        .enter()
        .append("line")
        .attr("class", "cuts child")
        .attr("clip-path", "url(#clip)")
        .style("stroke", "#d6296c") // colour the line
        .style("stroke-width", "2") // thicken the line
        .attr("x1", function (d) {
            return x(d[1]);
        }) // x position of the first end of the line
        .attr("y1", 0) // y position of the first end of the line
        .attr("x2", function (d) {
            return x(d[1]);
        }) // x position of the second end of the line
        .attr("y2", plotHeight) // y position of the second end of the line
        .on("mouseenter", function (d) {
            //'use strict';
            cut_div.transition()
                .duration(200)
                .style("opacity", 0.9);
            cut_div.html(
                    d[0] + ":" + d[1] + "<br/>"
                )
                .style("left", (d3.event.pageX - 85) + "px")
                .style("top", d3.event.pageY + "px");
        })
        .on("mouseleave", mouseleaveEnzyme);

    cuts
        .attr("x1", function (d) {
            return x(d[1]);
        }) // x position of the first end of the line
        .attr("y1", 0) // y position of the first end of the line
        .attr("x2", function (d) {
            return x(d[1]);
        }) // x position of the second end of the line
        .attr("y2", plotHeight); // y position of the second end of the line

    cuts.exit()
        .remove();



    var layer_g = svg.select('g.rektangle').selectAll("g.layer_g")
        .data(g_layers);
    layer_g.enter()
        .append("g")
        .attr("class", function (d, i) {
            return "layer_g bar" + i * 2;
        })
        .attr("clip-path", "url(#clip)");
    layer_g.exit()
        .transition()
        .duration(500)
        .remove();

    layer_g
        .data(g_layers)


    var rec = layer_g.selectAll("rect")
        .data(function (d) {
            return d.filter(getMax(dataPerPixel)).filter(inRange);
        });
    rec.enter().append("rect")
        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](d.y + d.y0);
        })
        .attr("height", function (d) {
            return y[3](d.y0) - y[3](d.y + d.y0);
        })
        .attr("width", barWidth)
        .on("mouseenter", g_mouseInAll)
        .on("mouseleave", mouseleave)
        .on('click', mouseClick);
    rec.exit()
        .remove();
    rec
        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](d.y + d.y0);
        })
        .attr("height", function (d) {
            return y[3](d.y0) - y[3](d.y + d.y0);
        })
        .attr("width", barWidth);

    var layer_l = svg.select('g.rektangle').selectAll("g.layer_l")
        .data(l_layers);
    layer_l.enter()
        .append("g")
        .attr("class", function (d, i) {
            return "layer_l bar" + ((i + 1) * 2 + 1);
        })
        .attr("clip-path", "url(#clip)");
    layer_l.exit()
        .transition()
        .duration(500)
        .remove();

    layer_l
        .data(l_layers)


    var rec = layer_l.selectAll("rect")
        .data(function (d) {
            return d.filter(getMax(dataPerPixel)).filter(inRange);
        });
    rec.enter().append("rect")
        .attr("class", function (d) {
            return d3.select(this.parentNode).attr('class').split(' ')[1];
        })
        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](d.y + d.y0);
        })
        .attr("height", function (d) {
            return y[3](d.y0) - y[3](d.y + d.y0);
        })
        .attr("width", barWidth)
        .on("mouseenter", l_mouseInAll)
        .on("mouseleave", mouseleave)
        .on('click', mouseClick);
    rec.exit()
        .remove();
    rec
        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](d.y + d.y0);
        })
        .attr("height", function (d) {
            return y[3](d.y0) - y[3](d.y + d.y0);
        })
        .attr("width", barWidth);

    svg.select("line.chart_start").attr("x1", x(datas.stats.start) - barWidth / 2).attr("x2", x(datas.stats.start) - barWidth / 2);
    svg.select("line.chart_end").attr("x1", x(datas.stats.end) + barWidth / 2).attr("x2", x(datas.stats.end) + barWidth / 2);


    svg.select("line.zero_line").attr("x1", x(datas['stats']['ClipS'] - 0.5)).attr("x2", x(datas['stats']['ClipS'] - 0.5));
    svg.select("line.possible_line").attr("x1", x(datas['stats']['ClipE'] - 0.5)).attr("x2", x(datas['stats']['ClipE'] - 0.5));
    svg.select("rect.junction")
        .attr("x", x(datas['stats']['ClipS'] - 0.5))
        .attr("width", x(datas['stats']['ClipE']) - x(datas['stats']['ClipS']));
    svg.select(".x.axis").call(xAxis);

    svg.select("text.axis-label-genome").attr("x", x(0) + t_genome_offset);
    svg.select("text.axis-label-L1").attr("x", x(0) + t_L1_offset);
}

function redraw(dat) {
    showCoverage();
    mouseleave();
    mouseleaveEnzyme();
    svg.select("g.sequence_g").selectAll("text").remove();
    svg.select("g.sequence_g").selectAll("rect").remove();
    svg.select("g.sequence_l").selectAll("text").remove();
    svg.select("g.sequence_l").selectAll("rect").remove();
    svg.select('g.each_seq').selectAll('g.jg_seq').remove();
    svg.select('g.each_seq').selectAll('g.jl_seq').remove();
    svg.select("g.bg").selectAll("rect").remove();

    svg.select("g.spacer").attr("visibility", "visible");
    svg.selectAll("text.axis-label").attr("visibility", "visible");



    svg.select('g.y1.axis').attr("visibility", "visible");
    //            .call(yAxis[0]);
    svg.select('g.y2.axis').attr("visibility", "visible");
    //            .call(yAxis[1]);
    svg.select('g.y3.axis').attr("visibility", "visible");
    //            .call(yAxis[2]);
    svg.select('g.y4.axis').attr("visibility", "visible");
    //            .call(yAxis[3]);


    svg.select('g.seqY.axis').attr("visibility", "hidden");




    initialized = false;
    'use strict';
    var counter = 0,
        plot_idx = "",
        origin = "",
        bars = "",
        dom = "",
        dataPerPixel = "",
        cuts = "",
        currentDomain = x.domain();
    enzymeCuts = dat.info.enzyme_cut_sites;
    if (enzymeCuts !== "")
    {
      enzymeCuts = enzymeCuts.split(':');
    }
    for (counter = 0; counter < enzymeCuts.length; counter += 1) {
        enzymeCuts[counter] = enzymeCuts[counter].split('-');
        if (dat.stats.complement === 1) {
            enzymeCuts[counter][1] *= -1;
        }
    }
    datas = dat;
    Zero_estimate = datas.stats.zero_offset;
    barWidth = width / dom_dist;
    if (dat.stats.complement === 0) {
        data = [dat.bins.g_gg.coverage, [{
                'x': 0,
                'y': 0
            }],
                            dat.bins.g_gl.coverage, dat.bins.l_gl.coverage,
                            dat.bins.g_rj.coverage, dat.bins.l_rj.coverage,

                            ];
        L1_start = -(dat.stats.l1_max - dat.stats.l1_min);
        t_genome_offset = 20;
        t_L1_offset = -70;
        x.domain([L1_start, (dat.stats.bp_max - dat.stats.bp_min)]);
    } else {
        data = [dat.bins.g_gg.coverage, [{
                'x': 0,
                'y': 0
            }],
                            dat.bins.g_gl.coverage, dat.bins.l_gl.coverage,
                            dat.bins.g_rj.coverage, dat.bins.l_rj.coverage,

                            ];
        L1_start = (dat.stats.l1_max - dat.stats.l1_min);
        t_genome_offset = -70;
        t_L1_offset = 20;
        x.domain([(dat.stats.bp_min - dat.stats.bp_max), L1_start]);
    }

    g_reads = datas['bins']['g_rj']['reads'].length
    l_reads = datas['bins']['l_rj']['reads'].length

    g_reads_sorted = datas['bins']['g_rj']['reads']
    if (datas.stats.complement) {
        g_reads_sorted.sort(function (a, b) {
            if (a.x !== b.x) {
                return a.x - b.x;
            } else {
                return a.cig[a.cig.length - 1][0].length - b.cig[b.cig.length - 1][0].length
            }
        });
    } else {
        g_reads_sorted.sort(function (a, b) {
            var offset = [0, 0];
            if (a.cig[a.cig.length - 1][1] == "green") {
                offset[0] = 0 //a.cig[a.cig.length - 1][0].length;
            }
            if (b.cig[b.cig.length - 1][1] == "green") {
                offset[1] = 0 //b.cig[b.cig.length - 1][0].length;
            }
            if ((b.x + offset[1]) !== (a.x + offset[0]))
                return ((a.x + offset[0]) - (b.x + offset[1]));
            else
                return a.cig[0][0].length - b.cig[0][0].length
        });
    }
    g_reads_sorted = g_reads_sorted.map(function (c, i) {

        var pos = c.x + datas.stats.complement;
        if (c.cig[0][1] == "red") {
            pos -= c.cig[0][0].length;
        }
        var lst = []
        for (var e = 0; e < c.cig.length; e++) {
            for (var x = 0; x < c.cig[e][0].length; x++) {
                lst.push({
                    "l": c.cig[e][0][x],
                    "x": pos++,
                    "y": i,
                    "c": c.cig[e][1]
                });
            }
        }
        return lst;
    });

    l_reads_sorted = datas['bins']['l_rj']['reads']
    if (datas.stats.complement) {
        l_reads_sorted.sort(function (a, b) {
            if ((b.x) !== (a.x))
                return ((a.x) - (b.x));
            else
                return b.cig[b.cig.length - 1][0].length - a.cig[a.cig.length - 1][0].length
        });
    } else {
        l_reads_sorted.sort(function (a, b) {
            var offset = [0, 0];
            if (a.cig[0][1] == "orange") {
                offset[0] = a.cig[0][0].length;
            }
            if (b.cig[0][1] == "orange") {
                offset[1] = b.cig[0][0].length;
            }
            if (a.cig.length > 1)
                if (a.cig[1][1] == "orange") {
                    offset[0] = a.cig[1][0].length;
                }
            if (b.cig.length > 1)
                if (b.cig[1][1] == "orange") {
                    offset[1] = b.cig[1][0].length;
                }
            if ((b.x + offset[1]) !== (a.x + offset[0])) {
                return ((b.x + offset[1]) - (a.x + offset[0]));
            } else {
                return b.cig[0][0].length - a.cig[0][0].length
            }
        });
    }
    l_reads_sorted = l_reads_sorted.map(function (c, i) {

        var pos = c.x;
        if (c.cig[c.cig.length - 1][1] == "red") {
            pos -= c.cig[c.cig.length - 1][0].length;
        }
        var lst = []
        for (var e = c.cig.length - 1; e >= 0; e--) {
            for (var x = 0; x < c.cig[e][0].length; x++) {
                lst.push({
                    "l": c.cig[e][0][x],
                    "x": pos++,
                    "y": -i - 1,
                    "c": c.cig[e][1]
                });
            }
        }
        return lst;
    });

    var numReads = plotHeight / (x(1) - x(0)) * 1;
    seqY.domain([-numReads / 2, numReads / 2]);

    dom_dist = (x.domain()[1] - x.domain()[0]);
    maxdom = x.domain();
    barWidth = width / dom_dist;

    zoom
        .x(x)
        .scaleExtent([1, dom_dist / 100]);
    zoom.on("zoom", zoomed);

    dataPerPixel = (dom_dist * 6) / width;
    barWidth *= Math.ceil(dataPerPixel);

    y[0].domain([0, 1.05 * d3.max(data[0], function (d) {
        return d.y;
    })]);
    y[1].domain([0, 1.05 * Math.max(d3.max(data[2], function (d) {
        return d.y;
    }), d3.max(data[3], function (d) {
        return d.y;
    }))]);
    y[2].domain([0, 1.05 * Math.max(d3.max(data[4], function (d) {
        return d.y;
    }), d3.max(data[5], function (d) {
        return d.y;
    }))]);
    y[3].domain([0, 1.05 * Math.max(
            Math.max(d3.max(dat.bins.g_gg.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.g_gl.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.g_jg.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.g_gn.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.g_jl.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.g_jn.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.g_jj.coverage, function (d) {
                return d.y;
            })),

            Math.max(d3.max(dat.bins.l_ll.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.l_gl.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.l_jg.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.l_ln.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.l_jl.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.l_jn.coverage, function (d) {
                return d.y;
            })) +
            Math.max(d3.max(dat.bins.l_jj.coverage, function (d) {
                return d.y;
            })))

                ]);



    svg.selectAll("g.y1.axis")
        //        .transition().duration(500).ease("sin-in-out")
        .call(yAxis[0]);
    svg.selectAll("g.y2.axis")
        //        .transition().duration(500).ease("sin-in-out")
        .call(yAxis[1]);
    svg.selectAll("g.y3.axis")
        //        .transition().duration(500).ease("sin-in-out")
        .call(yAxis[2]);
    svg.selectAll("g.y4.axis")
        //        .transition().duration(500).ease("sin-in-out")
        .call(yAxis[3]);

    var cuts = svg.select("g.enzyme_cs").selectAll(".cuts")
        .data(enzymeCuts);
    cuts
        .enter()
        .append("line")
        .attr("class", "cuts child")
        .attr("clip-path", "url(#clip)")
        .style("stroke", "#d6296c") // colour the line
        .style("stroke-width", "2") // thicken the line
        .attr("x1", x(0)) // x position of the first end of the line
        .attr("y1", 0) // y position of the first end of the line
        .attr("x2", x(0)) // x position of the second end of the line
        .attr("y2", plotHeight) // y position of the second end of the line
        .on("mouseenter", function (d) {
            //'use strict';
            cut_div.transition()
                .duration(200)
                .style("opacity", 0.9);
            cut_div.html(
                    d[0] + ":" + d[1] + "<br/>"
                )
                .style("left", (d3.event.pageX - 85) + "px")
                .style("top", d3.event.pageY + "px");
        })
        .on("mouseleave", mouseleaveEnzyme);

    cuts
        .attr("x1", function (d) {
            return x(d[1]);
        }) // x position of the first end of the line
        .attr("y1", 0) // y position of the first end of the line
        .attr("x2", function (d) {
            return x(d[1]);
        }) // x position of the second end of the line
        .attr("y2", plotHeight); // y position of the second end of the line

    cuts.exit()
        .remove();
    plot_classes = ['GGG', 'LLL', 'GGL', 'LGL', 'JJG', 'JJL']
    for (plot_idx = 0; plot_idx < 3; plot_idx += 1) {
        for (origin = 0; origin < 2; origin += 1) {
            var bars = svg.select("g.rekt").selectAll(".bar" + plot_classes[(plot_idx * 2 + origin)])
                .data(data[plot_idx * 2 + origin]
                    .filter(getMax(dataPerPixel))
                );
            bars.exit()
                .on("mouseenter", null)
                .on("mouseleave", null)
                //                .transition()
                //                .duration(500)
                //                .attr("width", 0)
                .attr("y", startHeight(plot_idx))
                .attr("height", 0)
                .remove();
            bars.enter()
                .append("rect")
                .attr("class", "bar" + plot_classes[(plot_idx * 2 + origin)])
                .attr("clip-path", "url(#clip)")
                .attr("x", calcX)
                .attr("width", barWidth)
                //pre animation height
                .attr("y", startHeight(plot_idx))
                .attr("height", 0)
                .on("mouseenter", mouseIn)
                .on("mouseleave", mouseleave)
                .on('click', mouseClick);
            bars
            //                .transition()
            //                .duration(500)
            //                .delay(function (d, i) {
            //                    return i;
            //                })
                .attr("x", calcX)
                .attr("width", barWidth)
                .attr("y", calcY(plot_idx))
                .attr("height", calcHeight(plot_idx));
            //                .attr("height", -5)
        }
    }
    all_classes = ['GGG', 'LLL', 'GGL', 'LGL', 'GGN', 'LLN', 'JL', 'JL', 'JG', 'JG', 'JN', 'JN', 'JJ', 'JJ']
    g_bins = [dat.bins.g_gg, dat.bins.g_gl, dat.bins.g_gn, dat.bins.g_jl, dat.bins.g_jg, dat.bins.g_jn, dat.bins.g_jj]

    g_layers = stack_g(g_bins.map(function (c) {
        return c.coverage.map(function (d) {
            return d;
        });
    }));




    var layer_g = svg.select('g.rektangle').selectAll("g.layer_g")
        .data(g_layers);
    layer_g.enter()
        .append("g")
        .attr("class", function (d, i) {
            return "layer_g bar" + all_classes[i * 2];
        })
        .attr("clip-path", "url(#clip)");
    layer_g.exit()
        .transition()
        .duration(500)
        .remove();

    var rec_g = layer_g.selectAll("rect")
        .data(function (d) {
            return d.filter(getMax(dataPerPixel));
        });
    rec_g.enter().append("rect")
        .attr("class", function (d) {
            return d3.select(this.parentNode).attr('class').split(' ')[1];
        })
        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](0);
        })
        .attr("height", 0)
        .attr("width", barWidth)
        .on("mouseenter", g_mouseInAll)
        .on("mouseleave", mouseleave)
        .on('click', mouseClick);
    rec_g.exit()
        //                .attr("width", 0)
        .attr("y", function (d) {
            return y[3](0);
        })
        .attr("height", 0)
        .remove();
    rec_g

        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](d.y + d.y0);
        })
        .attr("height", function (d) {
            return y[3](d.y0) - y[3](d.y + d.y0);
        })
        .attr("width", barWidth)

    l_bins = [dat.bins.l_ll, dat.bins.l_gl, dat.bins.l_ln, dat.bins.l_jl, dat.bins.l_jg, dat.bins.l_jn, dat.bins.l_jj]


    l_layers = stack_l(l_bins.map(function (c) {
        return c.coverage.map(function (d) {
            return d;
        });
    }));




    var layer_l = svg.select('g.rektangle').selectAll("g.layer_l")
        .data(l_layers);
    layer_l.enter()
        .append("g")
        .attr("class", function (d, i) {
            return "layer_l bar" + all_classes[(i * 2 + 1)];
        })
        .attr("clip-path", "url(#clip)");
    layer_l.exit()
        .transition()
        .duration(500)
        .remove();
    var rec_l = layer_l.selectAll("rect")
        .data(function (d) {
            return d.filter(getMax(dataPerPixel));
        });
    rec_l.enter().append("rect")
        .attr("class", function (d) {
            return d3.select(this.parentNode).attr('class').split(' ')[1];
        })
        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](0);
        })
        .attr("height", 0)
        .attr("width", barWidth)
        .on("mouseenter", l_mouseInAll)
        .on("mouseleave", mouseleave)
        .on('click', mouseClick);
    rec_l.exit()
        //                .attr("width", 0)
        .attr("y", function (d) {
            return y[3](0);
        })
        .attr("height", 0)
        .remove();
    rec_l

        .attr("x", calcX)
        .attr("y", function (d) {
            return y[3](d.y + d.y0);
        })
        .attr("height", function (d) {
            return y[3](d.y0) - y[3](d.y + d.y0);
        })
        .attr("width", barWidth)


    svg.select(".x.axis").call(xAxis);
    svg.select("text.axis-label-genome").attr("x", x(0) + t_genome_offset);
    svg.select("text.axis-label-L1").attr("x", x(0) + t_L1_offset);
    svg.select("line.zero_line").attr("x1", x(datas['stats']['ClipS'] - 0.5)).attr("x2", x(datas['stats']['ClipS'] - 0.5));
    svg.select("line.chart_start").attr("x1", x(datas.stats.start) - barWidth / 2).attr("x2", x(datas.stats.start) - barWidth / 2);
    svg.select("line.chart_end").attr("x1", x(datas.stats.end) + barWidth / 2).attr("x2", x(datas.stats.end) + barWidth / 2);
    svg.select("line.possible_line").attr("x1", x(datas['stats']['ClipE'] - 0.5)).attr("x2", x(datas['stats']['ClipE'] - 0.5));
    svg.select("rect.junction")
        .attr("x", x(datas['stats']['ClipS'] - 0.5))
        .attr("width", datas['stats']['ClipWidth']);
    $("#position").val(dat.stats.chromosome + ":" + dat.stats.bp_min + "-" + (dat.stats.bp_max + 160));

    //    svg.select('g.seqY.axis').call(seqYAxis);svg.select(".x.axis").transition().duration(500).call(xAxis);
    //    svg.select("text.axis-label-genome").transition().duration(500).attr("x", x(0) + t_genome_offset);
    //    svg.select("text.axis-label-L1").transition().duration(500).attr("x", x(0) + t_L1_offset);
    //    svg.select("line.zero_line").transition().duration(500).attr("x1", x(datas['stats']['ClipS'] - 0.5)).attr("x2", x(datas['stats']['ClipS'] - 0.5));
    //    svg.select("line.chart_start").transition().duration(500).attr("x1", x(datas.stats.start) - barWidth / 2).attr("x2", x(datas.stats.start) - barWidth / 2);
    //    svg.select("line.chart_end").transition().duration(500).attr("x1", x(datas.stats.end) + barWidth / 2).attr("x2", x(datas.stats.end) + barWidth / 2);
    //    svg.select("line.possible_line").transition().duration(500).attr("x1", x(datas['stats']['ClipE'] - 0.5)).attr("x2", x(datas['stats']['ClipE'] - 0.5));
    //    svg.select("rect.junction").transition().duration(500)
    //        .attr("x", x(datas['stats']['ClipS'] - 0.5))
    //        .attr("width", datas['stats']['ClipWidth']);
    //    $("#position").val(dat.stats.chromosome + ":" + dat.stats.bp_min + "-" + (dat.stats.bp_max + 160));
    //
    //    svg.select('g.seqY.axis').call(seqYAxis);
}



function resize() {
    /* Find the new window dimensions */
    width = parseInt(d3.select(".plot").style("width")) - margin.left - margin.right;
    height = parseInt(d3.select(".plot").style("height"), 10) - margin.top - margin.bottom - 100
    plotHeight = height + 60;

    /* Update the range of the scale with new width/height */
    x.range([0, width]);


    d3.select(svg.node().parentNode)
        .style('height', (height + margin.top + margin.bottom + 120) + 'px')
        .style('width', (width + margin.left + margin.right) + 'px');

    xAxis.ticks(Math.max(width / 50, 2));
    xAxis.tickSize(-plotHeight);
    //    yAxis.ticks(Math.max(height/50, 2));
    /* Update the axis with the new scale */
    svg.select("rect.clip").attr("width", width);
    svg.select("rect.clip").attr("height", height + margin.bottom + 120);

    svg.select("g.loader").selectAll("rect")
        .attr("width", width)
        .attr("height", plotHeight);

    svg.select("rect.clipRead").attr("width", width);
    svg.select("rect.clipRead").attr("height", plotHeight);

    svg.select('.x.axis')
        .attr("transform", "translate(0," + parseInt(plotHeight, 10) + ")")
        .call(xAxis);

    svg.select("text.axis-label-genome")
        .attr("y", -2);

    svg.select("text.axis-label-L1")
        .attr("y", -2);

    svg.select("text.axis-label-GG")
        .attr("x", -plotHeight / 8)
    svg.select("text.axis-label-LG")
        .attr("x", -3 * plotHeight / 8)
    svg.select("text.axis-label-J")
        .attr("x", -5 * plotHeight / 8)
    svg.select("text.axis-label-A")
        .attr("x", -7 * plotHeight / 8)

    svg.select("rect.spacer.W")
        .attr("y", plotHeight / 4 - 5)
        .attr("width", width + 5)
    svg.select("rect.spacer.X")
        .attr("y", (2 * plotHeight / 4) - 5)
        .attr("width", width + 5)
    svg.select("rect.spacer.Y")
        .attr("y", (3 * plotHeight / 4) - 5)
        .attr("width", width + 5)


    svg.select("line.zero_line").attr("y1", 0).attr("y2", plotHeight);
    svg.select("line.chart_start").attr("y1", 0).attr("y2", plotHeight);
    svg.select("line.chart_end").attr("y1", 0).attr("y2", plotHeight);
    svg.select("line.possible_line").attr("y1", 0).attr("y2", plotHeight);
    svg.select("rect.junction")
        .attr("y", 0).attr("height", plotHeight);


    svg.select("g.buttons").select("text.coverage")
        .attr("x", width / 2 - 75);

    svg.select("g.buttons").select("text.reads")
        .attr("x", width / 2 + 15);

    svg.select("g.buttons").select("rect.divisor")
        .attr("width", width + margin.left + margin.right);

    if (readsOn)
        svg.select("g.buttons").select("rect.underline")
        .attr("x", width / 2 + 10)
        .attr("width", 125);
    else
        svg.select("g.buttons").select("rect.underline")
        .attr("x", width / 2 - 80)
        .attr("width", 81);


    yAxis[0].tickSize(-width);
    yAxis[1].tickSize(-width);
    yAxis[2].tickSize(-width);
    yAxis[3].tickSize(-width);
    seqYAxis.tickSize(-width);

    y[0].range([plotHeight / 4 - 5, 0]);
    y[1].range([(2 * plotHeight / 4) - 5, (plotHeight / 4) + 5]);
    y[2].range([(3 * plotHeight / 4) - 5, (2 * plotHeight / 4) + 5]);
    y[3].range([(4 * plotHeight / 4), (3 * plotHeight / 4) + 5]);

    seqY.range([plotHeight, 0]);


    svg.select('g.y1.axis')
        .call(yAxis[0]);
    svg.select('g.y2.axis')
        .call(yAxis[1]);
    svg.select('g.y3.axis')
        .call(yAxis[2]);
    svg.select('g.y4.axis')
        .call(yAxis[3]);
    svg.select('g.seqY.axis')
        .call(seqYAxis);


    svg.selectAll(".spacer").attr("width", width + 2);

    if (datas !== "" && !readsOn) {
        zoomed();
    } else if (datas !== "" && readsOn) {
        var numLetters = width / 14;
        x.domain([-numLetters / 2, numLetters / 2]);
        zoom.x(x);
        var numReads = plotHeight / (x(1) - x(0)) * 1;
        seqY.domain([-numReads / 2, numReads / 2]);
        var trans = zoom.translate();
        zoom.y(seqY);
        zoom.translate(trans);
        zoomReads();
    }
}

d3.select(window).on('resize', resize);
$(document).ready(function () {
    'use strict';

    loadJSON(function (response) {
        //        // Do Something with the response e.g.
        //        //jsonresponse = JSON.parse(response);
        //        // Assuming json data is wrapped in square brackets as Drew suggests
        buildTable(JSON.parse(response));
        $('#data_table tbody tr').click(function () {
            $('#data_table tbody tr').removeClass("factive");
            $(this).addClass("factive");
        });
        if (location.hash != '') {
            updateData(location.hash.substring(1));
        }
    }, "table_info");

    $(document).on("click", ".sticky-thead th", function (e) {
        var table = $("#data_table");
        $("#header0").text("ID ◇");
        $("#header1").text("Gene ◇");
        $("#header2").text("P ◇");
        $("#header" + $(this).index()).text($("#header" + $(this).index()).text().substr(0, $("#header" + $(this).index()).text().length - 1) + "▵");
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
        this.asc = !this.asc;
        if (!this.asc) {
            rows = rows.reverse();
            $("#header" + $(this).index()).text($("#header" + $(this).index()).text().substr(0, $("#header" + $(this).index()).text().length - 1) + "▿");
        }
        for (var i = 0; i < rows.length; i++) {
            table.append(rows[i])
        }
    });
});

function comparer(index) {
    return function (a, b) {
        var valA = getCellValue(a, index),
            valB = getCellValue(b, index);
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.localeCompare(valB)
    }
};

function getCellValue(row, index) {
    return $(row).children('td').eq(index).html()
};

function updateData(fileID) {
    'use strict';
    //    svg.select("g.loader").attr("transform", "translate(-5000,0)");

    svg.select("g.loader")
        .attr("transform", "translate(" + -(width + margin.right + margin.left) + ",0)");

    svg.select("g.loader")
        .transition()
        .duration(1000)
        .ease("cubic")
        .attr("transform", "translate(0,0)");
    svg.select("g.plot")
        .transition()
        .duration(1000)
        .ease("cubic")
        .attr("transform", "translate(" + (width + margin.right + margin.left) + ",0)")
        .each("end", function () { // as seen above
            svg.select("g.plot") // this is the object          // a new transition!
                .attr("transform", "translate(" + (-width - margin.right - margin.left) + ",0)") // we could have had another
                // .each("end" construct here.
            loadJSON(function (response) {
                window.location.replace('#' + fileID);
                redraw(JSON.parse(response));
            }, fileID);
        });
}

var arc = d3.svg.arc()
    .innerRadius(30)
    .outerRadius(40)
    .startAngle(0);

function loading(percent) {
    var lod = svg.select("g.loader").selectAll("path")
        .data([{
            endAngle: percent * 2 * Math.PI
        }]);

    lod.enter()
        .append("path")
        .attr("class", "loading")
        .attr("transform", "translate(" + (width / 2) + "," + height / 2 + ")");

    lod
        .attr("d", arc);

    lod.exit()
        .remove();


}

function transferComplete() {
    svg.select("g.loader").transition().duration(1000).ease("cubic").attr("transform", "translate(" + (width + margin.right + margin.left) + ",0)")
        .each("end", function () {
            svg.select("g.loader").selectAll("path").remove();
        });
    svg.select("g.plot").transition().duration(1000).ease("cubic").attr("transform", "translate(0,0)");
}

svg.append("g")
    .attr("class", "plot");

svg.select("g.plot")
    .append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + parseInt(plotHeight, 10) + ")")
    .call(xAxis);

svg.select("g.plot")
    .append("g")
    .attr("class", "x axis genome")
    .append("text")
    .attr("class", "axis-label-genome")
    .attr("y", (-2))
    .attr("x", x(0) + t_genome_offset)
    .style("font-weight", "bold")
    .style("text-rendering", "geometricPrecision")
    .text('Genome');

svg.select("g.plot")
    .append("g")
    .attr("class", "x axis L1")
    .append("text")
    .attr("class", "axis-label-L1")
    .attr("y", -2)
    .attr("x", x(0) + t_L1_offset)
    .style("font-weight", "bold")
    .text('LINE-1');

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
    .call(yAxis[0]);



svg.append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("class", "clip")
    .attr("width", width)
    .attr("height", height + margin.bottom + 120);

svg.append("clipPath")
    .attr("id", "clipReads")
    .append("rect")
    .attr("class", "clipRead")
    .attr("width", width)
    .attr("height", plotHeight);




svg.select("g.y.axis")
    .append("g")
    .attr("class", "y2 axis")
    .call(yAxis[1]);

svg.select("g.y.axis")
    .append("g")
    .attr("class", "y3 axis")
    .call(yAxis[2]);

svg.select("g.y.axis")
    .append("g")
    .attr("class", "y4 axis")
    .call(yAxis[3]);


svg.select("g.y.axis")
    .append("g")
    .attr("class", "seqY axis")
    .attr("visibility", "hidden")
    .call(seqYAxis);

svg.select("g.y.axis")
    .attr("class", "y axis")
    .append("text")
    .attr("class", "axis-label GG")
    .attr("y", (-margin.left + 20))
    .attr("x", -plotHeight / 8)
    .attr("transform", "rotate(-90)")
    .text('G/G');

svg.select("g.y.axis")
    .attr("class", "y axis")
    .append("text")
    .attr("class", "axis-label LG")
    .attr("y", (-margin.left + 20))
    .attr("x", -3 * plotHeight / 8)
    .attr("transform", "rotate(-90)")
    .text('L1/G');

svg.select("g.y.axis")
    .attr("class", "y axis")
    .append("text")
    .attr("class", "axis-label J")
    .attr("y", (-margin.left + 20))
    .attr("x", -5 * plotHeight / 8)
    .attr("transform", "rotate(-90)")
    .text('J');


svg.select("g.y.axis")
    .attr("class", "y axis")
    .append("text")
    .attr("class", "axis-label ALL")
    .attr("y", (-margin.left + 20))
    .attr("x", -7 * plotHeight / 8)
    .attr("transform", "rotate(-90)")
    .text('ALL');


svg.select("g.guide")
    .append("line")
    .attr("class", "chart_start")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "#49d198") // colour the line
    .style("stroke-width", "2") // thicken the line
    .attr("x1", x(0)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(0)) // x position of the second end of the line
    .attr("y2", plotHeight); // y position of the second end of the line

svg.select("g.guide")
    .append("line")
    .attr("class", "chart_end")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "#49d198") // colour the line
    .style("stroke-width", "2") // thicken the line
    .attr("x1", x(0)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(0)) // x position of the second end of the line
    .attr("y2", plotHeight); // y position of the second end of the line

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

svg.select("g.plot")
    .append("g")
    .attr("class", "spacer");

svg.select("g.spacer")
    .append("rect")
    .attr("class", "spacer W")
    .attr("x", -1)
    .attr("y", plotHeight / 4 - 5)
    .attr("width", width + 5)
    .attr("height", 10);

svg.select("g.spacer")
    .append("rect")
    .attr("class", "spacer X")
    .attr("x", -1)
    .attr("y", (2 * plotHeight / 4) - 5)
    .attr("width", width + 5)
    .attr("height", 10);

svg.select("g.spacer")
    .append("rect")
    .attr("class", "spacer Y")
    .attr("x", -1)
    .attr("y", (3 * plotHeight / 4) - 5)
    .attr("width", width + 5)
    .attr("height", 10);



svg.append("g")
    .attr("class", "buttons");

svg.select("g.buttons")
    .append("rect")
    .attr("class", "divisor")
    .attr("x", -margin.left)
    .attr("y", -20)
    .attr("width", width + margin.right + margin.left)
    .attr("height", 1)
    .style("fill", "#aaaaaa");

svg.select("g.buttons")
    .append("text")
    .attr("class", "coverage")
    .attr("x", width / 2 - 75)
    .attr("y", -30)
    .style("fill", "#455A64")
    .style("font-size", "14px")
    .style("font-weight", "bold")
    .style("text-rendering", "geometricPrecision")
    .on("click", showCoverage)
    .text("COVERAGE");

svg.select("g.buttons")
    .append("rect")
    .attr("class", "underline")
    .attr("x", width / 2 - 80)
    .attr("y", -23)
    .attr("width", 81)
    .attr("height", 3)
    .style("fill", "#455A64")

svg.select("g.buttons")
    .append("text")
    .attr("class", "reads")
    .attr("x", width / 2 + 15)
    .attr("y", -30)
    .style("fill", "#b2b0b0")
    .style("font-size", "14px")
    .style("font-weight", "bold")
    .style("text-rendering", "geometricPrecision")
    .on("click", showReads)
    .text("JUNCTION READS");

// svg.select("g.buttons")
//     .append("text")
//     .attr("class", "scatter")
//     .attr("x", width / 2 + 205)
//     .attr("y", -30)
//     .style("fill", "#455A64")
//     .style("font-size", "14px")
//     .style("font-weight", "bold")
//     .style("text-rendering", "geometricPrecision")
//     .on("click", function OpenInNewTab() {
//         var win = window.open('parameters.html' + '?area=' + area + '&patientFolder=' + patientFolder + '&type=' + type, '_blank');
//         win.focus();
//     })
//     .text("PARAMETERS");

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
    .attr("height", plotHeight)
    .style("fill", "none")
    .style("stroke", "black")
    .style("stroke-width", 1);



svg.select("g.guide")
    .append("line")
    .attr("class", "possible_line")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "blue") // colour the line
    .attr("x1", x(Zero_estimate)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(Zero_estimate)) // x position of the second end of the line
    .attr("y2", plotHeight); // y position of the second end of the line

svg.select("g.guide")
    .append("line")
    .attr("class", "zero_line")
    .attr("clip-path", "url(#clip)")
    .style("stroke", "blue") // colour the line
    .attr("x1", x(0)) // x position of the first end of the line
    .attr("y1", 0) // y position of the first end of the line
    .attr("x2", x(0)) // x position of the second end of the line
    .attr("y2", plotHeight); // y position of the second end of the line

svg.select("g.guide")
    .append("rect")
    .attr("class", "junction")
    .attr("clip-path", "url(#clip)")
    .attr("x", x(0))
    .attr("y", 0)
    .attr("width", 0)
    .attr("height", plotHeight);

var readsOn = false;
var trans = [];
var scale = 0;

function showReads() {
    if (readsOn == false) {
        mouseleave();
        mouseleaveEnzyme();
        svg.select("g.buttons").select("text.coverage")
            .style("fill", "#b2b0b0")

        svg.select("g.buttons").select("text.reads")
            .style("fill", "#455A64")

        svg.select("g.buttons").select("rect.underline")
            .attr("x", width / 2 + 10)
            .attr("width", 125);

        svg.select("g.sequence_g").selectAll("rect").remove();
        svg.select("g.sequence_l").selectAll("rect").remove();
        svg.select("g.rekt").selectAll("rect").remove();
        svg.selectAll("g.layer_g").selectAll("rect").remove();
        svg.selectAll("g.layer_l").selectAll("rect").remove();
        svg.selectAll("g.enzyme_cs").selectAll("line").remove();

        svg.select("g.spacer").attr("visibility", "hidden");
        svg.selectAll("text.axis-label").attr("visibility", "hidden");

        svg.select('g.y1.axis').attr("visibility", "hidden");
        //            .call(yAxis[0]);
        svg.select('g.y2.axis').attr("visibility", "hidden");
        //            .call(yAxis[1]);
        svg.select('g.y3.axis').attr("visibility", "hidden");
        //            .call(yAxis[2]);
        svg.select('g.y4.axis').attr("visibility", "hidden");
        //            .call(yAxis[3]);

        svg.select('g.seqY.axis').attr("visibility", "visible");

        svg.select(".x.axis").call(xAxis);
        trans = zoom.translate();
        scale = zoom.scale();
        dom = x.domain();
        var numLetters = width / 14;
        x.domain([-numLetters / 2 + datas['stats']['ClipS'], numLetters / 2 + datas['stats']['ClipS']]);
        var numReads = plotHeight / (x(1) - x(0)) * 1;
        seqY.domain([0, numReads]);

        zoom
            .x(x)
            .y(seqY)
            .scaleExtent([1, 1]);
        zoom.on("zoom", zoomReads);
        zoomReads();
        readsOn = true;
    }
}


function showCoverage() {
    if (readsOn == true) {
        svg.select("g.buttons").select("text.coverage")
            .style("fill", "#455A64")

        svg.select("g.buttons").select("text.reads")
            .style("fill", "#b2b0b0")

        svg.select("g.buttons").select("rect.underline")
            .attr("x", width / 2 - 80)
            .attr("width", 81);

        svg.select('g.each_seq').selectAll('g.jl_seq').remove();
        svg.select('g.each_seq').selectAll('g.jg_seq').remove();

        svg.select("g.spacer").attr("visibility", "visible");
        svg.selectAll("text.axis-label").attr("visibility", "visible");



        svg.select('g.y1.axis').attr("visibility", "visible");
        //            .call(yAxis[0]);
        svg.select('g.y2.axis').attr("visibility", "visible");
        //            .call(yAxis[1]);
        svg.select('g.y3.axis').attr("visibility", "visible");
        //            .call(yAxis[2]);
        svg.select('g.y4.axis').attr("visibility", "visible");
        //            .call(yAxis[3]);

        svg.select('g.seqY.axis').attr("visibility", "hidden");
        readsOn = false;
        x.domain(maxdom);
        dom_dist = (maxdom[1] - maxdom[0]);
        zoom
            .x(x)
            .scaleExtent([1, dom_dist / 100]);
        zoom.translate(trans);
        zoom.scale(scale);
        zoom.on("zoom", zoomed);
        zoomed();
        //        redraw(datas);
    }
}
