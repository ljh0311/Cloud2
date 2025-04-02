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

/**
 * Main driver class for Singapore Traffic Analysis system.
 * This class handles command-line arguments and sets up the MapReduce jobs
 * for trend analysis, sentiment analysis, location analysis, and car brand analysis.
 */
public class TrafficAnalysisDriver {

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        
        if (otherArgs.length != 3) {
            System.err.println("Usage: TrafficAnalysis <input> <analysis_type> <output>");
            System.err.println("Analysis types: sentiment, trend, traffic, location, topic, engagement, brands");
            System.exit(2);
        }

        // Clean the input JSON file first
        String cleanedFilePath = cleanJsonDataset(otherArgs[0]);
        
        // Load properties
        Properties props = loadProperties();
        
        // Set the analysis type in configuration
        String analysisType = otherArgs[1].toLowerCase();
        conf.set("analysis.type", analysisType);

        // Generate output path with timestamp
        String outputPath = generateOutputPath(otherArgs[0], analysisType);
        
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

        Job job = Job.getInstance(conf, "Traffic Analysis - " + analysisType);
        job.setJarByClass(TrafficAnalysisDriver.class);
        
        // Set mapper and reducer classes
        job.setMapperClass(TrafficMapper.class);
        job.setReducerClass(TrafficReducer.class);
        
        // Set output key and value classes
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        
        // Set input and output paths - use cleaned file as input
        FileInputFormat.addInputPath(job, new Path(cleanedFilePath));
        FileOutputFormat.setOutputPath(job, new Path(outputPath));

        // Set the jar file
        job.setJar("target/CloudProjectHadoop-0.0.1-SNAPSHOT.jar");
        
        boolean success = job.waitForCompletion(true);
        
        // Clean up the temporary cleaned file
        new File(cleanedFilePath).delete();
        
        System.exit(success ? 0 : 1);
    }
    
    /**
     * Generate output path with timestamp
     * @param inputPath Original input file path
     * @param analysisType Type of analysis being performed
     * @return Generated output path
     */
    private static String generateOutputPath(String inputPath, String analysisType) {
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
        return String.format("%s_%s_%s", datasetName, analysisType, timestamp);
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
} 