// adapted from http://bl.ocks.org/mbostock/1153292

var graph_data;
var graph_nodes = {};
var graph_links = [];
var emails;

var width = 1100,
    height = 700;

var force, path, circle, text;

var svg = d3.select("#network-graph").append("svg")
    .attr("width", width)
    .attr("height", height);

// marker def for arrowhead
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

d3.json("hrcm-underground.json", function(error, data) {
  graph_data = data;

  // loop through keys in graph_data
  for (var source in graph_data) {
    for (var target in graph_data[source]) {
      if (target != source) {
        var link = {};
        link.source = graph_nodes[source] || (graph_nodes[source] = {name: source, inWeight: 0});
        link.target = graph_nodes[target] || (graph_nodes[target] = {name: target, inWeight: 0});
        link.time = graph_data[source][target];

        graph_nodes[target].inWeight += link.time;

        graph_links.push(link);
      }
    }
  }

  var time_extent = d3.extent(graph_links, function(d) {
    return d.time;
  });

  total_time_extent = d3.extent(d3.values(graph_nodes), function(d) {
    return d.inWeight;
  })

  // link distance scale (edge weight)
  var edgeWeight = d3.scale.linear()
    .domain(time_extent)
    .range([100, 300]);

  // opacity scale based on time val (edge weight)
  var opacityScale = d3.scale.linear()
      .domain(time_extent)
      .range([0.7, 1]);

  // color scale also based on time val (edge weight)
  var colorScale = d3.scale.linear()
      .domain(time_extent)
      .range([d3.rgb(200, 200, 200), d3.rgb(0, 0, 0)]);

  // node radius scale based on total time
  var radiusScale = d3.scale.pow(0.5)
      .domain(total_time_extent)
      .range([6, 12]);

  force = d3.layout.force()
      .nodes(d3.values(graph_nodes))
      .links(graph_links)
      .size([width, height])
      .linkDistance(function(d) {
        return edgeWeight(d.time)
      })
      .charge(-300)
      .gravity(0.4)
      .on("tick", tick)
      .start();

  path = svg.append("g").selectAll("path")
      .data(force.links())
    .enter().append("path")
      .attr("class", function(d) {
        var className = "link"
        if (d.target.name == d.source.name) {
          className += " selfloop " + fixEmail(d.target.name);
        } else {
          className += " " + fixEmail(d.target.name) + " " + fixEmail(d.source.name);
        }

        return className;
      })
      .attr("marker-end", function(d) {
        if (d.target.name == d.source.name) {
          return null;
        } else {
          return "url(#arrow)"; 
        }
      })
      .style("stroke", function(d) {
        return colorScale(d.time);
      })
      .style("opacity", function(d) {
        return opacityScale(d.time);
      });

  circle = svg.append("g").selectAll("circle")
      .data(force.nodes())
    .enter().append("circle")
      .attr("class", function(d) {
        return fixEmail(d.name);
      })
      .attr("r", function(d) {
        return radiusScale(d.inWeight);
      })
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
        // get email of this user
        var email = d3.select(this).attr("class");
        // set corresponding text visible
        d3.select("text." + email).style("visibility", "visible");
        // set all paths going into or out of this user to max opacity and color
        d3.selectAll("path." + email).style("opacity", 1);
        d3.selectAll("path." + email).style("stroke", "red");

      })
      .on("mouseout", function(d) {
        var email = d3.select(this).attr("class");
        d3.select("text." + email).style("visibility", "hidden");
        d3.selectAll("path." + email).style("opacity", function(d) {
          return opacityScale(d.time);
        });
        d3.selectAll("path." + email).style("stroke", function(d) {
          return colorScale(d.time);
        });
      });

  // select Willy and make him red
  if (willy = d3.select("circle.wxiao-college-harvard-edu")) {
    willy.style("fill", "red");
  }
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