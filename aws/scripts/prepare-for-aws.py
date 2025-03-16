#!/usr/bin/env python3
"""
Master script to prepare the Big Data Analytics project for AWS deployment.
This script:
1. Organizes data files
2. Prepares Hadoop and Spark jobs
3. Creates a deployment package
4. Generates instructions for AWS console deployment
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def create_deployment_directory(deploy_dir):
    """Create and clean deployment directory"""
    if os.path.exists(deploy_dir):
        print(f"Cleaning existing deployment directory: {deploy_dir}")
        shutil.rmtree(deploy_dir)
    
    os.makedirs(deploy_dir)
    print(f"Created deployment directory: {deploy_dir}")

def run_data_organization(data_dir, deploy_dir, bucket_name):
    """Run the data organization script"""
    script_path = os.path.join("aws", "scripts", "organize-data.py")
    
    if os.path.exists(script_path):
        print("\n=== Organizing Data Files ===")
        cmd = [
            sys.executable, script_path,
            "--data", data_dir,
            "--deploy", deploy_dir,
            "--bucket", bucket_name
        ]
        subprocess.run(cmd)
    else:
        print(f"Warning: Data organization script not found at {script_path}")

def run_job_preparation(src_dir, deploy_dir, bucket_name):
    """Run the job preparation script"""
    script_path = os.path.join("aws", "scripts", "prepare-jobs.py")
    
    if os.path.exists(script_path):
        print("\n=== Preparing Hadoop and Spark Jobs ===")
        cmd = [
            sys.executable, script_path,
            "--src", src_dir,
            "--deploy", deploy_dir,
            "--bucket", bucket_name
        ]
        subprocess.run(cmd)
    else:
        print(f"Warning: Job preparation script not found at {script_path}")

def copy_aws_files(deploy_dir):
    """Copy AWS configuration files to deployment directory"""
    print("\n=== Copying AWS Configuration Files ===")
    
    # Create AWS directory in deployment
    aws_deploy_dir = os.path.join(deploy_dir, "aws")
    os.makedirs(os.path.join(aws_deploy_dir, "config"), exist_ok=True)
    os.makedirs(os.path.join(aws_deploy_dir, "cloudformation"), exist_ok=True)
    
    # Copy config files
    config_src = os.path.join("aws", "config")
    config_dst = os.path.join(aws_deploy_dir, "config")
    
    if os.path.exists(config_src):
        for file in os.listdir(config_src):
            src_file = os.path.join(config_src, file)
            dst_file = os.path.join(config_dst, file)
            if os.path.isfile(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"Copied {src_file} to {dst_file}")
    
    # Copy CloudFormation template
    cf_src = os.path.join("aws", "cloudformation", "big-data-infrastructure.yaml")
    cf_dst = os.path.join(aws_deploy_dir, "cloudformation", "big-data-infrastructure.yaml")
    
    if os.path.exists(cf_src):
        shutil.copy2(cf_src, cf_dst)
        print(f"Copied {cf_src} to {cf_dst}")
    
    # Copy deployment instructions
    instructions_src = os.path.join("aws", "scripts", "deploy-instructions.md")
    instructions_dst = os.path.join(deploy_dir, "AWS_DEPLOYMENT_INSTRUCTIONS.md")
    
    if os.path.exists(instructions_src):
        shutil.copy2(instructions_src, instructions_dst)
        print(f"Copied {instructions_src} to {instructions_dst}")
    
    # Copy deployment checklist
    checklist_src = os.path.join("aws", "scripts", "deployment-checklist.md")
    checklist_dst = os.path.join(deploy_dir, "AWS_DEPLOYMENT_CHECKLIST.md")
    
    if os.path.exists(checklist_src):
        shutil.copy2(checklist_src, checklist_dst)
        print(f"Copied {checklist_src} to {checklist_dst}")

def create_master_readme(deploy_dir, bucket_name):
    """Create a master README file for the deployment package"""
    readme_path = os.path.join(deploy_dir, "README.md")
    
    with open(readme_path, "w") as f:
        f.write("# Big Data Analytics - AWS Deployment Package\n\n")
        f.write(f"Prepared on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This package contains all the necessary files for deploying the Big Data Analytics project on AWS.\n\n")
        
        f.write("## Package Contents\n\n")
        f.write("```\n")
        f.write("deploy/\n")
        f.write("├── data/               # Organized data files\n")
        f.write("├── hadoop-jobs/        # Hadoop MapReduce jobs\n")
        f.write("├── spark-jobs/         # Spark analysis jobs\n")
        f.write("├── config/             # Configuration files\n")
        f.write("├── aws/                # AWS deployment files\n")
        f.write("│   ├── config/         # AWS configuration files\n")
        f.write("│   └── cloudformation/ # CloudFormation templates\n")
        f.write("├── upload_data_to_s3.sh       # Script to upload data to S3\n")
        f.write("├── upload_to_s3.sh            # Script to upload jobs to S3\n")
        f.write("├── AWS_DEPLOYMENT_INSTRUCTIONS.md  # Detailed deployment instructions\n")
        f.write("└── AWS_DEPLOYMENT_CHECKLIST.md     # Deployment checklist\n")
        f.write("```\n\n")
        
        f.write("## Deployment Steps\n\n")
        f.write("1. Review the `AWS_DEPLOYMENT_INSTRUCTIONS.md` file for detailed step-by-step instructions\n")
        f.write("2. Use the `AWS_DEPLOYMENT_CHECKLIST.md` to track your progress\n")
        f.write("3. Upload data and jobs to your S3 bucket using the provided scripts or the AWS Management Console\n")
        f.write("4. Follow the instructions to set up EC2, RDS, and EMR resources\n\n")
        
        f.write("## S3 Bucket Configuration\n\n")
        f.write(f"The deployment is configured to use the following S3 bucket: `{bucket_name}`\n\n")
        f.write("If you want to use a different bucket name, you'll need to update the following files:\n\n")
        f.write("1. `upload_data_to_s3.sh`\n")
        f.write("2. `upload_to_s3.sh`\n")
        f.write("3. AWS CloudFormation template (if using)\n\n")
        
        f.write("## Web Console Deployment\n\n")
        f.write("This package is designed for deployment using the AWS Management Console (web interface).\n")
        f.write("No SSH access to the servers is required for the deployment process.\n\n")
        
        f.write("## Support\n\n")
        f.write("For questions or issues, please contact the project team.\n")
    
    print(f"Created master README file: {readme_path}")

def create_zip_archive(deploy_dir):
    """Create a ZIP archive of the deployment directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"big-data-analytics-aws-deploy_{timestamp}.zip"
    
    shutil.make_archive(
        os.path.splitext(zip_filename)[0],  # Base name
        'zip',                              # Format
        os.path.dirname(deploy_dir),        # Root directory
        os.path.basename(deploy_dir)        # Directory to zip
    )
    
    print(f"\nCreated deployment archive: {zip_filename}")
    print(f"You can now upload this archive to your local machine and extract it for AWS deployment.")

