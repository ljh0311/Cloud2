"""
Services for handling business logic
"""

from pyspark.sql import SparkSession
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
import requests
import os
import re
from bs4 import BeautifulSoup
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SparkService:
    def __init__(self):
        self.spark = None
        self.running_job = None
    
    def _initialize_spark(self, spark_settings=None):
        """Initialize Spark session with custom settings"""
        builder = SparkSession.builder.appName("Social Media Analysis")
        
        # Apply custom settings if provided
        if spark_settings:
            if 'master' in spark_settings and spark_settings['master']:
                builder = builder.master(spark_settings['master'])
            
            # Apply executor memory if provided
            if 'executorMemory' in spark_settings and spark_settings['executorMemory']:
                builder = builder.config("spark.executor.memory", spark_settings['executorMemory'])
            
            # Apply executor cores if provided
            if 'executorCores' in spark_settings and spark_settings['executorCores']:
                builder = builder.config("spark.executor.cores", spark_settings['executorCores'])
            
            # Apply custom config if provided
            if 'customConfig' in spark_settings.get('advancedSettings', {}) and spark_settings['advancedSettings']['customConfig']:
                try:
                    custom_config = json.loads(spark_settings['advancedSettings']['customConfig'])
                    for key, value in custom_config.items():
                        builder = builder.config(key, value)
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in custom config, ignoring")
        
        self.spark = builder.getOrCreate()
        logger.info("Spark session initialized")
        return self.spark
    
    def run_analysis(self, params):
        """Run the analysis based on provided parameters"""
        try:
            logger.info(f"Starting analysis with parameters: {params}")
            
            # Initialize Spark with custom settings if provided
            if 'sparkSettings' in params:
                self._initialize_spark(params['sparkSettings'])
            else:
                self._initialize_spark()
            
            # TODO: Implement actual Spark analysis based on parameters
            # This is a placeholder that returns dummy data
            
            # Log the processing mode
            processing_mode = params.get('processingMode', 'batch')
            logger.info(f"Processing mode: {processing_mode}")
            
            # Log the dataset being used
            dataset = params.get('dataset', 'unknown')
            logger.info(f"Dataset: {dataset}")
            
            # Log the analysis types
            analysis_types = params.get('analysisTypes', {})
            logger.info(f"Analysis types: {analysis_types}")
            
            # Simulate processing time based on the complexity of the analysis
            processing_time = 120
            if processing_mode == 'streaming':
                processing_time = 180
            elif processing_mode == 'hybrid':
                processing_time = 240
            
            # Simulate records processed based on the dataset
            records_processed = 10000
            if dataset == 'twitter':
                records_processed = 15000
            elif dataset == 'reddit':
                records_processed = 20000
            elif dataset == 'yelp':
                records_processed = 8000
            elif dataset == 'amazon':
                records_processed = 25000
            
            # Simulate trends found based on the analysis types
            trends_found = 5
            if analysis_types.get('trends', False):
                trends_found = 8
            
            # Simulate sentiment scores based on the analysis types
            sentiment_scores = {
                "positive": 0.6,
                "neutral": 0.3,
                "negative": 0.1
            }
            if analysis_types.get('sentiment', False):
                sentiment_scores = {
                    "positive": 0.55,
                    "neutral": 0.25,
                    "negative": 0.2
                }
            
            logger.info("Analysis completed successfully")
            
            return {
                "processing_time": processing_time,
                "records_processed": records_processed,
                "trends_found": trends_found,
                "sentiment_scores": sentiment_scores
            }
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def stop_analysis(self):
        """Stop the running analysis"""
        try:
            logger.info("Stopping analysis")
            
            # If we have a running Spark session, stop it
            if self.spark:
                self.spark.stop()
                self.spark = None
                logger.info("Spark session stopped")
            
            # If we have a running job, cancel it
            if self.running_job:
                self.running_job.cancel()
                self.running_job = None
                logger.info("Running job cancelled")
            
            return True
        except Exception as e:
            logger.error(f"Failed to stop analysis: {str(e)}")
            raise Exception(f"Failed to stop analysis: {str(e)}")

