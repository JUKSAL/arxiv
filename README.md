# ArXiv Paper Scraper

## Overview
The **ArXiv Paper Scraper** is a Python script that automates the process of fetching the latest papers from the [arXiv.org](https://arxiv.org) website. It scrapes the newest submissions in the specified subjects and generates a PDF report containing the details of the fetched papers.

## Features
- Scrapes the latest papers from arXiv's "New Submissions" section.
- Allows filtering by subjects (1 to 5 subjects can be specified).
- Generates a well-formatted PDF report with a timestamped file name.

## Requirements
The script requires the following Python libraries:

- `requests`
- `BeautifulSoup` (from `bs4`)
- `reportlab`
- `datetime` (standard Python library)

You can install the dependencies using pip:

```bash
pip install requests beautifulsoup4 reportlab
```

## How to Use

### 1. Clone or Download the Repository
Ensure the script (`arxiv.py`) is in your working directory.

### 2. Run the Script

Run the script using Python:

```bash
python arxiv.py
```

### 3. Generated Output
The script will generate a PDF file in the same directory with the name format:

```
arxiv_papers_<DDMMYYYY>_<HHMM>.pdf
```
For example: `arxiv_papers_11122024_1050.pdf`.

### 4. Customize Subjects
Modify the `fetch_arxiv_papers` function call in the script to include your desired subjects:

```python
fetch_arxiv_papers("cs", "math", "stat")
```

## Script Workflow
1. **Fetch New Submissions**: Sends an HTTP GET request to arXiv’s new submissions page.
2. **Parse HTML**: Extracts paper titles, abstracts, and other relevant details using BeautifulSoup.
3. **Generate PDF**: Formats the extracted details into a PDF report using `reportlab`.
4. **Save PDF**: Saves the PDF with a timestamped file name.

## Notes
- Ensure a stable internet connection when running the script.
- The script is currently configured to scrape new computer science (`cs`) submissions. Update the URL or logic as needed to target other sections.

## Error Handling
- The script raises an error if more than 5 or fewer than 1 subjects are provided.
- It checks for successful HTTP responses before proceeding with scraping.

## Automating Execution
To schedule the script to run daily, you can:

### Using Cron (Linux/Mac):
1. Create a shell script (`run_arxiv_scraper.sh`):

    ```bash
    #!/bin/bash
    cd /path/to/script
    python3 arxiv.py
    ```

2. Make it executable:

    ```bash
    chmod +x run_arxiv_scraper.sh
    ```

3. Add to your crontab:

    ```bash
    crontab -e
    ```

    Add the following line to schedule it at 7:00 AM daily:

    ```bash
    0 7 * * * /path/to/run_arxiv_scraper.sh
    ```

### Using Task Scheduler (Windows):
1. Open Task Scheduler and create a new task.
2. Set the action to run a batch script (`run_arxiv_scraper.bat`):

    ```bat
    @echo off
    cd \path\to\script
    python fetch_arxiv_papers.py
    ```

3. Schedule the task to run daily at your preferred time.

## License
This script is provided as-is, and you are free to modify and use it for your purposes. Attribution is appreciated.

## Author
Created by Jukka Salmenkylä

