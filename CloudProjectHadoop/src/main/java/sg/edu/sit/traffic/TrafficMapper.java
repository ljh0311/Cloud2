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
    private Set<String> timeframeKeywords;

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
        // Traffic Conditions
        trafficKeywords.add("congestion");
        trafficKeywords.add("accident");
        trafficKeywords.add("collision");
        trafficKeywords.add("breakdown");
        trafficKeywords.add("roadwork");
        trafficKeywords.add("construction");
        trafficKeywords.add("closure");
        trafficKeywords.add("detour");
        trafficKeywords.add("delay");
        trafficKeywords.add("slow");
        // Weather Conditions
        trafficKeywords.add("rain");
        trafficKeywords.add("flood");
        trafficKeywords.add("wet");
        trafficKeywords.add("fog");
        trafficKeywords.add("haze");
        trafficKeywords.add("storm");
        trafficKeywords.add("typhoon");
        // Time-based Keywords
        trafficKeywords.add("peak");
        trafficKeywords.add("rush");
        trafficKeywords.add("hour");
        trafficKeywords.add("morning");
        trafficKeywords.add("evening");
        trafficKeywords.add("weekend");
        trafficKeywords.add("holiday");

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
        // Additional Location Keywords
        locationKeywords.add("orchard");
        locationKeywords.add("raffles");
        locationKeywords.add("marina");
        locationKeywords.add("sentosa");
        locationKeywords.add("bugis");
        locationKeywords.add("chinatown");
        locationKeywords.add("little india");
        locationKeywords.add("kallang");
        locationKeywords.add("novena");
        locationKeywords.add("serangoon");

        // Initialize driving schools
        drivingSchools = new HashSet<>();
        drivingSchools.add("cdc");
        drivingSchools.add("bbdc");
        drivingSchools.add("ssdc");
        drivingSchools.add("comfortdelgro");
        drivingSchools.add("private");
        drivingSchools.add("school");
        // Additional Driving School Keywords
        drivingSchools.add("comfort");
        drivingSchools.add("delgro");
        drivingSchools.add("instructor");
        drivingSchools.add("learner");
        drivingSchools.add("practical");
        drivingSchools.add("theory");
        drivingSchools.add("test");
        drivingSchools.add("circuit");
        drivingSchools.add("road");
        drivingSchools.add("license");

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
        // Malaysian brands
        carBrands.add("proton");
        carBrands.add("perodua");
        carBrands.add("saga");
        carBrands.add("myvi");
        carBrands.add("axia");
        carBrands.add("alza");
        carBrands.add("x70");
        // Common model keywords
        carBrands.add("civic");
        carBrands.add("camry");
        carBrands.add("corolla");
        carBrands.add("altis");
        carBrands.add("vios");
        carBrands.add("accord");
        carBrands.add("vezel");
        carBrands.add("freed");
        carBrands.add("fit");
        carBrands.add("jazz");
        carBrands.add("hiace");
        carBrands.add("lancer");
        carBrands.add("attrage");
        carBrands.add("cx5");
        carBrands.add("mazda3");
        carBrands.add("mazda5");
        carBrands.add("mazda6");
        carBrands.add("3series");
        carBrands.add("cclass");
        carBrands.add("eclass");
        carBrands.add("a4");
        carBrands.add("golf");
        carBrands.add("a3");

        // Initialize timeframe keywords
        timeframeKeywords = new HashSet<>();
        // Time of day
        timeframeKeywords.add("morning");
        timeframeKeywords.add("afternoon");
        timeframeKeywords.add("evening");
        timeframeKeywords.add("night");
        timeframeKeywords.add("dawn");
        timeframeKeywords.add("dusk");
        // Days of week
        timeframeKeywords.add("monday");
        timeframeKeywords.add("tuesday");
        timeframeKeywords.add("wednesday");
        timeframeKeywords.add("thursday");
        timeframeKeywords.add("friday");
        timeframeKeywords.add("saturday");
        timeframeKeywords.add("sunday");
        timeframeKeywords.add("weekday");
        timeframeKeywords.add("weekend");
        // Peak hours
        timeframeKeywords.add("peak");
        timeframeKeywords.add("off-peak");
        timeframeKeywords.add("rush hour");
        // Holidays
        timeframeKeywords.add("holiday");
        timeframeKeywords.add("public holiday");
        timeframeKeywords.add("school holiday");
        timeframeKeywords.add("festival");
        timeframeKeywords.add("new year");
        timeframeKeywords.add("chinese new year");
        timeframeKeywords.add("christmas");
        timeframeKeywords.add("hari raya");
        timeframeKeywords.add("deepavali");
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
                case "timeframe":
                    processTimeframe(json, context);
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
            // Track errors with counter
            context.getCounter("TrafficMapper", "ErrorCount").increment(1);
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
        if (text == null || text.isEmpty() || text.equals("null"))
            return;

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
        
        text = text.toLowerCase();
        
        // Positive indicators for driving/traffic context
        String[] positiveWords = {
            "good", "great", "excellent", "smooth", "helpful", "easy",
            "recommend", "worth", "convenient", "perfect", "pass", "success",
            "patient", "professional", "friendly", "clear", "efficient",
            // Additional traffic-specific positive terms
            "flowing", "uncongested", "quick", "fast", "reliable",
            "comfortable", "safe", "accessible", "improved", "upgraded",
            "expanded", "widened", "new lane", "green light", "synchronized",
            "smart traffic", "real-time", "well-maintained", "resurfaced"
        };
        
        // Negative indicators
        String[] negativeWords = {
            "bad", "terrible", "horrible", "difficult", "hard", "expensive",
            "waste", "rude", "unprofessional", "fail", "confusing", "slow",
            "late", "cancel", "postpone", "poor", "stuck", "impossible",
            // Additional traffic-specific negative terms
            "jam", "congested", "gridlock", "standstill", "bottleneck", 
            "bumper-to-bumper", "backed up", "crawling", "stop-and-go",
            "accident", "collision", "crash", "breakdown", "roadblock",
            "pothole", "construction", "detour", "closed", "narrow",
            "dangerous", "risky", "unsafe", "flooded", "icy", "slippery"
        };
        
        int positiveCount = 0;
        int negativeCount = 0;
        int positiveTrafficCount = 0;
        int negativeTrafficCount = 0;
        
        // Calculate regular sentiment score
        for (String word : positiveWords) {
            if (text.contains(word)) positiveCount++;
        }
        for (String word : negativeWords) {
            if (text.contains(word)) negativeCount++;
        }
        
        // Calculate traffic-related sentiment
        // First check if this post is about traffic or driving
        boolean isTrafficRelated = false;
        for (String keyword : trafficKeywords) {
            if (text.contains(keyword)) {
                isTrafficRelated = true;
                break;
            }
        }
        
        // If it's traffic-related, do a more detailed sentiment analysis
        if (isTrafficRelated) {
            // Weight traffic-specific terms more heavily (2x)
            for (int i = 18; i < positiveWords.length; i++) { // Starting index of traffic-specific terms
                if (text.contains(positiveWords[i])) positiveTrafficCount += 2;
            }
            
            for (int i = 18; i < negativeWords.length; i++) { // Starting index of traffic-specific terms
                if (text.contains(negativeWords[i])) negativeTrafficCount += 2;
            }
            
            // Add regular sentiment but with less weight
            positiveTrafficCount += positiveCount;
            negativeTrafficCount += negativeCount;
            
            // Determine traffic-specific sentiment
            String trafficSentiment;
            if (positiveTrafficCount > negativeTrafficCount) {
                trafficSentiment = "positive";
            } else if (negativeTrafficCount > positiveTrafficCount) {
                trafficSentiment = "negative";
            } else {
                trafficSentiment = "neutral";
            }
            
            // Output traffic-specific sentiment
            word.set("traffic_sentiment:" + trafficSentiment);
            context.write(word, one);
            
            // Output sentiment intensity (ratio of sentiment words to total words)
            int totalSentimentWords = positiveTrafficCount + negativeTrafficCount;
            int totalWords = text.split("\\s+").length;
            if (totalWords > 0) {
                double intensity = (double) totalSentimentWords / totalWords;
                // Categorize intensity into levels
                String intensityLevel;
                if (intensity > 0.3) {
                    intensityLevel = "high";
                } else if (intensity > 0.15) {
                    intensityLevel = "medium";
                } else {
                    intensityLevel = "low";
                }
                word.set("traffic_sentiment_intensity:" + intensityLevel);
                context.write(word, one);
            }
        }
        
        // Standard sentiment output
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

    /**
     * Process data with timestamp to analyze traffic patterns by time
     */
    private void processTimeframe(JSONObject json, Context context) throws IOException, InterruptedException {
        // Extract timestamp if available
        if (json.has("created_utc")) {
            double utcTimestamp = json.getDouble("created_utc");
            // Convert to java.util.Date
            java.util.Date date = new java.util.Date((long)(utcTimestamp * 1000));
            
            // Extract time components
            java.util.Calendar cal = java.util.Calendar.getInstance();
            cal.setTime(date);
            
            int hourOfDay = cal.get(java.util.Calendar.HOUR_OF_DAY);
            int dayOfWeek = cal.get(java.util.Calendar.DAY_OF_WEEK);
            int month = cal.get(java.util.Calendar.MONTH);
            
            // Classify and output time-based patterns
            
            // Hour of day categories
            String hourCategory;
            if (hourOfDay >= 6 && hourOfDay < 10) {
                hourCategory = "morning_commute";
            } else if (hourOfDay >= 10 && hourOfDay < 16) {
                hourCategory = "midday";
            } else if (hourOfDay >= 16 && hourOfDay < 20) {
                hourCategory = "evening_commute";
            } else {
                hourCategory = "night";
            }
            
            word.set("time_of_day:" + hourCategory);
            context.write(word, one);
            
            // Specific hour tracking
            word.set("hour:" + hourOfDay);
            context.write(word, one);
            
            // Day of week
            String[] dayNames = {"sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"};
            String dayName = dayNames[dayOfWeek - 1]; // Calendar.SUNDAY is 1, not 0
            
            word.set("day_of_week:" + dayName);
            context.write(word, one);
            
            // Weekday vs Weekend
            boolean isWeekend = (dayOfWeek == java.util.Calendar.SATURDAY || dayOfWeek == java.util.Calendar.SUNDAY);
            word.set("day_type:" + (isWeekend ? "weekend" : "weekday"));
            context.write(word, one);
            
            // Month
            String[] monthNames = {"january", "february", "march", "april", "may", "june", 
                                   "july", "august", "september", "october", "november", "december"};
            word.set("month:" + monthNames[month]);
            context.write(word, one);
            
            // Now process the content for time-related keywords
            String text = json.optString("title", "") + " " + json.optString("text", "");
            text = text.toLowerCase();
            
            // Check for timeframe keywords
            for (String timeframe : timeframeKeywords) {
                if (text.contains(timeframe)) {
                    word.set("timeframe_keyword:" + timeframe);
                    context.write(word, one);
                }
            }
            
            // Check for specific time patterns in text (like "8am", "5:30pm")
            Pattern timePattern = Pattern.compile("\\b([0-9]{1,2})([:][0-9]{2})?\\s*(am|pm)\\b", Pattern.CASE_INSENSITIVE);
            Matcher matcher = timePattern.matcher(text);
            
            while (matcher.find()) {
                String matchedTime = matcher.group();
                word.set("mentioned_time:" + matchedTime);
                context.write(word, one);
            }
        }
    }

    private void processComment(JSONObject comment, Context context) throws IOException, InterruptedException {
        if (!comment.has("text"))
            return;

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
            case "timeframe":
                processTimeframe(comment, context);
                break;
        }
    }
}