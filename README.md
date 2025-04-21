# ArXiv Scraper and Summarizer

A system for scheduled scraping and summarization of ArXiv papers.

## Features

- Scrape papers from ArXiv based on topics of interest
- Generate PDF reports with paper information
- Create summaries of scraped papers
- Optional AI-powered summarization (requires OpenAI API key)
- Configurable scheduling for daily updates
- Command-line interface for easy usage

## Installation

### Prerequisites

- Python 3.8 or higher

### Install from source

1. Clone the repository:
```bash
git clone https://github.com/jukkasalmenkyla/arxiv.git
cd arxiv
```

2. Install in development mode:
```bash
pip install -e .
```

3. For AI-powered summarization:
```bash
pip install -e ".[ai]"
```

### Environment Variables

If you're using AI-powered summarization, create a `.env` file with:
```bash
OPENAI_API_KEY=your_api_key
```

## Usage

### Command Line Interface

The package provides a command-line interface for easy usage:

```bash
# Scrape papers from ArXiv
arxiv-scraper scrape

# Generate summaries of scraped papers
arxiv-scraper summarize

# Run the scheduler for daily updates
arxiv-scraper schedule
```

### Basic Usage

```python
from arxiv.scraper import ArxivScraper
from arxiv.summarizer import ArxivSummarizer

# Scrape papers
scraper = ArxivScraper(output_dir="ArxivPapers")
results = scraper.scrape_papers(["Machine Learning", "Artificial Intelligence"])

# Generate summaries
summarizer = ArxivSummarizer(input_dir="ArxivPapers", output_dir="ArxivSummaries")
summary_files = summarizer.summarize_latest_papers()
```

### Configuration

Create or edit `arxiv_config.json` to customize behavior:

```json
{
  "scrape_schedule": "09:00",
  "summary_schedule": "10:00",
  "use_ai_summaries": false,
  "openai_api_key": null,
  "max_papers_per_topic": 100,
  "arxiv_category": "cs",
  "log_level": "INFO"
}
```

### Topics File

Create a `topics.txt` file with one topic per line:

```
Machine Learning
Artificial Intelligence
Information Retrieval
Computation and Language
Neural and Evolutionary Computing
```

## Scheduled Operation

### Running as a Service

To run the scheduler as a background service, you can use:

```bash
nohup arxiv-scraper schedule > arxiv.log 2>&1 &
```

### Using Cron

Alternative to the built-in scheduler, you can use cron:

```bash
# Edit crontab
crontab -e

# Add these lines
0 9 * * * /path/to/python -m arxiv scrape
0 10 * * * /path/to/python -m arxiv summarize
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project uses:
- pylint for linting
- black for code formatting
- isort for import sorting

To format code:
```bash
black arxiv/
isort arxiv/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details

