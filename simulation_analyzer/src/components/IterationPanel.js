import '../App.css';
import React, { useEffect, useState } from 'react';

function IterationPanel(props) {
    

    return (
        <div 
            style={{marginRight:"20px", background: "none", flex:"1"}}
        >       
            <div style={{
                display: "flex", 
                flexDirection: "row", 
                marginBottom: "16px", 
                alignContent: "center",
                borderBottom: (props.iteration["iteration"] == props.curIteration) ? "4px solid #0A7CE5" : "4px solid #333",
                paddingBottom: "16px",
                alignItems: "center",
                justifyContent: "center",
                background: "none",
                height: "40px",
                cursor: "pointer",
                }}
                onClick={() => props.handleIterationClick(props.iteration["iteration"])}
            >
                <div style={{ 
                    minWidth: "28px", 
                    minHeight: "28px", 
                    background: (props.iteration["iteration"] == props.curIteration) ? "#0A7CE5" : "#444",
                    borderRadius: "50%",
                    textAlign: "center",
                    lineHeight: "28px",
                    fontSize: "16px",
                    fontWeight: "regular",
                    color: "#fff",
                    marginRight: "14px",
                }}>{props.iteration["iteration"]}</div>
                <div style={{ 
                    flex:"1", 
                    fontWeight: "700", 
                    alignItems: "center",  
                    lineHeight:'1.1em',
                    cursor: "pointer",
                     }}
                     onClick={() => props.handleIterationClick(props.iteration["iteration"])}
                >
                    <div style={{ background: "none",}}>
                        {props.iteration["name"]}
                    </div>
                </div>
            </div>
        
                <div style={{
                    display: "flex", flexDirection: "row", 
                    marginBottom: "2px", alignContent: "center",
                    height: "24px", background: "none",
                }}>
                    <div style={{marginRight: "8px", width: "140px", background: "none"}}>
                        <span className="list-label">Satisfaction: </span>
                    </div>
                    <div style={{marginRight: "8px",  background: "none",  width: "40px", textAlign: "right" }}>
                        {props.getChangeSymbol(props.iteration['satifsaction_diff'])}{props.iteration["satisfaction_diff"]} 
                    </div>
                    <div style={{marginRight: "8px", width: "20px", background: "none"}}>
                        {props.getStatusIcon('up-down', props.iteration['satisfaction_diff'])}
                    </div>
                </div>
           
                <div style={{
                    display: "flex", flexDirection: "row", 
                    marginBottom: "2px", alignContent: "center",
                    height: "24px", background: "none",
                }}>
                    <div style={{marginRight: "8px", width: "140px", background: "none"}}>
                        <span className="list-label">Fact Check: </span>
                    </div>
                    <div style={{marginRight: "8px",  background: "none",  width: "40px", textAlign: "right" }}>
                        {props.iteration['fact_eval']['choice_string']}
                    </div>
                    <div style={{marginRight: "8px", width: "20px", background: "none"}}>
                        {props.getStatusIcon('health', props.iteration['fact_eval']['choice_string'])}
                    </div>
                </div>

                <div style={{
                    display: "flex", flexDirection: "row", 
                    marginBottom: "2px", alignContent: "center",
                    height: "24px", background: "none",
                }}>
                    <div style={{marginRight: "8px", width: "140px", background: "none"}}>
                        <span className="list-label">Interest Matches: </span>
                    </div>
                    <div style={{marginRight: "8px",  background: "none",  width: "40px", textAlign: "right" }}>
                        {props.iteration['topic_matches']} 
                    </div>
                    <div style={{marginRight: "8px", width: "20px", background: "none"}}>
                        {props.getStatusIcon('interest_matches', props.iteration['topic_matches'])}
                    </div>
                </div>
                <div style={{
                    display: "flex", flexDirection: "row", 
                    marginBottom: "2px", alignContent: "center",
                    height: "24px", background: "none",
                }}>
                    <div style={{marginRight: "8px", width: "140px", background: "none"}}>
                        <span className="list-label">Type: </span>
                    </div>
                    <div style={{marginRight: "8px",  background: "none",  width: "40px", textAlign: "right" }}>
                         {props.iteration['type'] == "child" ? "Child" : "Tan"}
                    </div>
                    <div style={{marginRight: "8px", width: "20px", background: "none"}}>
                        {props.getStatusIcon('interation_type', props.iteration['type'])}
                    </div>
                </div>
            <ul>
            {/*
            <li><span className="list-label">New Topics: </span>{props.iteration["new_topic"]}</li>
            <li><span className="list-label">Type: </span>{props.iteration["type"]}</li>
            <li><span className="list-label">interest_score: </span>{props.iteration["interest_score"]}</li>
            <li><span className="list-label">relevance_score: </span>{props.iteration["relevance_score"]}</li>
            <li><span className="list-label">satisfaction_score: </span>{props.iteration["satisfaction_score"]}</li>
            <li><span className="list-label">weighted_score: </span>{props.iteration["weighted_score"]}</li>
            <li><span className="list-label">Topics: </span>
                {props.iteration["content"]["topics"].join(", ").slice(0, 20) + '...'}
            </li>*/}
            </ul>
        </div>
    );
}
     
export default IterationPanel;


