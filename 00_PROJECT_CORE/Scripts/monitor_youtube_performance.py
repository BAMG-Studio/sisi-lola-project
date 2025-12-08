"""Monitor YouTube Video Performance - Views, Engagement, Comments"""
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Recent video IDs
VIDEO_IDS = [
    "HQguupXW9BU",  # First authentic video
    "lMrtDuBe6-s",  # Agriculture tech
    "x123Obl7uro"   # Nigerian music AI
]

creds = Credentials.from_authorized_user_file("token_youtube.json")
youtube = build('youtube', 'v3', credentials=creds)

print("=" * 70)
print("SISI LOLA YOUTUBE PERFORMANCE MONITOR")
print("=" * 70)
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

total_views = 0
total_likes = 0
total_comments = 0

for i, video_id in enumerate(VIDEO_IDS, 1):
    # Get video statistics
    response = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    ).execute()
    
    if response['items']:
        video = response['items'][0]
        title = video['snippet']['title']
        stats = video['statistics']
        
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        total_views += views
        total_likes += likes
        total_comments += comments
        
        print(f"[{i}] {title[:50]}...")
        print(f"    URL: https://youtube.com/watch?v={video_id}")
        print(f"    Views: {views:,}")
        print(f"    Likes: {likes:,}")
        print(f"    Comments: {comments:,}")
        print(f"    Engagement: {(likes/views*100 if views > 0 else 0):.2f}%\n")

print("=" * 70)
print("TOTAL PERFORMANCE")
print("=" * 70)
print(f"Total Views: {total_views:,}")
print(f"Total Likes: {total_likes:,}")
print(f"Total Comments: {total_comments:,}")
print(f"Avg Engagement: {(total_likes/total_views*100 if total_views > 0 else 0):.2f}%")
print(f"\nVideos Tracked: {len(VIDEO_IDS)}")
