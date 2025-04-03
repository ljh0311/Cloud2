package sg.edu.sit.traffic;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.jobcontrol.ControlledJob;
import org.apache.hadoop.mapreduce.lib.jobcontrol.JobControl;
import org.apache.hadoop.util.GenericOptionsParser;
import sg.edu.sit.traffic.output.JSONOutputFormat;

/**
 * Driver class for complex multi-stage traffic analysis
 * This class implements job chaining to perform multiple analyses in sequence
 */
public class ComplexAnalysisDriver {
    
    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        
        if (otherArgs.length != 3) {
            System.err.println("Usage: ComplexAnalysis <input> <analysis_types> <output>");
            System.err.println("Analysis types: comma-separated list of: sentiment,trend,traffic,location,timeframe,brands");
            System.exit(2);
        }
        
        String inputPath = otherArgs[0];
        String[] analysisTypes = otherArgs[1].toLowerCase().split(",");
        String outputBasePath = otherArgs[2];
        
        // First job is always to clean the input data
        String cleanedDataPath = inputPath + "_cleaned";
        
        // Create job controller
        JobControl jobControl = new JobControl("ComplexTrafficAnalysis");
        
        // Setup the cleaning job
        ControlledJob cleaningJob = setupCleaningJob(conf, inputPath, cleanedDataPath);
        jobControl.addJob(cleaningJob);
        
        // List to hold all analysis jobs for tracking
        List<ControlledJob> analysisJobs = new ArrayList<>();
        
        // Create a job for each analysis type
        for (String analysisType : analysisTypes) {
            String outputPath = outputBasePath + "/" + analysisType;
            ControlledJob analysisJob = setupAnalysisJob(conf, cleanedDataPath, analysisType, outputPath);
            
            // This job depends on the cleaning job
            analysisJob.addDependingJob(cleaningJob);
            
            // Add job to controller
            jobControl.addJob(analysisJob);
            analysisJobs.add(analysisJob);
        }
        
        // If we have multiple analysis jobs, set up a final aggregation job
        if (analysisJobs.size() > 1) {
            // Set up paths for the aggregation job
            List<String> inputPaths = new ArrayList<>();
            for (String analysisType : analysisTypes) {
                inputPaths.add(outputBasePath + "/" + analysisType);
            }
            
            String finalOutputPath = outputBasePath + "/aggregated";
            ControlledJob aggregationJob = setupAggregationJob(conf, inputPaths, finalOutputPath, analysisTypes);
            
            // Add dependencies on all analysis jobs
            for (ControlledJob analysisJob : analysisJobs) {
                aggregationJob.addDependingJob(analysisJob);
            }
            
            // Add job to controller
            jobControl.addJob(aggregationJob);
        }
        
        // Run the job chain in a separate thread
        Thread jobControlThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    jobControl.run();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        
        // Start the thread
        jobControlThread.start();
        
        // Wait until all jobs complete
        while (!jobControl.allFinished()) {
            System.out.println("Jobs in waiting state: " + jobControl.getWaitingJobList().size());
            System.out.println("Jobs in ready state: " + jobControl.getReadyJobsList().size());
            System.out.println("Jobs in running state: " + jobControl.getRunningJobList().size());
            System.out.println("Jobs in success state: " + jobControl.getSuccessfulJobList().size());
            System.out.println("Jobs in failed state: " + jobControl.getFailedJobList().size());
            Thread.sleep(5000);
        }
        
        // Stop the controller
        jobControl.stop();
        
        // Check if all jobs completed successfully
        if (jobControl.getFailedJobList().size() > 0) {
            System.err.println("Some jobs failed!");
            for (ControlledJob job : jobControl.getFailedJobList()) {
                System.err.println("Failed job: " + job.getJobName());
            }
            System.exit(1);
        }
        
