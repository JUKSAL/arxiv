#!/bin/bash

# Run the ArXiv scraper and summarizer
# This script can be scheduled with cron

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the scraper and summarizer
if [ "$1" == "scrape" ]; then
    python -m arxiv scrape
elif [ "$1" == "summarize" ]; then
    python -m arxiv summarize
elif [ "$1" == "schedule" ]; then
    python -m arxiv schedule
else
    echo "Usage: $0 [scrape|summarize|schedule]"
    echo "  scrape    - Scrape papers from ArXiv"
    echo "  summarize - Generate summaries of scraped papers"
    echo "  schedule  - Run the scheduler for daily updates"
    exit 1
fi 