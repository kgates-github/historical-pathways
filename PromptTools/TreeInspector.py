#!/usr/bin/env python3

from string import Template
import IPython.display as dp
import IPython



s = Template(
    r"""
 <style>
    /* CSS */
    .link {
      fill: none;
      stroke: #444; 
      stroke-width: 1; 
    }

    .node circle {
      fill: #ccc; 
    }

    .node text {
      font: 14px sans-serif; 
      cursor:  pointer;
      fill: #ccc;
    }

    html, body {
      font: 14px sans-serif; 
      height: 100%;
      margin: 0;
      padding: 0;
      color: #ccc   
    }
</style>

<body style="background:"yellow">

<label for="mySelect">Select a topic:</label>
<select id="mySelect"></select>


<label for="themeSelect">Select a Theme:</label>
<select id="themeSelect">
    <!-- Options will be dynamically added based on themes -->
</select>
<label for="heightSelect">Height:</label>
<select id="heightSelect">
  <option value="600"></option>
  <option value="600">600</option>
  <option value="800">800</option>
  <option value="1000">1000</option>
  <option value="1200">1200</option>
  <option value="1400">1400</option>
  <option value="1600">1600</option>
  <option value="1800">1800</option>
</select>
<label for="widthSelect">Width:</label>
<select id="widthSelect">
  <option value="600"></option>
  <option value="600">600</option>
  <option value="800">800</option>
  <option value="1000">1000</option>
  <option value="1200">1200</option>
  <option value="1400">1400</option>
  <option value="1600">1600</option>
  <option value="1800">1800</option>
</select>

<div>Click on node to inspect</div>
<div style="display:flex; flex-direction: row; background:none;">
    <div id="$id" style="flex:1;"></div>
    <div>
        <button id="clear-button">Clear</button>
        <div id="text-container" style="overflow: auto; font-size: 14px; line-height: 1.3; height:100%; width:300px; border: 1px solid #999; color:#333; padding:20px;"></div>
    </div>
</div>

</body>
<script type="module">
  'use strict';
  
  import * as d3 from 'https://cdn.skypack.dev/d3';

  (async () => {
    
    const data = $data;
    let themes = {};
    let selectedTheme = null;
    let selectedData = data[0];
    let height = 1000;
    let width = 1000;

    // Ref for selects
    const heightSelect = document.getElementById("heightSelect");
    const widthSelect = document.getElementById("widthSelect");

    function recurse(node) {
        for (const theme of node["themes"]) {
            if (themes.hasOwnProperty(theme)) {
                themes[theme] += 1;
            } else {
                themes[theme] = 1;
            }
        }

        for (const child of node["children"]) {
            recurse(child);
        }
    }

    function updateThemeSelect(newData) {
      themes = {};
      recurse(newData);

      //alert(Object.keys(themes)[0]);

      const sortedThemes = Object.fromEntries(
        Object.entries(themes).sort((a, b) => b[1] - a[1]));

      // Populate the select menu with theme options
      const themeSelect = document.getElementById("themeSelect");

      for (var i = themeSelect.options.length - 1; i >= 0; i--) {
        themeSelect.remove(i);
      }

      for (const key in sortedThemes) {
          if (sortedThemes.hasOwnProperty(key)) {
              const option = document.createElement("option");
              option.value = key;
              option.textContent = key + ' ' + sortedThemes[key];
              themeSelect.appendChild(option);
          }
      }
    }

    // Function to update the selection
    function updateThemeSelection(event) {
      selectedTheme = event.target.value;
      updateTree(selectedData)
    }


    const clearButton = d3.select('#clear-button');

    clearButton.on('click', function() {
      d3.select('#text-container').html("");
    });
   
    

    // Get a reference to the select element
    const selectElement = document.getElementById("mySelect");

    data.forEach(item => {
      const option = document.createElement("option");
      option.value = item.id; 
      option.text = item.name; 
      selectElement.appendChild(option); 
    });


    // Function to handle the select change
    function handleSelectChange(event) {
      
      for (let i = 0; i < data.length; i++) {
        if (data[i].id == event.target.value) {
          selectedData = data[i];
          break;
        }
      }

      //updateThemeSelect(selectedData);
      updateTree(selectedData);
    }

    function updateDimensions(event) {
      if (event.target.id == "heightSelect") {
        height = event.target.value;
      } else {
        width = event.target.value;
      }
      
      d3.select('#$id')
        .attr('height', height)
        .attr('width', width)
      updateTree(selectedData);
    }

    
    updateThemeSelect(data[0])
    updateTree(data[0]);


    function updateTree(data) {
      
      // Clear the existing tree container
      d3.select('#$id').selectAll("*").remove();

      const margin = { top: 40, right: 40, bottom: 40, left: 40 };
      let [w, h] = [width, height];

      const treeLayout = d3.tree().size([h-160, w-600]);

      // Append an SVG element to the body
      const svg = d3.select('#$id').append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', 'translate(50,50)');

      // Create a hierarchical tree
      let root = d3.hierarchy(data);
      let tree = treeLayout(root);

      // Add links
      svg.selectAll('path.link')
        .data(tree.links())
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', d3.linkHorizontal()
          .x(d => d.y)
          .y(d => d.x));

      // Add nodes
      svg.selectAll('g.node')
        .data(tree.descendants())
        .enter().append('g')
        .attr('class', 'node')
        .attr('transform', d => 'translate('+d.y+','+d.x+')')
        .append('circle')
        .attr('r', 3);

      svg.selectAll('g.node')
        .append('rect')
        .attr('x', 0)
        .attr('y', 10)
        .attr('width', 200)
        .attr('height', 4)
        .attr('opacity', d => (d.data.themes && d.data.themes.indexOf(selectedTheme) !== -1) ? '1': '0')
        .attr('fill', 'red')

      // Add node labels
      svg.selectAll('g.node')
        .append('text')
        .attr('dx', 12)
        .attr('dy', 4)
        .text(d => d.data.name)
        .on("click", function(event, d, i) { 
          const textContainer = d3.select('#text-container');
          textContainer
          .html(
            textContainer.html()
            +"<div style='margin-bottom:16px'>"
            //+"<div>"+d.data.name+"</div>"
            //+"<div>"+d.data.dates[0]+" - "+d.data.dates[1]+"</div>"
            +"<div>"+d.data.summary.replace(/\&p\&/g, "<p>")+"</div>"
            +"</div>"
          )
        })
    }

    function writeToTextContainer(text) {
      const textContainer = d3.select('#text-container');
      textContainer.html(textContainer.html + '<p>' + text)
    }

    // Attach the event listener to the select element
    selectElement.addEventListener("change", handleSelectChange);
    themeSelect.addEventListener("change", updateThemeSelection);
    
    heightSelect.addEventListener("change", updateDimensions);
    widthSelect.addEventListener("change", updateDimensions);



   
    
  })();
</script>
"""
)

def view_tree(data):
  return dp.HTML(s.safe_substitute({"data": data, "id": "tree-container"}))





