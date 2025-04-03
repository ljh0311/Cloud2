"""
Views for the web application
"""

from flask import Blueprint, render_template, jsonify, request, send_file
from .services import (
    SparkService,
    VisualizationService,
    DatasetService,
    AnalysisService,
)
import os
from datetime import datetime, timedelta
import random
import praw
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
from collections import Counter
import json
import logging
from flask import current_app

main_bp = Blueprint("main", __name__)
dataset_service = DatasetService()
analysis_service = AnalysisService()

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="DrivingSG Analysis Bot v1.0",
)

# Data directory path
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)


@main_bp.route("/")
def index():
    """Home page with overview and statistics"""
    return render_template("index.html", title="Big Data Analytics Dashboard")


@main_bp.route("/analysis")
def analysis():
    """Data analysis and processing page"""
    return render_template("analysis.html", title="Data Analysis")


@main_bp.route("/visualizations")
def visualizations():
    """Render the visualizations page"""
    return render_template("visualizations.html", title="Visualizations")


@main_bp.route("/flask_path_test")
def flask_path_test():
    """Test page for checking file paths in Flask"""
    return render_template("flask_path_tester.html", title="Flask Path Tester")


@main_bp.route("/tracking")
def tracking():
    """Progress tracking page"""
    # Generate sample progress data
    progress_data = {
        "overall_progress": 65.5,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "components": {
            "Data Storage": {
                "progress": 85.0,
                "files": {
                    "storage_service.py": True,
                    "data_connector.py": True,
                    "cache_manager.py": False,
                },
            },
            "MapReduce": {
                "progress": 70.0,
                "files": {
                    "mapper.py": True,
                    "reducer.py": True,
                    "job_scheduler.py": False,
                },
            },
            "Spark Processing": {
                "progress": 60.0,
                "files": {
                    "spark_service.py": True,
                    "streaming_processor.py": False,
                    "batch_processor.py": True,
                },
            },
            "Web Interface": {
                "progress": 75.0,
                "files": {"views.py": True, "services.py": True, "templates/": True},
            },
        },
    }
    return render_template("tracking.html", progress_data=progress_data)


