// adapted from http://bl.ocks.org/mbostock/1153292

var graph_data;
var graph_nodes = {};
var graph_links = [];
var emails;

var width = 1100,
    height = 800;

var force, path, circle, text;

var svg = d3.select("#network-graph").append("svg")
    .attr("width", width)
    .attr("height", height);

// Per-type markers, as they don't inherit styles.
svg.append("defs")
  .append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
  .append("path")
    .attr("d", "M0,-5L10,0L0,5");

d3.json("scas_list_graph.json", function(error, data) {
  graph_data = data;

  // loop through keys in graph_data
  for (var source in graph_data) {
    for (var target in graph_data[source]) {
      var link = {};
      link.source = graph_nodes[source] || (graph_nodes[source] = {name: source});
      link.target = graph_nodes[target] || (graph_nodes[target] = {name: target});
      link.time = graph_data[source][target];

      graph_links.push(link);
    }
  }

  force = d3.layout.force()
      .nodes(d3.values(graph_nodes))
      .links(graph_links)
      .size([width, height])
      .linkDistance(60)
      .charge(-300)
      .gravity(0.4)
      .on("tick", tick)
      .start();

  path = svg.append("g").selectAll("path")
      .data(force.links())
    .enter().append("path")
      .attr("class", function(d) { 
        if (d.target.name == d.source.name) {
          return "link selfloop";
        } else {
          return "link";
        }
      })
      .attr("marker-end", function(d) {
        if (d.target.name == d.source.name) {
          return null;
        } else {
          return "url(#arrow)"; 
        }
      });

  circle = svg.append("g").selectAll("circle")
      .data(force.nodes())
    .enter().append("circle")
      .attr("class", function(d) {
        return fixEmail(d.name);
      })
      .attr("r", 6)
      .call(force.drag);

  text = svg.append("g").selectAll("text")
      .data(force.nodes())
    .enter().append("text")
      .attr("class", function(d) {
        return fixEmail(d.name);
      })
      .style("visibility", "hidden")
      .attr("x", 8)
      .attr("y", ".31em")
      .text(function(d) { return d.name; });

  // add mouseover handler so emails only appear on mouseover
  d3.selectAll("circle")
      .on("mouseover", function(d) {
        var email = d3.select(this).attr("class");
        console.log(email)
        d3.select("text." + email).style("visibility", "visible");
      })
      .on("mouseout", function(d) {
        var email = d3.select(this).attr("class");
        d3.select("text." + email).style("visibility", "hidden");
      })
  });

// Use elliptical arc path segments to doubly-encode directionality.
function tick() {
  path.attr("d", linkArc);
  circle.attr("transform", transform);
  text.attr("transform", transform);
}

function linkArc(d) {
  // console.log(d);
  var dx = d.target.x - d.source.x,
      dy = d.target.y - d.source.y,
      dr = Math.sqrt(dx * dx + dy * dy);
  if (dr == 0) {
    return "M" + d.source.x + "," + d.source.y + "A" + "10,10 0 1,1 " + d.target.x + "," + (d.target.y - 0.1);
  }
  return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
}

function transform(d) {
  return "translate(" + d.x + "," + d.y + ")";
}

// function to replace @ signs in emails with hyphens for CSS class names
function fixEmail(email) {
  return email.replace(/[@\.]/g, "-");
}