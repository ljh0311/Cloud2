package sg.edu.sit.traffic;

import java.io.IOException;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.conf.Configuration;
import org.json.JSONObject;
import org.json.JSONArray;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
import java.util.HashSet;
import java.util.Set;

public class TrafficMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();
    private String analysisType;
    private Set<String> trafficKeywords;
    private Set<String> locationKeywords;
    private Set<String> drivingSchools;
    private Set<String> carBrands;

    @Override
    protected void setup(Context context) throws IOException, InterruptedException {
        Configuration conf = context.getConfiguration();
        analysisType = conf.get("analysis.type", "trend");
        
        // Initialize traffic keywords
        trafficKeywords = new HashSet<>();
        // Driving-related terms
        trafficKeywords.add("driving");
        trafficKeywords.add("driver");
        trafficKeywords.add("learner");
        trafficKeywords.add("instructor");
        trafficKeywords.add("lesson");
        trafficKeywords.add("test");
        trafficKeywords.add("license");
        trafficKeywords.add("practical");
        trafficKeywords.add("theory");
        trafficKeywords.add("parking");
        trafficKeywords.add("reverse");
        trafficKeywords.add("parallel");
        trafficKeywords.add("vertical");
        // Road conditions
        trafficKeywords.add("traffic");
        trafficKeywords.add("jam");
        trafficKeywords.add("road");
        trafficKeywords.add("route");
        trafficKeywords.add("highway");
        trafficKeywords.add("expressway");
        // Vehicle types
        trafficKeywords.add("car");
        trafficKeywords.add("bike");
        trafficKeywords.add("motorcycle");
        trafficKeywords.add("scooter");
        trafficKeywords.add("pmd");
        
        // Initialize location keywords
        locationKeywords = new HashSet<>();
        // Major expressways
        locationKeywords.add("pie");
        locationKeywords.add("cte");
        locationKeywords.add("sle");
        locationKeywords.add("bke");
        locationKeywords.add("tpe");
        locationKeywords.add("ecp");
        locationKeywords.add("aye");
        locationKeywords.add("kje");
        locationKeywords.add("mce");
        // Areas
        locationKeywords.add("woodlands");
        locationKeywords.add("jurong");
        locationKeywords.add("tampines");
        locationKeywords.add("changi");
        locationKeywords.add("yishun");
        locationKeywords.add("amk");
        locationKeywords.add("ang mo kio");
        locationKeywords.add("bedok");
        locationKeywords.add("clementi");
        locationKeywords.add("punggol");
        locationKeywords.add("sengkang");
        
        // Initialize driving schools
        drivingSchools = new HashSet<>();
        drivingSchools.add("cdc");
        drivingSchools.add("bbdc");
        drivingSchools.add("ssdc");
        drivingSchools.add("comfortdelgro");
        drivingSchools.add("private");
        drivingSchools.add("school");

        // Initialize car brands
        carBrands = new HashSet<>();
        // Japanese brands
        carBrands.add("toyota");
        carBrands.add("honda");
        carBrands.add("nissan");
        carBrands.add("mazda");
        carBrands.add("subaru");
        carBrands.add("mitsubishi");
        carBrands.add("lexus");
        carBrands.add("infiniti");
        // European brands
        carBrands.add("mercedes");
        carBrands.add("bmw");
        carBrands.add("audi");
        carBrands.add("volkswagen");
        carBrands.add("volvo");
        carBrands.add("porsche");
        carBrands.add("ferrari");
        carBrands.add("lamborghini");
        carBrands.add("maserati");
        carBrands.add("bentley");
        carBrands.add("rolls royce");
        carBrands.add("mini");
        carBrands.add("land rover");
        carBrands.add("jaguar");
        // Korean brands
        carBrands.add("hyundai");
        carBrands.add("kia");
        // American brands
        carBrands.add("ford");
        carBrands.add("chevrolet");
        carBrands.add("tesla");
        // Common model keywords
        carBrands.add("civic");
        carBrands.add("camry");
        carBrands.add("corolla");
        carBrands.add("altis");
        carBrands.add("vios");
        carBrands.add("accord");
        carBrands.add("cx5");
        carBrands.add("3series");
        carBrands.add("cclass");
        carBrands.add("eclass");
        carBrands.add("a4");
        carBrands.add("golf");
    }

    @Override
    public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString().trim();
        try {
            JSONObject json = new JSONObject(line);
            
            switch (analysisType.toLowerCase()) {
                case "trend":
                    processTrend(json, context);
                    break;
                case "sentiment":
                    processSentiment(json, context);
                    break;
                case "traffic":
                    processTraffic(json, context);
                    break;
                case "location":
                    processLocation(json, context);
                    break;
                case "engagement":
                    processEngagement(json, context);
                    break;
                case "topic":
                    processTopic(json, context);
                    break;
                case "brands":
                    processBrands(json, context);
                    break;
                default:
                    processTrend(json, context);
            }
            
            // Process comments if they exist
            if (json.has("comments")) {
                JSONArray comments = json.getJSONArray("comments");
                for (int i = 0; i < comments.length(); i++) {
                    JSONObject comment = comments.getJSONObject(i);
                    processComment(comment, context);
                }
            }
        } catch (Exception e) {
            System.err.println("Error processing line: " + e.getMessage());
        }
    }

    private void processTrend(JSONObject json, Context context) throws IOException, InterruptedException {
        String title = json.optString("title", "");
        String text = json.optString("text", "");
        String flair = json.optString("flair", "");
        
        // Process flair if present
        if (!flair.isEmpty()) {
            word.set("flair:" + flair.toLowerCase());
            context.write(word, one);
        }
        
        processText(title + " " + text, context);
    }

    private void processText(String text, Context context) throws IOException, InterruptedException {
        if (text == null || text.isEmpty() || text.equals("null")) return;
        
        // Clean the text
        text = text.toLowerCase()
                  .replaceAll("\\\\n", " ")
                  .replaceAll("\\\\t", " ")
                  .replaceAll("\\\\r", " ")
                  .replaceAll("[^a-z0-9#\\s]", " ")
                  .replaceAll("\\s+", " ")
                  .trim();

        // Process keywords
        String[] words = text.split("\\s+");
        for (String w : words) {
            if (w.length() > 2 && trafficKeywords.contains(w)) {
                word.set("keyword:" + w);
                context.write(word, one);
            }
            if (w.length() > 2 && drivingSchools.contains(w)) {
                word.set("school:" + w);
                context.write(word, one);
            }
        }

        // Process common phrases
        String[] phrases = {
            "driving school", "private instructor", "test slot", "practical lesson",
            "theory test", "driving test", "traffic light", "parking lot",
            "driving license", "road test", "circuit training", "driving centre"
        };
        
        for (String phrase : phrases) {
            if (text.contains(phrase)) {
                word.set("phrase:" + phrase.replace(" ", "_"));
                context.write(word, one);
            }
        }
    }

    private void processSentiment(JSONObject json, Context context) throws IOException, InterruptedException {
        String text = json.optString("title", "") + " " + json.optString("text", "");
        if (text.isEmpty()) return;
        
        // Positive indicators for driving/traffic context
        String[] positiveWords = {
            "good", "great", "excellent", "smooth", "helpful", "easy",
            "recommend", "worth", "convenient", "perfect", "pass", "success",
            "patient", "professional", "friendly", "clear", "efficient"
        };
        
        // Negative indicators
        String[] negativeWords = {
            "bad", "terrible", "horrible", "difficult", "hard", "expensive",
            "waste", "rude", "unprofessional", "fail", "confusing", "slow",
            "late", "cancel", "postpone", "poor", "stuck", "impossible"
        };
        
        text = text.toLowerCase();
        int positiveCount = 0;
        int negativeCount = 0;
        
        for (String word : positiveWords) {
            if (text.contains(word)) positiveCount++;
        }
        for (String word : negativeWords) {
            if (text.contains(word)) negativeCount++;
        }
        
        String sentiment;
        if (positiveCount > negativeCount) {
            sentiment = "positive";
        } else if (negativeCount > positiveCount) {
            sentiment = "negative";
        } else {
            sentiment = "neutral";
        }
        
        // Add flair context if available
        String flair = json.optString("flair", "");
        if (!flair.isEmpty()) {
            word.set("sentiment:" + flair.toLowerCase() + ":" + sentiment);
        } else {
            word.set("sentiment:" + sentiment);
        }
        context.write(word, one);
    }

    private void processTraffic(JSONObject json, Context context) throws IOException, InterruptedException {
        String title = json.optString("title", "");
        String text = json.optString("text", "");
        String flair = json.optString("flair", "").toLowerCase();
        
        // Process flair-specific content
        if (!flair.isEmpty()) {
            word.set("category:" + flair);
            context.write(word, one);
        }
        
        String combinedText = (title + " " + text).toLowerCase();
        
        // Process traffic-related categories
        if (combinedText.contains("driving school") || combinedText.contains("instructor")) {
            word.set("category:learning");
            context.write(word, one);
        }
        if (combinedText.contains("test") || combinedText.contains("exam")) {
            word.set("category:test");
            context.write(word, one);
        }
        if (combinedText.contains("route") || combinedText.contains("road")) {
            word.set("category:route");
            context.write(word, one);
        }
    }

    private void processLocation(JSONObject json, Context context) throws IOException, InterruptedException {
        String text = json.optString("title", "") + " " + json.optString("text", "");
        text = text.toLowerCase();
        
        // Check for locations
        for (String location : locationKeywords) {
            if (text.contains(location)) {
                String flair = json.optString("flair", "").toLowerCase();
                if (!flair.isEmpty()) {
                    word.set("location:" + flair + ":" + location);
                } else {
                    word.set("location:" + location);
                }
                context.write(word, one);
            }
        }
    }

    private void processTopic(JSONObject json, Context context) throws IOException, InterruptedException {
        String flair = json.optString("flair", "").toLowerCase();
        if (!flair.isEmpty()) {
            word.set("topic:" + flair);
            context.write(word, one);
        }
    }

    private void processEngagement(JSONObject json, Context context) throws IOException, InterruptedException {
        // Process Reddit-specific engagement metrics
        if (json.has("score")) {
            word.set("score");
            context.write(word, new IntWritable(json.getInt("score")));
        }
        if (json.has("num_comments")) {
            word.set("comments");
            context.write(word, new IntWritable(json.getInt("num_comments")));
        }
        
        // Add flair context to engagement if available
        String flair = json.optString("flair", "").toLowerCase();
        if (!flair.isEmpty() && json.has("score")) {
            word.set("score:" + flair);
            context.write(word, new IntWritable(json.getInt("score")));
        }
    }

    private void processBrands(JSONObject json, Context context) throws IOException, InterruptedException {
        String text = json.optString("title", "") + " " + json.optString("text", "");
        text = text.toLowerCase();
        
        // Check for car brands
        for (String brand : carBrands) {
            if (text.contains(brand)) {
                String flair = json.optString("flair", "").toLowerCase();
                if (!flair.isEmpty()) {
                    word.set("brand:" + flair + ":" + brand);
                } else {
                    word.set("brand:" + brand);
                }
                context.write(word, one);
            }
        }
        
        // Process car brand mentions in comments
        if (json.has("comments")) {
            JSONArray comments = json.getJSONArray("comments");
            for (int i = 0; i < comments.length(); i++) {
                JSONObject comment = comments.getJSONObject(i);
                String commentText = comment.optString("text", "").toLowerCase();
                for (String brand : carBrands) {
                    if (commentText.contains(brand)) {
                        word.set("brand_comment:" + brand);
                        context.write(word, one);
                    }
                }
            }
        }
    }

    private void processComment(JSONObject comment, Context context) throws IOException, InterruptedException {
        if (!comment.has("text")) return;
        
        switch (analysisType.toLowerCase()) {
            case "sentiment":
                processSentiment(comment, context);
                break;
            case "trend":
            case "traffic":
                processText(comment.getString("text"), context);
                break;
            case "location":
                processLocation(comment, context);
                break;
            case "brands":
                processBrands(comment, context);
                break;
        }
    }
} 