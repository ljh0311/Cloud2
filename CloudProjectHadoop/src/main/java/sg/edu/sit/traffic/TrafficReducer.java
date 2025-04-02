package sg.edu.sit.traffic;

import java.io.IOException;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.conf.Configuration;
import java.util.*;

public class TrafficReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private String analysisType;
    private TreeMap<Integer, List<String>> topN;
    private final int N = 10; // Top N results to keep
    private Map<String, Integer> brandTotals; // For aggregating brand mentions

    @Override
    protected void setup(Context context) throws IOException, InterruptedException {
        Configuration conf = context.getConfiguration();
        analysisType = conf.get("analysis.type", "trend");
        topN = new TreeMap<>(Collections.reverseOrder()); // Sort in descending order
        
        if (analysisType.equals("brands")) {
            brandTotals = new HashMap<>();
        }
    }

    @Override
    public void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {
        int sum = 0;
        for (IntWritable val : values) {
            sum += val.get();
        }

        switch (analysisType.toLowerCase()) {
            case "brands":
                // For brands analysis, we want to track both individual mentions and category totals
                String keyStr = key.toString();
                if (keyStr.startsWith("brand:")) {
                    // Extract the brand name
                    String[] parts = keyStr.split(":");
                    String brand = parts[parts.length - 1];
                    
                    // Add to brand totals
                    brandTotals.put(brand, brandTotals.getOrDefault(brand, 0) + sum);
                    
                    // Add to topN for individual brand mentions
                    if (!topN.containsKey(sum)) {
                        topN.put(sum, new ArrayList<>());
                    }
                    topN.get(sum).add(keyStr);
                } else {
                    // Direct output for comment mentions
                    context.write(key, new IntWritable(sum));
                }
                break;

            case "sentiment":
                // For sentiment, we output directly as we only have three categories
                context.write(key, new IntWritable(sum));
                break;

            case "trend":
            case "traffic":
            case "location":
            case "topic":
                // For these types, we want to track top N results
                if (!topN.containsKey(sum)) {
                    topN.put(sum, new ArrayList<>());
                }
                topN.get(sum).add(key.toString());
                break;

            case "engagement":
                // For engagement metrics, output all values
                context.write(key, new IntWritable(sum));
                break;

            default:
                // Default behavior: output all results
                context.write(key, new IntWritable(sum));
        }
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        if (analysisType.equals("brands")) {
            // Output brand category totals
            for (Map.Entry<String, Integer> entry : brandTotals.entrySet()) {
                context.write(new Text("total:" + entry.getKey()), new IntWritable(entry.getValue()));
            }
            
            // Output top individual brand mentions
            int count = 0;
            for (Map.Entry<Integer, List<String>> entry : topN.entrySet()) {
                Collections.sort(entry.getValue());
                for (String term : entry.getValue()) {
                    if (count >= N) break;
                    context.write(new Text(term), new IntWritable(entry.getKey()));
                    count++;
                }
                if (count >= N) break;
            }
        } else if (analysisType.equals("trend") || 
                   analysisType.equals("traffic") || 
                   analysisType.equals("location") || 
                   analysisType.equals("topic")) {
            int count = 0;
            // Iterate through counts in descending order
            for (Map.Entry<Integer, List<String>> entry : topN.entrySet()) {
                // Sort the terms for each count alphabetically
                Collections.sort(entry.getValue());
                for (String term : entry.getValue()) {
                    if (count >= N) break;
                    context.write(new Text(term), new IntWritable(entry.getKey()));
                    count++;
                }
                if (count >= N) break;
            }
        }
    }
} 