class VisualizationService:
    def get_data(self, params):
        """Get visualization data based on parameters"""
        try:
            # TODO: Implement actual data retrieval
            # This is a placeholder that returns dummy data
            return {
                "trends": self._get_trend_data(),
                "sentiment": self._get_sentiment_data(),
                "engagement": self._get_engagement_data(),
                "topics": self._get_topic_data()
            }
        except Exception as e:
            raise Exception(f"Data retrieval failed: {str(e)}")
    
    def _get_trend_data(self):
        """Generate dummy trend data"""
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        return {
            "labels": [d.strftime('%Y-%m-%d') for d in dates],
            "datasets": [{
                "label": "Trend 1",
                "data": np.random.randint(100, 1000, 7).tolist()
            }, {
                "label": "Trend 2",
                "data": np.random.randint(100, 1000, 7).tolist()
            }]
        }
    
    def _get_sentiment_data(self):
        """Generate dummy sentiment data"""
        return {
            "labels": ["Positive", "Neutral", "Negative"],
            "datasets": [{
                "data": [60, 30, 10],
                "backgroundColor": ["#2ecc71", "#3498db", "#e74c3c"]
            }]
        }
    
    def _get_engagement_data(self):
        """Generate dummy engagement data"""
        hours = pd.date_range(end=datetime.now(), periods=24, freq='H')
        return {
            "labels": [h.strftime('%H:%M') for h in hours],
            "datasets": [{
                "label": "User Engagement",
                "data": np.random.randint(50, 500, 24).tolist()
            }]
        }
    
    def _get_topic_data(self):
        """Generate dummy topic distribution data"""
        return {
            "labels": ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"],
            "datasets": [{
                "data": np.random.randint(100, 1000, 5).tolist(),
                "backgroundColor": [
                    "#3498db",
                    "#2ecc71",
                    "#e74c3c",
                    "#f1c40f",
                    "#9b59b6"
                ]
            }]
        }

