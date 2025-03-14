"""
Progress Tracker for Big Data Analytics Project
Monitors project milestones and deadlines
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.deadline = datetime(2025, 4, 3)  # April 3, 2025
        self.progress_file = self.base_dir / "progress_status.json"

        self.milestones = {
            "individual_development": {
                "start_date": datetime(2025, 3, 6),  # Week 1-2
                "end_date": datetime(2025, 3, 19),
                "tasks": {
                    "JH": {
                        "data_storage_setup": {"status": "pending", "progress": 0},
                        "web_interface_setup": {"status": "pending", "progress": 0},
                    },
                    "Darrel": {
                        "mapreduce_implementation": {
                            "status": "pending",
                            "progress": 0,
                        },
                        "data_cleaning": {"status": "pending", "progress": 0},
                    },
                    "Xuan_Yu": {
                        "spark_setup": {"status": "pending", "progress": 0},
                        "realtime_analysis": {"status": "pending", "progress": 0},
                    },
                    "Javin": {
                        "visualization_dashboard": {"status": "pending", "progress": 0},
                        "analytics_implementation": {
                            "status": "pending",
                            "progress": 0,
                        },
                    },
                },
            },
            "integration": {
                "start_date": datetime(2025, 3, 20),  # Week 3
                "end_date": datetime(2025, 3, 26),
                "tasks": {
                    "storage_mapreduce": {"status": "pending", "progress": 0},
                    "mapreduce_spark": {"status": "pending", "progress": 0},
                    "spark_visualization": {"status": "pending", "progress": 0},
                    "web_visualization": {"status": "pending", "progress": 0},
                },
            },
            "testing": {
                "start_date": datetime(2025, 3, 27),  # Week 4
                "end_date": datetime(2025, 4, 2),
                "tasks": {
                    "unit_testing": {"status": "pending", "progress": 0},
                    "integration_testing": {"status": "pending", "progress": 0},
                    "performance_testing": {"status": "pending", "progress": 0},
                    "bug_fixes": {"status": "pending", "progress": 0},
                },
            },
            "documentation": {
                "start_date": datetime(2025, 4, 3),  # Final Week
                "end_date": datetime(2025, 4, 3),
                "tasks": {
                    "technical_documentation": {"status": "pending", "progress": 0},
                    "user_guide": {"status": "pending", "progress": 0},
                    "presentation_prep": {"status": "pending", "progress": 0},
                },
            },
        }
        self._load_progress()

    def _load_progress(self):
        """Load progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, "r") as f:
                saved_progress = json.load(f)
                # Convert string dates back to datetime objects
                for phase in saved_progress:
                    saved_progress[phase]["start_date"] = datetime.fromisoformat(
                        saved_progress[phase]["start_date"]
                    )
                    saved_progress[phase]["end_date"] = datetime.fromisoformat(
                        saved_progress[phase]["end_date"]
                    )
                self.milestones.update(saved_progress)

    def _save_progress(self):
        """Save current progress to file"""
        # Convert datetime objects to ISO format strings for JSON serialization
        progress_data = {}
        for phase, data in self.milestones.items():
            progress_data[phase] = {
                "start_date": data["start_date"].isoformat(),
                "end_date": data["end_date"].isoformat(),
                "tasks": data["tasks"],
            }

        with open(self.progress_file, "w") as f:
            json.dump(progress_data, f, indent=4)

    def update_task_progress(self, phase, task_path, status, progress):
        """Update the progress of a specific task"""
        if phase not in self.milestones:
            raise ValueError(f"Invalid phase: {phase}")

        # Handle nested task paths (e.g., "JH.data_storage_setup")
        current = self.milestones[phase]["tasks"]
        path_parts = task_path.split(".")

        for part in path_parts[:-1]:
            if part not in current:
                raise ValueError(f"Invalid task path: {task_path}")
            current = current[part]

        if path_parts[-1] not in current:
            raise ValueError(f"Invalid task: {path_parts[-1]}")

        current[path_parts[-1]].update({"status": status, "progress": progress})

        self._save_progress()
        logger.info(f"Updated {phase} - {task_path} progress: {progress}%")

    def get_phase_progress(self, phase):
        """Calculate overall progress for a phase"""
        if phase not in self.milestones:
            raise ValueError(f"Invalid phase: {phase}")

        tasks = self.milestones[phase]["tasks"]
        total_progress = 0
        task_count = 0

        def count_tasks(tasks_dict):
            progress_sum = 0
            count = 0

            for task in tasks_dict.values():
                if isinstance(task, dict):
                    if "progress" in task:
                        progress_sum += task["progress"]
                        count += 1
                    else:
                        sub_progress, sub_count = count_tasks(task)
                        progress_sum += sub_progress
                        count += sub_count

            return progress_sum, count

        total_progress, task_count = count_tasks(tasks)
        if task_count == 0:
            return 0

        return total_progress / task_count

    def get_overall_progress(self):
        """Calculate overall project progress"""
        phase_progress = {
            phase: self.get_phase_progress(phase) for phase in self.milestones
        }

        total_progress = sum(phase_progress.values()) / len(phase_progress)
        return {
            "overall_progress": total_progress,
            "phase_progress": phase_progress,
            "days_until_deadline": (self.deadline - datetime.now()).days,
        }

    def get_team_member_progress(self, member):
        """Get progress for a specific team member's tasks"""
        member_progress = {}

        for phase, data in self.milestones.items():
            if phase == "individual_development" and member in data["tasks"]:
                tasks = data["tasks"][member]
                progress = sum(task["progress"] for task in tasks.values()) / len(tasks)
                member_progress[phase] = progress

        return member_progress

    def check_overdue_tasks(self):
        """Check for overdue tasks"""
        current_date = datetime.now()
        overdue_tasks = []

        for phase, data in self.milestones.items():
            if current_date > data["end_date"]:
                tasks = data["tasks"]

                def check_tasks(tasks_dict, phase_name, parent=""):
                    for task_name, task in tasks_dict.items():
                        if isinstance(task, dict):
                            if "progress" in task and task["progress"] < 100:
                                full_task_name = (
                                    f"{parent}{task_name}" if parent else task_name
                                )
                                overdue_tasks.append(
                                    {
                                        "phase": phase_name,
                                        "task": full_task_name,
                                        "due_date": data["end_date"].isoformat(),
                                        "progress": task["progress"],
                                    }
                                )
                            else:
                                check_tasks(task, phase_name, f"{task_name}.")

                check_tasks(tasks, phase)

        return overdue_tasks

    def print_status(self):
        """Print formatted status of both integration points"""
        # Implementation of print_status method
        pass


def main():
    # Example usage
    base_dir = Path(__file__).parent.parent
    tracker = ProgressTracker(base_dir)

    # Update some task progress
    tracker.update_task_progress(
        "individual_development", "JH.data_storage_setup", "in_progress", 50
    )

    # Get overall progress
    progress = tracker.get_overall_progress()
    print("\nProject Progress:")
    print(json.dumps(progress, indent=2))

    # Check overdue tasks
    overdue = tracker.check_overdue_tasks()
    if overdue:
        print("\nOverdue Tasks:")
        print(json.dumps(overdue, indent=2))

    # Print formatted status of both integration points
    tracker.print_status()


if __name__ == "__main__":
    main()
