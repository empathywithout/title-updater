import os
import json
import re
import googleapiclient.discovery
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

VIDEO_ID = "mlBuiYg-cWA"
TITLE_TEMPLATE = '"{comment}" ← last comment = video title'
BANNED_WORDS = ["fuck", "shit", "ass", "bitch", "nigga", "nigger", "cunt", "dick", "pussy"]

def get_credentials():
    token_data = os.environ.get("TOKEN_JSON")
    info = json.loads(token_data)
    
    creds = Credentials(
        token=info.get("token"),
        refresh_token=info.get("refresh_token"),
        token_uri=info.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=info.get("client_id"),
        client_secret=info.get("client_secret"),
        scopes=["https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly"]
    )
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds

def clean_comment(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.strip().replace('\n', ' ')
    for word in BANNED_WORDS:
        text = re.sub(word, "***", text, flags=re.IGNORECASE)
    return text[:80]

def main():
    creds = get_credentials()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # Get latest comment
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=VIDEO_ID,
        order="time",
        maxResults=1
    ).execute()

    if not response.get("items"):
        print("No comments yet.")
        return

    raw = response["items"][0]["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    comment = clean_comment(raw)
    new_title = TITLE_TEMPLATE.format(comment=comment)

    # Update title
    youtube.videos().update(
        part="snippet",
        body={
            "id": VIDEO_ID,
            "snippet": {
                "title": new_title,
                "categoryId": "22"
            }
        }
    ).execute()

    print(f"Updated: {new_title}")

main()
