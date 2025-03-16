# AWS Deployment Checklist

Use this checklist to track your progress when setting up the Big Data Analytics project on AWS.

## Initial Setup

- [ ] AWS Account setup and access
- [ ] AWS Management Console access
- [ ] AWS region selection
- [ ] Project files prepared locally

## S3 Buckets

- [ ] Raw data bucket created
- [ ] Processed data bucket created
- [ ] EMR logs bucket created
- [ ] Lifecycle policies configured
- [ ] Data uploaded to raw data bucket

## RDS Database

- [ ] PostgreSQL instance created
- [ ] Security group configured
- [ ] Database initialized
- [ ] Connection tested
- [ ] Backup retention configured

## EC2 Instance

- [ ] Instance launched with correct AMI
- [ ] Security group configured
- [ ] User data script added
- [ ] Instance started successfully
- [ ] Web application accessible

## IAM Roles

- [ ] EC2 role created with S3 and EMR access
- [ ] EMR service role created
- [ ] EMR EC2 instance profile created
- [ ] Roles attached to respective services

## EMR Cluster

- [ ] Cluster created with correct applications
- [ ] Correct instance types selected
- [ ] Security groups configured
- [ ] Cluster started successfully
- [ ] Connection to S3 verified

## Data Processing

- [ ] Hadoop jobs uploaded to S3
- [ ] Spark jobs uploaded to S3
- [ ] Hadoop job executed successfully
- [ ] Spark job executed successfully
- [ ] Results stored in processed data bucket

## Monitoring and Alerts

- [ ] CloudWatch alarms configured
- [ ] SNS notifications set up
- [ ] Log monitoring enabled
- [ ] Dashboard created

## Security

- [ ] All security groups properly configured
- [ ] IAM permissions follow least privilege
- [ ] S3 bucket policies reviewed
- [ ] RDS encryption enabled
- [ ] EC2 key pair secured

## Cost Optimization

- [ ] Spot instances configured for EMR task nodes
- [ ] Auto-termination enabled for EMR cluster
- [ ] S3 lifecycle policies verified
- [ ] RDS instance sized appropriately

## Backup and Disaster Recovery

- [ ] RDS automated backups enabled
- [ ] S3 cross-region replication configured
- [ ] Recovery procedures documented
- [ ] Backup testing scheduled

## Final Verification

- [ ] Web application fully functional
- [ ] Data processing pipeline tested end-to-end
- [ ] All services communicating properly
- [ ] Documentation updated with actual resource names
- [ ] Costs estimated and approved 