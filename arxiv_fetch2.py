import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
import xml.sax.saxutils as saxutils

# Generate a timestamp
timestamp = datetime.now().strftime("%d%m%Y_%H%M")

def fetch_arxiv_papers(*subjects):
    # Validate number of subjects
    if len(subjects) < 1 or len(subjects) > 5:
        raise ValueError("The number of subjects should be between 1 and 5")

    results = []
    for search_phrase in subjects:
        url = "https://arxiv.org/list/cs/new"  # URL for the arXiv new submissions page

        # Request the page with exception handling
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Will raise HTTPError for bad responses (e.g., 404, 500)
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving data for '{search_phrase}': {e}")
            continue  # Skip to the next subject

        # Parse the page content
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error parsing HTML for '{search_phrase}': {e}")
            continue

        # Setup ReportLab styles with exception handling
        try:
            styles = getSampleStyleSheet()
            # Create 'Italic' style if not already defined
            if 'Italic' not in styles:
                styles.add(ParagraphStyle(name='Italic', parent=styles['Normal'], fontName='Helvetica-Oblique'))
            styles.add(ParagraphStyle(name='TitleStyle', fontSize=14, alignment=0, spaceAfter=12, textColor='navy'))
            styles.add(ParagraphStyle(name='LinkStyle', textColor='blue', alignment=0, spaceAfter=12))
        except Exception as e:
            print(f"Error setting up styles for '{search_phrase}': {e}")
            continue

        elements = []
        try:
            # Process each paper (assuming a one-to-one mapping between dt and dd tags)
            for dt, dd in zip(soup.find_all('dt'), soup.find_all('dd')):
                subjects_element = dd.find('div', class_='list-subjects')
                # Use a different variable name to avoid shadowing the function argument
                subjects_text = (subjects_element.get_text(strip=True).replace('Subjects:', '')
                                 if subjects_element else "Subjects not found")

                # Only process if the paper's subjects match the search phrase
                if search_phrase.lower() in subjects_text.lower():
                    # Extract title
                    title_element = dd.find('div', class_='list-title')
                    title = (title_element.get_text(strip=True).replace('Title:', '')
                             if title_element else "Title not found")

                    # Extract authors
                    authors_element = dd.find('div', class_='list-authors')
                    authors = (authors_element.get_text(strip=True).replace('Authors:', '')
                               if authors_element else "Authors not found")

                    # Extract abstract link
                    link_tag = dt.find('a', title='Abstract')
                    link = ("https://arxiv.org" + link_tag['href']
                            if link_tag and link_tag.has_attr('href') else "Link not found")

                    # Extract abstract
                    abstract_element = dd.find('p', class_='mathjax')
                    abstract = (abstract_element.get_text(strip=True)
                                if abstract_element else "Abstract not found")

                    # Escape text to avoid issues with ReportLab's markup parser
                    title_safe = saxutils.escape(title)
                    authors_safe = saxutils.escape(authors)
                    subjects_safe = saxutils.escape(subjects_text)
                    abstract_safe = saxutils.escape(abstract)

                    # Append the details to the elements list
                    elements.append(Paragraph(title_safe, styles['TitleStyle']))
                    elements.append(Paragraph(authors_safe, styles['Italic']))
                    elements.append(Paragraph(f'<link href="{link}">{link}</link>', styles['LinkStyle']))
                    elements.append(Paragraph(subjects_safe, styles['BodyText']))
                    elements.append(Paragraph(abstract_safe, styles['BodyText']))
                    elements.append(Spacer(1, 12 * 5))
        except Exception as e:
            print(f"Error processing HTML elements for '{search_phrase}': {e}")
            continue

        # Define the output PDF filename (adding the search phrase to avoid collisions)
        file_name = f"arxiv_papers_{timestamp}_{search_phrase.replace(' ', '_')}.pdf"

        # Build the PDF with exception handling
        try:
            pdf = SimpleDocTemplate(file_name, pagesize=letter)
            pdf.build(elements)
            print(f"PDF created successfully: {file_name}")
        except Exception as e:
            print(f"Error creating PDF for '{search_phrase}': {e}")
            continue

    return results

# Test the script


topics =["Information retrieval",
"Computation and Language",
"Machine Learning",
"Information Theory",
"Artificial Intelligence",
"Neurons and Cognition",
"Neural and Evolutionary Computing",
"Data Structures and Algorithms"]


for x in topics:
    fetch_arxiv_papers(x)