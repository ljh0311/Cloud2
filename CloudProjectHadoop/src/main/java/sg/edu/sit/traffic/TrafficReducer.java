package sg.edu.sit.traffic;

import java.io.IOException;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.conf.Configuration;
import java.util.*;
import org.apache.hadoop.io.WritableComparable;
import org.apache.hadoop.io.WritableComparator;
import java.io.DataInput;
import java.io.DataOutput;

public class TrafficReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private String analysisType;
    private TreeMap<Integer, List<String>> topN;
    private int n; // Configurable N for top-N results
    private Map<String, Integer> brandTotals; // For aggregating brand mentions
    private Map<String, List<Integer>> valuesByKey; // For custom aggregations
    private boolean enableSecondarySort;
    private String aggregationType;

    @Override
    protected void setup(Context context) throws IOException, InterruptedException {
        Configuration conf = context.getConfiguration();
        analysisType = conf.get("analysis.type", "trend");
        
        // Get configurable N for top-N results (default 10)
        n = conf.getInt("analysis.topn", 10);
        
        // Check if secondary sort is enabled
        enableSecondarySort = conf.getBoolean("analysis.secondary.sort", false);
        
        // Get the aggregation type
        aggregationType = conf.get("analysis.aggregation", "sum");
        
        topN = new TreeMap<>(Collections.reverseOrder()); // Sort in descending order
        
        if (analysisType.equals("brands")) {
            brandTotals = new HashMap<>();
        }
        
        // Initialize data structure for custom aggregations
        valuesByKey = new HashMap<>();
    }

    @Override
    public void reduce(Text key, Iterable<IntWritable> values, Context context)
            throws IOException, InterruptedException {
        // Collect all values for this key for custom aggregations
        List<Integer> valuesList = new ArrayList<>();
        for (IntWritable val : values) {
            valuesList.add(val.get());
        }
        
        // Store values for potential custom aggregations
        valuesByKey.put(key.toString(), valuesList);
        
        // Calculate the aggregation based on configuration
        int aggregatedValue = performAggregation(valuesList, aggregationType);
        
        // For secondary sorting, we'll aggregate the values but won't output anything yet
        if (enableSecondarySort) {
            if (analysisType.equals("brands")) {
                handleBrandsWithSecondarySorting(key.toString(), aggregatedValue, context);
            } else {
                handleGenericWithSecondarySorting(key.toString(), aggregatedValue, context);
            }
            return;
        }
        
        // If secondary sorting is disabled, proceed with regular behavior
        switch (analysisType.toLowerCase()) {
            case "brands":
                handleBrands(key.toString(), aggregatedValue, context);
                break;
            case "sentiment":
                // For sentiment, output directly as we only have three categories
                context.write(key, new IntWritable(aggregatedValue));
                break;
            case "trend":
            case "traffic":
            case "location":
            case "topic":
            case "timeframe":
                // For these types, track top N results
                if (!topN.containsKey(aggregatedValue)) {
                    topN.put(aggregatedValue, new ArrayList<>());
                }
                topN.get(aggregatedValue).add(key.toString());
                break;
            case "engagement":
                // For engagement metrics, output all values
                context.write(key, new IntWritable(aggregatedValue));
                break;
            default:
                // Default behavior: output all results
                context.write(key, new IntWritable(aggregatedValue));
        }
    }

    /**
     * Perform aggregation on the values based on the specified aggregation type
     */
    private int performAggregation(List<Integer> values, String aggregationType) {
        if (values.isEmpty()) {
            return 0;
        }
        
        switch (aggregationType.toLowerCase()) {
            case "sum":
                // Sum all values (default)
                return values.stream().mapToInt(Integer::intValue).sum();
            case "max":
                // Take the maximum value
                return values.stream().mapToInt(Integer::intValue).max().orElse(0);
            case "min":
                // Take the minimum value
                return values.stream().mapToInt(Integer::intValue).min().orElse(0);
            case "avg":
                // Calculate the average
                return (int) Math.round(values.stream().mapToInt(Integer::intValue).average().orElse(0));
            case "median":
                // Calculate the median
                List<Integer> sorted = new ArrayList<>(values);
                Collections.sort(sorted);
                if (sorted.size() % 2 == 0) {
                    int mid = sorted.size() / 2;
                    return (sorted.get(mid - 1) + sorted.get(mid)) / 2;
                } else {
                    return sorted.get(sorted.size() / 2);
                }
            case "count":
                // Just count the number of values
                return values.size();
            default:
                // Default to sum
                return values.stream().mapToInt(Integer::intValue).sum();
        }
    }
    
    /**
     * Handle brands analysis with secondary sorting
     */
    private void handleBrandsWithSecondarySorting(String keyStr, int sum, Context context) 
            throws IOException, InterruptedException {
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
            context.write(new Text(keyStr), new IntWritable(sum));
        }
    }
    
    /**
     * Handle generic analysis types with secondary sorting
     */
    private void handleGenericWithSecondarySorting(String keyStr, int sum, Context context) 
            throws IOException, InterruptedException {
        // Add to topN
        if (!topN.containsKey(sum)) {
            topN.put(sum, new ArrayList<>());
        }
        topN.get(sum).add(keyStr);
    }

    /**
     * Handle brands analysis without secondary sorting
     */
    private void handleBrands(String keyStr, int sum, Context context) 
            throws IOException, InterruptedException {
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
            context.write(new Text(keyStr), new IntWritable(sum));
        }
    }

    @Override
    protected void cleanup(Context context) throws IOException, InterruptedException {
        // Process results differently based on secondary sorting configuration
        if (enableSecondarySort) {
            outputWithSecondarySorting(context);
        } else {
            outputStandard(context);
        }
    }
    
    /**
     * Output results with secondary sorting (alphabetical order within same count)
     */
    private void outputWithSecondarySorting(Context context) throws IOException, InterruptedException {
        if (analysisType.equals("brands")) {
            // Output brand category totals
            for (Map.Entry<String, Integer> entry : brandTotals.entrySet()) {
                context.write(new Text("total:" + entry.getKey()), new IntWritable(entry.getValue()));
            }
        }
        
        // Output top items with secondary sorting
        int count = 0;
        // Iterate through counts in descending order
        for (Map.Entry<Integer, List<String>> entry : topN.entrySet()) {
            // Sort the terms for each count alphabetically (secondary sort)
            Collections.sort(entry.getValue());
            for (String term : entry.getValue()) {
                if (count >= n) break;
                context.write(new Text(term), new IntWritable(entry.getKey()));
                count++;
            }
            if (count >= n) break;
        }
    }
    
    /**
     * Output results with standard approach (no secondary sorting)
     */
    private void outputStandard(Context context) throws IOException, InterruptedException {
        if (analysisType.equals("brands")) {
            // Output brand category totals
            for (Map.Entry<String, Integer> entry : brandTotals.entrySet()) {
                context.write(new Text("total:" + entry.getKey()), new IntWritable(entry.getValue()));
            }
            
            // Output top individual brand mentions
            int count = 0;
            for (Map.Entry<Integer, List<String>> entry : topN.entrySet()) {
                for (String term : entry.getValue()) {
                    if (count >= n) break;
                    context.write(new Text(term), new IntWritable(entry.getKey()));
                    count++;
                }
                if (count >= n) break;
            }
        } else if (analysisType.equals("trend") || 
                   analysisType.equals("traffic") || 
                   analysisType.equals("location") || 
                   analysisType.equals("topic") ||
                   analysisType.equals("timeframe")) {
            int count = 0;
            // Iterate through counts in descending order
            for (Map.Entry<Integer, List<String>> entry : topN.entrySet()) {
                // Sort the terms for each count alphabetically
                Collections.sort(entry.getValue());
                for (String term : entry.getValue()) {
                    if (count >= n) break;
                    context.write(new Text(term), new IntWritable(entry.getKey()));
                    count++;
                }
                if (count >= n) break;
            }
        }
    }

    /**
     * Composite key for secondary sorting in Hadoop
     */
    public static class CompositeKey implements WritableComparable<CompositeKey> {
        private Text category;
        private IntWritable count;
        
        public CompositeKey() {
            this.category = new Text();
            this.count = new IntWritable();
        }
        
        public CompositeKey(String category, int count) {
            this.category = new Text(category);
            this.count = new IntWritable(count);
        }
        
        @Override
        public void write(DataOutput out) throws IOException {
            category.write(out);
            count.write(out);
        }
        
        @Override
        public void readFields(DataInput in) throws IOException {
            category.readFields(in);
            count.readFields(in);
        }
        
        @Override
        public int compareTo(CompositeKey other) {
            // Primary sort by count (descending)
            int cmp = -count.compareTo(other.count);
            if (cmp != 0) {
                return cmp;
            }
            // Secondary sort by category (ascending)
            return category.compareTo(other.category);
        }
        
        @Override
        public boolean equals(Object obj) {
            if (obj instanceof CompositeKey) {
                CompositeKey other = (CompositeKey) obj;
                return category.equals(other.category) && count.equals(other.count);
            }
            return false;
        }
        
        @Override
        public int hashCode() {
            return Objects.hash(category, count);
        }
    }
    
    /**
     * Grouping comparator for secondary sort
     * Groups records by the natural key for the reducer
     */
    public static class GroupingComparator extends WritableComparator {
        public GroupingComparator() {
            super(CompositeKey.class, true);
        }
        
        @Override
        public int compare(WritableComparable a, WritableComparable b) {
            CompositeKey key1 = (CompositeKey) a;
            CompositeKey key2 = (CompositeKey) b;
            // Group only by category
            return key1.category.compareTo(key2.category);
        }
    }
} 