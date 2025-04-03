package sg.edu.sit.traffic;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.File;
import java.util.Properties;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;
import org.json.JSONObject;
import org.json.JSONArray;
import java.util.ArrayList;
import java.util.List;
import sg.edu.sit.traffic.output.CSVOutputFormat;
import sg.edu.sit.traffic.output.JSONOutputFormat;
import java.util.Map;
import java.util.HashMap;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import sg.edu.sit.traffic.HDFSFileManager;

/**
 * Main driver class for Singapore Traffic Analysis system.
 * This class handles command-line arguments and sets up the MapReduce jobs
 * for trend analysis, sentiment analysis, location analysis, and car brand analysis.
 */
public class TrafficAnalysisDriver {

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        
        if (otherArgs.length < 3) {
            System.err.println("Usage: TrafficAnalysis <input> <analysis_type> <output_dir> [--start-time YYYY-MM-DD HH:MM] [--end-time YYYY-MM-DD HH:MM] [output_format]");
            System.err.println("Analysis types: sentiment, trend, traffic, location, topic, engagement, brands, timeframe");
            System.err.println("Output formats: default, csv, json");
            System.exit(2);
        }

        // Parse all arguments
        String inputPath = otherArgs[0];
        String analysisType = otherArgs[1].toLowerCase();
        String outputDir = otherArgs[2];
        
        // Default values
        String startTime = null;
        String endTime = null;
        String outputFormat = "default";
        
        // Parse optional arguments
        for (int i = 3; i < otherArgs.length; i++) {
            if (otherArgs[i].equals("--start-time") && i + 1 < otherArgs.length) {
                startTime = otherArgs[i + 1];
                i++; // Skip the next argument
            } else if (otherArgs[i].equals("--end-time") && i + 1 < otherArgs.length) {
                endTime = otherArgs[i + 1];
                i++; // Skip the next argument
            } else {
                // Assume this is the output format
                outputFormat = otherArgs[i].toLowerCase();
            }
        }
        
        // Set timestamps in configuration if provided
        if (startTime != null) {
            System.out.println("Using start timestamp filter: " + startTime);
            conf.set("analysis.timestamp.start", startTime);
        }
        
        if (endTime != null) {
            System.out.println("Using end timestamp filter: " + endTime);
            conf.set("analysis.timestamp.end", endTime);
        }

        // Clean the input JSON file first
        String cleanedFilePath = cleanJsonDataset(inputPath);
        
        // Load properties
        Properties props = loadProperties();
        
        // Set the analysis type in configuration
        conf.set("analysis.type", analysisType);

        // Generate output path with timestamp
        String outputPath = generateOutputPath(outputDir, inputPath, analysisType);
        
        // Delete existing output directory if it exists
        deleteExistingOutput(conf, outputPath);

        // Set additional configuration based on analysis type
        if (analysisType.equals("brands")) {
            String[] categories = props.getProperty("brands.categories", "japanese,european,korean,american").split(",");
            for (String category : categories) {
                String brands = props.getProperty("car.brands." + category, "");
                if (!brands.isEmpty()) {
                    conf.set("car.brands." + category, brands);
                }
            }
            String commonModels = props.getProperty("car.models.common", "");
            if (!commonModels.isEmpty()) {
                conf.set("car.models.common", commonModels);
            }
        }

        // Set up configurable Top-N analysis
        int topN = Integer.parseInt(props.getProperty("analysis.topn", "10"));
        conf.setInt("analysis.topn", topN);

        // Set up custom aggregation type
        String aggregationType = props.getProperty("analysis.aggregation", "sum");
        conf.set("analysis.aggregation", aggregationType);

        // Enable/disable secondary sorting
        boolean enableSecondarySorting = Boolean.parseBoolean(props.getProperty("analysis.secondary.sort", "false"));
        conf.setBoolean("analysis.secondary.sort", enableSecondarySorting);

