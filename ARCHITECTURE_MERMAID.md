# 🏗️ System Architecture - Mermaid Diagrams

## Complete System Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend Layer (React + Vite - Port 3001)"]
        UploadPage["UploadPage.jsx<br/>• Video Upload<br/>• Mode Selection"]
        ProcessingPage["ProcessingPage.jsx<br/>• Status Polling<br/>• Progress Bar"]
        ResultsPage["ResultsPage.jsx<br/>• Video Player<br/>• Emotion Charts"]
        HistoryPage["HistoryPage.jsx<br/>• Job History<br/>• Downloads"]
        Context["ExecutionModeContext<br/>(Global State)"]
        API["API Service (api.js)<br/>• HTTP Client<br/>• Backend Router"]
    end

    subgraph ColabBackend["Colab Backend (Django - Port 8000)"]
        DjangoAPI["Django REST API<br/>• /api/jobs/upload/<br/>• /api/jobs/{id}/status/"]
        DjangoDB["Database<br/>(SQLite/PostgreSQL)<br/>VideoJob Model"]
        GoogleDrive["Google Drive<br/>Storage"]
    end

    subgraph LocalBackend["Local Backend (FastAPI - Port 8001)"]
        FastAPI_Routes["FastAPI Routes<br/>• /local/jobs/upload<br/>• /local/jobs/{id}/status"]
        LocalDB["SQLite Database<br/>LocalJob Model"]
        LocalStorage["Local Filesystem<br/>storage/"]
    end

    subgraph ColabRuntime["Google Colab Runtime"]
        ColabNotebook["Jupyter Notebook<br/>(GPU: T4/P100/V100)"]
    end

    subgraph LocalRuntime["Local Pipeline Runner"]
        PipelineRunner["pipeline/runner.py<br/>(Python Thread)"]
    end

    subgraph AIPipeline["AI/ML Processing Pipeline"]
        Stage1["Stage 1: Face Detection<br/>InsightFace (buffalo_l)<br/>Output: face_detections.json"]
        Stage2["Stage 2: Emotion Detection<br/>DeepFace (VGG-Face)<br/>Output: emotions.json"]
        Stage3["Stage 3: Video Annotation<br/>OpenCV (cv2)<br/>Output: annotated_video.mp4"]
    end

    %% Frontend Connections
    UploadPage --> API
    ProcessingPage --> API
    ResultsPage --> API
    HistoryPage --> API
    Context -.-> UploadPage
    Context -.-> ProcessingPage
    Context -.-> ResultsPage
    Context -.-> HistoryPage

    %% API to Backends
    API -->|Colab Mode| DjangoAPI
    API -->|Local Mode| FastAPI_Routes

    %% Backend Connections
    DjangoAPI --> DjangoDB
    DjangoAPI --> GoogleDrive
    FastAPI_Routes --> LocalDB
    FastAPI_Routes --> LocalStorage

    %% Runtime Connections
    GoogleDrive --> ColabNotebook
    LocalStorage --> PipelineRunner

    %% Pipeline Connections
    ColabNotebook --> Stage1
    PipelineRunner --> Stage1
    Stage1 --> Stage2
    Stage2 --> Stage3

    %% Output Connections
    Stage3 -->|Results| GoogleDrive
    Stage3 -->|Results| LocalStorage

    style Frontend fill:#e3f2fd
    style ColabBackend fill:#fff3e0
    style LocalBackend fill:#f3e5f5
    style AIPipeline fill:#e8f5e9
    style ColabRuntime fill:#fff9c4
    style LocalRuntime fill:#f1f8e9
