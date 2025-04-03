package sg.edu.sit.traffic;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Utility class for HDFS file operations
 * Provides methods for reading, writing, and managing files in HDFS
 */
public class HDFSFileManager {
    
    private Configuration conf;
    private FileSystem fs;
    
    /**
     * Constructor with Hadoop configuration
     */
    public HDFSFileManager(Configuration conf) throws IOException {
        this.conf = conf;
        this.fs = FileSystem.get(conf);
    }
    
    /**
     * Check if a file or directory exists in HDFS
     */
    public boolean exists(String path) throws IOException {
        return fs.exists(new Path(path));
    }
    
    /**
     * Create a directory in HDFS
     */
    public boolean mkdir(String path) throws IOException {
        return fs.mkdirs(new Path(path));
    }
    
    /**
     * Delete a file or directory in HDFS
     */
    public boolean delete(String path, boolean recursive) throws IOException {
        return fs.delete(new Path(path), recursive);
    }
    
    /**
     * List files in a directory
     */
    public List<String> listFiles(String directory) throws IOException {
        List<String> fileList = new ArrayList<>();
        FileStatus[] statuses = fs.listStatus(new Path(directory));
        
        for (FileStatus status : statuses) {
            fileList.add(status.getPath().getName());
        }
        
        return fileList;
    }
    
    /**
     * Write a string to a file in HDFS
     */
    public void writeToFile(String content, String filePath) throws IOException {
        Path path = new Path(filePath);
        
        // Create parent directories if they don't exist
        Path parent = path.getParent();
        if (parent != null && !fs.exists(parent)) {
            fs.mkdirs(parent);
        }
        
        try (FSDataOutputStream out = fs.create(path, true)) {
            out.writeBytes(content);
        }
    }
    
    /**
     * Append content to an existing file in HDFS
     */
    public void appendToFile(String content, String filePath) throws IOException {
        Path path = new Path(filePath);
        
        if (!fs.exists(path)) {
            writeToFile(content, filePath);
            return;
        }
        
        try (FSDataOutputStream out = fs.append(path)) {
            out.writeBytes(content);
        }
    }
    
    /**
     * Read a file from HDFS and return its content as a string
     */
    public String readFile(String filePath) throws IOException {
        Path path = new Path(filePath);
        StringBuilder content = new StringBuilder();
        
        try (FSDataInputStream in = fs.open(path);
             BufferedReader reader = new BufferedReader(new InputStreamReader(in))) {
            
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
        }
        
        return content.toString();
    }
    
    /**
     * Copy a file from HDFS to the local file system
     */
    public void copyToLocal(String hdfsPath, String localPath) throws IOException {
        fs.copyToLocalFile(new Path(hdfsPath), new Path(localPath));
    }
    
    /**
     * Copy a file from the local file system to HDFS
     */
    public void copyFromLocal(String localPath, String hdfsPath) throws IOException {
        fs.copyFromLocalFile(new Path(localPath), new Path(hdfsPath));
    }
    
    /**
     * Save a JSONObject to a file in HDFS
     */
    public void saveJsonToFile(JSONObject json, String filePath, boolean pretty) throws IOException {
        String content = pretty ? json.toString(2) : json.toString();
        writeToFile(content, filePath);
    }
    
    /**
     * Save a JSONArray to a file in HDFS
     */
    public void saveJsonArrayToFile(JSONArray jsonArray, String filePath, boolean pretty) throws IOException {
        String content = pretty ? jsonArray.toString(2) : jsonArray.toString();
        writeToFile(content, filePath);
    }
    
    /**
     * Read a JSON file from HDFS and parse it as a JSONObject
     */
    public JSONObject readJsonObject(String filePath) throws IOException {
        String content = readFile(filePath);
        return new JSONObject(content);
    }
    
    /**
     * Read a JSON file from HDFS and parse it as a JSONArray
     */
    public JSONArray readJsonArray(String filePath) throws IOException {
        String content = readFile(filePath);
        return new JSONArray(content);
    }
    
    /**
     * Get all analysis results from a directory and combine them into a single visualization-friendly JSON
     */
    public JSONObject combineAnalysisResults(String directoryPath, String analysisType) throws IOException {
        JSONObject results = new JSONObject();
        results.put("analysis_type", analysisType);
        results.put("timestamp", new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new java.util.Date()));
        
        // Check if the directory exists
        if (!exists(directoryPath)) {
            // Return empty results with error message
            results.put("error", "Directory not found: " + directoryPath);
            results.put("data", new JSONArray());
            return results;
        }
        
        // Get all part files in the directory
        List<String> files = listFiles(directoryPath);
        List<JSONObject> partResults = new ArrayList<>();
        
