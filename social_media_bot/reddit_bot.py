"""Reddit Automation Bot for Sisi Lola
Handles Reddit posts, comments, and community management.
"""

import os
import praw
from typing import Dict, List

class RedditBot:
    def __init__(self):
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_PASSWORD')
        self.user_agent = 'Sisi Lola Bot v1.0 by u/sisilolalive'
        
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            user_agent=self.user_agent
        )
    
    def submit_text_post(self, subreddit: str, title: str, text: str) -> Dict:
        """Submit a text post to a subreddit"""
        subreddit_obj = self.reddit.subreddit(subreddit)
        submission = subreddit_obj.submit(title=title, selftext=text)
        
        return {
            'id': submission.id,
            'url': submission.url,
            'permalink': submission.permalink
        }
    
    def submit_link_post(self, subreddit: str, title: str, url: str) -> Dict:
        """Submit a link post to a subreddit"""
        subreddit_obj = self.reddit.subreddit(subreddit)
        submission = subreddit_obj.submit(title=title, url=url)
        
        return {
            'id': submission.id,
            'url': submission.url,
            'permalink': submission.permalink
        }
    
    def submit_image_post(self, subreddit: str, title: str, image_path: str) -> Dict:
        """Submit an image post to a subreddit"""
        subreddit_obj = self.reddit.subreddit(subreddit)
        submission = subreddit_obj.submit_image(title=title, image_path=image_path)
        
        return {
            'id': submission.id,
            'url': submission.url,
            'permalink': submission.permalink
        }
    
    def comment_on_post(self, submission_id: str, comment_text: str) -> Dict:
        """Comment on a Reddit post"""
        submission = self.reddit.submission(id=submission_id)
        comment = submission.reply(comment_text)
        
        return {
            'comment_id': comment.id,
            'permalink': comment.permalink
        }
    
    def get_subreddit_posts(self, subreddit: str, limit: int = 25, 
                           sort: str = 'hot') -> List[Dict]:
        """Get posts from a subreddit"""
        subreddit_obj = self.reddit.subreddit(subreddit)
        
        if sort == 'hot':
            posts = subreddit_obj.hot(limit=limit)
        elif sort == 'new':
            posts = subreddit_obj.new(limit=limit)
        elif sort == 'top':
            posts = subreddit_obj.top(limit=limit)
        else:
            posts = subreddit_obj.hot(limit=limit)
        
        return [
            {
                'id': post.id,
                'title': post.title,
                'score': post.score,
                'url': post.url,
                'num_comments': post.num_comments,
                'created_utc': post.created_utc
            }
            for post in posts
        ]
    
    def get_user_posts(self, limit: int = 25) -> List[Dict]:
        """Get posts from authenticated user"""
        user = self.reddit.user.me()
        posts = user.submissions.new(limit=limit)
        
        return [
            {
                'id': post.id,
                'title': post.title,
                'subreddit': post.subreddit.display_name,
                'score': post.score,
                'url': post.url
            }
            for post in posts
        ]

if __name__ == "__main__":
    bot = RedditBot()
    print("Reddit Bot initialized successfully!")
    print(f"Authenticated as: u/{bot.reddit.user.me().name}")
