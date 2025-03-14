"""
Example usage of the Integration Manager
"""

from integration_manager import IntegrationManager
import json
from pathlib import Path

def main():
    # Initialize the integration manager
    base_dir = Path(__file__).parent.parent
    manager = IntegrationManager(base_dir)

    # Example 1: Update integration status for storage to MapReduce
    print("\n1. Updating Storage to MapReduce integration status:")
    manager.update_integration_status(
        "storage_to_mapreduce",
        "in_progress",
        "Initial data transfer started"
    )

    # Example 2: Check if integration points are ready
    print("\n2. Checking integration readiness:")
    for point in ["storage_to_mapreduce", "mapreduce_to_spark", "spark_to_visualization"]:
        ready, message = manager.check_integration_readiness(point)
        print(f"{point}: Ready={ready}, Message={message}")

    # Example 3: Get current status of all integration points
    print("\n3. Current Integration Status:")
    status = manager.get_integration_status()
    print(json.dumps(status, indent=2))

    # Example 4: Validate specific integration
    print("\n4. Validating MapReduce to Spark integration:")
    valid, message = manager.validate_integration("mapreduce_to_spark")
    print(f"Valid={valid}, Message={message}")

    # Example 5: Simulating a complete integration flow
    print("\n5. Simulating complete integration flow:")
    
    # Step 1: Storage to MapReduce
    manager.update_integration_status(
        "storage_to_mapreduce",
        "completed",
        "Data successfully transferred to MapReduce"
    )
    
    # Step 2: MapReduce to Spark
    manager.update_integration_status(
        "mapreduce_to_spark",
        "in_progress",
        "Processing MapReduce output for Spark analysis"
    )
    
    # Step 3: Spark to Visualization
    manager.update_integration_status(
        "spark_to_visualization",
        "pending",
        "Waiting for Spark analysis completion"
    )

    # Final status check
    print("\n6. Final Integration Status:")
    final_status = manager.get_integration_status()
    print(json.dumps(final_status, indent=2))

if __name__ == "__main__":
    main() 