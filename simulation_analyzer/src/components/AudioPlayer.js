import React, { useEffect, useState, useMemo } from 'react';
import { Howl, Howler } from 'howler';


function AudioPlayer(props) {
    Howl.autoUnlock = false;
    const [trackList, setTrackList] = useState([]);
    const [sound, setSound] = useState(null);
    const [progress, setProgress] = useState(0);
    const progressWidth = useMemo(() => `${progress}%`, [progress]);

    useEffect(() => {
        function handleUserInteraction() {
            if (Howler.ctx.state === 'suspended') {
                Howler.ctx.resume();
            }
        }
        window.addEventListener('click', handleUserInteraction);
        window.addEventListener('keydown', handleUserInteraction);
    
        return () => {
            window.removeEventListener('click', handleUserInteraction);
            window.removeEventListener('keydown', handleUserInteraction);
        };
    }, []);

    useEffect(() => { 
        //console.log("audio = " + props.selectedSimulation["iterations"].map(iteration => iteration.audio))
        setTrackList(props.selectedSimulation["iterations"].map(iteration => iteration.audio));
        if (sound)  {
            sound.unload();
            setSound(null);
        }
        setSound(new Howl({ 
            src: [props.selectedSimulation["iterations"][0].audio],
            onend: () => {
                props.incrementIteration('next')
            }
        }));
    }, [props.selectedSimulation]);

    useEffect(() => { 
        if (sound) sound.unload();

        let audioPath = props.selectedSimulation["iterations"][props.curIteration-1].audio;
        audioPath = audioPath.replace(/^\//, '');
        console.log("audioPath = " + audioPath);

        setSound(new Howl({ 
            src: [audioPath],
            onend: () => {
                props.incrementIteration('next')
            }
        }));
       
    }, [props.curIteration]);

    useEffect(() => {
        if (Howler.ctx.state === 'suspended') {
            Howler.ctx.resume();
        }
        
        if (props.audioPlaying) sound.play();
        else if (sound && sound.playing()) sound.pause();
    }, [props.audioPlaying]);


    useEffect(() => {
        if (sound && props.audioPlaying) sound.play();
        /*
        const updateProgress = () => {
            if (sound) {
                const progress = (sound.seek() / sound.duration()) * 100;
                setProgress(progress);
                
            }
        };
    
        if (sound) {
            sound.on('play', () => {
                const progressInterval = setInterval(updateProgress, 100);
                return () => clearInterval(progressInterval);
            });
        }
        */
    }, [sound]);

    

    return (
        <div style={{
            display: "flex",
            flexDirection: "column",  
            background: "#111",
            height: "210px",
            paddingTop: "20px",
            paddingLeft: "20px",
            paddingRight: "20px",
            paddingBottom: "20px",
            marginBottom: "4px",
          }}>
            <div style={{
              fontWeight: "500", 
              display: "flex", 
              flexDirection: "row", 
              alignContent: "center",
            }}>
              <div style={{marginRight: "8px", width: "20px"}}>
                  <i className="material-icons 20 md-dark " style={{color: "#999", fontSize: "20px"}}>graphic_eq</i>
              </div>
              <div style={{
                  fontWeight: "500", 
                  color:"#ccc", 
                  whiteSpace: "nowrap", 
                  overflow: "hidden", 
                  textTransform: "uppercase",
                  textOverflow: "ellipsis"
              }}>
                  {props.selectedSimulation["iterations"][props.curIteration-1]["name"]}
              </div>
            </div>

            <div style={{flex:1}}></div>

            <div style={{
              display: "flex", 
              flexDirection: "row", 
              alignItems: "center",
              alignContent: "center",
              justifyContent: "space-between",
              background: "none",
              paddingTop: "16px",
            }}>
                  <div style={{ cursor:"pointer"}} onClick={() => props.incrementIteration('prev')}>
                      <i className="material-icons md-dark" style={{color: "#ccc", fontSize: "44px"}}>skip_previous</i>
                  </div>
                  <i className="material-icons md-dark" style={{color: "#777", fontSize: "34px"}}>replay_10</i>
                  <div style={{ cursor:"pointer"}} onClick={() => props.togglePlayAudio()}>
                      {props.getAudioButtonIcon()}
                  </div>
                  <i className="material-icons md-dark" style={{color: "#777", fontSize: "34px"}}>forward_10</i>
                  <div style={{ cursor:"pointer"}} onClick={() => props.incrementIteration('next')}>
                      <i className="material-icons md-dark " style={{color: "#999", fontSize: "44px"}}>skip_next</i>
                  </div>
            </div>

            <div style={{flex:1}}></div>

             {/* Progress Bar */}
             <div style={{
                  height: "4px",
                  backgroundColor: "#000",
                  borderRadius: "2px",
                  marginTop: "0px",
              }}>
                  <div style={{
                      height: "100%",
                      width: progressWidth,
                      backgroundColor: "#555",
                      borderRadius: "2px",
                  }}></div>
             </div>
             {/* End Progress Bar */}

              <div style={{display: "flex", flexDirection: "row", marginTop: "8px"}}>
                  <div style={{flex: "1", textAlign: "left", color: "#ccc"}}>0</div>
                  <div style={{flex: "1", textAlign: "center", color: "#ccc"}}>1x</div>
                  <div style={{flex: "1", textAlign: "right", color: "#ccc", background:"none"}}>-1:34</div>
              </div>
            
          </div>
    );
};

export default AudioPlayer;