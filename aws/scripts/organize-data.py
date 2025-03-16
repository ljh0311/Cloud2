#!/usr/bin/env python3
"""
Organize data files for AWS S3 upload.
This script:
1. Creates a structured directory for data files
2. Organizes files by data source (twitter, reddit, amazon, yelp)
3. Prepares them for easy upload to S3
"""

import os
import shutil
import argparse
from pathlib import Path

def create_directories():
    """Create structured directories for data organization"""
    dirs = [
        "deploy/data/twitter",
        "deploy/data/reddit",
        "deploy/data/amazon",
        "deploy/data/yelp"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("Created data directories")

def organize_data_files(data_dir, deploy_dir):
    """Organize data files by source"""
    # Check if source data directories exist
    sources = ["twitter", "reddit", "amazon", "yelp"]
    
    for source in sources:
        source_dir = os.path.join(data_dir, source)
        target_dir = os.path.join(deploy_dir, "data", source)
        
        if os.path.exists(source_dir):
            # Copy all files from source directory
            for file in os.listdir(source_dir):
                src_file = os.path.join(source_dir, file)
                dst_file = os.path.join(target_dir, file)
                
                if os.path.isfile(src_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"Copied {src_file} to {dst_file}")
        else:
            print(f"Warning: Source directory {source_dir} not found")

def create_s3_upload_script(bucket_name, deploy_dir):
    """Create a script to upload data files to S3"""
    script_path = os.path.join(deploy_dir, "upload_data_to_s3.sh")
    
    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write(f"# Upload data files to S3\n")
        f.write(f"aws s3 cp {deploy_dir}/data/ s3://{bucket_name}/ --recursive\n")
    
    # Make the script executable
    os.chmod(script_path, 0o755)
    print(f"Created S3 data upload script: {script_path}")

def create_readme(deploy_dir):
    """Create a README file with instructions"""
    readme_path = os.path.join(deploy_dir, "data", "README.md")
    
    with open(readme_path, "w") as f:
        f.write("# Data Files for AWS S3 Upload\n\n")
        f.write("This directory contains organized data files ready for upload to AWS S3.\n\n")
        f.write("## Directory Structure\n\n")
        f.write("```\n")
        f.write("data/\n")
        f.write("├── twitter/    # Twitter data files\n")
        f.write("├── reddit/     # Reddit data files\n")
        f.write("├── amazon/     # Amazon data files\n")
        f.write("└── yelp/       # Yelp data files\n")
        f.write("```\n\n")
        f.write("## Upload Instructions\n\n")
        f.write("### Using AWS Management Console\n\n")
        f.write("1. Sign in to the AWS Management Console\n")
        f.write("2. Navigate to the S3 service\n")
        f.write("3. Select your raw data bucket\n")
        f.write("4. Click 'Upload'\n")
        f.write("5. Drag and drop the contents of this directory or click 'Add files'\n")
        f.write("6. Click 'Upload'\n\n")
        f.write("### Using AWS CLI\n\n")
        f.write("Run the provided upload script:\n\n")
        f.write("```bash\n")
        f.write("./upload_data_to_s3.sh\n")
        f.write("```\n")
    
    print(f"Created README file: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description="Organize data files for AWS S3 upload")
    parser.add_argument("--data", default="data", help="Source data directory")
    parser.add_argument("--deploy", default="deploy", help="Deployment directory")
    parser.add_argument("--bucket", default="your-project-raw-data", help="S3 bucket name for data upload")
    
    args = parser.parse_args()
    
    # Create deployment directories
    create_directories()
    
    # Organize data files
    organize_data_files(args.data, args.deploy)
    
    # Create S3 upload script
    create_s3_upload_script(args.bucket, args.deploy)
    
    # Create README file
    create_readme(args.deploy)
    
    print("\nData organization complete!")
    print(f"Run the upload script to push data to S3: {os.path.join(args.deploy, 'upload_data_to_s3.sh')}")
    print(f"Or upload manually using the AWS Management Console")

if __name__ == "__main__":
    main() 