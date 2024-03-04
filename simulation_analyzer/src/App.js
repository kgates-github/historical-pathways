import { count } from 'd3';
import './App.css';
import SimulationApp from './components/SimulationApp';

import React, { useEffect, useState } from 'react';

function App() {
  const [simulationData, setSimulationData] = useState(null);
  const [selectedSimulation, setSelectedSimulation] = useState(null);


  const countMatches = (personaTopics, iterationTopics) => {
    
    let count = 0;
    for (let i = 0; i < personaTopics.length; i++) {
        if (iterationTopics.includes(personaTopics[i])) {
            count++;
        }
    }
  
    return count;
  };


  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('simulations.json');
        const raw_data = await response.json();
        
        let data = []
        for (let i = 0; i < raw_data.length; i++) {
          let visited_interations = raw_data[i]["iterations"].filter((iteration) => iteration['visited'] == 1);

          let count = 0;
          const areas_of_interest = raw_data[i]["persona"]["topics"];

          for (let j = 0; j < visited_interations.length; j++) {
            if (visited_interations[j]["content"]["topics"].some(area => areas_of_interest.includes(area))) {
              count += 1;
            }
          }
          
          let summary_data = {
            "satisfaction_diff": visited_interations[visited_interations.length - 1]["persona_satisfaction"] -
            visited_interations[0]["persona_satisfaction"],
            "interest_match": count,
            "interest_count_2": 2,
          }

          visited_interations.sort((a, b) => a.iteration - b.iteration);
          
          visited_interations.forEach((iteration) => {
            iteration.audio = iteration.audio.replace('frontend/public', '');
            iteration["topic_matches"] = countMatches(raw_data[i]["persona"].topics, iteration.content.topics);
          })

          data.push({
            "raw_data": raw_data[i],
            "persona": raw_data[i]["persona"],
            "logs": raw_data[i]["logs"],
            "iterations": visited_interations,
            "summary_data": summary_data,
          })
        }

        // Sort data by raw_data datetime in descending order
        data.sort((a, b) => new Date(b.raw_data.datetime) - new Date(a.raw_data.datetime));

        setSimulationData(data);
        setSelectedSimulation(data[0]);
      } catch (error) {
        console.error('Error fetching JSON file:', error);
      }
    };

    fetchData();
  }, []); 

  const handleSelectChange = (event) => {
    setSelectedSimulation(simulationData[event.target.value]);
  };

  return (
    (selectedSimulation !== null) ? 
      <SimulationApp 
        selectedSimulation={selectedSimulation}
        simulationData={simulationData}
        handleSelectChange={handleSelectChange}
      /> 
        : 
      <div style={{padding: "50px"}}>Attempting to load simulations.json...</div> 
  );
}
   
export default App;



