const START=document.getElementById('start');
const STOP=document.getElementById('stop');
const CSV=document.getElementById('csv');
const STATUS=document.getElementById('status');
const LOG=document.getElementById('log');

const SERVER='http://localhost:8001/local/process-frame';
const FPS=2;
const MAX_WIDTH=640;
const FRAME_SKIP=10; // Process 1 out of every 10 frames

let stream=null, video=null, canvas=null, ctx=null, interval=null;
let sessionId=0;
let activeSession=0;
let rows=[];
let frameCounter=0; // Counter for frame skipping

function log(msg){
  const d=document.createElement('div');
  d.textContent=new Date().toLocaleTimeString()+' — '+msg;
  LOG.prepend(d);
}

async function start(){
  sessionId++;
  const mySession=sessionId;
  activeSession=mySession;

  stream=await navigator.mediaDevices.getDisplayMedia({video:{cursor:'never'},audio:false});
  START.disabled=true;
  STOP.disabled=false;
  STATUS.textContent='Status: capturing';
  log('Capture started');

  video=document.createElement('video');
  video.srcObject=stream;
  video.muted=true;

  canvas=document.createElement('canvas');
  ctx=canvas.getContext('2d',{willReadFrequently:true});

  video.onloadedmetadata=()=>{
    if(activeSession!==mySession) return;
    video.play();
    interval=setInterval(()=>capture(mySession),1000/FPS);
  };

  stream.getVideoTracks()[0].addEventListener('ended',stop);
}

async function capture(mySession){
  if(activeSession!==mySession) return;
  if(!video||!video.videoWidth) return;

  // Frame skipping: only process every Nth frame
  frameCounter++;
  if(frameCounter % FRAME_SKIP !== 0) return;

  const w=Math.min(video.videoWidth,MAX_WIDTH);
  const h=Math.round(w/video.videoWidth*video.videoHeight);
  canvas.width=w; canvas.height=h;
  ctx.drawImage(video,0,0,w,h);

  canvas.toBlob(async blob=>{
    if(activeSession!==mySession||!blob) return;
    try{
      const fd=new FormData();
      fd.append('frame',blob,'frame.jpg');
      const res=await fetch(SERVER,{method:'POST',body:fd});
      const txt=await res.text();
      if(activeSession!==mySession) return;

      const data=JSON.parse(txt);
      
      // Handle new frame API response format
      if(data && data.frame_processed && data.faces && data.faces.length > 0){
        // Get the first detected face (primary person)
        const face = data.faces[0];
        const emotionScores = face.emotion_scores || {};
        const emotion = face.emotion || 'unknown';
        
        log(
          `Person ${face.person_id} | emotion=${emotion} | `+
          `angry=${(emotionScores.angry||0).toFixed(2)} `+
          `fear=${(emotionScores.fear||0).toFixed(2)} `+
          `happy=${(emotionScores.happy||0).toFixed(2)} `+
          `neutral=${(emotionScores.neutral||0).toFixed(2)} `+
          `sad=${(emotionScores.sad||0).toFixed(2)}`
        );

        rows.push({
          timestamp:new Date().toISOString(),
          person_id:face.person_id,
          dominant:emotion,
          angry:emotionScores.angry||0,
          disgust:emotionScores.disgust||0,
          fear:emotionScores.fear||0,
          happy:emotionScores.happy||0,
          neutral:emotionScores.neutral||0,
          sad:emotionScores.sad||0,
          surprise:emotionScores.surprise||0
        });
      } else if(data && data.frame_processed && data.total_faces === 0){
        log('No faces detected in frame');
      }
    }catch(e){
      if(activeSession===mySession) log('POST error: '+e.message);
    }
  },'image/jpeg',0.7);
}

function stop(){
  activeSession=0;
  if(interval) clearInterval(interval);
  if(stream) stream.getTracks().forEach(t=>t.stop());
  interval=null; stream=null;
  frameCounter=0; // Reset frame counter
  START.disabled=false;
  STOP.disabled=true;
  STATUS.textContent='Status: stopped';
  log('Capture stopped');
}

function downloadCsv(){
  let csv='timestamp,person_id,dominant,angry,disgust,fear,happy,neutral,sad,surprise\n';
  rows.forEach(r=>{
    csv+=`${r.timestamp},${r.person_id||'N/A'},${r.dominant},${r.angry},${r.disgust},${r.fear},${r.happy},${r.neutral},${r.sad},${r.surprise}\n`;
  });
  const blob=new Blob([csv],{type:'text/csv'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='emotion_report.csv';
  a.click();
}

START.onclick=start;
STOP.onclick=stop;
CSV.onclick=downloadCsv;

log('Dashboard ready. Click Start to select a screen.');
