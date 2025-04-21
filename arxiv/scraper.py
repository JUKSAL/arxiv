"""ArXiv paper scraper module."""

import os
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import xml.sax.saxutils as saxutils

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger(__name__)


class ArxivScraper:
    """Class for scraping papers from ArXiv."""

    def __init__(self, output_dir: str = "ArxivPapers", max_papers_per_topic: int = 100):
        """Initialize the ArXiv scraper.
        
        Args:
            output_dir: Directory to save the generated PDFs
            max_papers_per_topic: Maximum number of papers to include per topic
        """
        self.output_dir = output_dir
        self.max_papers_per_topic = max_papers_per_topic
        self._ensure_output_dir()
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        if 'Italic' not in self.styles:
            self.styles.add(ParagraphStyle(name='Italic', parent=self.styles['Normal'], 
                                          fontName='Helvetica-Oblique'))
        self.styles.add(ParagraphStyle(name='TitleStyle', fontSize=14, alignment=0, 
                                      spaceAfter=12, textColor='navy'))
        self.styles.add(ParagraphStyle(name='LinkStyle', textColor='blue', 
                                      alignment=0, spaceAfter=12))
    
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _fetch_arxiv_page(self, category: str = "cs", list_type: str = "new") -> Optional[str]:
        """Fetch the ArXiv page for a specific category and list type.
        
        Args:
            category: ArXiv category (e.g., "cs", "math", "physics")
            list_type: Type of list ("new" for new submissions, "recent" for recent papers)
            
        Returns:
            HTML content if successful, None otherwise
        """
        url = f"https://arxiv.org/list/{category}/{list_type}"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None
    
    def _parse_paper_data(self, html_content: str, topic: str) -> List[Dict[str, str]]:
        """Parse paper data from HTML content that matches the given topic.
        
        Args:
            html_content: HTML content from ArXiv
            topic: Topic to filter by
            
        Returns:
            List of papers as dictionaries with title, authors, etc.
        """
        papers = []
        if not html_content:
            return papers
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Process each paper
            for dt, dd in zip(soup.find_all('dt'), soup.find_all('dd')):
                # Extract subjects
                subjects_element = dd.find('div', class_='list-subjects')
                subjects_text = (subjects_element.get_text(strip=True).replace('Subjects:', '')
                               if subjects_element else "Subjects not found")
                
                # Only process if the paper's subjects match the topic
                if topic.lower() in subjects_text.lower():
                    # Extract title
                    title_element = dd.find('div', class_='list-title')
                    title = (title_element.get_text(strip=True).replace('Title:', '')
                           if title_element else "Title not found")
                    
                    # Extract authors
                    authors_element = dd.find('div', class_='list-authors')
                    authors = (authors_element.get_text(strip=True).replace('Authors:', '')
                             if authors_element else "Authors not found")
                    
                    # Extract link
                    link_tag = dt.find('a', title='Abstract')
                    link = ("https://arxiv.org" + link_tag['href']
                          if link_tag and link_tag.has_attr('href') else "Link not found")
                    
                    # Extract abstract
                    abstract_element = dd.find('p', class_='mathjax')
                    abstract = (abstract_element.get_text(strip=True)
                              if abstract_element else "Abstract not found")
                    
                    # Extract paper ID
                    paper_id = link.split('/')[-1] if 'arxiv.org/abs/' in link else None
                    
                    papers.append({
                        'title': title,
                        'authors': authors,
                        'link': link,
                        'abstract': abstract,
                        'subjects': subjects_text,
                        'paper_id': paper_id
                    })
                    
                    # Limit the number of papers
                    if len(papers) >= self.max_papers_per_topic:
                        break
        
        except Exception as e:
            logger.error(f"Error parsing HTML content: {e}")
        
        return papers
    
    def _create_pdf(self, papers: List[Dict[str, str]], topic: str) -> str:
        """Create a PDF containing the papers.
        
        Args:
            papers: List of paper dictionaries
            topic: Topic for the file name
            
        Returns:
            Path to the generated PDF file
        """
        if not papers:
            logger.warning(f"No papers found for topic: {topic}")
            return ""
        
        # Generate a timestamp
        timestamp = datetime.now().strftime("%d%m%Y_%H%M")
        
        # Create the PDF file name
        file_name = f"arxiv_papers_{timestamp}_{topic.replace(' ', '_')}.pdf"
        file_path = os.path.join(self.output_dir, file_name)
        
        elements = []
        
        # Add title page
        elements.append(Paragraph(f"ArXiv Papers: {topic}", self.styles['Title']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                                 self.styles['Normal']))
        elements.append(Paragraph(f"Contains {len(papers)} papers", self.styles['Normal']))
        elements.append(Spacer(1, 12 * 5))
        
        # Process each paper
        for paper in papers:
            # Escape text to avoid issues with ReportLab's markup parser
            title_safe = saxutils.escape(paper['title'])
            authors_safe = saxutils.escape(paper['authors'])
            subjects_safe = saxutils.escape(paper['subjects'])
            abstract_safe = saxutils.escape(paper['abstract'])
            
            # Add the paper details to the PDF
            elements.append(Paragraph(title_safe, self.styles['TitleStyle']))
            elements.append(Paragraph(authors_safe, self.styles['Italic']))
            elements.append(Paragraph(f"<link href='{paper['link']}'>{paper['link']}</link>", 
                                     self.styles['LinkStyle']))
            elements.append(Paragraph(subjects_safe, self.styles['BodyText']))
            elements.append(Paragraph(abstract_safe, self.styles['BodyText']))
            elements.append(Spacer(1, 12 * 5))
        
        try:
            # Create the PDF
            pdf = SimpleDocTemplate(file_path, pagesize=letter)
            pdf.build(elements)
            logger.info(f"PDF created successfully: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error creating PDF for topic '{topic}': {e}")
            return ""
    
    def scrape_papers(self, topics: List[str], category: str = "cs") -> Dict[str, str]:
        """Scrape papers from ArXiv for multiple topics.
        
        Args:
            topics: List of topics to scrape
            category: ArXiv category (default: "cs" for computer science)
            
        Returns:
            Dictionary mapping topics to PDF file paths
        """
        results = {}
        
        # Fetch the ArXiv page once
        html_content = self._fetch_arxiv_page(category=category)
        if not html_content:
            logger.error("Failed to fetch ArXiv page.")
            return results
        
        # Process each topic
        for topic in topics:
            logger.info(f"Processing topic: {topic}")
            papers = self._parse_paper_data(html_content, topic)
            
            if papers:
                pdf_path = self._create_pdf(papers, topic)
                if pdf_path:
                    results[topic] = pdf_path
        
        return results


def scrape_from_topics_file(topics_file: str = "topics.txt", 
                           output_dir: str = "ArxivPapers") -> List[str]:
    """Scrape papers based on topics from a file.
    
    Args:
        topics_file: Path to a file containing topics (one per line)
        output_dir: Directory to save the generated PDFs
        
    Returns:
        List of generated PDF file paths
    """
    try:
        with open(topics_file, 'r') as f:
            topics = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        logger.error(f"Error reading topics file '{topics_file}': {e}")
        return []
    
    scraper = ArxivScraper(output_dir=output_dir)
    results = scraper.scrape_papers(topics)
    
    return list(results.values()) 