        Job job = Job.getInstance(conf, "Traffic Analysis - " + analysisType);
        job.setJarByClass(TrafficAnalysisDriver.class);
        
        // Set mapper and reducer classes
        job.setMapperClass(TrafficMapper.class);
        job.setReducerClass(TrafficReducer.class);
        
        // Set custom partitioner
        job.setPartitionerClass(TrafficPartitioner.class);
        
        // Determine number of reducers based on analysis type and data size
        int numReducers = determineReducerCount(conf, analysisType, new Path(cleanedFilePath));
        job.setNumReduceTasks(numReducers);
        
        // Set output key and value classes
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        
        // Set output format based on user selection
        switch (outputFormat) {
            case "csv":
                // Set CSV output format
                job.setOutputFormatClass(CSVOutputFormat.class);
                // Set CSV header based on analysis type
                String csvHeader = generateCSVHeader(analysisType);
                conf.set(CSVOutputFormat.CSV_HEADER, csvHeader);
                conf.setBoolean(CSVOutputFormat.CSV_INCLUDE_HEADER, true);
                break;
            case "json":
                // Set JSON output format
                job.setOutputFormatClass(JSONOutputFormat.class);
                // Configure JSON format options
                conf.setBoolean(JSONOutputFormat.JSON_AS_ARRAY, true);
                conf.setBoolean(JSONOutputFormat.JSON_PRETTY_PRINT, true);
                conf.setBoolean(JSONOutputFormat.JSON_NEWLINE_SEPARATED, false);
                conf.set(JSONOutputFormat.JSON_ANALYSIS_TYPE, analysisType);
                break;
            default:
                // Use default Hadoop text output format
                break;
        }
        
        // Set input and output paths - use cleaned file as input
        FileInputFormat.addInputPath(job, new Path(cleanedFilePath));
        FileOutputFormat.setOutputPath(job, new Path(outputPath));

        // Set the jar file
        job.setJar("target/CloudProjectHadoop-0.0.1-SNAPSHOT.jar");
        
        boolean success = job.waitForCompletion(true);
        
        // Clean up the temporary cleaned file
        new File(cleanedFilePath).delete();
        
        // Generate a visualization-friendly summary file
        if (success) {
            generateVisualizationSummary(conf, outputPath, analysisType);
        }
        
        // If running with HDFS, copy results to a web-accessible location
        if (props.getProperty("hdfs.enabled", "false").equalsIgnoreCase("true")) {
            copyResultsToWebLocation(conf, outputPath, analysisType);
        }
        
