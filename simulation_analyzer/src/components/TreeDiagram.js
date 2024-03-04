import '../App.css';
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from "d3";
import { type } from '@testing-library/user-event/dist/type';

function TreeDiagram(props) {
    const svgRef = useRef(null);
    const leftColumnWidth = 440;
    const [width, setWidth] = useState(window.innerWidth - leftColumnWidth);
    
    const getStatusFormating = (type, value, attribute) => {   
        const formatting = props.getStatusFormatting(type, value);
        if (formatting) return (formatting[attribute])
        return "none"; 
    }

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

    const updateTree = () => {
        const svg = d3.select(svgRef.current);
        //const width = 1800;
        const height = 1000;

        svg.attr("width", width)
            .attr("height", height);

        const treeLayout = d3.tree().size([height, width-200]);
        
        function addIterations(raw_data, data) {
            data["children"] = raw_data.filter((iteration) => iteration['parent_id'] == data['id']);
        
            data["children"].forEach((child) => {
                addIterations(raw_data, child);
            });
            
            return data;
        }

        const getStatSummary = (data) => {
            let summary = "Satisfaction: " + data.satisfaction_diff + "    "
            summary += "Fact Check: " + data.fact_eval['choice_string']
            return summary
        }
        
        const raw_data = props.iterationData['raw_data']

        const data = [{
            name: raw_data['persona']['topics'][0] + ' ' + raw_data['persona']['topics'][0],
            id: "root",
            parent_id: null,
            children: [],
        }]
        
        const formattedData = addIterations(raw_data['iterations'], data[0]);

        const root = d3.hierarchy(formattedData);
        const treeData = treeLayout(root);
        const links = treeData.links();
        const cur_id = props.iterationData['iterations'][props.curIteration-1]['id']
        
        const linkPathGenerator = d3.linkHorizontal()
            .x(d => d.y)
            .y(d => d.x);

        svg.selectAll(".link")
            .data(links)
            .join("path")
            .attr('class', 'link')
            .attr("opacity", d => (d.source.data.id == cur_id || d.target.data.visited == 1)  ? 1 : 0.3)
            .attr("d", linkPathGenerator)
            .style("fill", "none")
            .style("stroke", "#777")
            .style("stroke-width", d => d.target.data.visited == 1 ? "1px" : "0.5px")
            .exit().remove();

        const nodes = treeData.descendants();

        svg.selectAll(".text")
            .data(nodes)
            .join("text")
            .attr('class', 'text')
            .attr("x", d => d.y + 0)
            .attr("y", d => d.x + 4)
            .style("font-size", "12px")
            .style("cursor", d => (d.data.visited == 1 || d.data.id == "root") ? "pointer" : "default")
            .style("font-family", "Roboto Mono", "sans-serif")
            .style("font-weight", d => (d.data.visited == 1) ? "bold" : "bold")
            .style("fill", d => (d.data.visited == 1) ? "#fff" : "#fff")
            .attr("opacity", d => (d.data.visited == 1 || d.data.parent_id == cur_id || d.data.id == "root") ? 1 : 0.2)
            .text(d => d.data.name.length > 30 ? d.data.name.substring(0, 30) + '...' : d.data.name)
            .on("click", (event, d) => {
                const it = (!d.data.iteration) ? 1 : d.data.iteration;
                props.setCurIteration(it);
            })
            //.text(d => console.log(d.data))
            //.text(d => d.data.name);  // || d.data.parent_id == d.data["iterations"][props.curIteration-1].id

            svg.selectAll(".text_scores")
            .data(nodes)
            .join("text")
            .attr('class', 'text_scores')
            .attr("x", d => d.y + 0)
            .attr("y", d => d.x - 12)
            .style("font-size", "12px")
            .style("font-family", "Roboto Mono", "sans-serif")
            .style("font-weight", d => (d.data.visited == 1) ? "bold" : "bold")
            .style("fill", d => (d.data.visited == 1) ? "#888" : "#888")
            .attr("opacity", d => (d.data.parent_id == cur_id) ? 1 : 0)
            .text(d => "Int: " + d.data.interest_score + " Rel: " + d.data.relevance_score)
        
        svg.selectAll(".subtext")
            .data(nodes)
            .join("text")
            .attr('class', 'subtext')
            .attr("x", d => d.y + 0)
            .attr("y", d => d.x + 21) 
            .style("font-size", "12px") 
            .style("font-family", "sans-serif")
            .style("fill", "#999")
            .attr("opacity", d => (d.data.id == cur_id || d.data.parent_id == cur_id) ? 1 : 0.2)
            .text(d => (d.data.visited == 1) ? "Satisfaction Diff: " + d.data.satisfaction_diff : '')
            .append("tspan")
            .attr("x", d => d.y + 114)
            .attr("y", d => d.x + 25) 
            .attr("font-family", "Material Icons") 
            .attr("font-size", "20px") 
            .style("fill", d => (d.data.visited == 1) ? getStatusFormating('up-down', d.data.satisfaction_diff, 'color') : "none")
            .text(d => (d.data.visited == 1) ? getStatusFormating('up-down', d.data.satisfaction_diff, 'name') : "")
            .attr("opacity", d => (d.data.id == cur_id || d.data.parent_id == cur_id) ? 1 : 0.2)

        svg.selectAll(".subtext2")
            .data(nodes)
            .join("text")
            .attr('class', 'subtext')
            .attr("x", d => d.y + 0)
            .attr("y", d => d.x + 36) 
            .style("font-size", "12px") 
            .style("font-family", "sans-serif")
            .style("fill", "#999")
            .attr("opacity", d => (d.data.id == cur_id || d.data.parent_id == cur_id) ? 1 : 0.2)
            .text(d => (d.data.visited == 1) ? "Fact Check: " + d.data.fact_eval['choice_string'] : '')
            .append("tspan")
            .attr("x", d => d.y + 114)
            .attr("y", d => d.x + 42) 
            .attr("font-family", "Material Icons") 
            .attr("font-size", "20px") 
            .style("fill", d => (d.data.visited == 1) ? getStatusFormating('health', d.data.fact_eval['choice_string'], 'color') : "none")
            .text(d => (d.data.visited == 1) ? getStatusFormating('health', d.data.fact_eval['choice_string'], 'name') : "")

        
        svg.selectAll(".node")
            .data(nodes)
            .join("circle")
            .attr('class', 'node')
            .attr("cx", d => d.y-28)
            .attr("cy", d => d.x)
            .attr("opacity", d => (d.data.visited) ? 1 : 0)
            .attr("r", 13)
            .style("fill", d =>  (d.data["iteration"] == props.curIteration) ? "#0A7CE5" : "#444")
        
        svg.selectAll(".text-num")
            .data(nodes)
            .join("text")
            .attr('class', 'text-num')
            .attr("x", d => d.y-28)
            .attr("y", d => d.x + 6)
            .attr("opacity", d => d.data.visited == "true" ? 1 : 1)
            .style("font-size", "18px")
            .style("font-family", "sans-serif")
            .style("font-weight", "normal")
            .style("fill", "#fff")
            .style('text-anchor', 'middle')
            .text(d => (d.data.visited) ? d.data.iteration : '')
            .exit().remove();

           
    };

    useEffect(() => {
        updateTree();
    }, [props.iterationData, width, props.curIteration]);

    return (
        <div style={{backgroundColor: "none", flexGrow: "1", flex: "1"}} >
            <svg ref={svgRef}></svg>
        </div>
    );
}
     
export default TreeDiagram;
