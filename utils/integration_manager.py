"""
Integration Manager for Big Data Analytics Project
Handles data flow and integration points between different components
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.integration_points = {
            "storage_to_mapreduce": {
                "source": "data_storage",
                "target": "mapreduce",
                "status": "pending",
                "last_sync": None
            },
            "mapreduce_to_spark": {
                "source": "mapreduce",
                "target": "spark_analysis",
                "status": "pending",
                "last_sync": None
            },
            "spark_to_visualization": {
                "source": "spark_analysis",
                "target": "visualization",
                "status": "pending",
                "last_sync": None
            },
            "web_to_visualization": {
                "source": "web_interface",
                "target": "visualization",
                "status": "pending",
                "last_sync": None
            }
        }
        self.status_file = self.base_dir / "integration_status.json"
        self._load_status()

    def _load_status(self):
        """Load integration status from file"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                saved_status = json.load(f)
                self.integration_points.update(saved_status)

    def _save_status(self):
        """Save current integration status to file"""
        with open(self.status_file, 'w') as f:
            json.dump(self.integration_points, f, indent=4, default=str)

    def update_integration_status(self, integration_point, status, message=""):
        """Update the status of an integration point"""
        if integration_point not in self.integration_points:
            raise ValueError(f"Invalid integration point: {integration_point}")
        
        self.integration_points[integration_point].update({
            "status": status,
            "last_sync": datetime.now().isoformat(),
            "message": message
        })
        self._save_status()
        logger.info(f"Updated {integration_point} status to {status}: {message}")

    def check_integration_readiness(self, integration_point):
        """Check if an integration point is ready for sync"""
        if integration_point not in self.integration_points:
            raise ValueError(f"Invalid integration point: {integration_point}")
        
        source = self.integration_points[integration_point]["source"]
        target = self.integration_points[integration_point]["target"]
        
        # Check if source and target components exist and are ready
        source_path = self.base_dir / "src" / source
        target_path = self.base_dir / "src" / target
        
        if not source_path.exists() or not target_path.exists():
            return False, "Source or target component missing"
        
        return True, "Components ready for integration"

    def get_integration_status(self):
        """Get the status of all integration points"""
        return {
            point: {
                "status": info["status"],
                "last_sync": info["last_sync"],
                "message": info.get("message", "")
            }
            for point, info in self.integration_points.items()
        }

    def validate_integration(self, integration_point):
        """Validate the integration between components"""
        if integration_point not in self.integration_points:
            raise ValueError(f"Invalid integration point: {integration_point}")
        
        ready, message = self.check_integration_readiness(integration_point)
        if not ready:
            return False, message
        
        # Add specific validation logic for each integration point
        if integration_point == "storage_to_mapreduce":
            # Validate data storage to MapReduce integration
            return self._validate_storage_mapreduce()
        elif integration_point == "mapreduce_to_spark":
            # Validate MapReduce to Spark integration
            return self._validate_mapreduce_spark()
        elif integration_point == "spark_to_visualization":
            # Validate Spark to Visualization integration
            return self._validate_spark_visualization()
        elif integration_point == "web_to_visualization":
            # Validate Web to Visualization integration
            return self._validate_web_visualization()
        
        return False, "Unknown integration point"

    def _validate_storage_mapreduce(self):
        """Validate data storage to MapReduce integration"""
        try:
            # TODO: Add specific validation logic
            return True, "Storage to MapReduce integration valid"
        except Exception as e:
            return False, str(e)

    def _validate_mapreduce_spark(self):
        """Validate MapReduce to Spark integration"""
        try:
            # TODO: Add specific validation logic
            return True, "MapReduce to Spark integration valid"
        except Exception as e:
            return False, str(e)

    def _validate_spark_visualization(self):
        """Validate Spark to Visualization integration"""
        try:
            # TODO: Add specific validation logic
            return True, "Spark to Visualization integration valid"
        except Exception as e:
            return False, str(e)

    def _validate_web_visualization(self):
        """Validate Web to Visualization integration"""
        try:
            # TODO: Add specific validation logic
            return True, "Web to Visualization integration valid"
        except Exception as e:
            return False, str(e)

def main():
    # Example usage
    base_dir = Path(__file__).parent.parent
    integration_manager = IntegrationManager(base_dir)
    
    # Update integration status
    integration_manager.update_integration_status(
        "storage_to_mapreduce",
        "in_progress",
        "Initial data transfer started"
    )
    
    # Check integration status
    status = integration_manager.get_integration_status()
    print("\nIntegration Status:")
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main() 