def main():
    parser = argparse.ArgumentParser(description="Prepare Big Data Analytics project for AWS deployment")
    parser.add_argument("--data", default="data", help="Source data directory")
    parser.add_argument("--src", default="src", help="Source code directory")
    parser.add_argument("--deploy", default="deploy", help="Deployment directory")
    parser.add_argument("--bucket", default="your-project-raw-data", help="S3 bucket name for upload")
    parser.add_argument("--zip", action="store_true", help="Create a ZIP archive of the deployment directory")
    
    args = parser.parse_args()
    
    print("=== Preparing Big Data Analytics Project for AWS Deployment ===\n")
    
    # Create deployment directory
    create_deployment_directory(args.deploy)
    
    # Run data organization
    run_data_organization(args.data, args.deploy, args.bucket)
    
    # Run job preparation
    run_job_preparation(args.src, args.deploy, args.bucket)
    
    # Copy AWS files
    copy_aws_files(args.deploy)
    
    # Create master README
    create_master_readme(args.deploy, args.bucket)
    
    # Create ZIP archive if requested
    if args.zip:
        create_zip_archive(args.deploy)
    
    print("\n=== Deployment Preparation Complete ===")
    print(f"Deployment package is ready in: {os.path.abspath(args.deploy)}")
    print("Follow the instructions in AWS_DEPLOYMENT_INSTRUCTIONS.md to deploy to AWS.")

if __name__ == "__main__":
    main() 