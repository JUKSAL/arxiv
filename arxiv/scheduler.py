"""Module for scheduling ArXiv scraping and summarization tasks."""

import os
import logging
import time
import argparse
import schedule
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
import json
from pathlib import Path

from arxiv.scraper import ArxivScraper, scrape_from_topics_file
from arxiv.summarizer import ArxivSummarizer, summarize_latest_papers

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("arxiv_scheduler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ArxivScheduler:
    """Class for scheduling ArXiv scraping and summarization tasks."""
    
    def __init__(self, topics_file: str = "topics.txt",
                output_dir: str = "ArxivPapers",
                summary_dir: str = "ArxivSummaries",
                log_file: str = "arxiv_scheduler.log",
                config_file: str = "arxiv_config.json"):
        """Initialize the ArXiv scheduler.
        
        Args:
            topics_file: Path to a file containing topics to scrape
            output_dir: Directory to save the scraped PDFs
            summary_dir: Directory to save the summaries
            log_file: Path to the log file
            config_file: Path to the configuration file
        """
        self.topics_file = topics_file
        self.output_dir = output_dir
        self.summary_dir = summary_dir
        self.log_file = log_file
        self.config_file = config_file
        
        self.config = self._load_config()
        self._setup_logging()
        self._ensure_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default config.
        
        Returns:
            Configuration dictionary
        """
        default_config = {
            "scrape_schedule": "09:00",  # Daily at 9 AM
            "summary_schedule": "10:00",  # Daily at 10 AM
            "use_ai_summaries": False,
            "openai_api_key": None,
            "max_papers_per_topic": 100,
            "arxiv_category": "cs",
            "log_level": "INFO"
        }
        
        # Try to load existing config
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
        
        # Create default config file
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            logger.error(f"Error creating config file: {e}")
        
        return default_config
    
    def _setup_logging(self) -> None:
        """Set up logging based on configuration."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        # Update root logger
        logging.getLogger().setLevel(log_level)
        
        # Add file handler if not already present
        if not any(isinstance(h, logging.FileHandler) and h.baseFilename.endswith(self.log_file) 
                for h in logging.getLogger().handlers):
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(file_handler)
    
    def _ensure_directories(self) -> None:
        """Ensure output directories exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.summary_dir, exist_ok=True)
    
    def _scrape_task(self) -> None:
        """Task to scrape papers from ArXiv."""
        logger.info("Starting ArXiv scraping task...")
        try:
            # Read topics from file
            with open(self.topics_file, 'r') as f:
                topics = [line.strip() for line in f.readlines() if line.strip()]
            
            # Create scraper
            scraper = ArxivScraper(
                output_dir=self.output_dir,
                max_papers_per_topic=self.config.get("max_papers_per_topic", 100)
            )
            
            # Scrape papers
            results = scraper.scrape_papers(
                topics=topics,
                category=self.config.get("arxiv_category", "cs")
            )
            
            # Log results
            if results:
                logger.info(f"Successfully scraped papers for {len(results)} topics")
                for topic, pdf_path in results.items():
                    logger.info(f"  - {topic}: {pdf_path}")
            else:
                logger.warning("No papers were scraped")
        
        except Exception as e:
            logger.error(f"Error in scraping task: {e}", exc_info=True)
    
    def _summary_task(self) -> None:
        """Task to generate summaries of the latest papers."""
        logger.info("Starting ArXiv summary task...")
        try:
            # Create summarizer
            summary_files = summarize_latest_papers(
                input_dir=self.output_dir,
                output_dir=self.summary_dir,
                use_ai=self.config.get("use_ai_summaries", False),
                openai_api_key=self.config.get("openai_api_key")
            )
            
            # Log results
            if summary_files:
                logger.info(f"Successfully created {len(summary_files)} summary files:")
                for summary_file in summary_files:
                    logger.info(f"  - {summary_file}")
            else:
                logger.warning("No summaries were generated")
        
        except Exception as e:
            logger.error(f"Error in summary task: {e}", exc_info=True)
    
    def run_once(self, scrape: bool = True, summarize: bool = True) -> None:
        """Run the scraping and summarization tasks once.
        
        Args:
            scrape: Whether to run the scraping task
            summarize: Whether to run the summarization task
        """
        if scrape:
            self._scrape_task()
        
        if summarize:
            self._summary_task()
    
    def schedule_tasks(self) -> None:
        """Schedule the scraping and summarization tasks."""
        # Schedule scraping task
        scrape_time = self.config.get("scrape_schedule", "09:00")
        logger.info(f"Scheduling daily scraping at {scrape_time}")
        schedule.every().day.at(scrape_time).do(self._scrape_task)
        
        # Schedule summary task
        summary_time = self.config.get("summary_schedule", "10:00")
        logger.info(f"Scheduling daily summarization at {summary_time}")
        schedule.every().day.at(summary_time).do(self._summary_task)
    
    def run_scheduler(self) -> None:
        """Run the scheduler loop."""
        self.schedule_tasks()
        
        logger.info("Starting scheduler. Press Ctrl+C to exit.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Error in scheduler: {e}", exc_info=True)


def main():
    """Main function to run the ArXiv scheduler."""
    parser = argparse.ArgumentParser(description='ArXiv Scraper and Summarizer')
    parser.add_argument('--run-once', action='store_true', 
                       help='Run the scraping and summarization tasks once')
    parser.add_argument('--scrape-only', action='store_true', 
                       help='Run only the scraping task')
    parser.add_argument('--summarize-only', action='store_true', 
                       help='Run only the summarization task')
    parser.add_argument('--topics-file', type=str, default='topics.txt',
                       help='Path to the topics file')
    parser.add_argument('--output-dir', type=str, default='ArxivPapers',
                       help='Directory to save the scraped PDFs')
    parser.add_argument('--summary-dir', type=str, default='ArxivSummaries',
                       help='Directory to save the summaries')
    parser.add_argument('--log-file', type=str, default='arxiv_scheduler.log',
                       help='Path to the log file')
    parser.add_argument('--config-file', type=str, default='arxiv_config.json',
                       help='Path to the configuration file')
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = ArxivScheduler(
        topics_file=args.topics_file,
        output_dir=args.output_dir,
        summary_dir=args.summary_dir,
        log_file=args.log_file,
        config_file=args.config_file
    )
    
    # Run tasks once if requested
    if args.run_once or args.scrape_only or args.summarize_only:
        scrape = not args.summarize_only
        summarize = not args.scrape_only
        scheduler.run_once(scrape=scrape, summarize=summarize)
    else:
        # Otherwise, run the scheduler loop
        scheduler.run_scheduler()


if __name__ == "__main__":
    main() 