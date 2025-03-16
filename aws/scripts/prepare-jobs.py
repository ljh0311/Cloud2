#!/usr/bin/env python3
"""
Prepare Hadoop and Spark jobs for AWS deployment.
This script:
1. Creates necessary directories in S3 buckets
2. Packages Hadoop and Spark jobs
3. Prepares them for upload to S3
"""

import os
import shutil
import argparse
import subprocess
from pathlib import Path

def create_directories():
    """Create local directories for packaging jobs"""
    dirs = [
        "deploy/hadoop-jobs",
        "deploy/spark-jobs",
        "deploy/config"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("Created deployment directories")

def package_hadoop_jobs(src_dir, deploy_dir):
    """Package Hadoop MapReduce jobs"""
    # Copy Hadoop source files
    hadoop_src = os.path.join(src_dir, "hadoop")
    hadoop_deploy = os.path.join(deploy_dir, "hadoop-jobs")
    
    if os.path.exists(hadoop_src):
        for file in os.listdir(hadoop_src):
            if file.endswith(".py"):
                src_file = os.path.join(hadoop_src, file)
                dst_file = os.path.join(hadoop_deploy, file)
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")
    else:
        print(f"Warning: Hadoop source directory {hadoop_src} not found")

def package_spark_jobs(src_dir, deploy_dir):
    """Package Spark jobs"""
    # Copy Spark source files
    spark_src = os.path.join(src_dir, "spark")
    spark_deploy = os.path.join(deploy_dir, "spark-jobs")
    
    if os.path.exists(spark_src):
        for file in os.listdir(spark_src):
            if file.endswith(".py"):
                src_file = os.path.join(spark_src, file)
                dst_file = os.path.join(spark_deploy, file)
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")
    else:
        print(f"Warning: Spark source directory {spark_src} not found")

def copy_config_files(config_dir, deploy_dir):
    """Copy configuration files"""
    deploy_config = os.path.join(deploy_dir, "config")
    
    if os.path.exists(config_dir):
        for file in os.listdir(config_dir):
            if file.endswith(".json") or file.endswith(".yaml") or file.endswith(".properties"):
                src_file = os.path.join(config_dir, file)
                dst_file = os.path.join(deploy_config, file)
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")
    else:
        print(f"Warning: Config directory {config_dir} not found")

def create_s3_upload_script(bucket_name, deploy_dir):
    """Create a script to upload files to S3"""
    script_path = os.path.join(deploy_dir, "upload_to_s3.sh")
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"# Upload Hadoop jobs to S3\n")
        f.write(f"aws s3 cp {deploy_dir}/hadoop-jobs/ s3://{bucket_name}/hadoop-jobs/ --recursive\n\n")
        f.write(f"# Upload Spark jobs to S3\n")
        f.write(f"aws s3 cp {deploy_dir}/spark-jobs/ s3://{bucket_name}/spark-jobs/ --recursive\n\n")
        f.write(f"# Upload configuration files to S3\n")
        f.write(f"aws s3 cp {deploy_dir}/config/ s3://{bucket_name}/config/ --recursive\n")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    print(f"Created S3 upload script: {script_path}")

def main():
    parser = argparse.ArgumentParser(description="Prepare Hadoop and Spark jobs for AWS deployment")
    parser.add_argument("--src", default="src", help="Source directory containing Hadoop and Spark code")
    parser.add_argument("--config", default="config", help="Configuration directory")
    parser.add_argument("--deploy", default="deploy", help="Deployment directory")
    parser.add_argument("--bucket", default="your-project-raw-data", help="S3 bucket name for job upload")
    
    args = parser.parse_args()
    
    # Create deployment directories
    create_directories()
    
    # Package Hadoop and Spark jobs
    package_hadoop_jobs(args.src, args.deploy)
    package_spark_jobs(args.src, args.deploy)
    
    # Copy configuration files
    copy_config_files(args.config, args.deploy)
    
    # Create S3 upload script
    create_s3_upload_script(args.bucket, args.deploy)
    
    print("\nDeployment preparation complete!")
    print(f"Run the upload script to push files to S3: {os.path.join(args.deploy, 'upload_to_s3.sh')}")

if __name__ == "__main__":
    main() 