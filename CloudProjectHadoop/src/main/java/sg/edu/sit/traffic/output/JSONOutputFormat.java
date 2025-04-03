package sg.edu.sit.traffic.output;

import java.io.DataOutputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.compress.CompressionCodec;
import org.apache.hadoop.io.compress.GzipCodec;
import org.apache.hadoop.mapreduce.RecordWriter;
import org.apache.hadoop.mapreduce.TaskAttemptContext;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.ReflectionUtils;
import org.json.JSONObject;
import org.json.JSONArray;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

/**
 * Custom OutputFormat that writes data as JSON files.
 * This format provides a structured JSON output for easy consumption by web applications.
 */
public class JSONOutputFormat<K, V> extends FileOutputFormat<K, V> {
    // Format options
    public static String JSON_AS_ARRAY = "mapreduce.output.json.as.array";
    public static String JSON_PRETTY_PRINT = "mapreduce.output.json.pretty";
    public static String JSON_NEWLINE_SEPARATED = "mapreduce.output.json.newline.separated";
    
    // Analysis type key for adding metadata
    public static String JSON_ANALYSIS_TYPE = "mapreduce.output.json.analysis.type";
    
    // Default formatting options
    public static boolean DEFAULT_AS_ARRAY = false;
    public static boolean DEFAULT_PRETTY_PRINT = false;
    public static boolean DEFAULT_NEWLINE_SEPARATED = true;

    /**
     * RecordWriter implementation for JSON format
     */
    protected static class JSONRecordWriter<K, V> extends RecordWriter<K, V> {
        private DataOutputStream out;
        private boolean asArray;
        private boolean prettyPrint;
        private boolean newlineSeparated;
        private String analysisType;
        private boolean firstRecord = true;
        private Map<String, List<JSONObject>> recordsByType;
        