        System.exit(success ? 0 : 1);
    }
    
    /**
     * Generate output path with timestamp
     * @param outputDir User-specified output directory
     * @param inputPath Original input file path
     * @param analysisType Type of analysis being performed
     * @return Generated output path
     */
    private static String generateOutputPath(String outputDir, String inputPath, String analysisType) {
        // Extract dataset name from input path
        String datasetName = new File(inputPath).getName();
        if (datasetName.contains(".")) {
            datasetName = datasetName.substring(0, datasetName.lastIndexOf('.'));
        }
        
        // Get current timestamp
        LocalDateTime now = LocalDateTime.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
        String timestamp = now.format(formatter);
        
        // Generate output path
        return String.format("%s/%s_%s_%s", outputDir, datasetName, analysisType, timestamp);
    }
    
    /**
     * Delete existing output directory if it exists
     * @param conf Hadoop configuration
     * @param outputPath Output path to check and delete
     */
    private static void deleteExistingOutput(Configuration conf, String outputPath) throws IOException {
        FileSystem fs = FileSystem.get(conf);
        Path output = new Path(outputPath);
        if (fs.exists(output)) {
            System.out.println("Deleting existing output directory: " + outputPath);
            fs.delete(output, true);
        }
    }

    /**
     * Clean the JSON dataset by keeping only required fields
     * @param inputPath Path to the input JSON file
     * @return Path to the cleaned JSON file
     */
    private static String cleanJsonDataset(String inputPath) throws IOException {
        String cleanedFilePath = inputPath + "_cleaned.json";
        int totalLines = 0;
        int processedLines = 0;
        
        try (BufferedReader reader = new BufferedReader(new FileReader(inputPath));
             FileWriter writer = new FileWriter(cleanedFilePath)) {
            
            StringBuilder jsonContent = new StringBuilder();
            String line;
            boolean isInArray = false;
            
            System.out.println("Starting to process JSON file: " + inputPath);
            System.out.println("Reading first few characters to determine format...");
            
            // Read the first non-empty line to check format
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    System.out.println("First non-empty line starts with: " + line.substring(0, Math.min(line.length(), 50)));
                    isInArray = line.trim().startsWith("[");
                    break;
                }
            }
            
            // Reset reader
            reader.close();
            BufferedReader newReader = new BufferedReader(new FileReader(inputPath));
            
            // If it's a JSON array, we need to handle it differently
            if (isInArray) {
                System.out.println("Detected JSON array format, processing accordingly...");
                StringBuilder fullContent = new StringBuilder();
                while ((line = newReader.readLine()) != null) {
                    fullContent.append(line.trim());
                }
                
                try {
                    JSONArray jsonArray = new JSONArray(fullContent.toString());
                    System.out.println("Successfully parsed JSON array with " + jsonArray.length() + " objects");
                    
                    for (int i = 0; i < jsonArray.length(); i++) {
                        JSONObject json = jsonArray.getJSONObject(i);
                        JSONObject cleanedJson = new JSONObject();
                        
                        // Keep only required fields
                        if (json.has("title")) {
                            cleanedJson.put("title", json.getString("title"));
                        }
                        if (json.has("text")) {
                            cleanedJson.put("text", json.getString("text"));
                        }
                        if (json.has("created_utc")) {
                            cleanedJson.put("created_utc", json.getDouble("created_utc"));
                        }
                        if (json.has("num_comments")) {
                            cleanedJson.put("num_comments", json.getInt("num_comments"));
                        }
                        
                        // Process comments if they exist
                        if (json.has("comments")) {
                            JSONArray originalComments = json.getJSONArray("comments");
                            JSONArray cleanedComments = new JSONArray();
                            
                            for (int j = 0; j < originalComments.length(); j++) {
                                JSONObject comment = originalComments.getJSONObject(j);
                                JSONObject cleanedComment = new JSONObject();
                                
                                if (comment.has("text")) {
                                    cleanedComment.put("text", comment.getString("text"));
                                }
                                if (comment.has("created_utc")) {
                                    cleanedComment.put("created_utc", comment.getDouble("created_utc"));
                                }
                                
                                cleanedComments.put(cleanedComment);
                            }
                            
                            cleanedJson.put("comments", cleanedComments);
                        }
                        
                        writer.write(cleanedJson.toString());
                        writer.write("\n");
                        processedLines++;
                        
                        if (processedLines % 100 == 0) {
                            System.out.println("Processed " + processedLines + " JSON objects...");
                        }
                    }
                } catch (Exception e) {
                    System.err.println("Error processing JSON array: " + e.getMessage());
                    throw new IOException("Failed to process JSON array: " + e.getMessage());
                }
            } else {
                // Process line by line for individual JSON objects
                System.out.println("Detected line-by-line JSON format, processing accordingly...");
                while ((line = newReader.readLine()) != null) {
                    totalLines++;
                    line = line.trim();
                    
                    if (line.isEmpty()) {
                        continue;
                    }
                    
                    try {
                        jsonContent.append(line);
                        
                        try {
                            JSONObject json = new JSONObject(jsonContent.toString());
                            JSONObject cleanedJson = new JSONObject();
                            
                            // Keep only required fields
                            if (json.has("title")) {
                                cleanedJson.put("title", json.getString("title"));
                            }
                            if (json.has("text")) {
                                cleanedJson.put("text", json.getString("text"));
                            }
                            if (json.has("created_utc")) {
                                cleanedJson.put("created_utc", json.getDouble("created_utc"));
                            }
                            if (json.has("num_comments")) {
                                cleanedJson.put("num_comments", json.getInt("num_comments"));
                            }
                            
                            // Process comments if they exist
                            if (json.has("comments")) {
                                JSONArray originalComments = json.getJSONArray("comments");
                                JSONArray cleanedComments = new JSONArray();
                                
                                for (int i = 0; i < originalComments.length(); i++) {
                                    JSONObject comment = originalComments.getJSONObject(i);
                                    JSONObject cleanedComment = new JSONObject();
                                    
                                    if (comment.has("text")) {
                                        cleanedComment.put("text", comment.getString("text"));
                                    }
                                    if (comment.has("created_utc")) {
                                        cleanedComment.put("created_utc", comment.getDouble("created_utc"));
                                    }
                                    
                                    cleanedComments.put(cleanedComment);
                                }
                                
                                cleanedJson.put("comments", cleanedComments);
                            }
                            
                            writer.write(cleanedJson.toString());
                            writer.write("\n");
                            jsonContent.setLength(0);
                            processedLines++;
                            
                            if (processedLines % 100 == 0) {
                                System.out.println("Processed " + processedLines + " JSON objects...");
                            }
                            
                        } catch (org.json.JSONException e) {
                            if (!line.endsWith("}")) {
                                continue;
                            } else {
                                System.err.println("Error processing JSON at line " + totalLines + ": " + e.getMessage());
                                System.err.println("Problematic JSON: " + jsonContent.toString());
                                jsonContent.setLength(0);
                            }
                        }
                    } catch (Exception e) {
                        System.err.println("Error processing line " + totalLines + ": " + e.getMessage());
                        System.err.println("Line content: " + line);
                        jsonContent.setLength(0);
                    }
                }
            }
            
            newReader.close();
        }
        
        System.out.println("\nJSON processing completed:");
        System.out.println("Total lines read: " + totalLines);
        System.out.println("Successfully processed JSON objects: " + processedLines);
        System.out.println("Created cleaned dataset at: " + cleanedFilePath);
        
        if (processedLines == 0) {
            throw new IOException("No valid JSON objects were processed. Please check the input file format and ensure it contains valid JSON data.");
        }
        
        return cleanedFilePath;
    }
    
    /**
     * Load properties from traffic-analysis.properties file
     */
    private static Properties loadProperties() {
        Properties properties = new Properties();
        
        // Try to load from src/main/resources directory
        String propFile = "src/main/resources/traffic-analysis.properties";
        
        try (FileInputStream fis = new FileInputStream(propFile)) {
            properties.load(fis);
            System.out.println("Loaded properties from: " + propFile);
        } catch (IOException e) {
            System.err.println("Warning: Could not load properties from " + propFile + ". Using defaults.");
            System.err.println("Error: " + e.getMessage());
        }
        
        return properties;
    }
    
    /**
     * Utility method to run an external Python script and capture its output
     */
    public static String runPythonScript(String scriptPath, String input) throws IOException {
        ProcessBuilder pb = new ProcessBuilder("python", scriptPath);
        Process process = pb.start();
        
        // Write input to the process
        if (input != null) {
            process.getOutputStream().write(input.getBytes());
            process.getOutputStream().close();
        }
        
        // Read the output
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            output.append(line);
            output.append("\n");
        }
        
        try {
            process.waitFor();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        return output.toString();
    }

    /**
     * Determine the appropriate number of reducers based on analysis type and input data size
     * @param conf Hadoop configuration
     * @param analysisType Type of analysis
     * @param inputPath Path to input data
     * @return Appropriate number of reducers
     */
    private static int determineReducerCount(Configuration conf, String analysisType, Path inputPath) throws IOException {
        // Get the input file size
        FileSystem fs = FileSystem.get(conf);
        long inputSize = fs.getFileStatus(inputPath).getLen();
        
        // Base number of reducers on input size (1 reducer per 32MB of input)
        int sizeBasedReducers = Math.max(1, (int)(inputSize / (32 * 1024 * 1024)));
        
        // Adjust based on analysis type
        switch(analysisType) {
            case "timeframe":
            case "location":
                // These analyses benefit from more reducers
                return Math.min(20, sizeBasedReducers * 2);
            case "sentiment":
            case "brands":
                // These have more complex reduce logic
                return Math.min(16, sizeBasedReducers * 2);
            case "traffic":
            case "trend":
                // Standard number of reducers
                return Math.min(12, sizeBasedReducers);
            default:
                // Default case
                return Math.min(8, sizeBasedReducers);
        }
    }

    /**
     * Generate a CSV header based on the analysis type
     */
    private static String generateCSVHeader(String analysisType) {
        switch (analysisType) {
            case "sentiment":
                return "Category,Sentiment,Count";
            case "trend":
                return "Keyword,Count";
            case "traffic":
                return "Category,Incident,Count";
            case "location":
                return "Location,Count";
            case "timeframe":
                return "TimeCategory,Period,Count";
            case "brands":
                return "Brand,Count";
            default:
                return "Key,Count";
        }
    }
    
    /**
     * Generate a visualization-friendly summary of the analysis results
     */
    private static void generateVisualizationSummary(Configuration conf, String outputPath, String analysisType) {
        try {
            // Create an HDFS file manager
            HDFSFileManager hdfsManager = new HDFSFileManager(conf);
            
            // Create the visualization directory
            String visualizationDir = outputPath + "/visualization";
            hdfsManager.mkdir(visualizationDir);
            
            // Combine results into a JSON object
            JSONObject summary = hdfsManager.combineAnalysisResults(outputPath, analysisType);
            
            // Add metadata to the summary
            summary.put("analysis_type", analysisType);
            summary.put("timestamp", new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new java.util.Date()));
            summary.put("output_path", outputPath);
            
            // Save as a JSON file
            hdfsManager.saveJsonToFile(summary, visualizationDir + "/summary.json", true);
            
            // Save as a CSV file for compatibility
            StringBuilder csvContent = new StringBuilder();
            csvContent.append("key,value\n");
            
            // Extract the data based on analysis type
            JSONArray dataArray = summary.getJSONArray("data");
            for (int i = 0; i < dataArray.length(); i++) {
                JSONObject item = dataArray.getJSONObject(i);
                String key = item.getString("key");
                int value = item.getInt("value");
                csvContent.append(key).append(",").append(value).append("\n");
            }
            
            hdfsManager.writeToFile(csvContent.toString(), visualizationDir + "/summary.csv");
            
            System.out.println("Generated visualization summary at: " + visualizationDir);
            
            // Close the HDFS manager
            hdfsManager.close();
        } catch (Exception e) {
            System.err.println("Error generating visualization summary: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * Process output files to create visualization-friendly data
     */
    private static JSONObject processOutputFiles(FileSystem fs, Path outputDir, String analysisType) throws IOException {
        JSONObject results = new JSONObject();
        
        // For each type of analysis, we need to aggregate different statistics
        switch (analysisType) {
            case "sentiment":
                results.put("sentiments", processSentimentOutput(fs, outputDir));
                break;
            case "location":
                results.put("locations", processLocationOutput(fs, outputDir));
                break;
            case "timeframe":
                results.put("timeframes", processTimeframeOutput(fs, outputDir));
                break;
            case "brands":
                results.put("brands", processBrandsOutput(fs, outputDir));
                break;
            case "trend":
            case "traffic":
            default:
                results.put("trends", processGenericOutput(fs, outputDir));
                break;
        }
        
        return results;
    }
    
    /**
     * Process sentiment output files
     */
    private static JSONArray processSentimentOutput(FileSystem fs, Path outputDir) throws IOException {
        JSONArray sentiments = new JSONArray();
        Map<String, Integer> sentimentCounts = new HashMap<>();
        int totalCount = 0;
        
        // Find part files and read them
        for (FileStatus status : fs.listStatus(outputDir, path -> path.getName().startsWith("part-"))) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(fs.open(status.getPath())))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("\\s+");
                    if (parts.length >= 2 && parts[0].contains("sentiment:")) {
                        String sentiment = parts[0].substring(parts[0].lastIndexOf(":") + 1);
                        int count = Integer.parseInt(parts[1]);
                        
                        sentimentCounts.put(sentiment, sentimentCounts.getOrDefault(sentiment, 0) + count);
                        totalCount += count;
                    }
                }
            }
        }
        
        // Convert to JSON array
        for (Map.Entry<String, Integer> entry : sentimentCounts.entrySet()) {
            JSONObject sentimentObj = new JSONObject();
            sentimentObj.put("sentiment", entry.getKey());
            sentimentObj.put("count", entry.getValue());
            sentimentObj.put("percentage", totalCount > 0 ? (entry.getValue() * 100.0 / totalCount) : 0);
            sentiments.put(sentimentObj);
        }
        
        return sentiments;
    }
    
    /**
     * Process location output files
     */
    private static JSONArray processLocationOutput(FileSystem fs, Path outputDir) throws IOException {
        // Implement location-specific processing
        JSONArray locations = new JSONArray();
        Map<String, Integer> locationCounts = new HashMap<>();
        
        // Find part files and read them
        for (FileStatus status : fs.listStatus(outputDir, path -> path.getName().startsWith("part-"))) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(fs.open(status.getPath())))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("\\s+");
                    if (parts.length >= 2 && parts[0].contains("location:")) {
                        String location = parts[0].substring(parts[0].lastIndexOf(":") + 1);
                        int count = Integer.parseInt(parts[1]);
                        
                        locationCounts.put(location, locationCounts.getOrDefault(location, 0) + count);
                    }
                }
            }
        }
        
        // Convert to JSON array with approximate coordinates
        Map<String, double[]> locationCoordinates = getLocationCoordinates();
        int totalIncidents = 0;
        
        for (Map.Entry<String, Integer> entry : locationCounts.entrySet()) {
            JSONObject locationObj = new JSONObject();
            locationObj.put("name", entry.getKey());
            locationObj.put("count", entry.getValue());
            
            // Add coordinates if available
            if (locationCoordinates.containsKey(entry.getKey())) {
                double[] coords = locationCoordinates.get(entry.getKey());
                JSONObject coordinates = new JSONObject();
                coordinates.put("lat", coords[0]);
                coordinates.put("lng", coords[1]);
                coordinates.put("description", "Traffic incidents: " + entry.getValue());
                locationObj.put("coordinates", coordinates);
            }
            
            locations.put(locationObj);
            totalIncidents += entry.getValue();
        }
        
        // Add summary info
        JSONObject summaryObj = new JSONObject();
        summaryObj.put("total_incidents", totalIncidents);
        summaryObj.put("total_locations", locationCounts.size());
        locations.put(summaryObj);
        
        return locations;
    }
    
    /**
     * Process timeframe output files
     */
    private static JSONArray processTimeframeOutput(FileSystem fs, Path outputDir) throws IOException {
        // Implement timeframe-specific processing
        JSONArray timeframes = new JSONArray();
        Map<String, Map<String, Integer>> timeframeCounts = new HashMap<>();
        
        // Categories to track
        timeframeCounts.put("time_of_day", new HashMap<>());
        timeframeCounts.put("day_of_week", new HashMap<>());
        timeframeCounts.put("month", new HashMap<>());
        timeframeCounts.put("hour", new HashMap<>());
        
        // Find part files and read them
        for (FileStatus status : fs.listStatus(outputDir, path -> path.getName().startsWith("part-"))) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(fs.open(status.getPath())))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("\\s+");
                    if (parts.length >= 2 && parts[0].contains(":")) {
                        String key = parts[0];
                        int count = Integer.parseInt(parts[1]);
                        
                        for (String category : timeframeCounts.keySet()) {
                            if (key.startsWith(category + ":")) {
                                String value = key.substring(category.length() + 1);
                                Map<String, Integer> counts = timeframeCounts.get(category);
                                counts.put(value, counts.getOrDefault(value, 0) + count);
                                break;
                            }
                        }
                    }
                }
            }
        }
        
        // Convert to JSON array
        for (Map.Entry<String, Map<String, Integer>> categoryEntry : timeframeCounts.entrySet()) {
            String category = categoryEntry.getKey();
            Map<String, Integer> counts = categoryEntry.getValue();
            
            JSONObject categoryObj = new JSONObject();
            categoryObj.put("category", category);
            
            JSONArray values = new JSONArray();
            for (Map.Entry<String, Integer> valueEntry : counts.entrySet()) {
                JSONObject valueObj = new JSONObject();
                valueObj.put("value", valueEntry.getKey());
                valueObj.put("count", valueEntry.getValue());
                values.put(valueObj);
            }
            
            categoryObj.put("data", values);
            timeframes.put(categoryObj);
        }
        
        return timeframes;
    }
    
    /**
     * Process brands output files
     */
    private static JSONArray processBrandsOutput(FileSystem fs, Path outputDir) throws IOException {
        // Implement brands-specific processing
        JSONArray brands = new JSONArray();
        Map<String, Integer> brandCounts = new HashMap<>();
        
        // Find part files and read them
        for (FileStatus status : fs.listStatus(outputDir, path -> path.getName().startsWith("part-"))) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(fs.open(status.getPath())))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("\\s+");
                    if (parts.length >= 2 && parts[0].contains("brand:")) {
                        String brand = parts[0].substring(parts[0].lastIndexOf(":") + 1);
                        int count = Integer.parseInt(parts[1]);
                        
                        brandCounts.put(brand, brandCounts.getOrDefault(brand, 0) + count);
                    }
                }
            }
        }
        
        // Convert to JSON array
        for (Map.Entry<String, Integer> entry : brandCounts.entrySet()) {
            JSONObject brandObj = new JSONObject();
            brandObj.put("brand", entry.getKey());
            brandObj.put("count", entry.getValue());
            brandObj.put("total", entry.getValue()); // For compatibility with visualization
            brands.put(brandObj);
        }
        
        return brands;
    }
    
    /**
     * Process generic output files for trends and other analysis types
     */
    private static JSONArray processGenericOutput(FileSystem fs, Path outputDir) throws IOException {
        JSONArray results = new JSONArray();
        Map<String, Integer> counts = new HashMap<>();
        
        // Find part files and read them
        for (FileStatus status : fs.listStatus(outputDir, path -> path.getName().startsWith("part-"))) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(fs.open(status.getPath())))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.split("\\s+");
                    if (parts.length >= 2) {
                        String key = parts[0];
                        int count = Integer.parseInt(parts[1]);
                        
                        counts.put(key, counts.getOrDefault(key, 0) + count);
                    }
                }
            }
        }
        
        // Convert to JSON array
        for (Map.Entry<String, Integer> entry : counts.entrySet()) {
            JSONObject obj = new JSONObject();
            String key = entry.getKey();
            
            if (key.contains(":")) {
                obj.put("category", key.substring(0, key.indexOf(":")));
                obj.put("keyword", key.substring(key.indexOf(":") + 1));
            } else {
                obj.put("keyword", key);
            }
            
            obj.put("count", entry.getValue());
            results.put(obj);
        }
        
        return results;
    }

    /**
     * Get approximate coordinates for Singapore locations
     */
    private static Map<String, double[]> getLocationCoordinates() {
        Map<String, double[]> coordinates = new HashMap<>();
        
        // Add major areas with approximate latitude and longitude
        coordinates.put("woodlands", new double[]{1.4382, 103.7891});
        coordinates.put("jurong", new double[]{1.3329, 103.7436});
        coordinates.put("tampines", new double[]{1.3546, 103.9450});
        coordinates.put("changi", new double[]{1.3644, 103.9915});
        coordinates.put("yishun", new double[]{1.4304, 103.8354});
        coordinates.put("ang mo kio", new double[]{1.3691, 103.8454});
        coordinates.put("amk", new double[]{1.3691, 103.8454});
        coordinates.put("bedok", new double[]{1.3236, 103.9273});
        coordinates.put("clementi", new double[]{1.3162, 103.7649});
        coordinates.put("punggol", new double[]{1.3984, 103.9069});
        coordinates.put("sengkang", new double[]{1.3868, 103.8914});
        coordinates.put("orchard", new double[]{1.3050, 103.8324});
        coordinates.put("raffles", new double[]{1.2902, 103.8519});
        coordinates.put("marina", new double[]{1.2800, 103.8550});
        coordinates.put("sentosa", new double[]{1.2494, 103.8303});
        coordinates.put("bugis", new double[]{1.3009, 103.8559});
        coordinates.put("chinatown", new double[]{1.2808, 103.8443});
        coordinates.put("little india", new double[]{1.3067, 103.8517});
        coordinates.put("kallang", new double[]{1.3100, 103.8719});
        coordinates.put("novena", new double[]{1.3203, 103.8439});
        coordinates.put("serangoon", new double[]{1.3554, 103.8679});
        
        // Add expressways with approximate midpoints
        coordinates.put("pie", new double[]{1.3400, 103.8000});
        coordinates.put("cte", new double[]{1.3200, 103.8400});
        coordinates.put("sle", new double[]{1.4000, 103.8100});
        coordinates.put("bke", new double[]{1.3900, 103.7700});
        coordinates.put("tpe", new double[]{1.3700, 103.9300});
        coordinates.put("ecp", new double[]{1.2950, 103.9200});
        coordinates.put("aye", new double[]{1.3300, 103.7200});
        coordinates.put("kje", new double[]{1.3800, 103.7400});
        coordinates.put("mce", new double[]{1.2800, 103.8600});
        
        return coordinates;
    }

    /**
     * Copy results to a web-accessible location in HDFS
     */
    private static void copyResultsToWebLocation(Configuration conf, String outputPath, String analysisType) {
        try {
            // Create an HDFS file manager
            HDFSFileManager hdfsManager = new HDFSFileManager(conf);
            
            // Get the web output directory
            String webOutputDir = conf.get("hdfs.web.directory", "/user/hadoop/traffic-web");
            
            // Create a unique directory name for this analysis
            String timestamp = new java.text.SimpleDateFormat("yyyyMMdd-HHmmss").format(new java.util.Date());
            String webResultDir = webOutputDir + "/" + analysisType + "-" + timestamp;
            
            // Create the web result directory
            hdfsManager.mkdir(webResultDir);
            
            // Get the visualization summary
            JSONObject summary = hdfsManager.combineAnalysisResults(outputPath, analysisType);
            
            // Save the summary to the web directory
            hdfsManager.saveJsonToFile(summary, webResultDir + "/visualization.json", true);
            
            // Create a summary file with metadata
            JSONObject metadata = new JSONObject();
            metadata.put("analysis_type", analysisType);
            metadata.put("timestamp", timestamp);
            metadata.put("path", webResultDir);
            
            // Save the metadata for the web app
            hdfsManager.appendToFile(metadata.toString() + "\n", webOutputDir + "/analyses.jsonl");
            
            System.out.println("Copied analysis results to web-accessible location: " + webResultDir);
            
            // Close the HDFS manager
            hdfsManager.close();
        } catch (Exception e) {
            System.err.println("Error copying results to web location: " + e.getMessage());
            e.printStackTrace();
        }
    }
} 