"""
Reddit data scraper module.

This module provides functionality to scrape data from Reddit using PRAW (Python Reddit API Wrapper),
which is the official and ethical way to access Reddit data according to their API terms of service.
"""

import os
import csv
import time
import logging
import datetime
import pandas as pd
from typing import Dict, List, Any, Optional
import praw
from praw.models import Submission
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path so we can import the config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditScraper:
    """Class for scraping Reddit data using PRAW."""
    
    def __init__(self):
        """
        Initialize the Reddit scraper with API credentials from environment variables.
        """
        try:
            # Get credentials from environment variables
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'DrivingSG Analysis Bot v1.0')
            
            if not all([client_id, client_secret]):
                raise ValueError("Missing Reddit API credentials. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")
            
            # Initialize the Reddit API client
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            logger.info("Successfully initialized Reddit API client")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API client: {str(e)}")
            raise
    
    def scrape_subreddit(self, subreddit_name: str, limit: int = 100, 
                         sort_by: str = 'hot', time_filter: str = 'all') -> List[Dict[str, Any]]:
        """
        Scrape posts and comments from a subreddit.
        
        Args:
            subreddit_name: Name of the subreddit to scrape (without the 'r/')
            limit: Maximum number of posts to scrape
            sort_by: How to sort posts ('hot', 'new', 'top', 'rising', 'controversial')
            time_filter: Time filter for 'top' and 'controversial' ('all', 'day', 'week', 'month', 'year')
            
        Returns:
            List of dictionaries containing post and comment data
        """
        try:
            logger.info(f"Scraping {limit} posts from r/{subreddit_name} sorted by {sort_by}")
            
            # Get the subreddit
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get posts based on sort method
            if sort_by == 'hot':
                posts = subreddit.hot(limit=limit)
            elif sort_by == 'new':
                posts = subreddit.new(limit=limit)
            elif sort_by == 'top':
                posts = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort_by == 'rising':
                posts = subreddit.rising(limit=limit)
            elif sort_by == 'controversial':
                posts = subreddit.controversial(time_filter=time_filter, limit=limit)
            else:
                logger.error(f"Invalid sort_by value: {sort_by}")
                raise ValueError(f"Invalid sort_by value: {sort_by}. Must be one of: hot, new, top, rising, controversial")
            
            # Process posts
            post_data = []
            for post in posts:
                try:
                    # Add a small delay to avoid hitting rate limits
                    time.sleep(0.5)
                    
                    # Get comments
                    post.comments.replace_more(limit=0)  # Only get top-level comments
                    comments = []
                    for comment in post.comments:
                        try:
                            comments.append({
                                'id': comment.id,
                                'text': comment.body,
                                'score': comment.score,
                                'created_utc': datetime.datetime.fromtimestamp(comment.created_utc).isoformat(),
                                'author': str(comment.author) if comment.author else '[deleted]'
                            })
                        except Exception as e:
                            logger.warning(f"Error processing comment {comment.id}: {str(e)}")
                            continue
                    
                    # Extract post data
                    post_dict = {
                        'id': post.id,
                        'title': post.title,
                        'text': post.selftext,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.datetime.fromtimestamp(post.created_utc).isoformat(),
                        'author': str(post.author) if post.author else '[deleted]',
                        'flair': post.link_flair_text,
                        'comments': comments
                    }
                    post_data.append(post_dict)
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(post_data)} posts from r/{subreddit_name}")
            return post_data
            
        except Exception as e:
            logger.error(f"Error scraping subreddit {subreddit_name}: {str(e)}")
            raise

    def save_to_json(self, posts: List[Dict[str, Any]], output_dir: str, 
                    subreddit_name: str) -> str:
        """
        Save scraped posts to a JSON file.
        
        Args:
            posts: List of post dictionaries
            output_dir: Directory to save the JSON file
            subreddit_name: Name of the subreddit (for filename)
            
        Returns:
            Path to the saved JSON file
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get date range from posts
        if posts:
            dates = [datetime.datetime.fromisoformat(post['created_utc']) for post in posts]
            start_date = min(dates).strftime('%Y%m%d')
            end_date = max(dates).strftime('%Y%m%d')
            date_range = f"{start_date}-{end_date}"
        else:
            date_range = "no_data"
        
        # Generate filename with new format
        scrape_date = datetime.datetime.now().strftime('%Y%m%d')
        filename = f"Reddit_{subreddit_name}_{scrape_date}_{date_range}.json"
        file_path = os.path.join(output_dir, filename)
        
        # Write to JSON
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'subreddit': subreddit_name,
                        'scrape_date': scrape_date,
                        'date_range': date_range,
                        'post_count': len(posts)
                    },
                    'posts': posts
                }, f, indent=2, ensure_ascii=False)
                    
            logger.info(f"Saved {len(posts)} posts to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving posts to JSON: {str(e)}")
            raise

def scrape_reddit_data(subreddit: str, limit: int = 100, 
                       output_dir: str = 'data/reddit') -> Dict[str, Any]:
    """
    Scrape data from a subreddit and save to JSON.
    
    Args:
        subreddit: Name of the subreddit to scrape (without the 'r/')
        limit: Maximum number of posts to scrape
        output_dir: Directory to save the JSON file
        
    Returns:
        Dictionary with scraping results
    """
    try:
        # Initialize scraper
        scraper = RedditScraper()
        
        # Scrape posts
        posts = scraper.scrape_subreddit(subreddit, limit=limit)
        
        # Save to JSON
        file_path = scraper.save_to_json(posts, output_dir, subreddit)
        
        return {
            "success": True,
            "file_path": file_path,
            "records": len(posts),
            "message": f"Successfully scraped {len(posts)} posts from r/{subreddit}"
        }
    except Exception as e:
        logger.error(f"Error in scrape_reddit_data: {str(e)}")
        return {
            "success": False,
            "message": f"Error scraping Reddit data: {str(e)}"
        }

if __name__ == "__main__":
    # Example usage
    result = scrape_reddit_data("drivingsg", limit=10)
    print(result) 