```

---

## AI/ML Processing Pipeline (Detailed)

```mermaid
flowchart TD
    Start([User Uploads Video]) --> Upload{Upload to<br/>Backend}
    
    Upload -->|Colab Mode| DjangoSave[Django Saves to<br/>Google Drive]
    Upload -->|Local Mode| FastAPISave[FastAPI Saves to<br/>Local Storage]
    
    DjangoSave --> CreateJobColab[Create VideoJob<br/>Status: PENDING]
    FastAPISave --> CreateJobLocal[Create LocalJob<br/>Status: PENDING]
    
    CreateJobColab --> ManualStart[User Opens Colab<br/>Clicks 'Run All']
    CreateJobLocal --> AutoStart[Pipeline Auto-Starts<br/>in Background Thread]
    
    ManualStart --> Pipeline
    AutoStart --> Pipeline
    
    subgraph Pipeline["Processing Pipeline (Identical for Both)"]
        direction TB
        
        Step1[Step 1: Face Detection<br/>━━━━━━━━━━━━━━━━━━━━<br/>Library: InsightFace<br/>Model: buffalo_l<br/>━━━━━━━━━━━━━━━━━━━━<br/>• Load model ~400MB<br/>• Process every frame<br/>• Detect faces 99.8% accuracy<br/>• Extract 512-dim embeddings<br/>• Track faces across frames<br/>━━━━━━━━━━━━━━━━━━━━<br/>Progress: 5% → 40%]
        
        Step1 --> Output1[Output: face_detections.json<br/>~1KB per 30 frames]
        
        Output1 --> Step2[Step 2: Emotion Detection<br/>━━━━━━━━━━━━━━━━━━━━<br/>Library: DeepFace<br/>Model: VGG-Face emotion<br/>━━━━━━━━━━━━━━━━━━━━<br/>• Load model ~15MB<br/>• Crop face regions<br/>• Analyze 7 emotions<br/>• Apply 5-sec smoothing<br/>• Filter confidence > 30%<br/>━━━━━━━━━━━━━━━━━━━━<br/>Progress: 45% → 85%]
        
        Step2 --> Output2[Output: emotions.json<br/>~2KB per 30 frames]
        
        Output2 --> Step3[Step 3: Video Annotation<br/>━━━━━━━━━━━━━━━━━━━━<br/>Library: OpenCV<br/>━━━━━━━━━━━━━━━━━━━━<br/>• Draw bounding boxes<br/>• Add emotion labels<br/>• Add confidence scores<br/>• Encode H264 codec<br/>━━━━━━━━━━━━━━━━━━━━<br/>Progress: 90% → 95%]
        
        Step3 --> Output3[Output: annotated_video.mp4<br/>~1.5x original size]
    end
    
    Output3 --> PostProcess[Post-Processing<br/>━━━━━━━━━━━━━━━━━━━━<br/>• Convert to H264<br/>• Move to final location<br/>• Clean temp files<br/>• Update DB status: DONE<br/>━━━━━━━━━━━━━━━━━━━━<br/>Progress: 100%]
    
    PostProcess --> Done([User Downloads Results])
    
    style Step1 fill:#e3f2fd
    style Step2 fill:#fff3e0
    style Step3 fill:#f3e5f5
    style Output1 fill:#c8e6c9
    style Output2 fill:#c8e6c9
    style Output3 fill:#c8e6c9
    style PostProcess fill:#ffecb3
```

---

## Emotion Categories

```mermaid
graph LR
    subgraph Emotions["7 Emotion Categories Detected by DeepFace"]
        Angry["😠 angry<br/>Color: Red<br/>RGB: 0,0,255"]
        Disgust["🤢 disgust<br/>Color: Dark Green<br/>RGB: 0,128,0"]
        Fear["😨 fear<br/>Color: Purple<br/>RGB: 128,0,128"]
        Happy["😊 happy<br/>Color: Yellow<br/>RGB: 0,255,255"]
        Sad["😢 sad<br/>Color: Blue<br/>RGB: 255,0,0"]
        Surprise["😲 surprise<br/>Color: Orange<br/>RGB: 0,165,255"]
        Neutral["😐 neutral<br/>Color: Gray<br/>RGB: 128,128,128"]
    end
    
    style Angry fill:#ffcdd2
    style Disgust fill:#c8e6c9
    style Fear fill:#e1bee7
    style Happy fill:#fff9c4
    style Sad fill:#bbdefb
    style Surprise fill:#ffe0b2
    style Neutral fill:#e0e0e0
