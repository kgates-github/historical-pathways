import '../App.css';
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from "d3";

function GanntChart(props) {
    const svgRef = useRef(null);
    const leftColumnWidth = 600;
    const marginLeft = 500;
    const [width, setWidth] = useState(window.innerWidth - leftColumnWidth);
    
    const handleResize = () => {
        setWidth(window.innerWidth - leftColumnWidth);
    };

    useEffect(() => {
        setWidth(window.innerWidth - leftColumnWidth);
        // Add event listener for window resize
        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    const updateChart = () => {
        const svg = d3.select(svgRef.current);
        const height = 1000;

        svg.attr("width", width)
            .attr("height", height);

        const formatData = () => {
            const formattedData = [];
            for (let i = 0; i < props.iterationData.iterations.length; i++) {
                const iteration = props.iterationData.iterations[i];
                const iterationNum = iteration.iteration;

                const formattedIteration = {
                    name: iteration.name,
                    start: new Date(iteration.content.dates.start),
                    end: new Date(iteration.content.dates.end),
                    type: "iteration",
                    iteration: iterationNum,
                };
                formattedData.push(formattedIteration);
                
                for (let j = 0; j < iteration.content.sections.length; j++) {
                    const section = iteration.content.sections[j];
                    
                    console.log(section)

                    const formattedSection = {
                        name: section.name,
                        start: new Date(section.dates.start),
                        end: new Date(section.dates.end),
                        type: "section",
                        iteration: iterationNum,
                    };
                    formattedData.push(formattedSection);
                }
            }
            return formattedData;
        };
        
        const data = formatData();
        const dataLabel = data.filter((d) => d.type == "iteration");
        
        // Convert the date strings to Date objects
        data.forEach((d) => {
            d.start = new Date(d.start);
            d.end = new Date(d.end);
        });

        // Define the x-scale for the Gantt chart
        const xScale = d3.scaleTime()
            .domain([d3.min(data, (d) => d.start), d3.max(data, (d) => d.end)])
            .range([marginLeft, width - 20]);

        // Define the y-scale for the Gantt chart
        const yScale = d3.scaleBand()
            .domain(data.map((d) => d.name))
            .range([50, height])
            .padding(0.1);

        // Draw the Gantt chart bars
        svg.selectAll(".bar")
            .data(data)
            .join("rect")
            .attr("class", "bar")
            .attr("x", (d) => xScale(d.start))
            .attr("y", (d) => yScale(d.name) - 1)
            .attr("width", (d) => xScale(d.end) - xScale(d.start) + 5)
            .attr("height", "4px") //yScale.bandwidth())
            .attr("fill", (d) => (d.iteration == props.curIteration) ? "#0A7CE5" : "#555")
            .exit().remove();

        // Add labels to the Gantt chart bars
        svg.selectAll(".label")
            .data(data)
            .join("text")
            .attr("class", "label")
            .attr("x", (d) => xScale(d.start) - 16)
            .attr("y", (d) => yScale(d.name) + yScale.bandwidth() / 2)
            .attr("dy", "-8px")
            .attr("text-anchor", "end") 
            .text((d) => d.name)
            .attr("fill", (d) => (d.type == "iteration") ? "#fff" : "#999")
            .exit().remove();

        const getWidth = (text) => {
            const textElement = svg.append('text')
                .text(text);
            const width = textElement.node().getBBox().width;
            textElement.remove(); // Remove the text element from the DOM
            return width + 38;
        }
        
        svg.selectAll(".node")
            .data(dataLabel)
            .join("circle")
            .attr('class', 'node')
            .attr("cx", (d) => xScale(d.start) - getWidth(d.name))
            .attr("cy", (d) => yScale(d.name) + yScale.bandwidth() / 2 - 13)
            .attr("opacity", d => (d.visited) ? 1 : 1)
            .attr("r", 13)
            .style("fill", d =>  (d["iteration"] == props.curIteration) ? "#0A7CE5" : "#444")
        
        svg.selectAll(".text-num")
            .data(dataLabel)
            .join("text")
            .attr('class', 'text-num')
            .attr("x", (d) => xScale(d.start) - getWidth(d.name))
            .attr("y", (d) => yScale(d.name) + yScale.bandwidth() / 2 - 7)
            .style("font-size", "18px")
            .style("font-family", "sans-serif")
            .style("font-weight", "bold")
            .style("fill", "#fff")
            .style('text-anchor', 'middle')
            .text(d => d.iteration)
            .exit().remove();
    };

    useEffect(() => {
        updateChart();
    }, [props.iterationData, width, props.curIteration]);

    return (
        <div style={{backgroundColor: "none", flexGrow: "1", flex: "1", marginTop:"20px"}} >
            <svg ref={svgRef}></svg>
        </div>
    );
}
     
export default GanntChart;
