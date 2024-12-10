"""
Script to build and submit the Flink job.
"""
import os
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_environment():
    """Prepare the Python environment for Flink job."""
    try:
        # Install required dependencies in the Flink container
        subprocess.run([
            "docker", "exec", "jobmanager",
            "pip", "install",
            "kafka-python",
            "apache-flink==1.17.1",
            "apache-flink-libraries==1.17.1"
        ], check=True)
        logger.info("Successfully installed dependencies in Flink container")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to prepare environment: {e}")
        return False

def submit_job():
    """Submit the Flink job to the cluster."""
    try:
        # Copy the price_processor.py to the Flink container
        subprocess.run([
            "docker", "cp",
            "src/processing/flink_processor/price_processor.py",
            "jobmanager:/opt/flink/price_processor.py"
        ], check=True)
        
        # Submit the job
        subprocess.run([
            "docker", "exec", "jobmanager",
            "./bin/flink", "run",
            "-py", "/opt/flink/price_processor.py",
            "-d"  # Detached mode
        ], check=True)
        
        logger.info("Successfully submitted Flink job")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to submit job: {e}")
        return False

def main():
    """Main entry point."""
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent.parent.parent.parent
    os.chdir(project_root)
    
    # Prepare environment
    if not prepare_environment():
        logger.error("Failed to prepare environment")
        return
    
    # Submit job
    if not submit_job():
        logger.error("Failed to submit job")
        return
    
    logger.info("Flink job setup completed successfully")
    logger.info("You can view the Flink dashboard at http://localhost:8082")

if __name__ == "__main__":
    main() 