        System.out.println("All jobs completed successfully!");
        System.exit(0);
    }
    
    /**
     * Set up a job for cleaning the input data
     */
    private static ControlledJob setupCleaningJob(Configuration conf, String inputPath, String outputPath) 
            throws IOException {
        // Create a new configuration for this job
        Configuration jobConf = new Configuration(conf);
        
        Job job = Job.getInstance(jobConf, "Data Cleaning");
        job.setJarByClass(ComplexAnalysisDriver.class);
        
        // Use custom mapper and reducer for cleaning
        job.setMapperClass(CleaningMapper.class);
        job.setReducerClass(CleaningReducer.class);
        
        // Set output key and value classes
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        
        // Set paths
        FileInputFormat.addInputPath(job, new Path(inputPath));
        FileOutputFormat.setOutputPath(job, new Path(outputPath));
        
        return new ControlledJob(job, null);
    }
    
    /**
     * Set up a job for a specific analysis type
     */
    private static ControlledJob setupAnalysisJob(Configuration conf, String inputPath, String analysisType, 
            String outputPath) throws IOException {
        // Create a new configuration for this job
        Configuration jobConf = new Configuration(conf);
        jobConf.set("analysis.type", analysisType);
        
        Job job = Job.getInstance(jobConf, "Traffic Analysis - " + analysisType);
        job.setJarByClass(ComplexAnalysisDriver.class);
        
        // Set mapper and reducer classes
        job.setMapperClass(TrafficMapper.class);
        job.setReducerClass(TrafficReducer.class);
        
        // Set partitioner
        job.setPartitionerClass(TrafficPartitioner.class);
        
        // Set output key and value classes
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);
        
        // For JSON output
        job.setOutputFormatClass(JSONOutputFormat.class);
        jobConf.setBoolean(JSONOutputFormat.JSON_AS_ARRAY, true);
        jobConf.setBoolean(JSONOutputFormat.JSON_PRETTY_PRINT, true);
        jobConf.set(JSONOutputFormat.JSON_ANALYSIS_TYPE, analysisType);
        
        // Set paths
        FileInputFormat.addInputPath(job, new Path(inputPath));
        FileOutputFormat.setOutputPath(job, new Path(outputPath));
        
        return new ControlledJob(job, null);
    }
    
    /**
     * Set up an aggregation job to combine results from multiple analyses
     */
    private static ControlledJob setupAggregationJob(Configuration conf, List<String> inputPaths, 
            String outputPath, String[] analysisTypes) throws IOException {
        // Create a new configuration for this job
        Configuration jobConf = new Configuration(conf);
        
        // Store the analysis types as a comma-separated string
        jobConf.set("analysis.types", String.join(",", analysisTypes));
        
        Job job = Job.getInstance(jobConf, "Traffic Analysis Aggregation");
        job.setJarByClass(ComplexAnalysisDriver.class);
        
        // Set mapper and reducer classes
        job.setMapperClass(AggregationMapper.class);
        job.setReducerClass(AggregationReducer.class);
        
        // Set output key and value classes
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        
        // For JSON output
        job.setOutputFormatClass(JSONOutputFormat.class);
        jobConf.setBoolean(JSONOutputFormat.JSON_AS_ARRAY, true);
        jobConf.setBoolean(JSONOutputFormat.JSON_PRETTY_PRINT, true);
        jobConf.set(JSONOutputFormat.JSON_ANALYSIS_TYPE, "aggregated");
        
        // Add all input paths
        for (String path : inputPaths) {
            FileInputFormat.addInputPath(job, new Path(path));
        }
        
        FileOutputFormat.setOutputPath(job, new Path(outputPath));
        
        return new ControlledJob(job, null);
    }
}

/**
 * Mapper for the data cleaning job
 */
class CleaningMapper extends org.apache.hadoop.mapreduce.Mapper<Object, Text, Text, Text> {
    private Text outputKey = new Text("json");
    private Text outputValue = new Text();
    
    @Override
    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString().trim();
        
        if (line.isEmpty()) {
            return;
        }
        
