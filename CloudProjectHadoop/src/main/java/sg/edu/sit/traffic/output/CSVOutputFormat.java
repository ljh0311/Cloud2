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
import org.apache.hadoop.io.compress.CompressionCodec;
import org.apache.hadoop.io.compress.GzipCodec;
import org.apache.hadoop.mapreduce.RecordWriter;
import org.apache.hadoop.mapreduce.TaskAttemptContext;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.ReflectionUtils;

/**
 * Custom OutputFormat that writes data as CSV files.
 * This format is useful for easy import into tools like Excel or Tableau.
 */
public class CSVOutputFormat<K, V> extends FileOutputFormat<K, V> {
    // Default field separator
    public static String DEFAULT_SEPARATOR = ",";
    // Default newline character sequence
    public static String DEFAULT_NEWLINE = "\n";
    // Field separator configuration key
    public static String CSV_SEPARATOR = "mapreduce.output.csv.separator";
    // Include header configuration key
    public static String CSV_INCLUDE_HEADER = "mapreduce.output.csv.include.header";
    // CSV header configuration key
    public static String CSV_HEADER = "mapreduce.output.csv.header";

    /**
     * RecordWriter implementation for CSV format
     */
    protected static class CSVRecordWriter<K, V> extends RecordWriter<K, V> {
        private DataOutputStream out;
        private String separator;
        private String newline;
        private boolean firstLine = true;
        private boolean includeHeader;
        private String header;

        public CSVRecordWriter(DataOutputStream out, String separator, String header, boolean includeHeader) {
            this.out = out;
            this.separator = separator;
            this.newline = DEFAULT_NEWLINE;
            this.header = header;
            this.includeHeader = includeHeader;
        }

        /**
         * Write the key and value as a CSV record
         */
        @Override
        public void write(K key, V value) throws IOException {
            if (includeHeader && firstLine && header != null && !header.isEmpty()) {
                out.write(header.getBytes("UTF-8"));
                out.write(newline.getBytes("UTF-8"));
                firstLine = false;
            }
            
            if (key == null && value == null) {
                return;
            }
            
            if (key == null) {
                writeObject(value);
            } else if (value == null) {
                writeObject(key);
            } else {
                writeObject(key);
                out.write(separator.getBytes("UTF-8"));
                writeObject(value);
            }
            out.write(newline.getBytes("UTF-8"));
        }

        /**
         * Convert an object to a string and write it to the output, escaping special characters
         */
        private void writeObject(Object o) throws IOException, UnsupportedEncodingException {
            if (o instanceof Text) {
                String text = o.toString();
                // Escape quotes and special characters
                text = text.replace("\"", "\"\"");
                if (text.contains("\"") || text.contains(separator) || text.contains("\n")) {
                    text = "\"" + text + "\"";
                }
                out.write(text.getBytes("UTF-8"));
            } else {
                out.write(o.toString().getBytes("UTF-8"));
            }
        }

        @Override
        public void close(TaskAttemptContext context) throws IOException {
            out.close();
        }
    }

    @Override
    public RecordWriter<K, V> getRecordWriter(TaskAttemptContext context) throws IOException {
        Configuration conf = context.getConfiguration();
        
        // Get the field separator from configuration, or use default
        String separator = conf.get(CSV_SEPARATOR, DEFAULT_SEPARATOR);
        
        // Get the CSV header from configuration
        String header = conf.get(CSV_HEADER, "");
        
        // Check if header should be included
        boolean includeHeader = conf.getBoolean(CSV_INCLUDE_HEADER, true);
        
        // Check if output should be compressed
        boolean isCompressed = getCompressOutput(context);
        
        // Set up the output file
        Path file = getDefaultWorkFile(context, ".csv");
        FileSystem fs = file.getFileSystem(conf);
        
        if (!isCompressed) {
            FSDataOutputStream fileOut = fs.create(file, false);
            return new CSVRecordWriter<K, V>(fileOut, separator, header, includeHeader);
        } else {
            // If output should be compressed, use compression codec
            Class<? extends CompressionCodec> codecClass = getOutputCompressorClass(context, GzipCodec.class);
            CompressionCodec codec = ReflectionUtils.newInstance(codecClass, conf);
            
            // Create the compressed output file with codec extension
            Path compressedFile = file.suffix(codec.getDefaultExtension());
            FSDataOutputStream fileOut = fs.create(compressedFile, false);
            return new CSVRecordWriter<K, V>(new DataOutputStream(codec.createOutputStream(fileOut)), separator, header, includeHeader);
        }
    }
} 