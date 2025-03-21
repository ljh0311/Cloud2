"""
Reddit API configuration

This file contains configuration settings for the Reddit API.
For security, in a production environment, these values should be stored
as environment variables or in a secure configuration system.
"""

# Reddit API credentials
# Replace these with your actual Reddit API credentials
REDDIT_CLIENT_ID = "YOUR_CLIENT_ID"
REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDDIT_USER_AGENT = "python:social-media-analyzer:v1.0 (by /u/your_username)"

# API usage limits
MAX_POSTS_PER_REQUEST = 100  # Maximum number of posts to retrieve in a single request
REQUEST_DELAY = 1.0  # Delay between requests in seconds to avoid rate limiting 