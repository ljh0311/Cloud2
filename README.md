# Big Data Analytics Project - AWS Deployment Guide

This guide provides detailed instructions for deploying the Big Data Analytics project on AWS infrastructure, including EC2 instances, RDS/S3 for data storage, and EMR clusters for Hadoop/Spark processing.

## AWS Infrastructure Overview

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  S3 Buckets      |     |  EC2 Instance    |     |  EMR Cluster     |
|  - Raw Data      |<--->|  - Web App       |<--->|  - Hadoop        |
|  - Processed Data|     |  - Flask API     |     |  - Spark         |
|  - EMR Logs      |     |  - Nginx         |     |  - Hive          |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
         ^                        ^                        ^
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  RDS Database    |     |  IAM Roles       |     |  CloudWatch      |
|  - PostgreSQL    |<--->|  - EC2 Role      |     |  - Monitoring    |
|  - Metadata      |     |  - EMR Roles     |     |  - Alarms        |
|  - Results       |     |  - S3 Access     |     |  - Logs          |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
```

The deployment uses the following AWS services:
- **EC2**: For running the web application and coordination services
- **S3**: For storing raw and processed data
- **RDS**: For storing application metadata and results
- **EMR**: For running Hadoop and Spark jobs
- **IAM**: For managing access permissions between services

## Prerequisites

1. AWS Account with appropriate permissions
2. Access to AWS Management Console
3. Project files prepared locally
4. Basic understanding of AWS services

## Project Structure for AWS Deployment

```
├── aws/                # AWS deployment scripts and templates
│   ├── cloudformation/ # CloudFormation templates
│   ├── scripts/        # Deployment and setup scripts
│   └── config/         # AWS configuration files
├── src/                # Application source code
├── data/               # Sample data and data schemas
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Deployment Instructions

For detailed step-by-step instructions using the AWS Management Console, please refer to:

[AWS Web Console Deployment Instructions](aws/scripts/deploy-instructions.md)

This document provides comprehensive guidance for setting up all required AWS services through the web interface.

## Deployment Checklist

To help track your progress during deployment, use the provided checklist:

[AWS Deployment Checklist](aws/scripts/deployment-checklist.md)

## CloudFormation Template (Optional)

For automated deployment, a CloudFormation template is provided:

[Big Data Infrastructure Template](aws/cloudformation/big-data-infrastructure.yaml)

To use this template:
1. Sign in to the AWS Management Console
2. Navigate to CloudFormation
3. Click "Create stack" > "With new resources"
4. Upload the template file
5. Follow the prompts to configure and create the stack

## Preparing Jobs for Deployment

To prepare your Hadoop and Spark jobs for deployment to AWS:

1. Run the preparation script:
   ```bash
   python aws/scripts/prepare-jobs.py --bucket your-project-raw-data
   ```

2. This will:
   - Create a deployment directory structure
   - Copy Hadoop and Spark jobs to the appropriate locations
   - Create an upload script for pushing files to S3

3. Upload the prepared files to S3 using the AWS Management Console:
   - Navigate to S3 in the AWS Management Console
   - Select your raw data bucket
   - Create folders for "hadoop-jobs", "spark-jobs", and "config"
   - Upload the files from the local "deploy" directory to the corresponding S3 folders

## Data Pipeline on AWS

1. Data Ingestion:
   - Upload data to S3 raw data bucket
   - Trigger Lambda function for preprocessing (optional)

2. Data Processing:
   - Run EMR jobs for data transformation
   - Store processed data in S3 processed data bucket

3. Data Analysis:
   - Run Spark jobs on EMR for advanced analytics
   - Store results in RDS database

4. Data Visualization:
   - Access web application on EC2 to view results
   - Generate reports and dashboards

## Monitoring and Management

For monitoring your AWS resources:

1. Use CloudWatch for metrics and alarms
2. Set up SNS notifications for important events
3. Review EMR logs stored in S3
4. Monitor RDS performance metrics

## Cost Optimization

To optimize costs in your AWS deployment:

1. Use Spot Instances for EMR task nodes
2. Configure S3 lifecycle policies for data tiering
3. Schedule EMR cluster auto-termination
4. Right-size RDS instances based on workload

## Security Best Practices

1. Use IAM roles instead of access keys when possible
2. Enable encryption for S3 buckets and RDS instances
3. Use security groups to restrict access to resources
4. Regularly rotate credentials and audit access logs
5. Use VPC for network isolation

## Troubleshooting

### Common Issues

1. **EC2 Connection Issues**
   - Verify security group allows HTTP (port 80)
   - Ensure your instance is in the "running" state

2. **S3 Access Issues**
   - Verify IAM roles and policies are correctly configured
   - Check bucket permissions and CORS configuration

3. **EMR Job Failures**
   - Check EMR logs in S3 bucket
   - Verify input/output paths are correct
   - Ensure sufficient resources for the job

4. **RDS Connection Issues**
   - Verify security group allows PostgreSQL (port 5432) from your EC2 security group
   - Check database credentials in the .env file
   - Ensure the RDS instance is in the "available" state

## License

This project is licensed under the MIT License - see the LICENSE file for details.
