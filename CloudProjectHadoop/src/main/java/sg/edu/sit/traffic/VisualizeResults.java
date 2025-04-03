package sg.edu.sit.traffic;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;

/**
 * Command-line tool to generate visualizations from analysis results
 */
public class VisualizeResults {
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: VisualizeResults <input_path> <output_dir> [template_dir]");
            System.out.println("  input_path: HDFS path containing analysis results");
            System.out.println("  output_dir: Local directory to save visualization files");
            System.out.println("  template_dir: Optional. Directory containing HTML templates (defaults to 'templates')");
            System.exit(1);
        }
        
        String inputPath = args[0];
        String outputDir = args[1];
        String templateDir = args.length > 2 ? args[2] : "templates";
        
        // Ensure template dir exists and is valid
        File templateDirFile = new File(templateDir);
        if (!templateDirFile.exists() || !templateDirFile.isDirectory()) {
            // Try to find templates in resources
            templateDir = "src/main/resources/templates";
            templateDirFile = new File(templateDir);
            
            if (!templateDirFile.exists() || !templateDirFile.isDirectory()) {
                System.err.println("Error: Template directory not found at '" + templateDir + "'");
                System.exit(1);
            }
        }
        
        // Ensure output dir exists
        File outputDirFile = new File(outputDir);
        if (!outputDirFile.exists()) {
            if (!outputDirFile.mkdirs()) {
                System.err.println("Error: Could not create output directory '" + outputDir + "'");
                System.exit(1);
            }
        }
        
        try {
            // Initialize Hadoop configuration
            Configuration conf = new Configuration();
            
            // Check if input path exists
            FileSystem fs = FileSystem.get(conf);
            Path inputHdfsPath = new Path(inputPath);
            
            if (!fs.exists(inputHdfsPath)) {
                System.err.println("Error: Input path '" + inputPath + "' does not exist in HDFS");
                System.exit(1);
            }
            
            System.out.println("Generating visualizations from " + inputPath + "...");
            
            // Initialize the visualization generator
            VisualizationGenerator visualizer = new VisualizationGenerator(conf, templateDir, outputDir);
            
            // Track generated visualization paths
            List<String> generatedVisualizations = new ArrayList<>();
            
            // Check for specific analysis types
            String[] analysisTypes = {"brands", "keywords", "sentiment", "heatmap", "time"};
            boolean foundAnyAnalysis = false;
            
            for (String analysisType : analysisTypes) {
                Path analysisPath = new Path(inputPath + "/" + analysisType);
                
                if (fs.exists(analysisPath)) {
                    foundAnyAnalysis = true;
                    System.out.println("Found " + analysisType + " analysis. Generating visualization...");
                    
                    try {
                        String visualizationPath = visualizer.generateVisualization(inputPath + "/" + analysisType, analysisType);
                        generatedVisualizations.add(visualizationPath);
                        System.out.println("Generated " + analysisType + " visualization at: " + visualizationPath);
                    } catch (Exception e) {
                        System.err.println("Error generating visualization for " + analysisType + ": " + e.getMessage());
                        e.printStackTrace();
                    }
                }
            }
            
            // If we found specific analysis types, generate an index page
            if (foundAnyAnalysis) {
                String indexPath = visualizer.generateIndexPage(generatedVisualizations);
                System.out.println("Generated index page at: " + indexPath);
            } else {
                // No specific analysis types found, try the base directory
                try {
                    System.out.println("No specific analysis types found. Treating input as single analysis...");
                    
                    // Try to determine the analysis type from directory name
                    String analysisType = new Path(inputPath).getName();
                    String visualizationPath = visualizer.generateVisualization(inputPath, analysisType);
                    
                    System.out.println("Generated visualization at: " + visualizationPath);
                } catch (Exception e) {
                    System.err.println("Error generating visualization: " + e.getMessage());
                    e.printStackTrace();
                    System.exit(1);
                }
            }
            
            // Close the visualizer
            visualizer.close();
            
            System.out.println("Visualization generation complete!");
            System.out.println("To view the results, open " + outputDir + "/index.html in a web browser.");
            
        } catch (IOException e) {
            System.err.println("Error accessing HDFS: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
} 