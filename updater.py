import os
import json
import re
import googleapiclient.discovery
import google.auth.transport.requests
from google.oauth2.credentials import Credentials

VIDEO_ID = "YOUR_VIDEO_ID_HERE"
TITLE_TEMPLATE = '"{comment}" ← last comment = video title'
BANNED_WORDS = ["fuck", "shit", "ass", "bitch", "nigga", "nigger", "cunt", "dick", "pussy"]

def get_credentials():
    token_data = os.environ.get("TOKEN_JSON")
    creds = Credentials.from_authorized_user_info(json.loads(token_data))
    if creds.expired and creds.refresh_token:
        creds.refresh(google.auth.transport.requests.Request())
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
