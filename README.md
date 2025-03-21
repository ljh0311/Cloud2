# Social Media Analyzer

A comprehensive web application for scraping, analyzing, and visualizing social media data.

## Features

- **Data Collection**: Scrape data from Reddit using PRAW (Python Reddit API Wrapper)
- **Data Analysis**: Analyze social media data for sentiment, trends, engagement, and topics
- **Visualization**: Interactive visualizations of analysis results
- **API Endpoints**: RESTful API for accessing analysis files and visualization data

## Project Structure

```
.
├── app.py                  # Main application entry point
├── config/                 # Configuration files
│   └── reddit_config.py    # Reddit API credentials
├── data/                   # Data storage
│   ├── analysis/           # Analysis results
│   └── reddit/             # Scraped Reddit data
├── src/                    # Source code
│   ├── data/               # Data processing modules
│   │   └── reddit_scraper.py  # Reddit scraper
│   └── web/                # Web application
│       ├── services.py     # Business logic services
│       ├── views.py        # Flask routes and API endpoints
│       └── templates/      # HTML templates
│           ├── analysis.html    # Analysis page
│           └── visualizations.html  # Visualizations page
└── requirements.txt        # Project dependencies
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure Reddit API credentials in `config/reddit_config.py`
4. Run the application:
   ```
   python app.py
   ```
5. Access the application at http://localhost:5000

## API Endpoints

- `/api/get-analysis-files`: Get a list of available analysis files
- `/api/get-visualizations`: Get visualization data for a specific analysis
- `/api/analyze-reddit-data`: Analyze Reddit data from a specified file

## Analysis Files

Analysis files are stored in the `data/analysis` directory by default. These files contain the results of data analysis operations and are used by the visualization system.

For detailed information about how analysis files are managed, see [README_ANALYSIS.md](README_ANALYSIS.md).

To verify that analysis files are being saved correctly, you can run the test script:
```
python test_analysis_save.py
```

## Dependencies

- Flask: Web framework
- PySpark: Big data processing
- PRAW: Reddit API wrapper
- Pandas/NumPy: Data manipulation
- Matplotlib/Seaborn: Data visualization
- NLTK: Natural language processing

## License

MIT