```

---

## Data Flow Sequence

```mermaid
sequenceDiagram
    actor User
    participant Frontend as React Frontend
    participant Backend as Backend API
    participant Pipeline as AI Pipeline
    participant Storage as Storage

    User->>Frontend: Upload video.mp4
    Frontend->>Backend: POST /jobs/upload
    Backend->>Storage: Save video
    Backend->>Backend: Create job (PENDING)
    Backend-->>Frontend: Job ID + status
    Frontend-->>User: Show job ID
    
    Backend->>Pipeline: Start processing
    Pipeline->>Pipeline: Load InsightFace model
    
    loop Status Polling (every 1 second)
        Frontend->>Backend: GET /jobs/{id}/status
        Backend-->>Frontend: Status: PROCESSING, Progress: X%
        Frontend-->>User: Update progress bar
    end
    
    Pipeline->>Pipeline: Stage 1: Face Detection
    Note over Pipeline: Process every frame<br/>Extract face embeddings<br/>Track faces
    Pipeline->>Storage: Save face_detections.json
    
    Pipeline->>Pipeline: Stage 2: Emotion Detection
    Note over Pipeline: Analyze each face<br/>Predict 7 emotions<br/>Apply smoothing
    Pipeline->>Storage: Save emotions.json
    
    Pipeline->>Pipeline: Stage 3: Video Annotation
    Note over Pipeline: Draw bounding boxes<br/>Add emotion labels<br/>Encode video
    Pipeline->>Storage: Save annotated_video.mp4
    
    Pipeline->>Backend: Update status: DONE
    
    Frontend->>Backend: GET /jobs/{id}/status
    Backend-->>Frontend: Status: DONE
    Frontend-->>User: Navigate to Results
    
    User->>Frontend: View results
    Frontend->>Backend: GET /jobs/{id}/results
    Backend-->>Frontend: Video URL + JSON data
    Frontend->>Storage: Stream video
    Storage-->>Frontend: Video chunks
    Frontend-->>User: Play annotated video + charts
```

---

## Technology Stack

```mermaid
graph TB
    subgraph FrontendTech["Frontend Stack"]
        React["React 18.x"]
        Router["React Router 6.x"]
        Recharts["Recharts<br/>(Visualization)"]
        Axios["Axios<br/>(HTTP Client)"]
        Vite["Vite<br/>(Build Tool)"]
    end
    
    subgraph ColabStack["Colab Backend Stack"]
        Django["Django 4.x"]
        DRF["Django REST<br/>Framework"]
        DriveAPI["Google Drive API<br/>(pydrive2)"]
        DB1["PostgreSQL/<br/>SQLite"]
    end
    
    subgraph LocalStack["Local Backend Stack"]
        FastAPI["FastAPI"]
        SQLAlchemy["SQLAlchemy<br/>(ORM)"]
        Uvicorn["Uvicorn<br/>(ASGI Server)"]
        DB2["SQLite"]
    end
    
    subgraph AIStack["AI/ML Libraries"]
        InsightFace["InsightFace 0.7.3<br/>(Face Detection)"]
        DeepFace["DeepFace 0.0.79<br/>(Emotion Detection)"]
        OpenCV["OpenCV 4.8+<br/>(Video Processing)"]
        NumPy["NumPy 1.26.4<br/>(Computing)"]
        ONNX["ONNX Runtime<br/>(Inference)"]
        TensorFlow["TensorFlow/Keras<br/>(DeepFace Backend)"]
    end
    
    style FrontendTech fill:#e3f2fd
    style ColabStack fill:#fff3e0
    style LocalStack fill:#f3e5f5
    style AIStack fill:#e8f5e9
