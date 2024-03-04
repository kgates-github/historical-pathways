import '../App.css';
import React from 'react';
import MaterialIcon, {colorPalette} from 'material-icons-react';
import ChartWindow from './ChartWindow';
import IterationPanel from './IterationPanel';
import AudioPlayer from './AudioPlayer';
import { useState, useEffect } from 'react';


function SimulationApp(props) {
    const [audioPlaying, setAudioPlaying] = useState(false);
    const [curIteration, setCurIteration] = useState(1);
    

    const togglePlayAudio = () => {
        setAudioPlaying(!audioPlaying)
    }

    const getAudioButtonIcon = () => {
        if (audioPlaying) {
            return (<i className="material-icons" style={{color: "#ccc", fontSize: "70px"}}>pause</i>);
        } else {            
            return (<i className="material-icons" style={{padding: "0px", color: "#ccc", fontSize: "70px"}}>play_arrow</i>);
        }
    }

    const incrementIteration = (dir) => {
        const highestIteration = Math.max(...props.selectedSimulation.iterations.map(item => item.iteration));
        let nextIteration = 1
        if (dir == 'next') {
            nextIteration = (curIteration == highestIteration) ? 1 : curIteration + 1;
        } else {
            nextIteration = (curIteration > 1) ? curIteration - 1 : highestIteration;
        }
        
        setCurIteration(nextIteration);
    }

    const handleIterationClick = (iteration) => {   
        setCurIteration(iteration);
    }

    const fact_check_criteria = {
        'A': "The submitted answer is a subset of the expert answer and is fully consistent with it.",
        'B': "The submitted answer is a superset of the expert answer and is fully consistent with it.",
        'C': "The submitted answer contains all the same details as the expert answer.",
        'D': "There is a disagreement between the submitted answer and the expert answer.",
        'E': "The answers differ, but these differences don't matter from the perspective of factuality.",
    }

    const getStatusFormatting = (type, value) => {
        if (type == 'up-down') {
            if (value > 0) {
                return {'color': "#00ff66", 'fontSize': "20px", "name": "arrow_upwards"};
            } else if (value < 0) {
                return {'color': "#aa3333", 'fontSize': "20px", "name": "arrow_downwards"};
            }
        } else if (type == 'health') {
            if (value == 'D') {
                return {'color': "#993333", 'fontSize': "20px", "name": "error"};
            } else if (value == 'error') {
                return {'color': "#cc9900", 'fontSize': "20px", "name": "warning"};
            } else {
                return {'color': "#00ff66", 'fontSize': "20px", "name": "check"};
            }
        } else if (type == 'interest_matches') {
            if (value > 0) {
                return {'color': "#00ff66", 'fontSize': "20px", "name": "check"};
            } else {
                return {'color': "#aa3333", 'fontSize': "20px", "name": "close"};
            }
        }
    }

    const getStatusIcon = (type, value) => {
        if (type == 'up-down') {
            if (value > 0) {
                return (<i className="material-icons 20 md-dark " style={{color: "#00ff66", fontSize: "20px"}}>arrow_upwards</i>);
            } else if (value < 0) {
                return (<i className="material-icons 20 md-dark " style={{color: "#cc3333", fontSize: "20px"}}>arrow_downwards</i>);
            } else {
                return (<i className="material-icons 20 md-dark " style={{color: "#666", fontSize: "20px"}}>close</i>);
            }
        } else if (type == 'health') {
            if (value == 'D') {
                return (<i className="material-icons 20 md-dark " style={{color: "#cc3333", fontSize: "20px"}}>error</i>);
            } else if (value == 'error') {
                return (<i className="material-icons 20 md-dark " style={{color: "#cc9900", fontSize: "20px"}}>warning</i>);
            } else {
                return (<i className="material-icons 20 md-dark " style={{color: "#00ff66", fontSize: "20px"}}>check</i>);
            }
        } else if (type == 'interation_type') {
            if (value == "tangent") {
                return (<i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>fork_right</i>);
            } else if (value == 'child') {
                return (<i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>trending_flat</i>);
            } 
            return <></>

        } else if (type == 'interest_matches') {
            if (value > 0) {
                return (<i className="material-icons 20 md-dark " style={{color: "#00ff66", fontSize: "20px"}}>check</i>);
            } else {
                return (<i className="material-icons 20 md-dark " style={{color: "#cc3333", fontSize: "20px"}}>close</i>);
            }
        }
        return <></>;
    }

    const getChangeSymbol = (value) => {
        if (value > 0) {
            return "+";
        } 
        return "";
    }

    useEffect(() => {
        setCurIteration(1); // Always set to first iteration when simulation changes
        setAudioPlaying(false);
    }, [props.selectedSimulation]);


  return (
    <div style={{
      width: "100%", 
      height: "100vh", 
      backgroundColor: "none",
      display: "flex",
      flexDirection: "column",
    }}> 
      <div style={{display: "flex", flexDirection: "column", flexGrow: "1", background: "none", margin: "20px"}}>
        {/* Top Bar */}
        <div style={{
            display:"flex", 
            flexDirection: "row", 
            alignItems: "center", 
            marginBottom: "4px", 
            background: "#111", 
            height: "60px",
            padding:"4px"
        }}>
          <div style={{marginRight: "80px"}}>
            <select onChange={props.handleSelectChange} style={{
              padding: "12px", 
              marginLeft: "20px",
              backgroundColor: "#191919", 
              color: "#ccc",
              borderTop: "none",
              borderLeft: "none",
              borderRight: "none",
              borderBottom: "2px solid #666",
              textTransform: "uppercase",
            }}> 
              <option value="0">Select a Simulation</option>
              {props.simulationData &&
                Object.keys(props.simulationData).map((key) => (
                  <option key={key} value={key}>
                    {
                      props.simulationData[key]["raw_data"]["datetime"] + ' - ' + 
                      //props.simulationData[key]["persona"]["name"] + ' - ' + 
                      props.simulationData[key]["iterations"][0]["name"] + ' - ' + 
                      props.simulationData[key]["persona"]["time_constraint"] + ' - ' + 
                      props.simulationData[key]["persona"]["autopilot_on"] + ' - ' + 
                      props.simulationData[key]["persona"]["continuity"] + ' - ' + 
                      props.simulationData[key]["persona"]["interests"]
                    } 
                  </option>
                ))}
            </select>
          </div>
          <div style={{marginRight: "80px", alignItems: "center", width: "200px"}}>
            <div>
              <div style={{fontWeight: "500"}}>TIME OF RUN</div>
              <div> {props.selectedSimulation["raw_data"]["datetime"]}</div>
            </div>
          </div>
         
          <div style={{marginRight: "80px", alignItems: "center", maxWidth: "800px"}}>
            <div>
              <div style={{fontWeight: "500"}}>DESCRIPTION</div>
              <div>
                    {props.selectedSimulation["raw_data"]["description"]}
                </div>
            </div>
          </div>
          
        </div>
        {/* End Top Bar */}
        {/* Main Outer */}
        <div style={{display: "flex", flexDirection: "row", flexGrow: "1", background: "none"}}>
          {/* Left Column */}
          <div style={{
            display: "flex", 
            minWidth: "340px", 
            maxWidth: "340px",
            flexDirection: "column", 
            marginRight: "4px",
          }}>
            {/* Left Column Top */}
            <AudioPlayer 
                selectedSimulation={props.selectedSimulation} 
                curIteration={curIteration} 
                setCurIteration={setCurIteration}
                togglePlayAudio={togglePlayAudio}
                audioPlaying={audioPlaying}
                incrementIteration={incrementIteration}
                getAudioButtonIcon={getAudioButtonIcon}
            />
            
            {/* End Left Column Top*/}
            {/* Left Column Settings Top */}
             <div style={{
              display: "flex",
              flexDirection: "column",  
              background: "none",
              padding: "20px",
              background: "#111",
              marginBottom: "4px",
            }}>
              <div style={{
                fontWeight: "500", 
                display: "flex", 
                flexDirection: "row", 
                alignContent: "center",
              }}>
                    <div style={{marginRight: "8px", width: "20px"}}>
                        <i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>settings</i>
                    </div>
                    <div style={{fontWeight: "500", color:"#ccc", marginBottom:"16px"}}>SIMULATION CONFIG</div>
              </div>

              <div style={{flexGrow: "1", background: "none", marginTop:"10px"}}>
                
                {/* Autopilot Settings*/}

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                    <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Era: </div> 
                    <div style={{width: "100%",}}>
                        {props.selectedSimulation["persona"]["eras"].join(", ")}
                    </div>
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                    <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Topics: </div> 
                    <div style={{width: "100%",}}>
                    {props.selectedSimulation["persona"]["topics"].join(", ")}
                    </div>
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                    <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Time: </div> 
                    <div style={{width: "100%",}}>
                    {props.selectedSimulation["persona"]["time_constraint"]}
                    </div>
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                    <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Autopilot: </div> 
                    <div style={{width: "100%",}}>
                    {props.selectedSimulation["persona"]["autopilot_on"] ? "On" : "Off"}
                    </div>
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                    <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Continuity: 
                    ({props.selectedSimulation["persona"]["continuity"]}) </div> 
                    <div style={{
                        height: "4px",
                        width: "100%",
                        backgroundColor: "#333",
                        borderRadius: "2px",
                        marginTop: "8px",
                        display:"flex", 
                        flexDirection: "row",
                    }}>
                        <div style={{
                            width: (props.selectedSimulation["persona"]["continuity"] - 1) * 100/9 + "%",
                        }}></div>
                        <div style={{marginTop:"-2px", width:"7px", height:"7px", borderRadius: "50%", background:"#ccc"}}></div>
                    </div>
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                    <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Interests: 
                    ({props.selectedSimulation["persona"]["interests"]}) </div> 
                    <div style={{
                        height: "4px",
                        width: "100%",
                        backgroundColor: "#333",
                        borderRadius: "2px",
                        marginTop: "8px",
                        display:"flex", 
                        flexDirection: "row",
                    }}>
                        <div style={{
                            width: (props.selectedSimulation["persona"]["interests"] - 1) * 100/9 + "%",
                        }}></div>
                        <div style={{marginTop:"-2px", width:"7px", height:"7px", borderRadius: "50%", background:"#ccc"}}></div>
                    </div>
                </div>
 
              </div>
            
            </div>
            {/* End Left Column Middle Top*/}
            {/* Left Column Middle Top */}
             <div style={{
              display: "flex",
              flexDirection: "column",  
              background: "none",
              padding: "20px",
              background: "#111",
              marginBottom: "4px",
            }}>
              <div style={{
                fontWeight: "500", 
                display: "flex", 
                flexDirection: "row", 
                alignContent: "center",
              }}>
                    <div style={{marginRight: "8px", width: "20px"}}>
                        <i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>insert_chart</i>
                    </div>
                    <div style={{fontWeight: "500", color:"#ccc", marginBottom:"16px"}}>EVALUATION</div>
              </div>

              <div style={{flexGrow: "1", background: "none", marginTop:"10px"}}>
                
                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Fact Check: </div> 
                {props.selectedSimulation["iterations"]
                    .map((iteration, index) => (
                        <div id={"fact_"+index} style={{marginRight: "8px", width: "20px", background: "none"}}>
                            {getStatusIcon('health', iteration['fact_eval']['choice_string'])}
                        </div>
                ))}
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                <div className="list-label" style={{marginBottom:"4px",  width: "350px"}}>Interest Matches: </div> 
                {props.selectedSimulation["iterations"]
                    .map((iteration, index) => (
                        <div id={"topic_"+index} style={{marginRight: "8px", width: "20px", background: "none"}}>
                            {getStatusIcon('interest_matches', iteration['topic_matches'])}
                        </div>
                ))}
                </div>
                
                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                <div className="list-label" style={{marginBottom:"4px", width: "350px"}}>Connection Type: </div> 
                {props.selectedSimulation["iterations"]
                    .map((iteration, index) => (
                        <div id={"type_"+index} style={{marginRight: "8px", width: "20px", background: "none"}}>
                            {getStatusIcon('interation_type', iteration['type'])}
                        </div>
                ))}
                </div>

                <div style={{display:"flex", flexDirection: "row", marginBottom: "12px"}}>
                <div className="list-label" style={{marginBottom:"4px",  width: "350px"}}>Satisfaction: </div> 
                {props.selectedSimulation["iterations"]
                    .map((iteration, index) => (
                        <div id={"satisfaction_"+index} style={{marginRight: "8px", width: "20px", background: "none"}}>
                            {getStatusIcon('up-down', iteration['satisfaction_diff'])}
                        </div>
                ))}
                </div>

                <div style={{display: "flex", flexDirection: "row", marginBottom:"12px"}}> 
                    <div className="list-label" style={{ width: "350px"}}>Satisfaction Delta: </div>
                    <div style={{marginLeft: "8px", marginRight: "8px", width: "20px", background: "none", textAlign: "center"}}>
                        {props.selectedSimulation["summary_data"]["satisfaction_diff"]}
                    </div>
                    <div style={{marginRight: "8px", width: "20px", background: "none"}}>
                        {getStatusIcon('up-down', props.selectedSimulation["summary_data"]["satisfaction_diff"])}
                    </div>
                </div>
                
                <div style={{marginTop: "28px",}}>
                    <span className="list-label">Expectation: </span> 
                    <span dangerouslySetInnerHTML={{ __html: props.selectedSimulation["raw_data"]["persona"]["expectation"] }}></span>
                </div>
                    
              </div>
            
            </div>
            {/* End Left Column Middle Top*/}
            {/* Left Column Middle */}
             <div style={{
              display: "flex",
              flexDirection: "column",  
              background: "none",
              padding: "20px",
              //border: "1px solid #333",
              background: "#111",
              marginBottom: "4px",
            }}>
              <div style={{
                fontWeight: "500", 
                display: "flex", 
                flexDirection: "row", 
                alignContent: "center",
              }}>
                <div style={{marginRight: "8px", width: "20px"}}>
                    <i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>person</i>
                </div>
                <div style={{fontWeight: "500", color:"#ccc"}}>PERSONA</div>
              </div>
              <div style={{flexGrow: "1", background: "none"}}>
                <ul style={{listStyleType: "none", padding: "0"}}>
                    <li><span className="list-label">Name: </span>{props.selectedSimulation["persona"]["name"]}</li>
                    <li><span className="list-label">Location: </span>{props.selectedSimulation["persona"]["location"]}</li>
                    <li><span className="list-label">Age: </span>{props.selectedSimulation["persona"]["age"]}</li>
                    <li><span className="list-label">Education: </span>{props.selectedSimulation["persona"]["education"]}</li>
                </ul>
              </div>
            
            </div>
            {/* End Left Column Middle */}
            {/* Left Column Bottom*/}
            <div style={{
              display: "flex",
              flexGrow: "1",
              flex: "1",
              flexDirection: "column",  
              background: "none",
              paddingTop: "20px",
              paddingBottom: "10px",
              paddingLeft: "20px",
              paddingRight: "10px",
              //border: "1px solid #333",
              background: "#111",
              marginBottom: "20px",
            }}>
              <div style={{display: "flex", flexDirection: "row", marginBottom: "28px", alignContent: "center"}}>
                <div style={{marginRight: "8px", width: "20px"}}>
                    <i className="material-icons md-dark " style={{color: "#999", fontSize: "20px"}}>format_list_bulleted</i>
                </div>
                <div style={{fontWeight: "500", color:"#ccc"}}>LOGS</div>
              </div>
              <div style={{
                flexGrow: "1", 
                height:"300px", 
                marginBottom: "8px", 
                background: "none", 
                overflowY: "scroll",
                paddingRight: "10px",
              }}>
                
                {props.selectedSimulation["logs"]
                     .filter((log) => log["type"] === "message")
                     .map((log, index) => (
                         <div key={index} style={{borderTop: "1px dashed #999", marginBottom: "12px", paddingTop: "12px"}}>
                             <div>{log["timestamp"]}</div>
                             <div>{log["content"]}</div>
                         </div>
                ))}
                
              </div>
            
            </div>
            {/* End Left Column Bottom*/}
          </div>
          {/* End Left Column */}
          {/* Right Column */}
          <div style={{
            display: "flex", 
            flex: "1",
            flexDirection: "column",  
            background: "none"
          }}>
            {/* Right Column Top */}
            <div style={{
              display: "flex",
              height: "210px",
              overflowY: "hidden",
              flexDirection: "column",  
              background: "none",
              padding: "20px",
              //border: "1px solid #333",
              background: "#111",
              marginBottom: "4px",
            }}>
              <div style={{display: "flex", flexDirection: "row", marginBottom: "16px", alignContent: "center"}}>
                <div style={{marginRight: "8px", width: "20px"}}>
                    <i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>route</i>
                </div>
                <div style={{fontWeight: "500", color: "#ccc"}}>USER JOURNEY</div>
              </div>
              <div style={{marginBottom: "20px", background: "none",  display: "flex", flexDirection: "row",}}>
               {props.selectedSimulation["iterations"]
                    .map((iteration, index) => (
                        <IterationPanel 
                            key={"iteration_"+index} 
                            iteration={iteration} 
                            getStatusIcon={getStatusIcon}
                            getChangeSymbol={getChangeSymbol}
                            handleIterationClick={handleIterationClick}
                            curIteration={curIteration}
                            audioPlaying={audioPlaying}
                            persona={props.selectedSimulation["persona"]}
                        />
                ))}
             
              </div>
            </div>
            {/* End Right Column Top*/}
            {/* Right Column Middle*/}
            
            <ChartWindow 
                iterationData={props.selectedSimulation} 
                curIteration={curIteration} 
                setCurIteration={setCurIteration}
                getStatusFormatting={getStatusFormatting}
                fact_check_criteria={fact_check_criteria}
                getStatusIcon={getStatusIcon}
            />

            {/* End Right Column Middle*/}
            {/* Right Column Bottom */}
            <div style={{
              display: "flex",
              height: "200px",
              overflowY: "hidden",
              flexDirection: "column",
              background: "none",
              padding: "20px",
              //border: "1px solid #333",
              background: "#111",
              marginBottom: "20px",
              overflowY: "scroll",
            }}>
              <div style={{display: "flex", flexDirection: "row", marginBottom: "28px", alignContent: "center"}}>
                <div style={{marginRight: "8px", width: "20px"}}>
                    <i className="material-icons md-dark " style={{color: "#999", fontSize: "20px"}}>fact_check</i>
                </div>
                <div style={{fontWeight: "500", color: "#999"}}>FACT CHECKER</div>
              </div>
              
              <div style={{marginBottom: "20px", background: "none",  display: "flex", flexDirection: "row",}}>
                {props.selectedSimulation["iterations"]
                    .map((iteration, index) => (
                    <div key={"fact_check_"+index} style={{marginRight:"20px", background: "none", flex:"1"}}>
                        <div style={{ display: "flex", flexDirection: "row", marginBottom: "4px", alignContent: "center",}}>
                            <div style={{
                                display: "flex", flexDirection: "row", 
                                marginBottom: "12px", alignContent: "center",
                            }}>
                                <div style={{marginRight: "8px", width: "20px", background: "none"}}>
                                    {getStatusIcon('health', iteration['fact_eval']['choice_string'])}
                                </div>
                                <div style={{marginTop: "0px", fontWeight: "700", alignContent: "center",  alignItems: "center", background: "none"}}>
                                    <span className="list-label">{iteration["iteration"]+": "}{iteration["name"].slice(0, 30) + '...'}</span>
                                </div>
                            </div>
                        </div>
                        
                        <ul style={{listStyleType: "none", padding: "0", background:"none", margin:"0"}}>
                        <li style={{marginBottom: "12px"}}>
                            <span className="list-label">Eval: </span>
                                
                            {"("+iteration['fact_eval']['choice_string']+") "}
                            {fact_check_criteria[iteration['fact_eval']['choice_string']]}
                        </li>
                        <li style={{marginBottom: "12px"}}>
                            <span className="list-label">Wikipedia page: </span>
                            <a href={"https://en.wikipedia.org/wiki/"+ iteration['fact_eval']['wikipedia_page']} target="_blank">
                                {iteration['fact_eval']['wikipedia_page'].replace(/_/g, ' ')}
                            </a>
                        </li>
                        {/*<li><span className="list-label">Reason: </span>{iteration['fact_eval']['reason']}</li>*/}
                        </ul>
                        
                    </div>
                ))}
             
              </div>
            
            </div>
            {/* End Right Column Bottom*/}
           
          </div>
          {/* End Right Column*/}

        </div>
        {/* End Main Outer */}
      </div>

      
    </div>
  );
}

export default SimulationApp;