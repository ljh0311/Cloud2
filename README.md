# Big Data Analytics Project

This project analyzes large-scale social media data to identify trends, popular topics, and user engagement patterns using Hadoop and Spark.

## Project Structure

```
├── src/
│   ├── data/           # Data ingestion and preprocessing scripts
│   ├── hadoop/         # Hadoop MapReduce jobs
│   ├── spark/          # Spark processing scripts
│   ├── visualization/  # Data visualization scripts
│   └── web/            # Web interface components
├── utils/              # Utility functions and tracking tools
├── config/             # Configuration files
├── tests/              # Unit tests
├── docs/               # Documentation
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup Instructions

### Prerequisites

1. Python 3.8 or higher
2. Hadoop 3.3.x or higher with HADOOP_HOME environment variable set
3. Spark 3.5.0 or higher with SPARK_HOME environment variable set
4. Git for version control

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/big-data-analytics.git
   cd big-data-analytics
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (create a .env file in the project root):
   ```
   HADOOP_HOME=/path/to/hadoop
   SPARK_HOME=/path/to/spark
   FLASK_APP=src.web.app
   FLASK_ENV=development
   ```

## Running the Project

### Web Application

1. Start the web application:
   ```bash
   python -m src.web.run
   ```
   
2. Access the web interface at http://localhost:5000

### Data Processing Pipeline

1. Data Ingestion:
   ```bash
   python -m src.data.ingest --source <source_path> --dest <destination_path>
   ```

2. Run MapReduce Jobs:
   ```bash
   python -m src.hadoop.runner --input <input_path> --output <output_path>
   ```

3. Run Spark Analysis:
   ```bash
   python -m src.spark.analyzer --input <input_path> --output <output_path>
   ```

4. Generate Visualizations:
   ```bash
   python -m src.visualization.generator --data <data_path> --output <output_path>
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

## Integration Points

1. Storage to MapReduce:
   - Data storage system to MapReduce jobs
   - Managed by JH and Darrel
   - Integration files: `src/data/storage.py` and `src/hadoop/input_reader.py`

2. MapReduce to Spark:
   - MapReduce output to Spark analysis
   - Managed by Darrel and Xuan Yu
   - Integration files: `src/hadoop/output_writer.py` and `src/spark/input_reader.py`

3. Spark to Visualization:
   - Analysis results to visualization
   - Managed by Xuan Yu and Javin
   - Integration files: `src/spark/output_writer.py` and `src/visualization/data_loader.py`

4. Web to Visualization:
   - Web interface to visualization components
   - Managed by JH and Javin
   - Integration files: `src/web/services.py` and `src/visualization/web_renderer.py`

## Project Timeline

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

## Team Members and Responsibilities

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

## Troubleshooting

### Common Issues

1. **Hadoop Connection Issues**
   - Ensure HADOOP_HOME is correctly set
   - Verify Hadoop services are running with `jps` command

2. **Spark Execution Errors**
   - Check SPARK_HOME is correctly set
   - Ensure Python dependencies are installed
   - Verify Spark master is running

3. **Web Application Not Starting**
   - Check Flask environment variables
   - Ensure port 5000 is not in use
   - Verify virtual environment is activated

## License

This project is licensed under the MIT License - see the LICENSE file for details.
