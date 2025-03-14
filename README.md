# Big Data Analytics Project

This project analyzes large-scale social media data to identify trends, popular topics, and user engagement patterns using Hadoop and Spark.

## Project Structure

```
├── src/
│   ├── data/           # Data ingestion and preprocessing scripts
│   ├── hadoop/         # Hadoop MapReduce jobs
│   ├── spark/          # Spark processing scripts
│   ├── visualization/  # Data visualization scripts
│   └── web/           # Web interface components
├── utils/             # Utility functions and tracking tools
├── config/            # Configuration files
├── tests/            # Unit tests
├── docs/             # Documentation
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Setup Instructions

1. Install Python 3.8 or higher
2. Install Hadoop and ensure HADOOP_HOME is set
3. Install Spark and ensure SPARK_HOME is set
4. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Progress Tracking and Integration Management

The project includes a comprehensive tracking system to monitor progress and manage component integration. Access the tracking dashboard at `http://localhost:5000/tracking` after starting the web application.

### Setting Up Progress Tracking

1. Initialize the tracking system:
   ```python
   from utils.progress_tracker import ProgressTracker
   tracker = ProgressTracker(".")
   ```

2. Update task progress:
   ```python
   # Update individual task progress
   tracker.update_task_progress(
       phase="individual_development",
       task_path="your_name.task_name",
       status="in_progress",
       progress=50  # percentage complete
   )
   ```

3. Check progress:
   ```python
   # Get overall progress
   progress = tracker.get_overall_progress()
   
   # Get team member progress
   member_progress = tracker.get_team_member_progress("your_name")
   
   # Check overdue tasks
   overdue = tracker.check_overdue_tasks()
   ```

### Managing Component Integration

1. Initialize the integration manager:
   ```python
   from utils.integration_manager import IntegrationManager
   manager = IntegrationManager(".")
   ```

2. Update integration status:
   ```python
   # Update integration point status
   manager.update_integration_status(
       "integration_point_name",
       "in_progress",
       "Status message"
   )
   ```

3. Check integration readiness:
   ```python
   # Check if components are ready for integration
   ready, message = manager.check_integration_readiness("integration_point_name")
   ```

### Using the Web Interface

1. Access the tracking dashboard at `/tracking`
2. Features available:
   - View overall project progress
   - Monitor team member progress
   - Track integration status
   - Update task progress
   - Manage integration points
   - View overdue tasks

### Integration Points

1. Storage to MapReduce:
   - Data storage system to MapReduce jobs
   - Managed by JH and Darrel

2. MapReduce to Spark:
   - MapReduce output to Spark analysis
   - Managed by Darrel and Xuan Yu

3. Spark to Visualization:
   - Analysis results to visualization
   - Managed by Xuan Yu and Javin

4. Web to Visualization:
   - Web interface to visualization components
   - Managed by JH and Javin

### Project Timeline

1. Individual Development (March 6-19, 2025):
   - Setup and component development
   - Regular progress updates required

2. Integration Phase (March 20-26, 2025):
   - Component integration
   - Daily status updates recommended

3. Testing Phase (March 27-April 2, 2025):
   - Testing and refinement
   - Bug tracking and fixes

4. Documentation (April 3, 2025):
   - Final documentation
   - Presentation preparation

## Running the Project

TODO: Add specific instructions for running each component

## Team Members

1. JH Tasks (Infrastructure & Web Interface):
   - Setup & Configuration
   - Web application framework
   - Data storage modules

2. Darrel's Tasks (MapReduce & Batch Processing):
   - MapReduce jobs
   - Data cleaning
   - Batch processing pipeline

3. Xuan Yu's Tasks (Spark & Real-time Analysis):
   - Spark streaming
   - Real-time analysis
   - Trend detection

4. Javin's Tasks (Visualization & Analytics):
   - Dashboard design
   - Interactive visualizations
   - Analytics reports
