package sg.edu.sit.traffic;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Utility class for generating HTML/JavaScript visualizations from analysis results
 */
public class VisualizationGenerator {
    
    private Configuration conf;
    private HDFSFileManager hdfsManager;
    
    // Templates directory
    private String templatesDir;
    // Output directory for generated visualizations
    private String outputDir;
    
    /**
     * Constructor
     * 
     * @param conf Hadoop configuration
     * @param templatesDir Directory containing visualization templates
     * @param outputDir Directory to save generated visualizations
     * @throws IOException if HDFS operations fail
     */
    public VisualizationGenerator(Configuration conf, String templatesDir, String outputDir) throws IOException {
        this.conf = conf;
        this.templatesDir = templatesDir;
        this.outputDir = outputDir;
        this.hdfsManager = new HDFSFileManager(conf);
    }
    
    /**
     * Generate visualization for a specific analysis result
     * 
     * @param analysisPath The HDFS path containing analysis results
     * @param analysisType The type of analysis
     * @return The path to the generated visualization HTML file
     */
    public String generateVisualization(String analysisPath, String analysisType) throws IOException {
        // Get the summary JSON data
        JSONObject summary = hdfsManager.combineAnalysisResults(analysisPath, analysisType);
        
        // Choose appropriate visualization type
        String templateName = selectTemplateForAnalysis(analysisType);
        
        // Generate the HTML
        String htmlContent = generateHtmlFromTemplate(templateName, summary);
        
        // Create output directory if it doesn't exist
        new File(outputDir).mkdirs();
        
        // Write the HTML file
        String outputFilename = outputDir + File.separator + analysisType + "_visualization.html";
        FileWriter writer = new FileWriter(outputFilename);
        writer.write(htmlContent);
        writer.close();
        
        return outputFilename;
    }
    
    /**
     * Generate HTML content from a template and JSON data
     */
    private String generateHtmlFromTemplate(String templateName, JSONObject data) throws IOException {
        String templateContent = readTemplate(templateName);
        
        // Replace placeholders in the template
        String htmlContent = templateContent
                .replace("{{ANALYSIS_TYPE}}", data.getString("analysis_type"))
                .replace("{{TIMESTAMP}}", data.getString("timestamp"))
                .replace("{{DATA_JSON}}", data.toString());
        
        return htmlContent;
    }
    
    /**
     * Read a template file
     */
    private String readTemplate(String templateName) throws IOException {
        String templatePath = templatesDir + File.separator + templateName;
        return new String(Files.readAllBytes(Paths.get(templatePath)));
    }
    
    /**
     * Select the appropriate visualization template based on analysis type
     */
    private String selectTemplateForAnalysis(String analysisType) {
        switch (analysisType.toLowerCase()) {
            case "brands":
                return "brand_chart.html";
            case "keywords":
                return "keyword_chart.html";
            case "sentiment":
                return "sentiment_chart.html";
            case "heatmap":
                return "heatmap.html";
            case "time":
                return "time_series.html";
            default:
                // Try to use analysis.html as a more robust default template
                if (fileExists(templatesDir + File.separator + "analysis.html")) {
                    return "analysis.html";
                } else {
                    return "generic_chart.html";
                }
        }
    }
    
    /**
     * Check if a file exists
     */
    private boolean fileExists(String path) {
        return new File(path).exists();
    }
    
    /**
     * Generate an index page that links to all visualizations
     */
    public String generateIndexPage(List<String> visualizationPaths) throws IOException {
        StringBuilder linksHtml = new StringBuilder();
        
        for (String path : visualizationPaths) {
            File file = new File(path);
            String filename = file.getName();
            String analysisType = filename.replace("_visualization.html", "");
            
            linksHtml.append("<li><a href=\"").append(filename).append("\">")
                    .append(analysisType.toUpperCase()).append(" Analysis</a></li>\n");
        }
        
        String indexTemplate = readTemplate("index_template.html");
        String indexContent = indexTemplate
                .replace("{{VISUALIZATION_LINKS}}", linksHtml.toString())
                .replace("{{GENERATION_TIME}}", new java.util.Date().toString());
        
        String indexPath = outputDir + File.separator + "index.html";
        FileWriter writer = new FileWriter(indexPath);
        writer.write(indexContent);
        writer.close();
        
        return indexPath;
    }
    
    /**
     * Generate visualizations for all analysis results in a directory
     */
    public void generateAllVisualizations(String baseDir) throws IOException {
        List<String> generatedPaths = new ArrayList<>();
        
        // Find all analysis directories
        String[] analyses = {"brands", "keywords", "sentiment", "heatmap", "time"};
        
        for (String analysis : analyses) {
            String analysisPath = baseDir + "/" + analysis;
            
            // Check if this analysis exists
            if (hdfsManager.exists(analysisPath)) {
                String visualizationPath = generateVisualization(analysisPath, analysis);
                generatedPaths.add(visualizationPath);
                System.out.println("Generated visualization for " + analysis + " at " + visualizationPath);
            }
        }
        
        // Generate an index page
        if (!generatedPaths.isEmpty()) {
            String indexPath = generateIndexPage(generatedPaths);
            System.out.println("Generated index page at " + indexPath);
        }
    }
    
    /**
     * Close resources
     * 
     * @throws IOException if closing HDFS operations fail
     */
    public void close() throws IOException {
        if (hdfsManager != null) {
            hdfsManager.close();
        }
    }
} 