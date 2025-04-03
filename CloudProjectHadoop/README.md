# Enhanced Hadoop Traffic Analysis System

This project provides a comprehensive framework for analyzing traffic data using Hadoop MapReduce. The system supports various types of analysis, visualization generation, and advanced features like custom partitioning, job chaining, secondary sorting, and more.

## Features

- **Multiple Analysis Types**:
  - Brand Analysis: Analyze mentions of specific car brands in traffic data
  - Keyword Analysis: Extract and count traffic-related keywords
  - Sentiment Analysis: Analyze sentiment of traffic-related posts
  - Time-based Analysis: Analyze traffic patterns by time
  - Heatmap Analysis: Visualize traffic incidents/mentions on a geographical map

- **Advanced Processing Features**:
  - Custom Partitioning: Efficiently distribute data across reducers
  - Job Chaining: Run multiple MapReduce jobs in sequence
  - Secondary Sorting: Sort by keys and values
  - Top-N Analysis: Get the top N results for any analysis
  - Custom Aggregations: Sum, Average, Max, Min, Median, Count

- **Visualization Support**:
  - Interactive HTML/JS visualizations
  - Charts, maps, and tables
  - Exportable data in CSV and JSON formats

## System Requirements

- Java 8 or higher
- Hadoop 3.x
- Maven 3.x

## Project Structure

```
CloudProjectHadoop/
├── src/main/java/sg/edu/sit/traffic/
│   ├── TrafficMapper.java             # Core mapper implementation
│   ├── TrafficReducer.java            # Core reducer implementation
│   ├── TrafficAnalysisDriver.java     # Main driver program
│   ├── ComplexAnalysisDriver.java     # Driver for complex analysis chains
│   ├── HDFSFileManager.java           # HDFS file operations utility
│   ├── VisualizationGenerator.java    # Visualization generation utility
│   ├── VisualizeResults.java          # Command-line visualization tool
│   └── ... other supporting classes
│
├── src/main/resources/
│   ├── config.properties              # Configuration properties
│   └── templates/                     # Visualization templates
│       ├── generic_chart.html
│       ├── time_series.html
│       ├── heatmap.html
│       └── index_template.html
│
└── README.md                          # This file
```

## Building the Project

To build the project, run:

```bash
cd CloudProjectHadoop
mvn clean package
```

This will create a JAR file in the `target` directory.

## Running Traffic Analysis

### Basic Analysis

To run a basic traffic analysis, use:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.TrafficAnalysisDriver <input_path> <analysis_type> <output_path>
```

Where:
- `<input_path>`: HDFS path to the input data
- `<analysis_type>`: Type of analysis to perform (brands, keywords, sentiment, time, heatmap)
- `<output_path>`: HDFS path to store the results

Example:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.TrafficAnalysisDriver /user/hadoop/traffic-data brands /user/hadoop/traffic-results
```

### Advanced Analysis with Configuration

For more advanced analysis, you can provide a properties file:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.TrafficAnalysisDriver -conf /path/to/my-config.properties <input_path> <analysis_type> <output_path>
```

Example `my-config.properties`:

```properties
# Car brands to analyze
analysis.brands.categories=luxury,economy,sports
analysis.brands.luxury=BMW,Mercedes,Audi,Lexus
analysis.brands.economy=Toyota,Honda,Hyundai,Kia
analysis.brands.sports=Ferrari,Porsche,Lamborghini

# Top-N results to return
analysis.topn=10

# Secondary sorting
analysis.secondary.sort=true

# Aggregation type: sum, avg, max, min, median, count
analysis.aggregation=sum

# HDFS web directory for results
hdfs.enabled=true
hdfs.web.directory=/user/hadoop/traffic-web
```

### Complex Analysis with Job Chaining

To run complex analysis with job chaining:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.ComplexAnalysisDriver <input_path> <analysis_types> <output_path>
```

Where:
- `<analysis_types>`: Comma-separated list of analysis types to run (e.g., "brands,keywords,sentiment")

Example:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.ComplexAnalysisDriver /user/hadoop/traffic-data brands,keywords,sentiment /user/hadoop/complex-results
```

This will:
1. Clean the data
2. Run each analysis in sequence
3. Aggregate the results

## Generating Visualizations

To generate visualizations from analysis results:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.VisualizeResults <input_path> <output_dir> [template_dir]
```

Where:
- `<input_path>`: HDFS path containing analysis results
- `<output_dir>`: Local directory to save visualization files
- `[template_dir]`: Optional. Directory containing HTML templates (defaults to 'templates')

Example:

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.VisualizeResults /user/hadoop/traffic-results ./visualizations
```

After generating visualizations, open the `index.html` file in your browser:

```bash
# On Windows
start visualizations\index.html

# On Linux
xdg-open visualizations/index.html

# On macOS
open visualizations/index.html
```

## Configuration Options

Here are the main configuration options available:

| Option | Description | Default |
|--------|-------------|---------|
| `analysis.brands.categories` | Categories of brands to analyze | luxury,economy,sports |
| `analysis.brands.<category>` | Brands in each category | (varies) |
| `analysis.topn` | Number of top results to return | 10 |
| `analysis.secondary.sort` | Enable secondary sorting | false |
| `analysis.aggregation` | Aggregation type | sum |
| `hdfs.enabled` | Copy results to web-accessible location | false |
| `hdfs.web.directory` | HDFS directory for web access | /user/hadoop/traffic-web |

## Examples

### Analyzing Brand Mentions with Top-5 Results

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.TrafficAnalysisDriver -D analysis.topn=5 /user/hadoop/traffic-data brands /user/hadoop/brand-results
```

### Time-based Analysis with Average Aggregation

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.TrafficAnalysisDriver -D analysis.aggregation=avg /user/hadoop/traffic-data time /user/hadoop/time-results
```

### Complex Analysis with Web Visualization

```bash
hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.ComplexAnalysisDriver -D hdfs.enabled=true /user/hadoop/traffic-data brands,sentiment,heatmap /user/hadoop/web-results

hadoop jar CloudProjectHadoop.jar sg.edu.sit.traffic.VisualizeResults /user/hadoop/web-results ./web-visualizations
```

## Troubleshooting

If you encounter issues:

1. **Ensure input data exists**: 
   ```bash
   hadoop fs -ls <input_path>
   ```

2. **Check output directory**: Make sure the output directory doesn't already exist.
   ```bash
   hadoop fs -rm -r <output_path>
   ```

3. **View Hadoop logs**: 
   ```bash
   yarn logs -applicationId <application_id>
   ```

4. **Verify template directory**: Ensure the visualization templates exist.
   ```bash
   ls -la src/main/resources/templates/
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 