class DatasetService:
    """Service for retrieving and managing datasets"""
    
    def __init__(self, data_dir="data"):
        """Initialize the dataset service"""
        self.data_dir = data_dir
        self.datasets_cache = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "twitter"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "reddit"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "yelp"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "amazon"), exist_ok=True)
        
        logger.info(f"Dataset service initialized with data directory: {data_dir}")
    
    def search_datasets(self, query, source="kaggle", limit=5):
        """Search for datasets based on query"""
        logger.info(f"Searching for datasets with query: {query}, source: {source}")
        
        if source == "kaggle":
            return self._search_kaggle(query, limit)
        elif source == "reddit":
            return self._search_reddit(query, limit)
        elif source == "twitter":
            return self._search_twitter(query, limit)
        else:
            # Default to a general web search
            return self._search_general(query, limit)
    
    def _search_kaggle(self, query, limit=5):
        """Search for datasets on Kaggle"""
        try:
            # This is a simplified version - in production, you would use Kaggle API
            # For now, we'll simulate results
            
            # Simulate network delay
            time.sleep(1)
            
            # Sample datasets related to social media
            sample_datasets = [
                {
                    "id": "kaggle_twitter_1",
                    "title": "Twitter Sentiment Analysis Dataset",
                    "description": "A dataset of 1.6 million tweets with sentiment labels",
                    "size": "250MB",
                    "records": 1600000,
                    "url": "https://www.kaggle.com/datasets/kazanova/sentiment140",
                    "format": "CSV"
                },
                {
                    "id": "kaggle_reddit_1",
                    "title": "Reddit Comments Dataset",
                    "description": "A collection of Reddit comments from various subreddits",
                    "size": "500MB",
                    "records": 3000000,
                    "url": "https://www.kaggle.com/datasets/reddit/reddit-comments-may-2015",
                    "format": "JSON"
                },
                {
                    "id": "kaggle_yelp_1",
                    "title": "Yelp Reviews Dataset",
                    "description": "Business reviews from the Yelp dataset challenge",
                    "size": "2.8GB",
                    "records": 5200000,
                    "url": "https://www.kaggle.com/datasets/yelp-dataset/yelp-dataset",
                    "format": "JSON"
                },
                {
                    "id": "kaggle_amazon_1",
                    "title": "Amazon Product Reviews",
                    "description": "Product reviews from Amazon across multiple categories",
                    "size": "3.5GB",
                    "records": 7800000,
                    "url": "https://www.kaggle.com/datasets/cynthiarempel/amazon-us-customer-reviews-dataset",
                    "format": "CSV"
                },
                {
                    "id": "kaggle_social_1",
                    "title": "Social Media Trends 2023",
                    "description": "Trending topics and hashtags across social platforms",
                    "size": "150MB",
                    "records": 500000,
                    "url": "https://www.kaggle.com/datasets/example/social-trends-2023",
                    "format": "CSV"
                },
                {
                    "id": "kaggle_instagram_1",
                    "title": "Instagram Influencer Dataset",
                    "description": "Data on top Instagram influencers and their engagement metrics",
                    "size": "80MB",
                    "records": 100000,
                    "url": "https://www.kaggle.com/datasets/example/instagram-influencers",
                    "format": "CSV"
                }
            ]
            
            # Filter based on query
            if query:
                filtered_datasets = [
                    ds for ds in sample_datasets 
                    if query.lower() in ds["title"].lower() or query.lower() in ds["description"].lower()
                ]
            else:
                filtered_datasets = sample_datasets
            
            # Return limited results
            return filtered_datasets[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Kaggle: {str(e)}")
            return []
    
    def _search_reddit(self, query, limit=5):
        """Search for datasets from Reddit"""
        # Similar implementation as Kaggle but for Reddit
        # This would use Reddit API in production
        time.sleep(0.8)
        
        sample_datasets = [
            {
                "id": "reddit_data_1",
                "title": "r/DataScience Discussions",
                "description": "Discussions from the DataScience subreddit",
                "size": "120MB",
                "records": 250000,
                "url": "https://www.reddit.com/r/datascience",
                "format": "JSON"
            },
            {
                "id": "reddit_data_2",
                "title": "r/MachineLearning Posts",
                "description": "Posts and comments from the MachineLearning subreddit",
                "size": "200MB",
                "records": 350000,
                "url": "https://www.reddit.com/r/machinelearning",
                "format": "JSON"
            }
        ]
        
        if query:
            filtered_datasets = [
                ds for ds in sample_datasets 
                if query.lower() in ds["title"].lower() or query.lower() in ds["description"].lower()
            ]
        else:
            filtered_datasets = sample_datasets
        
        return filtered_datasets[:limit]
    
    def _search_twitter(self, query, limit=5):
        """Search for datasets from Twitter"""
        # Similar implementation as Kaggle but for Twitter
        # This would use Twitter API in production
        time.sleep(0.8)
        
        sample_datasets = [
            {
                "id": "twitter_data_1",
                "title": "COVID-19 Twitter Dataset",
                "description": "Tweets related to COVID-19 pandemic",
                "size": "500MB",
                "records": 1000000,
                "url": "https://example.com/covid-twitter-dataset",
                "format": "JSON"
            },
            {
                "id": "twitter_data_2",
                "title": "Political Discourse on Twitter",
                "description": "Political tweets and discussions",
                "size": "350MB",
                "records": 750000,
                "url": "https://example.com/political-twitter-dataset",
                "format": "JSON"
            }
        ]
        
        if query:
            filtered_datasets = [
                ds for ds in sample_datasets 
                if query.lower() in ds["title"].lower() or query.lower() in ds["description"].lower()
            ]
        else:
            filtered_datasets = sample_datasets
        
        return filtered_datasets[:limit]
    
    def _search_general(self, query, limit=5):
        """General web search for datasets"""
        # This would use a general search API in production
        time.sleep(1)
        
        # Combine results from different sources
        kaggle_results = self._search_kaggle(query, limit=2)
        reddit_results = self._search_reddit(query, limit=2)
        twitter_results = self._search_twitter(query, limit=1)
        
        combined_results = kaggle_results + reddit_results + twitter_results
        random.shuffle(combined_results)
        
        return combined_results[:limit]
    
    def download_dataset(self, dataset_id, destination=None):
        """Download a dataset by ID"""
        logger.info(f"Downloading dataset with ID: {dataset_id}")
        
        try:
            # In a real implementation, this would download the actual dataset
            # For now, we'll simulate the download
            
            # Simulate network delay for download
            time.sleep(2)
            
            # Determine dataset type from ID
            dataset_type = "unknown"
            if "twitter" in dataset_id:
                dataset_type = "twitter"
            elif "reddit" in dataset_id:
                dataset_type = "reddit"
            elif "yelp" in dataset_id:
                dataset_type = "yelp"
            elif "amazon" in dataset_id:
                dataset_type = "amazon"
            
            # Set destination path
            if destination is None:
                destination = os.path.join(self.data_dir, dataset_type, f"{dataset_id}.csv")
            
            # Create a dummy dataset file
            with open(destination, 'w') as f:
                f.write("id,text,timestamp,user_id,sentiment\n")
                # Write some dummy data
                for i in range(100):
                    sentiment = random.choice(["positive", "neutral", "negative"])
                    f.write(f"{i},This is a sample text for {dataset_type} dataset,2023-01-{random.randint(1,30)},user_{random.randint(1000,9999)},{sentiment}\n")
            
            logger.info(f"Dataset downloaded to: {destination}")
            
            return {
                "success": True,
                "file_path": destination,
                "records": 100,
                "message": f"Dataset downloaded successfully to {destination}"
            }
            
        except Exception as e:
            logger.error(f"Error downloading dataset: {str(e)}")
            return {
                "success": False,
                "message": f"Error downloading dataset: {str(e)}"
            }
    
    def get_available_datasets(self):
        """Get a list of already downloaded datasets"""
        available_datasets = []
        
        # Scan the data directory for datasets
        for dataset_type in ["twitter", "reddit", "yelp", "amazon"]:
            type_dir = os.path.join(self.data_dir, dataset_type)
            if os.path.exists(type_dir):
                for filename in os.listdir(type_dir):
                    if filename.endswith('.csv') or filename.endswith('.json'):
                        file_path = os.path.join(type_dir, filename)
                        file_size = os.path.getsize(file_path)
                        
                        # Count lines in the file to estimate records
                        record_count = 0
                        try:
                            with open(file_path, 'r') as f:
                                for _ in f:
                                    record_count += 1
                        except:
                            record_count = -1
                        
                        available_datasets.append({
                            "id": os.path.splitext(filename)[0],
                            "title": f"{dataset_type.capitalize()} Dataset: {os.path.splitext(filename)[0]}",
                            "file_path": file_path,
                            "size": f"{file_size / (1024*1024):.2f}MB",
                            "records": record_count - 1 if record_count > 0 else "Unknown",  # Subtract header row
                            "type": dataset_type,
                            "format": os.path.splitext(filename)[1][1:].upper()
                        })
        
        return available_datasets
    
    def scrape_twitter_data(self, query, limit=100):
        """Scrape Twitter data based on a query (simulated)"""
        logger.info(f"Scraping Twitter data for query: {query}, limit: {limit}")
        
        try:
            # In a real implementation, this would use Twitter API or web scraping
            # For now, we'll simulate the scraping
            
            # Simulate network delay
            time.sleep(2)
            
            # Generate simulated tweets
            tweets = []
            for i in range(limit):
                sentiment = random.choice(["positive", "neutral", "negative"])
                tweet = {
                    "id": f"tweet_{i}_{int(time.time())}",
                    "text": f"This is a simulated tweet about {query}. #{query.replace(' ', '')} #BigData",
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat(),
                    "user": f"user_{random.randint(1000, 9999)}",
                    "likes": random.randint(0, 1000),
                    "retweets": random.randint(0, 200),
                    "sentiment": sentiment
                }
                tweets.append(tweet)
            
            # Save to a file
            filename = f"twitter_scraped_{query.replace(' ', '_')}_{int(time.time())}.csv"
            file_path = os.path.join(self.data_dir, "twitter", filename)
            
            with open(file_path, 'w') as f:
                f.write("id,text,timestamp,user,likes,retweets,sentiment\n")
                for tweet in tweets:
                    f.write(f"{tweet['id']},{tweet['text']},{tweet['timestamp']},{tweet['user']},{tweet['likes']},{tweet['retweets']},{tweet['sentiment']}\n")
            
            logger.info(f"Scraped {len(tweets)} tweets and saved to {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "records": len(tweets),
                "message": f"Successfully scraped {len(tweets)} tweets related to '{query}'"
            }
            
        except Exception as e:
            logger.error(f"Error scraping Twitter data: {str(e)}")
            return {
                "success": False,
                "message": f"Error scraping Twitter data: {str(e)}"
            }
    
    def scrape_reddit_data(self, subreddit, limit=100):
        """Scrape Reddit data from a subreddit (simulated)"""
        logger.info(f"Scraping Reddit data for subreddit: {subreddit}, limit: {limit}")
        
        try:
            # In a real implementation, this would use Reddit API or web scraping
            # For now, we'll simulate the scraping
            
            # Simulate network delay
            time.sleep(2)
            
            # Generate simulated Reddit posts
            posts = []
            for i in range(limit):
                sentiment = random.choice(["positive", "neutral", "negative"])
                post = {
                    "id": f"post_{i}_{int(time.time())}",
                    "title": f"Simulated Reddit post about {subreddit}",
                    "text": f"This is a simulated Reddit post in r/{subreddit}. Discussing big data analytics and social media trends.",
                    "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
                    "author": f"redditor_{random.randint(1000, 9999)}",
                    "upvotes": random.randint(0, 5000),
                    "comments": random.randint(0, 500),
                    "sentiment": sentiment
                }
                posts.append(post)
            
            # Save to a file
            filename = f"reddit_scraped_{subreddit}_{int(time.time())}.csv"
            file_path = os.path.join(self.data_dir, "reddit", filename)
            
            with open(file_path, 'w') as f:
                f.write("id,title,text,timestamp,author,upvotes,comments,sentiment\n")
                for post in posts:
                    f.write(f"{post['id']},{post['title']},{post['text']},{post['timestamp']},{post['author']},{post['upvotes']},{post['comments']},{post['sentiment']}\n")
            
            logger.info(f"Scraped {len(posts)} Reddit posts and saved to {file_path}")
            
            return {
                "success": True,
                "file_path": file_path,
                "records": len(posts),
                "message": f"Successfully scraped {len(posts)} posts from r/{subreddit}"
            }
            
        except Exception as e:
            logger.error(f"Error scraping Reddit data: {str(e)}")
            return {
                "success": False,
                "message": f"Error scraping Reddit data: {str(e)}"
            } 