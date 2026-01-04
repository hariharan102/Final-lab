"""
Google Drive Service

This module handles all interactions with Google Drive for the emotion detection system.

ARCHITECTURE NOTES:
- Google Drive acts as shared storage between Django backend and Google Colab
- Backend uploads input videos and reads status/results
- Colab reads input videos and writes outputs + status updates
- This creates a clean separation: no AI inference in backend

SETUP REQUIRED:
1. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
2. Set up Google Drive API credentials (see README)
3. Download credentials.json from Google Cloud Console
4. First run will prompt for authentication

FOLDER STRUCTURE IN GOOGLE DRIVE:
/ai_emotion_project/
   /input_videos/     <- Backend writes, Colab reads
   /output_videos/    <- Colab writes, Backend reads
   /output_json/      <- Colab writes, Backend reads
   /status/           <- Colab writes, Backend reads (live updates)
"""

import os
import json
import io
from pathlib import Path
from django.conf import settings

# Google Drive API imports
# NOTE: Install these packages: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("Warning: Google Drive API libraries not installed. Install with:")
    print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class GoogleDriveService:
    """
    Service class for Google Drive operations.
    
    Handles:
    - Uploading input videos
    - Reading status updates from Colab
    - Downloading output videos and JSON results
    """
    
    # OAuth 2.0 scopes required
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self):
        """
        Initialize Google Drive service.
        Authenticates using credentials.json (first time) or token.json (subsequent).
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("Google Drive API libraries not installed")
        
        self.service = self._authenticate()
        self.folder_ids = self._get_or_create_folders()
    
    def _authenticate(self):
        """
        Authenticate with Google Drive API.
        
        First run: Uses credentials.json to get user consent
        Subsequent runs: Uses token.json for automatic authentication
        """
        creds = None
        token_path = Path(settings.BASE_DIR) / 'token.json'
        credentials_path = Path(settings.BASE_DIR) / 'credentials.json'
        
        try:
            # Check if we have saved credentials
            if token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)
                except Exception as e:
                    print(f"Invalid token.json: {e}")
                    token_path.unlink()
            
            # If credentials are invalid or don't exist, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"Token refresh failed: {e}")
                        creds = None
                
                if not creds:
                    if not credentials_path.exists():
                        raise FileNotFoundError(
                            "credentials.json not found. Please download it from Google Cloud Console:\n"
                            "1. Go to https://console.cloud.google.com/\n"
                            "2. Create/select project\n"
                            "3. Enable Google Drive API\n"
                            "4. Create OAuth 2.0 credentials\n"
                            "5. Download credentials.json to project root"
                        )
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(credentials_path), self.SCOPES
                        )
                        print("Opening browser for Google authentication...")
                        creds = flow.run_local_server(port=0, open_browser=True)
                        print("✅ Authentication successful!")
                    except Exception as e:
                        print(f"Authentication failed: {e}")
                        raise
                
                # Save credentials for future use
                try:
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Warning: Could not save token: {e}")
            
            return build('drive', 'v3', credentials=creds)
        
        except Exception as e:
            print(f"Fatal authentication error: {e}")
            raise
    
    def _get_or_create_folders(self):
        """
        Get or create the required folder structure in Google Drive.
        
        Returns dict mapping folder names to Drive folder IDs.
        """
        folder_ids = {}
        
        # Create root folder
        root_folder_id = self._get_or_create_folder('ai_emotion_project', parent_id=None)
        
        # Create subfolders
        subfolders = ['input_videos', 'output_videos', 'output_json', 'status']
        for folder_name in subfolders:
            folder_ids[folder_name] = self._get_or_create_folder(
                folder_name,
                parent_id=root_folder_id
            )
        
        return folder_ids
    
    def _get_or_create_folder(self, folder_name, parent_id=None):
        """
        Get existing folder ID or create new folder.
        """
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # Create folder if it doesn't exist
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        return folder.get('id')
    
    def upload_video(self, video_file, drive_path, job_id):
        """
        Upload a video file to Google Drive.
        
        Args:
            video_file: Django UploadedFile object
            drive_path: Target path in Google Drive (e.g., '/input_videos/123.mp4')
            job_id: Job UUID for naming
        """
        # Save video temporarily
        temp_path = settings.TEMP_VIDEO_DIR / f"{job_id}.mp4"
        
        # Write file and ensure it's closed before uploading
        with open(temp_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        # File is now closed (exited 'with' block)
        
        try:
            # Upload to Google Drive
            file_metadata = {
                'name': f'{job_id}.mp4',
                'parents': [self.folder_ids['input_videos']]
            }
            
            media = MediaFileUpload(
                str(temp_path),
                mimetype='video/mp4',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        
        finally:
            # Always clean up temp file, even if upload fails
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception as e:
                    print(f"Warning: Could not delete temp file {temp_path}: {e}")
    
    def read_status_file(self, job_id):
        """
        Read status JSON file written by Colab.
        
        Args:
            job_id: Job UUID
            
        Returns:
            dict with keys: status, message, timestamp
            
        Status file format (written by Colab):
        {
          "status": "PROCESSING",
          "message": "Processing frame 45/120",
          "timestamp": 1710000000
        }
        """
        try:
            # Search for status file
            query = f"name='{job_id}.json' and '{self.folder_ids['status']}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return None
            
            # Download and parse JSON
            file_id = files[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            status_data = json.loads(file_content.read().decode('utf-8'))
            
            return status_data
            
        except Exception as e:
            print(f"Error reading status file: {e}")
            return None
    
    def read_emotion_results(self, job_id):
        """
        Read emotion detection results JSON from Google Drive.
        
        Args:
            job_id: Job UUID
            
        Returns:
            dict containing emotion detection results per person
            
        Expected JSON format (written by Colab):
        {
          "person_1": {
            "frame_count": 120,
            "emotions": {
              "happy": 45,
              "sad": 12,
              "angry": 3,
              "neutral": 60
            }
          },
          "person_2": {...}
        }
        """
        try:
            # Search for results file
            query = f"name='{job_id}.json' and '{self.folder_ids['output_json']}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return {"error": "Results file not found"}
            
            # Download and parse JSON
            file_id = files[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            emotion_data = json.loads(file_content.read().decode('utf-8'))
            
            return emotion_data
            
        except Exception as e:
            print(f"Error reading emotion results: {e}")
            return {"error": str(e)}
    
    def get_video_download_url(self, job_id, video_type='output'):
        """
        Get a download URL for a video file.
        
        Args:
            job_id: Job UUID
            video_type: 'input' or 'output'
            
        Returns:
            Google Drive download URL
        """
        folder_key = 'output_videos' if video_type == 'output' else 'input_videos'
        
        try:
            # Search for video file
            query = f"name='{job_id}.mp4' and '{self.folder_ids[folder_key]}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, webContentLink)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                return None
            
            file_id = files[0]['id']
            
            # Generate shareable link
            # Make file accessible to anyone with the link
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            # Return direct download URL
            return f"https://drive.google.com/uc?export=download&id={file_id}"
            
        except Exception as e:
            print(f"Error getting video URL: {e}")
            return None
    
    def download_video(self, job_id, video_type='output', destination_path=None):
        """
        Download a video file from Google Drive.
        
        Args:
            job_id: Job UUID
            video_type: 'input' or 'output'
            destination_path: Local path to save file (optional)
            
        Returns:
            Path to downloaded file
        """
        folder_key = 'output_videos' if video_type == 'output' else 'input_videos'
        
        if destination_path is None:
            destination_path = settings.MEDIA_ROOT / f"{job_id}_output.mp4"
        
        # Search for video file
        query = f"name='{job_id}.mp4' and '{self.folder_ids[folder_key]}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        if not files:
            raise FileNotFoundError(f"Video file not found in Google Drive")
        
        # Download file
        file_id = files[0]['id']
        request = self.service.files().get_media(fileId=file_id)
        
        with open(destination_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        
        return destination_path


# Fallback mock service for development without Google Drive API
class MockGoogleDriveService:
    """
    Mock service for testing without Google Drive integration.
    Stores files locally and simulates Drive behavior.
    """
    
    def __init__(self):
        from pathlib import Path
        self.mock_storage = Path(settings.MEDIA_ROOT) / 'mock_drive'
        self.mock_storage.mkdir(parents=True, exist_ok=True)
        
        for folder in ['input_videos', 'output_videos', 'output_json', 'status']:
            (self.mock_storage / folder).mkdir(parents=True, exist_ok=True)
    
    def upload_video(self, video_file, drive_path, job_id):
        """Mock upload - saves locally"""
        dest = self.mock_storage / 'input_videos' / f'{job_id}.mp4'
        with open(dest, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        return str(dest)
    
    def read_status_file(self, job_id):
        """Mock status read"""
        status_file = self.mock_storage / 'status' / f'{job_id}.json'
        if status_file.exists():
            with open(status_file, 'r') as f:
                return json.load(f)
        return None
    
    def read_emotion_results(self, job_id):
        """Mock results read"""
        results_file = self.mock_storage / 'output_json' / f'{job_id}.json'
        if results_file.exists():
            with open(results_file, 'r') as f:
                return json.load(f)
        return {"mock": "data"}
    
    def get_video_download_url(self, job_id, video_type='output'):
        """Mock video URL"""
        return f"/media/mock_drive/output_videos/{job_id}.mp4"
    
    def download_video(self, job_id, video_type='output', destination_path=None):
        """Mock download"""
        return self.mock_storage / 'output_videos' / f'{job_id}.mp4'
