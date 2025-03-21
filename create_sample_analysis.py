import json
import os

# Sample analysis data
sample_analysis = {
  "dataset": "Reddit Technology Data",
  "source_file": "data/reddit/reddit_scraped_technology_1710652800.csv",
  "record_count": 100,
  "date_range": "2025-03-10 to 2025-03-17",
  "processing_mode": "batch",
  "analysis_types": ["sentiment", "trend", "engagement", "topic"],
  "created_at": "2025-03-17 13:30:00",
  "results": {
    "sentiment_analysis": {
      "positive_count": 45,
      "neutral_count": 35,
      "negative_count": 20,
      "sentiment_over_time": {
        "time_periods": ["2025-03-10", "2025-03-11", "2025-03-12", "2025-03-13", "2025-03-14", "2025-03-15", "2025-03-16", "2025-03-17"],
        "positive_percentages": [40, 45, 50, 55, 45, 50, 45, 40],
        "neutral_percentages": [35, 30, 30, 25, 35, 30, 35, 40],
        "negative_percentages": [25, 25, 20, 20, 20, 20, 20, 20]
      },
      "word_frequencies": {
        "technology": 50,
        "programming": 45,
        "python": 40,
        "javascript": 35,
        "data": 30,
        "cloud": 25,
        "software": 20,
        "development": 18,
        "code": 15,
        "computer": 12
      }
    },
    "trend_analysis": {
      "time_periods": ["2025-03-10", "2025-03-11", "2025-03-12", "2025-03-13", "2025-03-14", "2025-03-15", "2025-03-16", "2025-03-17"],
      "mention_counts": [12, 15, 18, 20, 15, 10, 8, 12]
    },
    "engagement_analysis": {
      "time_periods": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
      "engagement_counts": [5, 8, 15, 25, 30, 35, 25, 15],
      "top_influencers": {
        "user_123": 150,
        "user_456": 120,
        "user_789": 100,
        "user_101": 90,
        "user_202": 80,
        "user_303": 70,
        "user_404": 60,
        "user_505": 50
      }
    },
    "topic_analysis": {
      "topic_distribution": {
        "Programming": 0.35,
        "Web Development": 0.25,
        "Data Science": 0.20,
        "Cloud Computing": 0.15,
        "Cybersecurity": 0.05
      }
    }
  }
}

# Ensure the directory exists
os.makedirs("data/analysis", exist_ok=True)

# Write the sample analysis to a file
with open("data/analysis/reddit_sample_analysis.json", "w") as f:
    json.dump(sample_analysis, f, indent=2)

print("Sample analysis file created successfully.") 