```

---

## File Structure

```mermaid
graph TB
    Root["Final lab/"]
    
    Root --> Frontend["frontend/"]
    Root --> Backend["backend/"]
    Root --> LocalBackend["local_backend/"]
    Root --> Colab["Colab Notebooks/"]
    
    Frontend --> FrontendSrc["src/"]
    FrontendSrc --> Components["components/<br/>EmotionChart.jsx"]
    FrontendSrc --> Pages["pages/<br/>UploadPage.jsx<br/>ProcessingPage.jsx<br/>ResultsPage.jsx<br/>HistoryPage.jsx"]
    FrontendSrc --> Context["context/<br/>ExecutionModeContext.jsx"]
    FrontendSrc --> Services["services/<br/>api.js"]
    
    Backend --> Jobs["jobs/<br/>models.py<br/>views.py<br/>serializers.py"]
    Backend --> EmotionBackend["emotion_backend/<br/>settings.py<br/>urls.py"]
    
    LocalBackend --> Pipeline["pipeline/<br/>face_detection.py<br/>emotion_detection.py<br/>runner.py"]
    LocalBackend --> Models["models.py"]
    LocalBackend --> Routes["routes.py"]
    LocalBackend --> Main["main.py"]
    LocalBackend --> Storage["storage/<br/>input_videos/<br/>output_videos/<br/>output_json/<br/>status/<br/>temp/"]
    
    Colab --> Notebook["final_code_emotion_detection.ipynb"]
    
    style Root fill:#fff3e0
    style Frontend fill:#e3f2fd
    style Backend fill:#f3e5f5
    style LocalBackend fill:#e8f5e9
    style Colab fill:#fff9c4
```

---

## Processing Performance Comparison

```mermaid
gantt
    title Video Processing Time Comparison (1-minute video @ 30 FPS)
    dateFormat X
    axisFormat %s
    
    section GPU (Colab)
    Face Detection (GPU)    :0, 30s
    Emotion Detection (GPU) :30s, 45s
    Video Annotation (GPU)  :45s, 60s
    Post-Processing (GPU)   :60s, 90s
    
    section CPU (Local)
    Face Detection (CPU)    :0, 120s
    Emotion Detection (CPU) :120s, 240s
    Video Annotation (CPU)  :240s, 270s
    Post-Processing (CPU)   :270s, 300s
```

---

## Database Models

```mermaid
erDiagram
    VideoJob ||--o{ EmotionData : "generates"
    LocalJob ||--o{ EmotionData : "generates"
    
    VideoJob {
        string id PK "UUID"
        string status "PENDING|PROCESSING|DONE|FAILED"
        string original_filename
        string drive_file_id
        string colab_url
        datetime created_at
        datetime updated_at
    }
    
    LocalJob {
        string id PK "UUID"
        string status "PENDING|PROCESSING|DONE|FAILED"
        string input_video_path
        string output_video_path
        string output_json_path
        string progress "0-100"
        datetime created_at
        datetime updated_at
    }
    
    EmotionData {
        int frame_number
        float timestamp
        string face_id
        array bbox "x,y,w,h"
        string emotion "angry|disgust|fear|happy|sad|surprise|neutral"
        float confidence "0-100"
        json all_emotions
    }
```

---

## Storage Architecture

```mermaid
graph LR
    subgraph ColabStorage["Colab Mode Storage (Google Drive)"]
        CD1["📁 input_videos/"]
        CD2["📁 output_videos/"]
        CD3["📁 output_json/"]
        CD4["📁 status/"]
    end
    
    subgraph LocalStorage["Local Mode Storage (Filesystem)"]
        LD1["📁 storage/input_videos/"]
        LD2["📁 storage/output_videos/"]
        LD3["📁 storage/output_json/"]
        LD4["📁 storage/status/"]
        LD5["📁 storage/temp/"]
    end
    
    Input[Input Video] -->|Colab| CD1
    Input -->|Local| LD1
    
    CD1 --> Processing1[Processing]
    LD1 --> Processing1
    
    Processing1 -->|Colab| CD2
    Processing1 -->|Colab| CD3
    Processing1 -->|Colab| CD4
    
    Processing1 -->|Local| LD2
    Processing1 -->|Local| LD3
    Processing1 -->|Local| LD4
    
    LD5 -.->|Temp Files<br/>Auto-Cleaned| Processing1
    
    style ColabStorage fill:#fff3e0
    style LocalStorage fill:#f3e5f5
    style Processing1 fill:#e8f5e9
```

---

*Last Updated: January 3, 2026*
