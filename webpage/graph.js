// adapted from http://bl.ocks.org/mbostock/1153292

// create graph of given list file in div with that id
function create_graph(list) {
  var width = 400,
      height = 350;

  var svg = d3.select("#" + list + " .network-graph").append("svg")
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

  d3.json(list + ".json", function(error, data) {
    var graph_data = data;
    var graph_nodes = {};
    var graph_links = [];

    // loop through keys in graph_data
    for (var source in graph_data) {
      for (var target in graph_data[source]) {
        if (target != source) {
          var link = {};
          link.source = graph_nodes[source] || (graph_nodes[source] = {name: source, totalDegree: 0});
          link.target = graph_nodes[target] || (graph_nodes[target] = {name: target, totalDegree: 0});
          link.time = graph_data[source][target];

          graph_nodes[source].totalDegree += link.time;
          graph_nodes[target].totalDegree += link.time;

          graph_links.push(link);
        }
      }
    }

    var time_extent = d3.extent(graph_links, function(d) {
      return d.time;
    });

    total_time_extent = d3.extent(d3.values(graph_nodes), function(d) {
      return d.totalDegree;
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

    var force = d3.layout.force()
        .nodes(d3.values(graph_nodes))
        .links(graph_links)
        .size([width, height])
        .linkDistance(function(d) {
          return edgeWeight(d.time)
        })
        .charge(-300)
        .gravity(0.4)
        .on("tick", function(d) {
            path.attr("d", linkArc);
            circle.attr("transform", transform);
            text.attr("transform", transform);
        })
        .start();

    var path = svg.append("g").selectAll("path")
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

    var circle = svg.append("g").selectAll("circle")
        .data(force.nodes())
      .enter().append("circle")
        .attr("class", function(d) {
          return fixEmail(d.name);
        })
        .attr("r", function(d) {
          return radiusScale(d.totalDegree);
        })
        .call(force.drag);

    var text = svg.append("g").selectAll("text")
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
    svg.selectAll("circle")
        .on("mouseover", function(d) {
          // get email of this user
          var email = d3.select(this).attr("class");
          // set corresponding text visible
          svg.select("text." + email).style("visibility", "visible");
          // set all paths going into or out of this user to max opacity and color
          svg.selectAll("path." + email).style("opacity", 1);
          svg.selectAll("path." + email).style("stroke", "red");

        })
        .on("mouseout", function(d) {
          var email = d3.select(this).attr("class");
          svg.select("text." + email).style("visibility", "hidden");
          svg.selectAll("path." + email).style("opacity", function(d) {
            return opacityScale(d.time);
          });
          svg.selectAll("path." + email).style("stroke", function(d) {
            return colorScale(d.time);
          });
        });

    // select Willy and make him red
    if (willy = svg.select("circle.wxiao-college-harvard-edu")) {
      willy.style("fill", "red");
    }

    // select Robbie and make him blue
    if (robbie = svg.select("circle.rkgibson2-gmail-com")) {
      robbie.style("fill", "blue");
    }

    // select Robbie and make him blue
    if (robbie = svg.select("circle.huihuifan-college-harvard-edu")) {
      robbie.style("fill", "green");
    }

    // find node with max degree, and color it purple
    maxDegree = d3.values(graph_nodes).reduce(function(prevElt, currElt) {
      return (!prevElt || currElt.totalDegree > prevElt.totalDegree) ? currElt : prevElt;
    }, null);
    if (maxNode = svg.select("circle." + fixEmail(maxDegree.name))) {
      maxNode.style("fill", "purple");
    }
  });
}

// Use elliptical arc path segments to doubly-encode directionality.
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

create_graph("scas-board-2013");
create_graph("scas-board-2014");
create_graph("premed-exec-2013");
create_graph("premed-exec-2014");