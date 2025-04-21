"""Command-line interface for the ArXiv scraper and summarizer."""

import sys
import argparse
from arxiv.scheduler import ArxivScheduler

def main():
    """Main function for the ArXiv CLI."""
    parser = argparse.ArgumentParser(
        description='ArXiv Paper Scraper and Summarizer',
        prog='python -m arxiv'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape papers from ArXiv')
    scrape_parser.add_argument('--topics-file', type=str, default='topics.txt',
                              help='Path to the topics file')
    scrape_parser.add_argument('--output-dir', type=str, default='ArxivPapers',
                              help='Directory to save the scraped PDFs')
    scrape_parser.add_argument('--config-file', type=str, default='arxiv_config.json',
                              help='Path to the configuration file')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Generate summaries of papers')
    summarize_parser.add_argument('--input-dir', type=str, default='ArxivPapers',
                                 help='Directory containing the scraped PDFs')
    summarize_parser.add_argument('--output-dir', type=str, default='ArxivSummaries',
                                 help='Directory to save the summaries')
    summarize_parser.add_argument('--use-ai', action='store_true',
                                 help='Use AI to generate summaries')
    summarize_parser.add_argument('--config-file', type=str, default='arxiv_config.json',
                                 help='Path to the configuration file')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Run the scheduled tasks')
    schedule_parser.add_argument('--topics-file', type=str, default='topics.txt',
                               help='Path to the topics file')
    schedule_parser.add_argument('--output-dir', type=str, default='ArxivPapers',
                               help='Directory to save the scraped PDFs')
    schedule_parser.add_argument('--summary-dir', type=str, default='ArxivSummaries',
                               help='Directory to save the summaries')
    schedule_parser.add_argument('--log-file', type=str, default='arxiv_scheduler.log',
                               help='Path to the log file')
    schedule_parser.add_argument('--config-file', type=str, default='arxiv_config.json',
                               help='Path to the configuration file')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    # Create scheduler with appropriate arguments
    scheduler = ArxivScheduler(
        topics_file=getattr(args, 'topics_file', 'topics.txt'),
        output_dir=getattr(args, 'output_dir', 'ArxivPapers'),
        summary_dir=getattr(args, 'summary_dir', 'ArxivSummaries') if hasattr(args, 'summary_dir') 
                   else getattr(args, 'output_dir', 'ArxivSummaries'),
        log_file=getattr(args, 'log_file', 'arxiv_scheduler.log'),
        config_file=args.config_file
    )
    
    # Execute the appropriate command
    if args.command == 'scrape':
        scheduler.run_once(scrape=True, summarize=False)
    elif args.command == 'summarize':
        # Update configuration for AI summaries if specified
        if args.use_ai:
            scheduler.config['use_ai_summaries'] = True
        scheduler.run_once(scrape=False, summarize=True)
    elif args.command == 'schedule':
        scheduler.run_scheduler()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 