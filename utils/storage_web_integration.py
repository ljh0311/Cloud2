"""
Track integration status for Data Storage and Web Interface components
"""

from utils.integration_manager import IntegrationManager
import json
from pathlib import Path
import time

class StorageWebIntegrationTracker:
    def __init__(self):
        self.manager = IntegrationManager(".")
        
    def update_storage_status(self, status, message):
        """Update storage to MapReduce integration status"""
        self.manager.update_integration_status(
            "storage_to_mapreduce",
            status,
            message
        )
        
    def update_web_status(self, status, message):
        """Update web to visualization integration status"""
        self.manager.update_integration_status(
            "web_to_visualization",
            status,
            message
        )
        
    def check_storage_readiness(self):
        """Check if storage is ready for MapReduce integration"""
        return self.manager.check_integration_readiness("storage_to_mapreduce")
        
    def check_web_readiness(self):
        """Check if web interface is ready for visualization integration"""
        return self.manager.check_integration_readiness("web_to_visualization")
    
    def get_current_status(self):
        """Get current status of both integration points"""
        return self.manager.get_integration_status()
    
    def print_status(self):
        """Print current status in a readable format"""
        status = self.get_current_status()
        
        print("\nCurrent Integration Status:")
        print("-" * 50)
        
        # Storage to MapReduce Status
        storage_status = status.get("storage_to_mapreduce", {})
        print("Storage to MapReduce Integration:")
        print(f"Status: {storage_status.get('status', 'unknown')}")
        print(f"Last Update: {storage_status.get('last_sync', 'never')}")
        print(f"Message: {storage_status.get('message', 'No message')}")
        print()
        
        # Web to Visualization Status
        web_status = status.get("web_to_visualization", {})
        print("Web to Visualization Integration:")
        print(f"Status: {web_status.get('status', 'unknown')}")
        print(f"Last Update: {web_status.get('last_sync', 'never')}")
        print(f"Message: {web_status.get('message', 'No message')}")
        print("-" * 50)

def main():
    # Initialize the tracker
    tracker = StorageWebIntegrationTracker()
    
    # Example workflow for your integration points
    
    # 1. Starting work on data storage setup
    print("\n1. Starting data storage setup...")
    tracker.update_storage_status(
        "in_progress",
        "Setting up HDFS and configuring data storage paths"
    )
    
    # 2. Check if storage is ready for MapReduce
    print("\n2. Checking storage readiness...")
    ready, message = tracker.check_storage_readiness()
    print(f"Storage ready for MapReduce: {ready}, Message: {message}")
    
    # 3. Starting web interface setup
    print("\n3. Starting web interface setup...")
    tracker.update_web_status(
        "in_progress",
        "Implementing web interface components"
    )
    
    # 4. Simulate some progress (in real usage, these would be actual implementation steps)
    print("\n4. Making progress on both components...")
    
    # Storage progress
    tracker.update_storage_status(
        "in_progress",
        "Data storage structure created, implementing data access layer"
    )
    
    # Web interface progress
    tracker.update_web_status(
        "in_progress",
        "Basic web interface implemented, working on visualization integration"
    )
    
    # 5. Print current status
    print("\n5. Current status of your integration points:")
    tracker.print_status()
    
    # 6. Simulate completion of storage setup
    print("\n6. Completing storage setup...")
    tracker.update_storage_status(
        "completed",
        "Data storage fully configured and ready for MapReduce integration"
    )
    
    # 7. Final status check
    print("\n7. Final status:")
    tracker.print_status()

if __name__ == "__main__":
    main() 