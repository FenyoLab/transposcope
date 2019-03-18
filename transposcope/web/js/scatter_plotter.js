function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
		vars[key] = value.split("#")[0];
	});
	return vars;
}

if (location.search == '') {
	window.location.replace("home.html");
}
console.log(location.search)
var area = getUrlVars()["area"];
var patientFolder = getUrlVars()["patientFolder"];
var type = getUrlVars()["type"];

$(".IDtext").text(area + "-" + type);

var width = 0,
	height = 0,
	plotHeight = 0;
var margin = {
	top: 50,
	right: 30,
	bottom: 40,
	left: 60
},

width = parseInt(d3.select(".plot").style("width"), 10) - margin.left - margin.right,
	height = parseInt(d3.select(".plot").style("height"), 10) - margin.top - margin.bottom - 100,
	plotHeight = height + 60;

var organized = {'negative':[], 'positive':[], 'unlabled':[]};

var colorV = d3.scale.linear()
	.domain([0, 20])
	.range(["#0e0e24", "#2194c7"]);

var colorA = d3.scale.linear()
	.domain([0, 1])
	.range(["red", "chartreuse"]);

var rad = d3.scale.linear()
	.domain([0, 12])
	.range([1, 5]);

var legScale = d3.scale.linear().range([10, 100]).domain([0,20]);

// setup x
var xValue = function(d) { return d[mapping[config["x"]]]}, // data -> value
	xScale0 = d3.scale.linear().range([0, width/3 - 5]), // value -> display
	xMap0 = function(d) { return xScale0(xValue(d));}, // data -> display
	xAxis0 = d3.svg.axis().scale(xScale0).orient("bottom").tickSize(-height),

	xScale1 = d3.scale.linear().range([width/3 + 5, 2*width/3 - 5]), // value -> display
	xMap1 = function(d) { return xScale1(xValue(d));}, // data -> display
	xAxis1 = d3.svg.axis().scale(xScale1).orient("bottom").tickSize(-height),

	xScale2 = d3.scale.linear().range([2*width/3 + 5, 3*width/3]), // value -> display
	xMap2 = function(d) { return xScale2(xValue(d));}, // data -> display
	xAxis2 = d3.svg.axis().scale(xScale2).orient("bottom").tickSize(-height);

// setup y
var yValue = function(d) { return d[mapping[config["y"]]];}, // data -> value
	yScale = d3.scale.linear().range([height, 0]), // value -> display
	yMap = function(d) { return yScale(yValue(d));}, // data -> display
	yAxis = d3.svg.axis().scale(yScale).orient("left").tickSize(-width);

var svg = d3.select("#chart").append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom + 120)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
	.style("background_color", "#a9b7cb");

