import '../App.css';
import React, { useEffect, useRef, useState } from 'react';
import TreeDiagram from './TreeDiagram';
import GanntChart from './GanntChart';
import PromptInspector from './PromptInspector';
import MaterialIcon, {colorPalette} from 'material-icons-react';

function ChartWindow(props) {

    const [chartType, setChartType] = useState('TREE');

    const switchChart = (type) => {
        setChartType(type)
    }

    const getChart = (chartType, props) => {
        if (chartType == "TREE") {
            return <TreeDiagram 
                iterationData={props.iterationData} 
                curIteration={props.curIteration} 
                getStatusFormatting={props.getStatusFormatting}
                setCurIteration={props.setCurIteration}
            />
        } else if (chartType == "GANNT") {
            return <GanntChart 
                iterationData={props.iterationData} 
                curIteration={props.curIteration} 
                setCurIteration={props.setCurIteration}
            />
        } else if (chartType == "PROMPT") {
            return <PromptInspector 
                iterationData={props.iterationData} 
                curIteration={props.curIteration} 
                setCurIteration={props.setCurIteration}
                fact_check_criteria={props.fact_check_criteria}
                getStatusIcon={props.getStatusIcon}
            />
        }
    }

    useEffect(() => {
    
    }, []);
    
    return (
        <div style={{
            display: "flex",
            flexDirection: "column", 
            flexGrow: "1",
            flex: "1",
            background: "none",
            padding: "20px",
            //border: "1px solid #333",
            background: "#111",
            marginBottom: "4px",
          }}>
            <div style={{display: "flex", flexDirection: "row", marginBottom: "8px"}}>
                
                <div style={{marginRight: "8px", width: "20px"}}>
                    <i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>insights</i>
                </div>
                <div 
                    style={{
                        fontWeight: "500", 
                        color:"#ccc", 
                        cursor: "pointer",
                        marginRight: "140px",
                }}>INSPECTOR</div>
                <div 
                    onClick={() => switchChart('TREE')}
                    style={{
                        fontWeight: "500", 
                        color: (chartType == "TREE") ? "#ccc" : "#999", 
                        paddingBottom: "6px",
                        borderBottom: (chartType == "TREE") ? "4px solid #0A7CE5" : "none",
                        cursor: "pointer",
                        marginRight: "40px",
                }}>Tree Diagram</div>
                <div 
                    onClick={() => switchChart('GANNT')}
                    style={{
                        fontWeight: "500", 
                        color: (chartType == "GANNT") ? "#ccc" : "#999", 
                        paddingBottom: "6px",
                        borderBottom: (chartType == "GANNT") ? "4px solid #0A7CE5" : "none",
                        cursor: "pointer",
                        marginRight: "40px",
                }}>Gannt Chart</div>
                 <div 
                    onClick={() => switchChart('PROMPT')}
                    style={{
                        fontWeight: "500", 
                        color: (chartType == "PROMPT") ? "#ccc" : "#999", 
                        paddingBottom: "6px",
                        borderBottom: (chartType == "PROMPT") ? "4px solid #0A7CE5" : "none",
                        cursor: "pointer",
                        marginRight: "40px",
                }}>Content Inspector</div>
                
                <div style={{flex: "1"}}></div> 
                <div style={{opacity:0}}>
                    <MaterialIcon icon="unfold_more" size={24} color="#999"/>
                </div>
                <div style={{opacity:0}}>
                    <MaterialIcon icon="unfold_less" size={24} color="#999"/>
                </div>
                
            </div>
            
            {getChart(chartType, props)}
            
          </div>
    );
}
     
export default ChartWindow;