        // Clean and validate the JSON
        try {
            // Parse as JSON to validate
            org.json.JSONObject json = new org.json.JSONObject(line);
            
            // Simplified JSON with only required fields
            org.json.JSONObject cleanJson = new org.json.JSONObject();
            
            // Copy only required fields
            if (json.has("title")) {
                cleanJson.put("title", json.getString("title"));
            }
            if (json.has("text")) {
                cleanJson.put("text", json.getString("text"));
            }
            if (json.has("created_utc")) {
                cleanJson.put("created_utc", json.get("created_utc"));
            }
            if (json.has("flair")) {
                cleanJson.put("flair", json.getString("flair"));
            }
            if (json.has("score")) {
                cleanJson.put("score", json.getInt("score"));
            }
            if (json.has("num_comments")) {
                cleanJson.put("num_comments", json.getInt("num_comments"));
            }
            
            // Process comments if they exist
            if (json.has("comments")) {
                org.json.JSONArray comments = json.getJSONArray("comments");
                org.json.JSONArray cleanedComments = new org.json.JSONArray();
                
                for (int i = 0; i < comments.length(); i++) {
                    org.json.JSONObject comment = comments.getJSONObject(i);
                    org.json.JSONObject cleanedComment = new org.json.JSONObject();
                    
                    if (comment.has("text")) {
                        cleanedComment.put("text", comment.getString("text"));
                    }
                    if (comment.has("created_utc")) {
                        cleanedComment.put("created_utc", comment.get("created_utc"));
                    }
                    
                    cleanedComments.put(cleanedComment);
                }
                
                cleanJson.put("comments", cleanedComments);
            }
            
            // Set the cleaned JSON as output
            outputValue.set(cleanJson.toString());
            context.write(outputKey, outputValue);
            
        } catch (Exception e) {
            // Log error but don't propagate - we want to skip invalid records
            context.getCounter("CleaningMapper", "InvalidJSON").increment(1);
        }
    }
}

/**
 * Reducer for the data cleaning job
 */
class CleaningReducer extends org.apache.hadoop.mapreduce.Reducer<Text, Text, Text, Text> {
    private Text outputKey = new Text();
    
    @Override
    public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        // Just pass through the cleaned values
        int i = 0;
        for (Text value : values) {
            outputKey.set(Integer.toString(i++));
            context.write(outputKey, value);
        }
    }
}

/**
 * Mapper for the aggregation job
 */
class AggregationMapper extends org.apache.hadoop.mapreduce.Mapper<Object, Text, Text, Text> {
    private Text outputKey = new Text();
    private Text outputValue = new Text();
    
    @Override
    public void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString().trim();
        
        if (line.isEmpty()) {
            return;
        }
        
        try {
            // Parse the line as JSON
            org.json.JSONObject json = new org.json.JSONObject(line);
            
            // Extract the analysis type from input split
            String inputPath = context.getInputSplit().toString();
            String analysisType = "unknown";
            
            // Find the analysis type from the path
            for (String type : context.getConfiguration().get("analysis.types").split(",")) {
                if (inputPath.contains("/" + type + "/")) {
                    analysisType = type;
                    break;
                }
            }
            
            // Set the key as the analysis type
            outputKey.set(analysisType);
            
            // Set the value as the JSON data
            outputValue.set(json.toString());
            
            context.write(outputKey, outputValue);
        } catch (Exception e) {
            context.getCounter("AggregationMapper", "InvalidJSON").increment(1);
        }
    }
}

/**
 * Reducer for the aggregation job
 */
class AggregationReducer extends org.apache.hadoop.mapreduce.Reducer<Text, Text, Text, Text> {
    private Text outputKey = new Text();
    private Text outputValue = new Text();
    
    @Override
    public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {
        String analysisType = key.toString();
        
        // Create a JSON array for this analysis type
        org.json.JSONArray results = new org.json.JSONArray();
        
        // Process all values
        for (Text value : values) {
            try {
                org.json.JSONObject json = new org.json.JSONObject(value.toString());
                results.put(json);
            } catch (Exception e) {
                context.getCounter("AggregationReducer", "InvalidJSON").increment(1);
            }
        }
        
        // Create output
        org.json.JSONObject output = new org.json.JSONObject();
        output.put("analysis_type", analysisType);
        output.put("results", results);
        
        // Write output
        outputKey.set(analysisType);
        outputValue.set(output.toString());
        context.write(outputKey, outputValue);
    }
} 