        for (String file : files) {
            if (file.startsWith("part-") || file.equals("visualization_summary.json")) {
                try {
                    String content = readFile(directoryPath + "/" + file);
                    
                    // Check if the file is a JSON file 
                    if (file.endsWith(".json")) {
                        try {
                            // Attempt to parse as a single JSON object
                            JSONObject jsonObj = new JSONObject(content);
                            
                            // If this is a visualization summary, extract its results
                            if (file.equals("visualization_summary.json")) {
                                if (jsonObj.has("results")) {
                                    return jsonObj; // Return the summary directly
                                }
                            }
                            
                            partResults.add(jsonObj);
                        } catch (Exception e1) {
                            try {
                                // Try to parse as a JSON array
                                JSONArray jsonArr = new JSONArray(content);
                                for (int i = 0; i < jsonArr.length(); i++) {
                                    partResults.add(jsonArr.getJSONObject(i));
                                }
                            } catch (Exception e2) {
                                // If not a valid JSON array, try line by line
                                parseJsonLines(content, partResults);
                            }
                        }
                    } else {
                        // For non-JSON files, process line by line
                        parseJsonLines(content, partResults);
                    }
                } catch (Exception e) {
                    System.err.println("Error reading file " + file + ": " + e.getMessage());
                }
            }
        }
        
        // Check if we found any results
        if (partResults.isEmpty()) {
            // Try to read regular text files line by line
            for (String file : files) {
                if (file.startsWith("part-")) {
                    try {
                        String content = readFile(directoryPath + "/" + file);
                        String[] lines = content.split("\n");
                        
                        JSONArray dataArray = new JSONArray();
                        
                        for (String line : lines) {
                            line = line.trim();
                            if (!line.isEmpty()) {
                                // Try to parse as "key value" format
                                String[] parts = line.split("\\s+");
                                if (parts.length >= 2) {
                                    String key = parts[0];
                                    // Try to parse the value as an integer
                                    try {
                                        int value = Integer.parseInt(parts[parts.length - 1]);
                                        JSONObject item = new JSONObject();
                                        item.put("key", key);
                                        item.put("value", value);
                                        dataArray.put(item);
                                    } catch (NumberFormatException e) {
                                        // Ignore non-numeric values
                                    }
                                }
                            }
                        }
                        
                        if (dataArray.length() > 0) {
                            results.put("data", dataArray);
                            return results;
                        }
                    } catch (Exception e) {
                        System.err.println("Error processing file " + file + ": " + e.getMessage());
                    }
                }
            }
            
            // If we still have no results, return empty data
            results.put("data", new JSONArray());
            results.put("message", "No data found in " + directoryPath);
            return results;
        }
        
        // Organize results by category
        JSONObject categories = new JSONObject();
        JSONArray dataArray = new JSONArray();
        
        for (JSONObject result : partResults) {
            // Convert to standardized format for the visualization
            JSONObject standardItem = new JSONObject();
            
            if (result.has("key")) {
                standardItem.put("key", result.getString("key"));
                
                // Use either "value" or "count" field
                if (result.has("value")) {
                    standardItem.put("value", result.getInt("value"));
                } else if (result.has("count")) {
                    standardItem.put("value", result.getInt("count"));
                } else {
                    // Default to 1 if no value/count is found
                    standardItem.put("value", 1);
                }
                
                dataArray.put(standardItem);
                
                // Also organize by categories
                String key = result.getString("key");
                String category = "other";
                if (key.contains(":")) {
                    category = key.substring(0, key.indexOf(":"));
                }
                
                if (!categories.has(category)) {
                    categories.put(category, new JSONArray());
                }
                
                categories.getJSONArray(category).put(result);
            }
        }
        
        // Sort data array by value (descending)
        JSONArray sortedData = new JSONArray();
        List<JSONObject> dataList = new ArrayList<>();
        
        for (int i = 0; i < dataArray.length(); i++) {
            dataList.add(dataArray.getJSONObject(i));
        }
        
        Collections.sort(dataList, new Comparator<JSONObject>() {
            @Override
            public int compare(JSONObject a, JSONObject b) {
                int valA = a.optInt("value", 0);
                int valB = b.optInt("value", 0);
                return Integer.compare(valB, valA); // Descending order
            }
        });
        
        for (JSONObject item : dataList) {
            sortedData.put(item);
        }
        
        results.put("data", sortedData);
        results.put("categories", categories);
        return results;
    }
    
    /**
     * Parse content as JSON Lines format (one JSON object per line)
     */
    private void parseJsonLines(String content, List<JSONObject> results) {
        String[] lines = content.split("\n");
        
        for (String line : lines) {
            line = line.trim();
            if (!line.isEmpty()) {
                try {
                    // Try to parse as JSON
                    JSONObject json = new JSONObject(line);
                    results.add(json);
                } catch (Exception e) {
                    // Try to parse as key-value format if it's not valid JSON
                    try {
                        String[] parts = line.split("\\s+");
                        if (parts.length >= 2) {
                            String key = parts[0];
                            int value = Integer.parseInt(parts[parts.length - 1]);
                            
                            JSONObject item = new JSONObject();
                            item.put("key", key);
                            item.put("value", value);
                            results.add(item);
                        }
                    } catch (Exception e2) {
                        // Skip lines that can't be parsed
                    }
                }
            }
        }
    }
    
    /**
     * Close the file system
     */
    public void close() throws IOException {
        if (fs != null) {
            fs.close();
        }
    }
} 