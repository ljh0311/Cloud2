# AWS Web Console Deployment Instructions

This document provides step-by-step instructions for deploying the Big Data Analytics project using the AWS Management Console (web interface) instead of command-line tools.

## 1. Create S3 Buckets

1. **Sign in** to the [AWS Management Console](https://console.aws.amazon.com/)
2. Navigate to the **S3 service**
3. Create three buckets:
   - **Raw Data Bucket**: `your-project-raw-data`
   - **Processed Data Bucket**: `your-project-processed-data`
   - **EMR Logs Bucket**: `your-project-emr-logs`

   For each bucket:
   - Click **Create bucket**
   - Enter the bucket name
   - Select your preferred region
   - Keep default settings or customize as needed
   - Click **Create bucket**

4. **Configure Lifecycle Rules** for the processed data bucket:
   - Select the `your-project-processed-data` bucket
   - Go to the **Management** tab
   - Click **Create lifecycle rule**
   - Name: `ProcessedDataLifecycle`
   - Apply to: Choose "Limit the scope using prefix" and enter `processed/`
   - Select **Transition to Standard-IA after 30 days**
   - Select **Transition to Glacier after 90 days**
   - Select **Expire objects after 365 days**
   - Click **Create rule**
   
   Create another rule:
   - Name: `LogsLifecycle`
   - Apply to: Choose "Limit the scope using prefix" and enter `logs/`
   - Select **Expire objects after 90 days**
   - Click **Create rule**

5. **Upload Data** to the raw data bucket:
   - Select the `your-project-raw-data` bucket
   - Click **Upload**
   - Drag and drop files from your local `data/` directory or click **Add files**
   - Click **Upload**

## 2. Create RDS Database

1. Navigate to the **RDS service**
2. Click **Create database**
3. Choose **Standard create**
4. Select **PostgreSQL** as the engine type
5. Choose **Free tier** or appropriate tier for your needs
6. Settings:
   - **DB instance identifier**: `your-project-db`
   - **Master username**: `admin` (or your preferred username)
   - **Master password**: Create a secure password
7. Instance configuration:
   - **DB instance class**: `db.t3.micro`
   - **Storage**: `20` GB
8. Connectivity:
   - **VPC**: Default VPC (or create a new one)
   - **Public access**: No
   - **VPC security group**: Create new
   - **New security group name**: `rds-security-group`
9. Additional configuration:
   - **Initial database name**: `projectdb`
   - **Backup retention period**: `7` days
10. Click **Create database**
11. **Note the endpoint URL** from the database details page for later use

## 3. Launch EC2 Instance

1. Navigate to the **EC2 service**
2. Click **Launch instance**
3. Name: `BigDataAnalytics-WebApp`
4. Choose an **Amazon Machine Image (AMI)**:
   - Select **Amazon Linux 2 AMI**
5. Choose an **Instance Type**:
   - Select `t2.medium`
6. Key pair:
   - Create a new key pair or select an existing one
   - If creating new: Name it `your-project-key` and download the `.pem` file
7. Network settings:
   - **VPC**: Default VPC (or the same VPC as your RDS)
   - **Auto-assign public IP**: Enable
   - **Security group**: Create a new security group
   - **Security group name**: `web-server-sg`
   - Add inbound rules:
     - HTTP (port 80) from Anywhere
     - HTTPS (port 443) from Anywhere
     - SSH (port 22) from Your IP
     - Custom TCP (port 5000) from Anywhere
8. Configure storage:
   - **Size**: `30` GB
9. Advanced details:
   - **User data**: Copy and paste the following script (update with your specific values):

```bash
#!/bin/bash -xe
yum update -y
yum install -y python3 python3-pip git
amazon-linux-extras install -y postgresql12

# Install AWS CLI
pip3 install awscli

# Clone repository
git clone https://github.com/your-username/big-data-analytics.git /home/ec2-user/big-data-analytics
chown -R ec2-user:ec2-user /home/ec2-user/big-data-analytics

# Install dependencies
cd /home/ec2-user/big-data-analytics
pip3 install -r requirements.txt

# Configure environment variables
cat > /home/ec2-user/big-data-analytics/.env << EOL
S3_RAW_BUCKET=your-project-raw-data
S3_PROCESSED_BUCKET=your-project-processed-data
RDS_HOST=your-rds-endpoint.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=projectdb
RDS_USERNAME=admin
RDS_PASSWORD=your-secure-password
FLASK_APP=src.web.app
FLASK_ENV=production
EOL

# Setup web application to start on boot
cat > /etc/systemd/system/bigdata-webapp.service << EOL
[Unit]
Description=Big Data Analytics Web Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/big-data-analytics
ExecStart=/usr/bin/python3 -m src.web.run
Restart=always

[Install]
WantedBy=multi-user.target
EOL

systemctl enable bigdata-webapp.service
systemctl start bigdata-webapp.service

# Install and configure Nginx
amazon-linux-extras install -y nginx1

cat > /etc/nginx/conf.d/bigdata.conf << EOL
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOL

systemctl enable nginx
systemctl start nginx
```

10. Click **Launch instance**
11. **Note the public IP address** or DNS name of your instance

## 4. Configure IAM Roles

1. Navigate to the **IAM service**
2. Create a role for EC2 to access S3 and EMR:
   - Click **Roles** > **Create role**
   - Select **AWS service** as the trusted entity
   - Choose **EC2** as the service
   - Click **Next: Permissions**
   - Search for and select:
     - `AmazonS3FullAccess`
     - `AmazonEMRFullAccessPolicy_v2`
   - Click **Next: Tags** (add optional tags)
   - Click **Next: Review**
   - Role name: `EC2-S3-EMR-Role`
   - Click **Create role**

3. Create EMR service roles:
   - Click **Roles** > **Create role**
   - Select **AWS service** as the trusted entity
   - Choose **EMR** as the service
   - Select **EMR** use case
   - Click **Next: Permissions**
   - The `AmazonEMRServicePolicy` should be automatically selected
   - Click **Next: Tags** (add optional tags)
   - Click **Next: Review**
   - Role name: `EMR-Service-Role`
   - Click **Create role**

   Repeat for the EC2 instance profile:
   - Click **Roles** > **Create role**
   - Select **AWS service** as the trusted entity
   - Choose **EC2** as the service
   - Click **Next: Permissions**
   - Search for and select `AmazonElasticMapReduceforEC2Role`
   - Click **Next: Tags** (add optional tags)
   - Click **Next: Review**
   - Role name: `EMR-EC2-Role`
   - Click **Create role**

## 5. Create EMR Cluster

1. Navigate to the **EMR service**
2. Click **Create cluster**
3. Choose **Advanced options**
4. Software configuration:
   - Release: `emr-6.10.0`
   - Applications: Select **Hadoop**, **Spark**, and **Hive**
5. Hardware configuration:
   - Instance type: `m5.xlarge` (or choose based on your needs)
   - Number of instances: `3` (1 master, 2 core)
   - Network: Default VPC (or the same VPC as your EC2)
   - EC2 subnet: Choose a public subnet
6. General cluster settings:
   - Name: `BigDataAnalytics-EMR`
   - Logging: Enable, browse to your `your-project-emr-logs` S3 bucket
   - Debugging: Enable
7. Security and access:
   - EC2 key pair: Select the same key pair used for your EC2 instance
   - Permissions:
     - Service role: `EMR-Service-Role`
     - Instance profile: `EMR-EC2-Role`
   - EC2 security groups: Use default
8. Click **Create cluster**
9. **Note the cluster ID** for later use

## 6. Configure Security Group Rules

1. Navigate to the **EC2 service** > **Security Groups**
2. Find the security group for your RDS instance:
   - Click on the security group
   - Click **Edit inbound rules**
   - Add a rule:
     - Type: **PostgreSQL**
     - Source: Select the security group of your EC2 instance
     - Description: "Allow EC2 to connect to RDS"
   - Click **Save rules**

## 7. Upload Data to S3

1. Navigate to the **S3 service**
2. Select your `your-project-raw-data` bucket
3. Create folders for different data types:
   - Click **Create folder**
   - Create folders for: `twitter`, `reddit`, `amazon`, `yelp`
4. Upload data files to each folder:
   - Navigate into each folder
   - Click **Upload**
   - Select files from your local machine
   - Click **Upload**

## 8. Run Hadoop and Spark Jobs on EMR

### Running a Hadoop Job

1. Navigate to the **EMR service**
2. Select your cluster
3. Click **Steps** > **Add step**
4. Configure the step:
   - Step type: **Custom JAR**
   - Name: `Hadoop-Data-Processing`
   - JAR location: `s3://your-project-raw-data/hadoop-jobs/your-job.jar`
   - Arguments: Add any required arguments
   - Action on failure: **Continue**
5. Click **Add**

### Running a Spark Job

1. Navigate to the **EMR service**
2. Select your cluster
3. Click **Steps** > **Add step**
4. Configure the step:
   - Step type: **Spark application**
   - Name: `Spark-Data-Analysis`
   - Deploy mode: **Cluster**
   - Application location: `s3://your-project-raw-data/spark-jobs/your-job.py`
   - Arguments: Add any required arguments
   - Action on failure: **Continue**
5. Click **Add**

## 9. Monitor and Manage Resources

### Monitoring EMR Cluster

1. Navigate to the **EMR service**
2. Select your cluster
3. View the **Summary** tab for cluster status
4. View the **Steps** tab to monitor job progress
5. View the **Monitoring** tab for detailed metrics

### Setting Up CloudWatch Alarms

1. Navigate to the **CloudWatch service**
2. Click **Alarms** > **Create alarm**
3. Click **Select metric**
4. Choose **EC2** > **Per-Instance Metrics**
5. Find your EC2 instance and select **CPUUtilization**
6. Click **Select metric**
7. Configure the alarm:
   - Statistic: **Average**
   - Period: **5 minutes**
   - Threshold type: **Static**
   - Condition: **Greater than**
   - Threshold value: `80`
8. Click **Next**
9. Configure notification:
   - Select **Create new topic**
   - Topic name: `your-project-alerts`
   - Email endpoints: Enter your email
   - Click **Create topic**
10. Click **Next**
11. Name and description:
    - Name: `EC2-High-CPU`
    - Description: "Alert when CPU exceeds 80%"
12. Click **Next**
13. Click **Create alarm**

## 10. Access the Web Application

1. Use the public DNS name or IP address of your EC2 instance
2. Open a web browser and navigate to: `http://your-ec2-public-dns`
3. You should see the Big Data Analytics web interface

## 11. Backup and Disaster Recovery

### Configure RDS Automated Backups

1. Navigate to the **RDS service**
2. Select your database instance
3. Click **Modify**
4. Under **Backup**:
   - Set **Backup retention period** to `7` days
   - Set **Backup window** as preferred
5. Click **Continue**
6. Choose **Apply immediately**
7. Click **Modify DB Instance**

### Configure S3 Cross-Region Replication

1. Navigate to the **S3 service**
2. Create a backup bucket in a different region:
   - Click **Create bucket**
   - Name: `your-project-raw-data-backup`
   - Region: Choose a different region than your primary bucket
   - Click **Create bucket**

3. Set up replication:
   - Select your primary `your-project-raw-data` bucket
   - Go to the **Management** tab
   - Click **Replication** > **Create replication rule**
   - Rule name: `CrossRegionBackup`
   - Status: **Enabled**
   - Source bucket: All objects
   - Destination: Choose your backup bucket
   - IAM role: Create new role
   - Click **Save**

## 12. Cost Optimization

### Use Spot Instances for EMR Task Nodes

1. When creating a new EMR cluster:
   - In the hardware configuration step
   - Click **Add task instance group**
   - Instance type: Choose appropriate type
   - Purchasing option: Select **Spot**
   - Set a maximum price
   - Click **Add**

### Schedule EMR Cluster Auto-Termination

1. When creating a new EMR cluster:
   - In the general cluster settings
   - Under **Cluster auto-termination**
   - Enable **Auto-termination**
   - Set idle time to appropriate value (e.g., 1 hour)
   - Click **Create cluster**

## Troubleshooting

### EC2 Connection Issues
- Check that your security group allows inbound traffic on port 22 (SSH)
- Verify you're using the correct key pair
- Ensure your instance is in the "running" state

### S3 Access Issues
- Verify IAM roles and policies are correctly configured
- Check bucket permissions and CORS configuration
- Ensure your EC2 instance has the correct IAM role attached

### EMR Job Failures
- Check EMR logs in the S3 logs bucket
- Verify input/output paths are correct
- Ensure sufficient resources for the job

### RDS Connection Issues
- Verify security group allows PostgreSQL (port 5432) from your EC2 security group
- Check database credentials in the .env file
- Ensure the RDS instance is in the "available" state 