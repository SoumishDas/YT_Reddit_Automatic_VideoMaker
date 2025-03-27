# import necessary modules
import sys                # for handling command-line arguments
import os                 # for file path operations
import google_auth_oauthlib.flow  # for handling OAuth 2.0 flow for user authentication
import googleapiclient.discovery  # for building the YouTube API service object
import googleapiclient.errors     # for handling API errors
import googleapiclient.http       # for handling media upload operations

# API service details and client secrets file name
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
CLIENT_SECRETS_FILE = "client_secrets.json"  # This file should be downloaded from Google Cloud Console

def get_authenticated_service():
    """
    This function handles the OAuth 2.0 authentication process to obtain credentials for the YouTube Data API.
    It uses the client secrets file and a set of defined scopes to get access.
    Returns an authenticated YouTube API client service object.
    """
    # Define the scope needed to upload videos
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    
    # Initialize the OAuth flow from the client_secrets.json file and defined scopes.
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes)
    
    # Run the OAuth flow in the console. This will open a URL for the user to authenticate.
    credentials = flow.run_local_server(port=0, open_browser=True)

    
    # Build and return the YouTube API service using the obtained credentials.
    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def upload_video(file_path, title, description, categoryId="22", privacyStatus="public"):
    """
    Uploads a video file to YouTube using the authenticated service.
    
    Parameters:
    - file_path: Path to the video file on your local system.
    - title: Title for the YouTube video.
    - description: Description for the video.
    - categoryId: Category ID for the video (default is 22, which usually corresponds to People & Blogs).
    - privacyStatus: Video privacy status (e.g., "public", "private", "unlisted").
    
    Returns:
    - The response from the YouTube API which includes details like the video ID.
    """
    # Obtain an authenticated YouTube service object.
    youtube = get_authenticated_service()

    # Create a dictionary for the video's metadata including snippet and status.
    body = {
        "snippet": {
            "title": title,             # Video title
            "description": description, # Video description
            "tags": ["Shorts", "YouTube Shorts"],  # Tags to help classify the video as a Short
            "categoryId": categoryId    # Video category ID
        },
        "status": {
            "privacyStatus": privacyStatus  # Video privacy setting
        }
    }

    # Prepare the media file for upload using a resumable upload method.
    # chunksize=-1 indicates that the file should be uploaded in a single request.
    media_file = googleapiclient.http.MediaFileUpload(
        file_path, chunksize=-1, resumable=True
    )

    # Create an API request to insert the video using the metadata and media file.
    request = youtube.videos().insert(
        part="snippet,status",  # Specify which parts of the video resource are being set.
        body=body,              # The metadata dictionary created above.
        media_body=media_file   # The media file to be uploaded.
    )

    print("Uploading video...")
    response = None

    # The request is performed in a loop to handle resumable uploads.
    # Each call to next_chunk() uploads the next chunk of the video.
    while response is None:
        status, response = request.next_chunk()
        if status:
            # Print upload progress in percentage
            print(f"Upload progress: {int(status.progress() * 100)}%")
    
    # Once the response is received, the upload is complete.
    print("Upload complete!")
    # Extract the video ID from the response, which can be used to view the video.
    print("Video ID:", response.get("id"))
    return response
