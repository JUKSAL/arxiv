"""Module for generating summaries of ArXiv papers."""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import re
import PyPDF2
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Optional OpenAI integration for advanced summaries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class ArxivSummarizer:
    """Class for generating summaries of ArXiv papers."""
    
    def __init__(self, input_dir: str = "ArxivPapers", 
                output_dir: str = "ArxivSummaries",
                openai_api_key: Optional[str] = None):
        """Initialize the ArXiv summarizer.
        
        Args:
            input_dir: Directory containing PDF papers to summarize
            output_dir: Directory to save the summaries
            openai_api_key: Optional OpenAI API key for enhanced summaries
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.openai_api_key = openai_api_key
        
        self._ensure_output_dir()
        self._setup_styles()
        
        # Initialize OpenAI if API key is provided
        if openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = openai_api_key
    
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _setup_styles(self) -> None:
        """Set up PDF styles for summary documents."""
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='TitleStyle', fontSize=14, 
                                      alignment=0, spaceAfter=12, textColor='navy'))
        self.styles.add(ParagraphStyle(name='SectionTitle', fontSize=12, 
                                      alignment=0, spaceAfter=6, textColor='black'))
        self.styles.add(ParagraphStyle(name='LinkStyle', textColor='blue', 
                                      alignment=0, spaceAfter=12))
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def _parse_papers_from_pdf(self, pdf_path: str) -> List[Dict[str, str]]:
        """Parse multiple papers from a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of papers with title, authors, abstract, etc.
        """
        text = self._extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        papers = []
        
        # Extract paper information
        # This is a simple heuristic based on the structure of ArXiv papers PDFs
        # Fine-tune this for better accuracy
        
        # First identify title blocks
        title_pattern = r"(?:^|\n)(.+?)\n(.*?Authors:.*?)(?:https://arxiv\.org\S+)\n(.*?Subjects:.*?)\n(.*?)(?:\n\n|\Z)"
        matches = re.findall(title_pattern, text, re.DOTALL)
        
        for match in matches:
            title = match[0].strip()
            authors = match[1].strip().replace("Authors:", "").strip()
            subjects = match[2].strip().replace("Subjects:", "").strip()
            abstract = match[3].strip() if len(match) > 3 else "Abstract not found"
            
            # Extract ArXiv link if present
            link_match = re.search(r"(https://arxiv\.org\S+)", match[1] + match[2])
            link = link_match.group(1) if link_match else None
            
            # Extract paper ID from the link
            paper_id = link.split('/')[-1] if link and 'arxiv.org/abs/' in link else None
            
            papers.append({
                'title': title,
                'authors': authors,
                'subjects': subjects,
                'abstract': abstract,
                'link': link,
                'paper_id': paper_id
            })
        
        return papers
    
    def _generate_simple_summary(self, paper: Dict[str, str]) -> str:
        """Generate a simple summary of a paper.
        
        Args:
            paper: Paper data including title, authors, abstract, etc.
            
        Returns:
            Summary text
        """
        abstract = paper.get('abstract', '')
        
        # Extract first few sentences for a simple summary
        sentences = abstract.split('. ')
        summary = '. '.join(sentences[:3]) + ('.' if not abstract.endswith('.') else '')
        
        return summary
    
    def _generate_ai_summary(self, paper: Dict[str, str]) -> str:
        """Generate an AI-enhanced summary of a paper using OpenAI.
        
        Args:
            paper: Paper data including title, authors, abstract, etc.
            
        Returns:
            AI-generated summary text
        """
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return self._generate_simple_summary(paper)
        
        try:
            # Prepare prompt for OpenAI
            prompt = f"""
            Title: {paper.get('title', 'Unknown')}
            Authors: {paper.get('authors', 'Unknown')}
            Subjects: {paper.get('subjects', 'Unknown')}
            Abstract: {paper.get('abstract', 'No abstract available')}
            
            Please provide a 3-4 sentence summary of this research paper, highlighting the main problem addressed, methodology used, and key findings.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a scientific paper summarizer. Create concise, accurate summaries of research papers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return self._generate_simple_summary(paper)
    
    def _create_summary_pdf(self, papers: List[Dict[str, str]], 
                          topic: str, use_ai: bool = False) -> str:
        """Create a PDF with summaries of multiple papers.
        
        Args:
            papers: List of paper dictionaries
            topic: Topic name for the file name
            use_ai: Whether to use AI for generating summaries
            
        Returns:
            Path to the generated PDF file
        """
        if not papers:
            logger.warning(f"No papers to summarize for topic: {topic}")
            return ""
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%d%m%Y_%H%M")
        
        # Create file name for the summary PDF
        file_name = f"arxiv_summary_{timestamp}_{topic.replace(' ', '_')}.pdf"
        file_path = os.path.join(self.output_dir, file_name)
        
        elements = []
        
        # Add title page
        elements.append(Paragraph(f"ArXiv Papers Summary: {topic}", self.styles['Title']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                                 self.styles['Normal']))
        elements.append(Paragraph(f"Contains summaries of {len(papers)} papers", 
                                 self.styles['Normal']))
        elements.append(Spacer(1, 12 * 5))
        
        # Process each paper
        for paper in papers:
            title = paper.get('title', 'Unknown Title')
            authors = paper.get('authors', 'Unknown Authors')
            link = paper.get('link', '')
            
            # Generate summary
            if use_ai:
                summary = self._generate_ai_summary(paper)
            else:
                summary = self._generate_simple_summary(paper)
            
            # Add to PDF
            elements.append(Paragraph(title, self.styles['TitleStyle']))
            elements.append(Paragraph(authors, self.styles['Italic']))
            if link:
                elements.append(Paragraph(f"<link href='{link}'>{link}</link>", 
                                         self.styles['LinkStyle']))
            
            elements.append(Paragraph("Summary:", self.styles['SectionTitle']))
            elements.append(Paragraph(summary, self.styles['BodyText']))
            elements.append(Spacer(1, 12 * 3))
        
        try:
            # Create the PDF
            pdf = SimpleDocTemplate(file_path, pagesize=letter)
            pdf.build(elements)
            logger.info(f"Summary PDF created successfully: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error creating summary PDF for topic '{topic}': {e}")
            return ""
    
    def summarize_papers(self, pdf_path: str, use_ai: bool = False) -> str:
        """Summarize papers from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file containing papers
            use_ai: Whether to use AI for generating summaries
            
        Returns:
            Path to the generated summary PDF
        """
        # Extract topic from filename
        file_name = os.path.basename(pdf_path)
        topic_match = re.search(r'arxiv_papers_\d+_(.+)\.pdf', file_name)
        topic = topic_match.group(1).replace('_', ' ') if topic_match else "Unknown"
        
        # Parse papers from PDF
        papers = self._parse_papers_from_pdf(pdf_path)
        
        # Create summary PDF
        return self._create_summary_pdf(papers, topic, use_ai)
    
    def summarize_latest_papers(self, use_ai: bool = False) -> List[str]:
        """Summarize the latest papers for each topic.
        
        Args:
            use_ai: Whether to use AI for generating summaries
            
        Returns:
            List of paths to generated summary PDFs
        """
        summary_files = []
        
        # Get all PDF files in the input directory
        pdf_files = []
        for file in os.listdir(self.input_dir):
            if file.endswith('.pdf') and 'arxiv_papers_' in file:
                pdf_files.append(os.path.join(self.input_dir, file))
        
        # Group PDF files by topic
        topics = {}
        for pdf_file in pdf_files:
            # Extract topic from filename
            file_name = os.path.basename(pdf_file)
            topic_match = re.search(r'arxiv_papers_(\d+)_(.+)\.pdf', file_name)
            
            if topic_match:
                date_str = topic_match.group(1)
                topic = topic_match.group(2).replace('_', ' ')
                
                if topic not in topics:
                    topics[topic] = []
                
                topics[topic].append((date_str, pdf_file))
        
        # Get the latest PDF for each topic
        for topic, files in topics.items():
            # Sort by date (most recent first)
            files.sort(reverse=True)
            latest_file = files[0][1]
            
            # Generate summary
            summary_file = self.summarize_papers(latest_file, use_ai)
            if summary_file:
                summary_files.append(summary_file)
        
        return summary_files


def summarize_latest_papers(input_dir: str = "ArxivPapers", 
                          output_dir: str = "ArxivSummaries",
                          use_ai: bool = False,
                          openai_api_key: Optional[str] = None) -> List[str]:
    """Summarize the latest papers for each topic.
    
    Args:
        input_dir: Directory containing PDF papers to summarize
        output_dir: Directory to save the summaries
        use_ai: Whether to use AI for generating summaries
        openai_api_key: Optional OpenAI API key for enhanced summaries
        
    Returns:
        List of paths to generated summary PDFs
    """
    summarizer = ArxivSummarizer(input_dir=input_dir, 
                                output_dir=output_dir,
                                openai_api_key=openai_api_key)
    
    return summarizer.summarize_latest_papers(use_ai=use_ai) 