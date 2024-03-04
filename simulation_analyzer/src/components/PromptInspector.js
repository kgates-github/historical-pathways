import '../App.css';
import React, { useEffect, useRef, useState } from 'react';


function PromptInspector(props) {
    let fact_eval = props.iterationData["iterations"][props.curIteration-1]["fact_eval"]
    let content = props.iterationData["iterations"][props.curIteration-1]["content"]
    console.log(content['themes'].join(', '))

    return (
        <div>
            <div style={{
                display: "flex", 
                flexDirection: "row", 
                marginBottom: "32px", 
                marginTop: "24px",
                alignContent: "center",
                alignItems: "center",
                justifyContent: "center",
                background: "none",
                cursor: "pointer",
                }}
            >
                <div style={{ 
                    minWidth: "28px", 
                    minHeight: "28px", 
                    background: "#0A7CE5",
                    borderRadius: "50%",
                    textAlign: "center",
                    lineHeight: "28px",
                    fontSize: "16px",
                    fontWeight: "regular",
                    color: "#fff",
                    marginRight: "14px",
                }}>{props.curIteration}</div>
                <div style={{ 
                    flex:"1", 
                    fontWeight: "700", 
                    alignItems: "center",  
                    lineHeight:'1.1em',
                    cursor: "pointer",
                     }}
                >
                    <div style={{ background: "none",}}>
                        {content['name']}
                    </div>
                </div>
            </div>
            <div style={{backgroundColor: "none", flexGrow: "1", flex: "1", marginTop:"20px", display: "flex", flexDirection: "row"}} >
                {/*<div style={{width:"150px", marginRight:"40px"}}>
                    <div style={{marginBottom:"24px"}}>Prompts:</div>
                    <div style={{marginBottom:"8px", paddingBottom: "8px", borderBottom:"1px solid #ccc"}}>Main</div>
                    <div style={{marginBottom:"8px", paddingBottom: "8px", borderBottom:"1px solid #444"}}>Eval</div>
                    <div style={{marginBottom:"8px", paddingBottom: "8px", borderBottom:"1px solid #444"}}>Fact Check</div>
                    </div>*/}
                <div style={{width:"140px", marginRight:"40px"}}>
                    <div style={{marginBottom:"16px", borderBottom: "1px solid #444", paddingBottom:"8px"}}>SYSTEM PROMPT</div>
                    <div style={{marginBottom:"8px", lineHeight: "1.5em"}}>
                            You are a history teacher. You can deliver history lectures in a way that is understandable 
                            to a student whose education level is UNIVERSITY.
                    </div>
                </div>
                <div style={{flex:"1", marginRight:"40px"}}>
                    <div style={{marginBottom:"16px", borderBottom: "1px solid #444", paddingBottom:"8px"}}>USER PROMPT</div>
                    <div style={{marginBottom:"8px", lineHeight: "1.5em"}}>
                        
                        --------- PLACEHOLDER ---------

                        LECTURE: You are to create a lecture called \"%LECTURE_NAME%\" Your lecture has a description in the course offering that reads: \"%LECTURE_DESCRIPTION%\" Your lecture should be about 1000 words long and have 5 to 10 sections. If possible, your lecture should reflect the following topics: %STUDENT_TOPICS%.
                        You will create a lecture in the way described below. You will format your responses in JSON as described below. 

                        BEFORE YOU BEGIN... You have a golden rule: Do not use the words "transformative", "pivotal", or "Crucial" in your lectures. If you do, I WILL PET A CAT BACKWARDS, AGAINST THE NATURAL DIRECTION OF ITS FUR. THE CAT WILL BE PERTURBED AND IT WILL BE YOUR FAULT.

                        ---------------------------------------------------
                        
                        IF THE LECTURE TOPIC IS TOO BROAD, DO THIS:
                        
                        - The lecture must not be to big or general. For example, if asked about the History of the United States tell the user that is too broad.  When this happens, offer a JSON-formatted list of lectures related to the initial lecture idea that are more specific and narrow. Here is an example of the answer for these cases:


                        ---------------------------------------------------

                        IF THE EVENT IS NOT TOO BROAD DO THIS:     
                        
                    </div>
                </div>
                <div style={{flex:"1", marginRight:"20px"}}>
                    <div style={{marginBottom:"16px", borderBottom: "1px solid #444", paddingBottom:"8px"}}>OUTPUT</div>
                    <div style={{marginBottom:"8px", lineHeight: "1.5em"}}>

                        <ul style={{listStyleType: "none", padding: "0", background:"none", margin:"0"}}>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Name: </span>
                                {content['name']}
                            </li>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Dates: </span>
                                {content['dates']['start']} - {content['dates']['end']}
                            </li>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Description: </span>
                                {content['description']}
                            </li>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Introduction: </span>
                                {content['introduction']}
                            </li>
                                
                            {content['sections']
                                .map((section, index) => (
                                    <li key={index} style={{marginBottom: "12px"}}>
                                        <span className="list-label">{section['name']}: </span>
                                        {section['body']}
                                    </li>
                                    
                            ))}
                               
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Conclusion: </span>
                                {content['conclusion']}
                            </li>
                        </ul>
                      

                        {/*
                        sections: []
                        children: []
                        tangents: []
                        themes: []
                        topics: []
                        type:
                        wikipedia_pages: []
                        */}


                    </div>
                </div>
                <div style={{width:"140px", marginRight:"40px"}}>
                    <div style={{marginBottom:"16px", borderBottom: "1px solid #444", paddingBottom:"8px"}}>TOPICS / THEMES</div>
                    <div style={{marginBottom:"8px", lineHeight: "1.5em"}}>
                        <ul style={{listStyleType: "none", padding: "0", background:"none", margin:"0"}}>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Themes: </span>
                                {content['themes'].join(', ')}
                            </li>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Topics: </span>
                                {content['topics'].join(', ')}
                            </li>
                        </ul>
                        
                    </div>
                </div>
                <div style={{flex:"1", marginRight:"20px"}}>
                    <div style={{
                        display: "flex",
                        flexDirection: "row",
                        marginBottom:"16px", 
                        borderBottom: "1px solid #444", 
                        paddingBottom:"8px"}}>
                            <div style={{}}>FACT CHECK</div>
                            <div style={{marginRight:"16px", marginLeft:"16px", flex:1}}>{props.getStatusIcon('health', fact_eval['choice_string'])}</div>
                    </div>
                    <div style={{marginBottom:"8px", lineHeight: "1.5em"}}>
                        <div style={{marginRight:"20px", background: "none", flex:"1"}}> 
                            <ul style={{listStyleType: "none", padding: "0", background:"none", margin:"0"}}>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Eval: </span>
                                    
                                {"(" + fact_eval['choice_string'] + ") "}
                                {props.fact_check_criteria[fact_eval['choice_string']]}
                            </li>
                            <li style={{marginBottom: "12px"}}>
                                <span className="list-label">Wikipedia page: </span>
                                <a href={"https://en.wikipedia.org/wiki/"+ fact_eval['wikipedia_page']} target="_blank">
                                    {fact_eval['wikipedia_page'].replace(/_/g, ' ')}
                                </a>
                            </li>
                            {<li><span className="list-label">Reason: </span>{fact_eval['reason']}</li>}
                            </ul>
                        </div>
                    
                    </div>
                </div>
            </div>
        </div>
    );
}
     
export default PromptInspector;