        public JSONRecordWriter(DataOutputStream out, boolean asArray, boolean prettyPrint, 
                               boolean newlineSeparated, String analysisType) {
            this.out = out;
            this.asArray = asArray;
            this.prettyPrint = prettyPrint;
            this.newlineSeparated = newlineSeparated;
            this.analysisType = analysisType;
            
            // Initialize record collection if we're writing as a single array
            if (asArray) {
                recordsByType = new HashMap<>();
            }
            
            try {
                // If we're writing as an array, write the array start
                if (asArray) {
                    out.write("{\n".getBytes("UTF-8"));
                    if (analysisType != null && !analysisType.isEmpty()) {
                        out.write(("  \"analysis_type\": \"" + analysisType + "\",\n").getBytes("UTF-8"));
                        out.write(("  \"generated_at\": \"" + new java.util.Date() + "\",\n").getBytes("UTF-8"));
                    }
                    out.write("  \"results\": {\n".getBytes("UTF-8"));
                }
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

        /**
         * Write the key and value as a JSON record
         */
        @Override
        public void write(K key, V value) throws IOException {
            if (key == null) {
                return;
            }
            
            JSONObject json = new JSONObject();
            String keyStr = key.toString();
            int count = 0;
            
            // Parse the key to determine category
            String category = "other";
            if (keyStr.contains(":")) {
                category = keyStr.substring(0, keyStr.indexOf(":"));
            }
            
            if (value instanceof IntWritable) {
                count = ((IntWritable) value).get();
            }
            
            // Add data to JSON object
            json.put("key", keyStr);
            json.put("count", count);
            
            // Add additional fields based on key type
            if (keyStr.startsWith("location:")) {
                String location = keyStr.substring(keyStr.lastIndexOf(":") + 1);
                json.put("location", location);
            } else if (keyStr.startsWith("brand:")) {
                String brand = keyStr.substring(keyStr.lastIndexOf(":") + 1);
                json.put("brand", brand);
            } else if (keyStr.startsWith("sentiment:")) {
                String sentiment = keyStr.substring(keyStr.lastIndexOf(":") + 1);
                json.put("sentiment", sentiment);
            }
            
            if (asArray) {
                // Add to collection for array output at close
                List<JSONObject> records = recordsByType.computeIfAbsent(category, k -> new ArrayList<>());
                records.add(json);
            } else {
                // Write directly as newline-separated JSON objects
                String jsonStr = json.toString(prettyPrint ? 2 : 0);
                
                if (newlineSeparated) {
                    out.write(jsonStr.getBytes("UTF-8"));
                    out.write("\n".getBytes("UTF-8"));
                } else {
                    if (!firstRecord) {
                        out.write(",".getBytes("UTF-8"));
                        if (prettyPrint) {
                            out.write("\n".getBytes("UTF-8"));
                        }
                    }
                    out.write(jsonStr.getBytes("UTF-8"));
                    firstRecord = false;
                }
            }
        }

        @Override
        public void close(TaskAttemptContext context) throws IOException {
            if (asArray) {
                // Write all collected records as a JSON array by category
                boolean firstCategory = true;
                for (Map.Entry<String, List<JSONObject>> entry : recordsByType.entrySet()) {
                    if (!firstCategory) {
                        out.write(",\n".getBytes("UTF-8"));
                    }
                    
                    String category = entry.getKey();
                    List<JSONObject> records = entry.getValue();
                    
                    out.write(("    \"" + category + "\": [\n").getBytes("UTF-8"));
                    
                    for (int i = 0; i < records.size(); i++) {
                        String jsonStr = records.get(i).toString(prettyPrint ? 4 : 0);
                        out.write(("      " + jsonStr).getBytes("UTF-8"));
                        
                        if (i < records.size() - 1) {
                            out.write(",\n".getBytes("UTF-8"));
                        } else {
                            out.write("\n".getBytes("UTF-8"));
                        }
                    }
                    
                    out.write("    ]".getBytes("UTF-8"));
                    firstCategory = false;
                }
                
                // Close the JSON object
                out.write("\n  }\n}".getBytes("UTF-8"));
            } else if (!newlineSeparated) {
                // Close the array if not newline separated
                out.write("\n]".getBytes("UTF-8"));
            }
            
            out.close();
        }
    }

    @Override
    public RecordWriter<K, V> getRecordWriter(TaskAttemptContext context) throws IOException {
        Configuration conf = context.getConfiguration();
        
        // Get format options from configuration
        boolean asArray = conf.getBoolean(JSON_AS_ARRAY, DEFAULT_AS_ARRAY);
        boolean prettyPrint = conf.getBoolean(JSON_PRETTY_PRINT, DEFAULT_PRETTY_PRINT);
        boolean newlineSeparated = conf.getBoolean(JSON_NEWLINE_SEPARATED, DEFAULT_NEWLINE_SEPARATED);
        String analysisType = conf.get(JSON_ANALYSIS_TYPE, "");
        
        // Check if output should be compressed
        boolean isCompressed = getCompressOutput(context);
        
        // Set up the output file
        Path file = getDefaultWorkFile(context, ".json");
        FileSystem fs = file.getFileSystem(conf);
        
        if (!isCompressed) {
            FSDataOutputStream fileOut = fs.create(file, false);
            return new JSONRecordWriter<K, V>(fileOut, asArray, prettyPrint, newlineSeparated, analysisType);
        } else {
            // If output should be compressed, use compression codec
            Class<? extends CompressionCodec> codecClass = getOutputCompressorClass(context, GzipCodec.class);
            CompressionCodec codec = ReflectionUtils.newInstance(codecClass, conf);
            
            // Create the compressed output file with codec extension
            Path compressedFile = file.suffix(codec.getDefaultExtension());
            FSDataOutputStream fileOut = fs.create(compressedFile, false);
            return new JSONRecordWriter<K, V>(new DataOutputStream(codec.createOutputStream(fileOut)), 
                                             asArray, prettyPrint, newlineSeparated, analysisType);
        }
    }
} 