// add the tooltip area to the webpage
	var tooltip = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);

	var mapping = {"TagetRDs": "H8_TargRDs", "TargBPs": "H9_TargBPs", "TargMis":"H10_TargMis", "TargInd":"H11_TargInd", "Targ_Clip":"H12_TargClip", 
		"Width": "H23_W","Depth": "H24_D", "PolyA": "H26_PolyAT", "Junction Reads": "H27_SC", "VariantIdx": "H25_VaritIdx", "Probability": "H31_pred", 
		"Uniq": "H28_Uniq", "Prop": "H29_Prop"};
	var config = {x: "Width", y: "Depth", outline: "PolyA", size: "Junction Reads", fill: "VariantIdx"};

	//function findMinMax(set, parameter) {
	//    return []
	//}

	function setParameters(arr) {
		console.log(arr);
		config = arr;
		draw([0, 16], [4,15], [0,1], [0,20], [0,12], [0,1]);
	};

	function limit(Depth, Width, Poly, Var, JuncR, Prob) {
		'use strict';
		return function (d) {
			if (Depth[0] <= d.H24_D && d.H24_D <= Depth[1] &&
			    Width[0] <= d.H23_W && d.H23_W <= Width[1] &&
			    Poly[0] <= d.H26_PolyAT && d.H26_PolyAT <= Poly[1] &&
			    Var[0] <= d.H25_VaritIdx && d.H25_VaritIdx <= Var[1] &&
			    JuncR[0] <= d.H27_SC && d.H27_SC <= JuncR[1] &&
			    Prob[0] <= d.H31_pred && d.H31_pred <= Prob[1])
			return d;
		};
	};

	function draw(D, W, P, V, JR, Prob) {
		//    svg.select("g.pos").selectAll(".dot").remove();
		//    svg.select("g.neg").selectAll(".dot").remove();
		//    svg.select("g.unl").selectAll(".dot").remove();
		var filtered = {'unlabled': jQuery.grep(organized.unlabled, limit(D, W, P, V, JR, Prob)),
			'positive': jQuery.grep(organized.positive, limit(D, W, P, V, JR, Prob)),
		'negative': jQuery.grep(organized.negative, limit(D, W, P, V, JR, Prob))}
		var nl = filtered.negative.length,
			pl = filtered.positive.length,
			ul = filtered.unlabled.length;
		var minmax = [Math.min(((nl > 0) ? d3.min(filtered.negative, xValue) : 9999), ((pl > 0) ? d3.min(filtered.positive, xValue) : 9999), ((ul > 0) ? d3.min(filtered.unlabled, xValue) : 9999)),
			Math.max(((nl > 0) ? d3.max(filtered.negative, xValue) : 0), ((pl > 0) ? d3.max(filtered.positive, xValue) : 0), ((ul > 0) ? d3.max(filtered.unlabled, xValue) : 0))];
		//    console.log(minmax);
		xScale0.domain(minmax);
		xScale1.domain(minmax);
		xScale2.domain(minmax);
		yScale.domain([Math.min(((nl > 0) ? d3.min(filtered.negative, yValue) : 9999), ((pl > 0) ? d3.min(filtered.positive, yValue) : 9999), ((ul > 0) ? d3.min(filtered.unlabled, yValue) : 9999)),
			      Math.max(((nl > 0) ? d3.max(filtered.negative, yValue) : 0), ((pl > 0) ? d3.max(filtered.positive, yValue) : 0), ((ul > 0) ? d3.max(filtered.unlabled, yValue) : 0))]);

			      svg.select("g.labels").select("text.count.N").text("Negative : " + nl);
			      svg.select("g.labels").select("text.count.P").text("Positive : " + pl);
			      svg.select("g.labels").select("text.count.U").text("Unlabled : " + ul);
			      var neg = svg.select("g.neg").selectAll(".dot")
				      .data(filtered.negative);
			      //      .data(organized.negative.filter(limit(D, W, P, V, JR, Prob)));
				      neg.exit().remove();
				      neg.enter().append("circle")
					      .attr("class", "dot")
					      .attr("r", function(d) { return rad(d.H27_SC);})
					      .attr("cx", xMap0)
					      .attr("cy", yMap)
					      .style("fill", function(d) { return colorV(d.H25_VaritIdx);})
					      .style("stroke", function(d) { return colorA(d.H26_PolyAT);})
					      .style("stroke-width", 0.5)
					      .on("mouseover", function(d) {
						      tooltip.transition()
							      .duration(200)
							      .style("opacity", .9);
						      tooltip.html(d.H1_ClipChr + ":" +d.H2_ClipS + "<br/>" +
								   "Depth : " + +d.H24_D.toFixed(3) + "<br/>" +
								   "Width : " + +d.H23_W.toFixed(3) + "<br/>" +
								   "PolyAT : " + +d.H26_PolyAT.toFixed(3) + "<br/>" +
								   "VariantIdx : " + +d.H25_VaritIdx.toFixed(3) + "<br/>" +
								   "Junction Reads : " + +d.H27_SC.toFixed(3) + "<br/>" +
								   "P : " + +d.H31_pred.toFixed(3) + "<br/>")
						      .style("left", (d3.event.pageX + 5) + "px")
						      .style("top", (d3.event.pageY - 28) + "px");
					      })
					      .on("mouseout", function(d) {
						      tooltip.transition()
							      .duration(500)
							      .style("opacity", 0);
					      });

					      neg.attr("r", function(d) { return rad(d.H27_SC);})
						      .attr("cx", xMap0)
						      .attr("cy", yMap)
						      .style("fill", function(d) { return colorV(d.H25_VaritIdx);})
						      .style("stroke", function(d) { return colorA(d.H26_PolyAT);});


					      var pos = svg.select("g.pos").selectAll(".dot")
						      .data(filtered.positive);
					      pos.exit().remove();

					      pos.enter().append("circle")
						      .attr("class", "dot")
						      .attr("r", function(d) { return rad(d.H27_SC);})
						      .attr("cx", xMap1)
						      .attr("cy", yMap)
						      .style("fill", function(d) { return colorV(d.H25_VaritIdx);})
						      .style("stroke", function(d) { return colorA(d.H26_PolyAT);})
						      .style("stroke-width", 0.5)
						      .on("mouseover", function(d) {
							      tooltip.transition()
								      .duration(200)
								      .style("opacity", .9);
							      tooltip.html(d.H1_ClipChr + ":" +d.H2_ClipS + "<br/>" +
									   "Depth : " + +d.H24_D.toFixed(3) + "<br/>" +
									   "Width : " + +d.H23_W.toFixed(3) + "<br/>" +
									   "PolyAT : " + +d.H26_PolyAT.toFixed(3) + "<br/>" +
									   "VariantIdx : " + +d.H25_VaritIdx.toFixed(3) + "<br/>" +
									   "Junction Reads : " + +d.H27_SC.toFixed(3) + "<br/>" +
									   "P : " + +d.H31_pred.toFixed(3) + "<br/>")
							      .style("left", (d3.event.pageX + 5) + "px")
							      .style("top", (d3.event.pageY - 28) + "px");
						      })
						      .on("mouseout", function(d) {
							      tooltip.transition()
								      .duration(500)
								      .style("opacity", 0);
						      })

						      pos.attr("r", function(d) { return rad(d.H27_SC);})
							      .attr("cx", xMap1)
							      .attr("cy", yMap)
							      .style("fill", function(d) { return colorV(d.H25_VaritIdx);})
							      .style("stroke", function(d) { return colorA(d.H26_PolyAT);});

						      var unl = svg.select("g.unl").selectAll(".dot")
							      .data(filtered.unlabled);

						      unl.exit().remove();
						      unl.enter().append("circle")
							      .attr("class", "dot")
							      .attr("r", function(d) { return rad(d.H27_SC);})
							      .attr("cx", xMap2)
							      .attr("cy", yMap)
							      .style("fill", function(d) { return colorV(d.H25_VaritIdx);})
							      .style("stroke", function(d) { return colorA(d.H26_PolyAT);})
							      .style("stroke-width", 0.5)
							      .on("mouseover", function(d) {
								      tooltip.transition()
									      .duration(200)
									      .style("opacity", .9);
								      tooltip.html(d.H1_ClipChr + ":" +d.H2_ClipS + "<br/>" +
										   "Depth : " + +d.H24_D.toFixed(3) + "<br/>" +
										   "Width : " + +d.H23_W.toFixed(3) + "<br/>" +
										   "PolyAT : " + +d.H26_PolyAT.toFixed(3) + "<br/>" +
										   "VariantIdx : " + +d.H25_VaritIdx.toFixed(3) + "<br/>" +
										   "Junction Reads : " + +d.H27_SC.toFixed(3) + "<br/>" +
										   "P : " + +d.H31_pred.toFixed(3) + "<br/>")
								      .style("left", (d3.event.pageX + 5) + "px")
								      .style("top", (d3.event.pageY - 28) + "px");
							      })
							      .on("mouseout", function(d) {
								      tooltip.transition()
									      .duration(500)
									      .style("opacity", 0);
							      })

							      unl.attr("r", function(d) { return rad(d.H27_SC);})
								      .attr("cx", xMap2)
								      .attr("cy", yMap)
								      .style("fill", function(d) { return colorV(d.H25_VaritIdx);})
								      .style("stroke", function(d) { return colorA(d.H26_PolyAT);});


							      svg.select("g.x.axis.N").call(xAxis0);
							      svg.select("g.x.axis.P").call(xAxis1);
							      svg.select("g.x.axis.U").call(xAxis2);
							      svg.select("g.y.axis").call(yAxis);

							      svg.select("g.x.axis.N").select("text.label.x").text(config.x);
							      svg.select("g.y.axis").select("text.label.y").text(config.y);
	};

	d3.tsv("csv/" + area + "/" + patientFolder + "/" + type + "/" + type + ".repred", function(error, data) {

		//   change string (from CSV) into number format

		data.forEach(function(obj) {
			var row = {'H1_ClipChr': obj.H1_ClipChr, 'H2_ClipS': obj.H2_ClipS,
				'H8_TargRDs': obj.H8_TargRDs,	'H9_TargBPs': obj.H9_TargBPs,
				'H10_TargMis': obj.H10_TargMis,	'H11_TargInd': obj.H11_TargInd,
				'H12_TargClip': obj.H12_TargClip,
				'H23_W': +obj.H23_W, 'H24_D': +obj.H24_D,
				'H27_SC': +obj.H27_SC, 'H25_VaritIdx': +obj.H25_VaritIdx,
				'H26_PolyAT': +obj.H26_PolyAT, 'H31_pred': +obj.H31_pred,
				'H28_Uniq': +obj.H28_Uniq, 'H29_Prop': +obj.H29_Prop};
			if (+obj.H30_label === 0)
				organized.negative.push(row);
			if (+obj.H30_label === 0.5)
				organized.unlabled.push(row);
			if (+obj.H30_label === 1)
				organized.positive.push(row);
			obj.H23_W = +obj.H23_W;
			obj.H24_D = +obj.H24_D;
		});
		// don't want dots overlapping axis, so add in buffer to data domain
		xScale0.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
		xScale1.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
		xScale2.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
		yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);
		//  data = null;

		// x-axis
		svg.append("g")
			.attr("class", "x axis N")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis0)
			.append("text")
			.attr("class", "label x")
			.attr("x", width)
			.attr("y", -6)
			.style("text-anchor", "end")
			.text("Width");

		svg.append("g")
			.attr("class", "x axis P")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis1);

		svg.append("g")
			.attr("class", "x axis U")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis2);

		svg.append("g")
			.attr("class", "legend");

		svg.append("g")
			.attr("class", "labels");

		svg.select("g.legend")
			.append("rect")
			.attr("class", "stroke-color")
			.attr("x", width/6 )
			.attr("y", height)
			.attr("width", 5)
			.attr("height", 5)
			.style("fill", "black");

		svg.select("g.labels")
			.append("text")
			.attr("class", "count N")
			.attr("x", width/6)
			.attr("y", -5)
			.style("text-anchor", "end")
			.text("Negative:0");

		svg.select("g.labels")
			.append("text")
			.attr("class", "count P")
			.attr("x", 3*width/6)
			.attr("y", -5)
			.style("text-anchor", "end")
			.text("Positive:0");

		svg.select("g.labels")
			.append("text")
			.attr("class", "count U")
			.attr("x", 5*width/6)
			.attr("y", -5)
			.style("text-anchor", "end")
			.text("Unlabled:0");

		// y-axis
			svg.append("g")
				.attr("class", "y axis")
				.call(yAxis)
				.append("text")
				.attr("class", "label y")
				.attr("transform", "rotate(-90)")
				.attr("y", 6)
				.attr("dy", ".71em")
				.style("text-anchor", "end")
				.text("Depth");

			svg.append("g")
				.attr("class", "neg")

			svg.append("g")
				.attr("class", "pos")

			svg.append("g")
				.attr("class", "unl")
			//var inc = []
				//svg.append("g")
				//    .attr("class", "varLeg")
				//    .append()

				// draw dots
				// draw legend

				setParameters(config);
	});
