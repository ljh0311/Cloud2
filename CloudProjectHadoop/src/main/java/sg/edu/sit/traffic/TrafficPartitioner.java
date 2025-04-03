package sg.edu.sit.traffic;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Partitioner;

/**
 * Custom partitioner for the Traffic Analysis job.
 * This partitioner ensures that related types of data are sent to the same reducer.
 * For example, all location data goes to one partition, all sentiment data to another, etc.
 * This improves the efficiency of the reducers and makes the output data more organized.
 */
public class TrafficPartitioner extends Partitioner<Text, IntWritable> {

    @Override
    public int getPartition(Text key, IntWritable value, int numPartitions) {
        String keyText = key.toString();
        
        // Use a different partition for each analysis type
        if (keyText.startsWith("location:")) {
            // Location data goes to partition 0
            return 0 % numPartitions;
        } else if (keyText.startsWith("sentiment:") || keyText.startsWith("traffic_sentiment:")) {
            // Sentiment data goes to partition 1
            return 1 % numPartitions;
        } else if (keyText.startsWith("brand:") || keyText.startsWith("brand_comment:")) {
            // Brand data goes to partition 2
            return 2 % numPartitions;
        } else if (keyText.startsWith("timeframe:") || keyText.startsWith("time_of_day:") || 
                  keyText.startsWith("day_of_week:") || keyText.startsWith("month:") ||
                  keyText.startsWith("hour:") || keyText.startsWith("day_type:")) {
            // Timeframe data goes to partition 3
            return 3 % numPartitions;
        } else if (keyText.startsWith("keyword:") || keyText.startsWith("phrase:")) {
            // Keyword data goes to partition 4
            return 4 % numPartitions;
        } else if (keyText.startsWith("category:")) {
            // Category data goes to partition 5
            return 5 % numPartitions;
        } else if (keyText.startsWith("score:") || keyText.startsWith("comments:")) {
            // Engagement metrics go to partition 6
            return 6 % numPartitions;
        } else if (keyText.startsWith("flair:") || keyText.startsWith("topic:")) {
            // Topic/flair data goes to partition 7
            return 7 % numPartitions;
        } else if (keyText.startsWith("school:")) {
            // Driving school data goes to partition 8
            return 8 % numPartitions;
        }
        
        // Default partition for any other data
        // Use hash code to distribute evenly across remaining partitions
        return Math.abs(keyText.hashCode()) % numPartitions;
    }
} 