@main_bp.route("/tracking/dashboard")
def tracking_dashboard():
    """Project tracking dashboard"""
    # Generate sample progress data for the dashboard
    progress_data = {"overall_progress": 68.5, "days_until_deadline": 14}

    # Team progress data
    team_progress = {
        "JH": {"individual_development": 85.0, "tasks_completed": 8, "tasks_total": 10},
        "Darrel": {
            "individual_development": 70.0,
            "tasks_completed": 7,
            "tasks_total": 10,
        },
        "Xuan Yu": {
            "individual_development": 65.0,
            "tasks_completed": 6,
            "tasks_total": 10,
        },
        "Javin": {
            "individual_development": 75.0,
            "tasks_completed": 7,
            "tasks_total": 10,
        },
    }

    # Integration status
    integration_status = {
        "storage_to_mapreduce": {
            "status": "completed",
            "message": "Successfully integrated data storage with MapReduce",
            "last_sync": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        "mapreduce_to_spark": {
            "status": "in_progress",
            "message": "Working on connecting MapReduce output to Spark",
            "last_sync": datetime.now().strftime("%Y-%m-%d"),
        },
        "spark_to_visualization": {
            "status": "pending",
            "message": "Not started yet",
            "last_sync": "N/A",
        },
        "web_to_visualization": {
            "status": "in_progress",
            "message": "Implementing web interface for visualizations",
            "last_sync": datetime.now().strftime("%Y-%m-%d"),
        },
    }

    # Overdue tasks
    overdue_tasks = [
        {
            "task": "Implement real-time streaming",
            "phase": "Individual Development",
            "due_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "progress": 60,
        },
        {
            "task": "Complete MapReduce to Spark integration",
            "phase": "Integration",
            "due_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "progress": 75,
        },
    ]

    return render_template(
        "tracking/dashboard.html",
        progress_data=progress_data,
        team_progress=team_progress,
        integration_status=integration_status,
        overdue_tasks=overdue_tasks,
    )


@main_bp.route("/api/run-analysis", methods=["POST"])
def run_analysis():
    """API endpoint to trigger data analysis"""
    try:
        # Get analysis parameters from request
        params = request.get_json()

        # Initialize spark service
        spark_service = SparkService()

        # Run analysis with the comprehensive parameters
        result = spark_service.run_analysis(params)

        return jsonify(
            {
                "status": "success",
                "message": "Analysis completed successfully",
                "data": result,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/stop-analysis", methods=["POST"])
def stop_analysis():
    """API endpoint to stop running analysis"""
    try:
        # Get stop parameters from request
        params = request.get_json()

        # Initialize spark service
        spark_service = SparkService()

        # Stop the analysis
        spark_service.stop_analysis()

        return jsonify(
            {"status": "success", "message": "Analysis stopped successfully"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/get-visualizations")
def get_visualizations():
    """API endpoint to get visualization data"""
    try:
        # Get visualization parameters from query string
        params = request.args.to_dict()

        # Initialize visualization service
        viz_service = VisualizationService()

        # Get visualization data
        data = viz_service.get_data(params)

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/progress")
def get_progress():
    """API endpoint to get progress data"""
    try:
        # Generate sample progress data
        progress_data = {
            "overall_progress": 65.5,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "components": {
                "Data Storage": {
                    "progress": 85.0,
                    "files": {
                        "storage_service.py": True,
                        "data_connector.py": True,
                        "cache_manager.py": False,
                    },
                },
                "MapReduce": {
                    "progress": 70.0,
                    "files": {
                        "mapper.py": True,
                        "reducer.py": True,
                        "job_scheduler.py": False,
                    },
                },
                "Spark Processing": {
                    "progress": 60.0,
                    "files": {
                        "spark_service.py": True,
                        "streaming_processor.py": False,
                        "batch_processor.py": True,
                    },
                },
                "Web Interface": {
                    "progress": 75.0,
                    "files": {
                        "views.py": True,
                        "services.py": True,
                        "templates/": True,
                    },
                },
            },
        }

        return jsonify({"status": "success", "data": progress_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/progress/update", methods=["POST"])
def update_progress():
    """API endpoint to update project progress"""
    try:
        data = request.get_json()

        # In a real application, this would update a database
        # For now, we'll just return success

        return jsonify(
            {"status": "success", "message": "Progress updated successfully"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/integration/update", methods=["POST"])
def update_integration():
    """API endpoint to update integration status"""
    try:
        data = request.get_json()

        # In a real application, this would update a database
        # For now, we'll just return success

        return jsonify(
            {"status": "success", "message": "Integration status updated successfully"}
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/search-datasets")
def search_datasets():
    """API endpoint to search for datasets"""
    try:
        query = request.args.get("query", "")
        source = request.args.get("source", "all")
        limit = int(request.args.get("limit", 5))

        results = dataset_service.search_datasets(query, source, limit)

        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/download-dataset", methods=["POST"])
def download_dataset():
    """API endpoint to download a dataset"""
    try:
        params = request.get_json()
        dataset_id = params.get("dataset_id")

        if not dataset_id:
            return jsonify({"status": "error", "message": "Dataset ID is required"})

        result = dataset_service.download_dataset(dataset_id)

        return jsonify(
            {
                "status": "success" if result["success"] else "error",
                "message": result["message"],
                "data": result,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/datasets")
def available_datasets():
    """API endpoint to get available datasets"""
    try:
        datasets = dataset_service.get_available_datasets()

        return jsonify({"status": "success", "data": datasets})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@main_bp.route("/api/scrape-reddit", methods=["POST"])
def scrape_reddit():
    """Scrape data from r/drivingsg subreddit"""
    try:
        data = request.get_json()
        subreddit = data.get("subreddit", "drivingsg")
        limit = int(data.get("limit", 500))
        sort_by = data.get("sort_by", "new")
        post_type = data.get("post_type", "all")

        # Get subreddit instance
        sub = reddit.subreddit(subreddit)

        # Get posts based on sort type
        if sort_by == "hot":
            posts = sub.hot(limit=limit)
        elif sort_by == "top":
            posts = sub.top(limit=limit)
        elif sort_by == "controversial":
            posts = sub.controversial(limit=limit)
        else:
            posts = sub.new(limit=limit)

        # Collect post data
        posts_data = []
        for post in posts:
            # Skip if post type filter is active and post doesn't match
            if post_type != "all":
                if (
                    post_type == "discussion"
                    and not post.link_flair_text == "Discussion"
                ):
                    continue
                if post_type == "question" and not post.link_flair_text == "Question":
                    continue
                if (
                    post_type == "incident"
                    and not post.link_flair_text == "Traffic Incident"
                ):
                    continue

            # Get post data
            post_dict = {
                "id": post.id,
                "title": post.title,
                "text": post.selftext,
                "created_utc": post.created_utc,
                "score": post.score,
                "num_comments": post.num_comments,
                "flair": post.link_flair_text,
                "author": str(post.author),
                "comments": [],
            }

            # Get comments
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                post_dict["comments"].append(
                    {
                        "id": comment.id,
                        "text": comment.body,
                        "created_utc": comment.created_utc,
                        "score": comment.score,
                        "author": str(comment.author),
                    }
                )

            posts_data.append(post_dict)

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"drivingsg_data_{timestamp}.json"
        filepath = os.path.join("data", "reddit", filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(posts_data, f)

        return jsonify(
            {
                "success": True,
                "message": f"Successfully scraped {len(posts_data)} posts",
                "file_path": filepath,
                "records": len(posts_data),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@main_bp.route("/api/analyze-reddit-data", methods=["POST"])
def analyze_reddit_data():
    """Analyze scraped Reddit data"""
    try:
        data = request.get_json()
        file_path = data.get("file_path")
        analysis_types = data.get("analysis_types", [])

        # Get the project root directory
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        # Convert input file path to absolute path if it's relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(project_root, file_path)

        # Load the data
        with open(file_path, "r", encoding="utf-8") as f:
            posts_data = json.load(f)

        # Initialize results dictionary
        results = {}

        # Perform sentiment analysis
        if "sentiment" in analysis_types:
            sentiment_results = analyze_sentiment(posts_data)
            results["sentiment_analysis"] = sentiment_results

        # Perform trend detection
        if "trend" in analysis_types:
            trend_results = analyze_trends(posts_data)
            results["trend_analysis"] = trend_results

        # Perform traffic incident analysis
        if "traffic" in analysis_types:
            traffic_results = analyze_traffic_incidents(posts_data)
            results["traffic_analysis"] = traffic_results

        # Perform location analysis
        if "location" in analysis_types:
            location_results = analyze_locations(posts_data)
            results["location_analysis"] = location_results

        # Perform topic modeling
        if "topic" in analysis_types:
            topic_results = analyze_topics(posts_data)
            results["topic_analysis"] = topic_results

        # Save analysis results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = f"drivingsg_analysis_{timestamp}.json"

        # Use absolute path for analysis output
        analysis_dir = os.path.join(project_root, "data", "analysis")
        analysis_path = os.path.join(analysis_dir, analysis_file)

        # Ensure analysis directory exists
        os.makedirs(analysis_dir, exist_ok=True)

        # Save the results
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        current_app.logger.info(f"Analysis results saved to: {analysis_path}")

        return jsonify(
            {
                "status": "success",
                "message": "Analysis completed successfully",
                "analysis_file": analysis_file,
                "analysis_path": analysis_path,
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error in analyze_reddit_data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})


def analyze_sentiment(posts_data):
    """Analyze sentiment of posts and comments"""
    from textblob import TextBlob

    sentiment_results = {
        "positive_count": 0,
        "neutral_count": 0,
        "negative_count": 0,
        "sentiment_over_time": {"timestamps": [], "sentiments": []},
    }

    for post in posts_data:
        # Analyze post content
        text = f"{post['title']} {post['text']}"
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity

        # Categorize sentiment
        if sentiment > 0.1:
            sentiment_results["positive_count"] += 1
        elif sentiment < -0.1:
            sentiment_results["negative_count"] += 1
        else:
            sentiment_results["neutral_count"] += 1

        # Add to time series
        sentiment_results["sentiment_over_time"]["timestamps"].append(
            post["created_utc"]
        )
        sentiment_results["sentiment_over_time"]["sentiments"].append(sentiment)

        # Analyze comments
        for comment in post.get("comments", []):
            blob = TextBlob(comment["text"])
            sentiment = blob.sentiment.polarity

            if sentiment > 0.1:
                sentiment_results["positive_count"] += 1
            elif sentiment < -0.1:
                sentiment_results["negative_count"] += 1
            else:
                sentiment_results["neutral_count"] += 1

    return sentiment_results


def analyze_trends(posts_data):
    """Analyze trends in posts and comments"""
    from collections import Counter
    import re

    trend_results = {
        "common_phrases": Counter(),
        "trending_topics": Counter(),
        "engagement_patterns": [],
    }

    # Extract phrases and topics
    for post in posts_data:
        # Get phrases from title and text
        text = f"{post['title']} {post['text']}"
        phrases = extract_phrases(text)
        trend_results["common_phrases"].update(phrases)

        # Track engagement
        trend_results["engagement_patterns"].append(
            {
                "timestamp": post["created_utc"],
                "score": post["score"],
                "num_comments": post["num_comments"],
            }
        )

        # Process comments
        for comment in post.get("comments", []):
            phrases = extract_phrases(comment["text"])
            trend_results["common_phrases"].update(phrases)

    # Get top phrases and topics
    trend_results["common_phrases"] = dict(
        trend_results["common_phrases"].most_common(20)
    )

    return trend_results


def analyze_traffic_incidents(posts_data):
    """Analyze traffic incidents from posts and comments"""
    incident_keywords = {
        "accident": ["accident", "crash", "collision"],
        "traffic_jam": ["jam", "congestion", "heavy traffic"],
        "road_work": ["construction", "roadwork", "maintenance"],
        "weather": ["rain", "flood", "weather"],
        "violation": ["speeding", "red light", "illegal"],
    }

    incident_results = {
        "incident_types": Counter(),
        "incident_locations": Counter(),
        "incident_times": [],
    }

    for post in posts_data:
        text = f"{post['title']} {post['text']}".lower()

        # Check for incidents
        for incident_type, keywords in incident_keywords.items():
            if any(keyword in text for keyword in keywords):
                incident_results["incident_types"][incident_type] += 1

                # Extract location if available
                locations = extract_locations(text)
                incident_results["incident_locations"].update(locations)

                # Add timestamp
                incident_results["incident_times"].append(
                    {"type": incident_type, "timestamp": post["created_utc"]}
                )

        # Check comments for additional incident reports
        for comment in post.get("comments", []):
            text = comment["text"].lower()
            for incident_type, keywords in incident_keywords.items():
                if any(keyword in text for keyword in keywords):
                    incident_results["incident_types"][incident_type] += 1
                    locations = extract_locations(text)
                    incident_results["incident_locations"].update(locations)

    return incident_results


def analyze_locations(posts_data):
    """Analyze location mentions in posts and comments"""
    # Singapore locations and areas
    sg_locations = {
        "regions": ["north", "south", "east", "west", "central"],
        "areas": [
            "woodlands",
            "tampines",
            "jurong",
            "changi",
            "yishun",
            "ang mo kio",
            "bedok",
            "clementi",
            "punggol",
            "sengkang",
        ],
        "roads": [
            "pie",
            "cte",
            "sle",
            "bke",
            "tpe",
            "ecp",
            "aye",
            "kje",
            "orchard road",
            "thomson road",
            "bukit timah",
        ],
    }

    location_results = {
        "region_mentions": Counter(),
        "area_mentions": Counter(),
        "road_mentions": Counter(),
        "location_context": [],
    }

    for post in posts_data:
        text = f"{post['title']} {post['text']}".lower()

        # Check regions
        for region in sg_locations["regions"]:
            if region in text:
                location_results["region_mentions"][region] += 1

        # Check areas
        for area in sg_locations["areas"]:
            if area in text:
                location_results["area_mentions"][area] += 1
                location_results["location_context"].append(
                    {
                        "location": area,
                        "timestamp": post["created_utc"],
                        "context": extract_context(text, area),
                    }
                )

        # Check roads
        for road in sg_locations["roads"]:
            if road in text:
                location_results["road_mentions"][road] += 1
                location_results["location_context"].append(
                    {
                        "location": road,
                        "timestamp": post["created_utc"],
                        "context": extract_context(text, road),
                    }
                )

        # Process comments
        for comment in post.get("comments", []):
            text = comment["text"].lower()
            for region in sg_locations["regions"]:
                if region in text:
                    location_results["region_mentions"][region] += 1
            for area in sg_locations["areas"]:
                if area in text:
                    location_results["area_mentions"][area] += 1
            for road in sg_locations["roads"]:
                if road in text:
                    location_results["road_mentions"][road] += 1

    return location_results


def analyze_topics(posts_data):
    """Perform topic modeling on posts and comments"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import NMF

    # Combine post and comment text
    documents = []
    for post in posts_data:
        # Add post text
        documents.append(f"{post['title']} {post['text']}")
        # Add comment text
        for comment in post.get("comments", []):
            documents.append(comment["text"])

    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(
        max_features=1000, stop_words="english", ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Perform topic modeling using NMF
    num_topics = 5
    nmf_model = NMF(n_components=num_topics, random_state=42)
    topic_matrix = nmf_model.fit_transform(tfidf_matrix)

    # Get feature names (words) for each topic
    feature_names = vectorizer.get_feature_names_out()

    # Extract top words for each topic
    topic_results = {"topics": [], "topic_distribution": [], "topic_keywords": []}

    for topic_idx, topic in enumerate(nmf_model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[: -10 - 1 : -1]]
        topic_results["topics"].append(f"Topic {topic_idx + 1}")
        topic_results["topic_keywords"].append(top_words)

        # Calculate topic distribution
        topic_docs = sum(1 for doc in topic_matrix if doc.argmax() == topic_idx)
        topic_results["topic_distribution"].append(topic_docs / len(documents))

    return topic_results


def extract_phrases(text):
    """Extract meaningful phrases from text"""
    import re
    from collections import Counter

    # Remove special characters and convert to lowercase
    text = re.sub(r"[^\w\s]", " ", text.lower())

    # Split into words
    words = text.split()

    # Create phrases (bigrams)
    phrases = [" ".join(words[i : i + 2]) for i in range(len(words) - 1)]

    return Counter(phrases)


def extract_locations(text):
    """Extract location mentions from text"""
    # Singapore location keywords
    locations = [
        "woodlands",
        "tampines",
        "jurong",
        "changi",
        "yishun",
        "ang mo kio",
        "bedok",
        "clementi",
        "punggol",
        "sengkang",
        "pie",
        "cte",
        "sle",
        "bke",
        "tpe",
        "ecp",
        "aye",
        "kje",
    ]

    found_locations = []
    text = text.lower()

    for location in locations:
        if location in text:
            found_locations.append(location)

    return found_locations


def extract_context(text, keyword, window=50):
    """Extract context around a keyword mention"""
    text = text.lower()
    keyword = keyword.lower()

    # Find the position of the keyword
    pos = text.find(keyword)
    if pos == -1:
        return ""

    # Get the surrounding context
    start = max(0, pos - window)
    end = min(len(text), pos + len(keyword) + window)

    return text[start:end]


@main_bp.route("/api/dataset-file/<path:filename>")
def dataset_file(filename):
    """API endpoint to get a dataset file"""
    try:
        # Ensure the filename is within the data directory
        if ".." in filename or filename.startswith("/"):
            return jsonify({"status": "error", "message": "Invalid filename"})

        file_path = os.path.join(dataset_service.data_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "File not found"})

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"Error retrieving file: {str(e)}"}
        )


@main_bp.route("/api/get-analysis-files", methods=["GET"])
def get_analysis_files():
    """API endpoint to get available analysis files"""
    try:
        # Get the project root directory (two levels up from the current file)
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        analysis_dir = os.path.join(project_root, "data", "analysis")

        current_app.logger.info(f"Project root: {project_root}")
        current_app.logger.info(f"Analysis directory: {analysis_dir}")

        files = []

        if os.path.exists(analysis_dir):
            for filename in os.listdir(analysis_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(analysis_dir, filename)
                    stats = os.stat(file_path)

                    # Get relative path from project root
                    rel_path = os.path.relpath(file_path, project_root)

                    files.append(
                        {
                            "filename": filename,
                            "size": stats.st_size,
                            "created": stats.st_mtime,
                            "path": rel_path,
                            "full_path": file_path,
                        }
                    )

        # Sort files by creation time (newest first)
        files.sort(key=lambda x: x["created"], reverse=True)

        return jsonify(
            {
                "status": "success",
                "files": files,
                "analysis_dir": analysis_dir,
                "project_root": project_root,
            }
        )
    except Exception as e:
        current_app.logger.error(f"Error in get_analysis_files: {str(e)}")
        return jsonify(
            {
                "status": "error",
                "message": f"Error loading analysis files: {str(e)}",
                "analysis_dir": (
                    analysis_dir if "analysis_dir" in locals() else "Not set"
                ),
                "project_root": (
                    project_root if "project_root" in locals() else "Not set"
                ),
            }
        )


@main_bp.route("/api/get-visualizations", methods=["GET"])
def get_analysis_visualizations():
    """API endpoint to get visualization data for an analysis"""
    try:
        file_path = request.args.get("file")
        viz_type = request.args.get("type", "all")
        timeframe = request.args.get("timeframe", "30d")

        # Get the project root directory
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        # Convert relative path to absolute path if necessary
        if not os.path.isabs(file_path):
            file_path = os.path.join(project_root, file_path)

        current_app.logger.info(f"Loading visualizations from: {file_path}")

        if not os.path.exists(file_path):
            return jsonify(
                {"status": "error", "message": f"Analysis file not found: {file_path}"}
            )

        # Read the analysis file
        with open(file_path, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)

        # Filter data based on visualization type if needed
        if viz_type != "all":
            filtered_data = {}
            for key, value in analysis_data.items():
                if key.startswith(viz_type):
                    filtered_data[key] = value
            analysis_data = filtered_data

        return jsonify({"status": "success", "data": analysis_data})
    except Exception as e:
        current_app.logger.error(f"Error loading visualizations: {str(e)}")
        return jsonify(
            {
                "status": "error",
                "message": f"Error loading visualizations: {str(e)}",
                "file_path": file_path if "file_path" in locals() else "Not set",
            }
        )


@main_bp.route("/api/list-datasets")
def list_datasets():
    """API endpoint to list available datasets from the data directory"""
    try:
        datasets = []
        # Scan through each data source directory
        for source in ["reddit", "twitter", "amazon", "yelp"]:
            source_dir = os.path.join(DATA_DIR, source)
            if os.path.exists(source_dir):
                for file in os.listdir(source_dir):
                    file_path = os.path.join(source_dir, file)
                    if os.path.isfile(file_path):
                        # Get file stats
                        stats = os.stat(file_path)
                        # Get file format
                        format = file.split(".")[-1].upper()

                        # Generate a readable title from filename
                        title = " ".join(
                            word.capitalize()
                            for word in file.split(".")[0].replace("_", " ").split()
                        )

                        datasets.append(
                            {
                                "title": title,
                                "source": source,
                                "file_path": file_path,
                                "size": stats.st_size,
                                "format": format,
                                "updated": datetime.fromtimestamp(
                                    stats.st_mtime
                                ).strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )

        return jsonify(datasets)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/dataset-info")
def get_dataset_info():
    """API endpoint to get detailed information about a specific dataset"""
    try:
        file_path = request.args.get("path")
        if not file_path or not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "Invalid file path"}), 400

        # Get file stats
        stats = os.stat(file_path)
        format = file_path.split(".")[-1].upper()

        # Generate title from filename
        filename = os.path.basename(file_path)
        title = " ".join(
            word.capitalize()
            for word in filename.split(".")[0].replace("_", " ").split()
        )

        # Get record count and description based on file format
        records = 0
        description = ""

        try:
            if format == "JSON":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records = len(data)
                    elif isinstance(data, dict):
                        records = 1
                    description = f"JSON dataset containing {records} records"

            elif format == "CSV":
                df = pd.read_csv(file_path)
                records = len(df)
                description = (
                    f"CSV dataset with {len(df.columns)} columns and {records} records"
                )
        except Exception as e:
            description = f"Unable to read file contents: {str(e)}"
            records = 0

        return jsonify(
            {
                "title": title,
                "size": stats.st_size,
                "format": format,
                "records": records,
                "updated": datetime.fromtimestamp(stats.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "description": description,
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@main_bp.route("/api/analyze", methods=["POST"])
def analyze():
    """Process data analysis form submission and execute the analysis"""
    try:
        print("Received analysis request")
        if request.content_type.startswith('multipart/form-data'):
            form_data = request.form.to_dict()
            files = request.files
            print(f"Form data: {form_data}")
            print(f"Files: {list(files.keys())}")
            
            # Get parameters
            selected_dataset = form_data.get('dataset_id')
            analysis_types = form_data.getlist('analysis_types[]') if 'analysis_types[]' in form_data else []
            
            # Handle Hadoop job execution
            if form_data.get('hadoop_input_file'):
                # Extract Hadoop parameters
                input_file = form_data.get('hadoop_input_file')
                analysis_type = form_data.get('hadoop_analysis_type')
                output_dir = form_data.get('hadoop_output_dir')
                timerange_start = form_data.get('hadoop_timerange_start', '')
                timerange_end = form_data.get('hadoop_timerange_end', '')
                
                # Call the run_hadoop_job function
                from src.web.services import run_hadoop_job
                result = run_hadoop_job(
                    input_file=input_file,
                    analysis_type=analysis_type,
                    output_dir=output_dir,
                    timerange_start=timerange_start,
                    timerange_end=timerange_end
                )
                
                print(f"Hadoop job result: {result}")
                return jsonify(result)
            
            # For dataset analysis
            elif selected_dataset:
                # Call the appropriate analysis service based on the dataset source
                if selected_dataset.startswith('reddit_'):
                    result = analysis_service.analyze_reddit_data(selected_dataset, analysis_types)
                elif selected_dataset.startswith('twitter_'):
                    result = analysis_service.analyze_twitter_data(selected_dataset, analysis_types)
                else:
                    result = analysis_service.analyze_dataset(selected_dataset, analysis_types)
                
                return jsonify(result)
            
            # For Reddit scraper
            elif form_data.get('reddit_sort'):
                # Prepare data for scrape-reddit endpoint
                sort_by = form_data.get('reddit_sort')
                limit = int(form_data.get('reddit_limit', 25))
                time_filter = form_data.get('reddit_time_filter', 'day')
                
                # Call scrape-reddit through internal redirect
                data = {
                    "subreddit": "drivingsg", 
                    "limit": limit,
                    "sort_by": sort_by,
                    "post_type": "all"
                }
                
                # Create a fake request for the scrape-reddit endpoint
                from flask import make_response
                with app.test_request_context('/api/scrape-reddit', 
                                            method='POST', 
                                            data=json.dumps(data),
                                            content_type='application/json'):
                    scrape_result = scrape_reddit()
                    
                if isinstance(scrape_result, str):
                    scrape_result = json.loads(scrape_result)
                    
                # If scraping succeeded, analyze the data
                if scrape_result.get('success') and scrape_result.get('file_path'):
                    # Set up data for analyze-reddit-data
                    analysis_data = {
                        "file_path": scrape_result["file_path"],
                        "analysis_types": analysis_types
                    }
                    
                    # Call analyze-reddit-data
                    with app.test_request_context('/api/analyze-reddit-data', 
                                                method='POST', 
                                                data=json.dumps(analysis_data),
                                                content_type='application/json'):
                        analysis_result = analyze_reddit_data()
                        
                    return analysis_result
                else:
                    return jsonify(scrape_result)
            
            return jsonify({
                'status': 'error',
                'message': 'No valid analysis configuration provided'
            }), 400
            
        else:
            # If sent as JSON
            data = request.get_json()
            print(f"JSON data: {data}")
            
            # For Hadoop job
            if data.get('input_file') and data.get('analysis_type') and data.get('output_dir'):
                from src.web.services import run_hadoop_job
                result = run_hadoop_job(
                    input_file=data.get('input_file'),
                    analysis_type=data.get('analysis_type'),
                    output_dir=data.get('output_dir'),
                    timerange_start=data.get('timerange_start', ''),
                    timerange_end=data.get('timerange_end', '')
                )
                return jsonify(result)
            
            return jsonify({
                'status': 'success',
                'message': 'Analysis request received',
                'job_id': 'sample_job_id'
            })
            
    except Exception as e:
        import traceback
        print(f"Error in analyze API: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Error processing analysis request: {str(e)}'
        }), 500
