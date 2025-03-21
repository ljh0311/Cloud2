import os
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import logging

logger = logging.getLogger(__name__)

class SparkService:
    def __init__(self):
        """Initialize the Spark service"""
        self.spark = None
        self.conf = SparkConf() \
            .setAppName("RedditAnalysis") \
            .setMaster("local[*]") \
            .set("spark.driver.memory", "4g") \
            .set("spark.executor.memory", "4g") \
            .set("spark.sql.execution.arrow.pyspark.enabled", "true")

    def get_session(self):
        """Get or create a Spark session"""
        if not self.spark:
            try:
                self.spark = SparkSession.builder \
                    .config(conf=self.conf) \
                    .getOrCreate()
                
                # Register UDFs and UDTFs
                self.register_functions()
                
                logger.info("Spark session created successfully")
            except Exception as e:
                logger.error(f"Error creating Spark session: {str(e)}")
                raise
        
        return self.spark

    def register_functions(self):
        """Register custom UDFs and UDTFs"""
        from textblob import TextBlob
        
        def analyze_sentiment(text):
            """Analyze sentiment of text using TextBlob"""
            try:
                blob = TextBlob(str(text))
                return {'polarity': blob.sentiment.polarity, 'subjectivity': blob.sentiment.subjectivity}
            except:
                return {'polarity': 0.0, 'subjectivity': 0.0}
        
        # Register the sentiment analysis function
        self.spark.udf.register("textblob", analyze_sentiment)

    def submit_mapreduce_job(self, input_path, mapper, reducer, output_path):
        """Submit a MapReduce job using Hadoop Streaming"""
        try:
            # Ensure mapper and reducer scripts exist
            mapper_path = os.path.join('src', 'mapreduce', mapper)
            reducer_path = os.path.join('src', 'mapreduce', reducer)
            
            if not os.path.exists(mapper_path) or not os.path.exists(reducer_path):
                raise FileNotFoundError("Mapper or reducer script not found")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Build Hadoop streaming command
            hadoop_streaming_jar = os.getenv('HADOOP_STREAMING_JAR', '/usr/lib/hadoop/hadoop-streaming.jar')
            
            command = f"""
            hadoop jar {hadoop_streaming_jar} \
                -input {input_path} \
                -output {output_path} \
                -mapper {mapper_path} \
                -reducer {reducer_path} \
                -file {mapper_path} \
                -file {reducer_path}
            """
            
            # Execute the command
            import subprocess
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"MapReduce job failed: {stderr.decode()}")
            
            logger.info(f"MapReduce job completed successfully: {stdout.decode()}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting MapReduce job: {str(e)}")
            raise

    def stop(self):
        """Stop the Spark session"""
        if self.spark:
            try:
                self.spark.stop()
                self.spark = None
                logger.info("Spark session stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Spark session: {str(e)}")
                raise 