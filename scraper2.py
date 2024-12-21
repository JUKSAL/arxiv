# Import cleanup
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

# Generate a timestamp
timestamp = datetime.now().strftime("%d%m%Y_%H%M")

def fetch_arxiv_papers(*subjects):
    if not (1 <= len(subjects) <= 5):
        raise ValueError("The number of subjects should be between 1 and 5")

    try:
        url = "https://arxiv.org/list/cs/new"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Failed to retrieve the page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleStyle', fontSize=14, alignment=0, spaceAfter=12, textColor='navy'))
    styles.add(ParagraphStyle(name='LinkStyle', textColor='blue', alignment=0, spaceAfter=12))

    elements = []
    for search_phrase in subjects:
        for dt, dd in zip(soup.find_all('dt'), soup.find_all('dd')):
            subjects_element = dd.find('div', class_='list-subjects')
            subjects_text = subjects_element.get_text(strip=True).replace('Subjects:', '') if subjects_element else "Subjects not found"
            
            if search_phrase.lower() in subjects_text.lower():
                title = dd.find('div', class_='list-title').get_text(strip=True).replace('Title:', '')
                authors = dd.find('div', class_='list-authors').get_text(strip=True).replace('Authors:', '')
                link = "https://arxiv.org" + dt.find('a', title='Abstract')['href']
                abstract_element = dd.find('p', class_='mathjax')
                abstract = abstract_element.get_text(strip=True) if abstract_element else "Abstract not found"

                elements.extend([
                    Paragraph(title, styles['TitleStyle']),
                    Paragraph(authors, styles['BodyText']),
                    Paragraph(f'<link href="{link}">{link}</link>', styles['LinkStyle']),
                    Paragraph(subjects_text, styles['BodyText']),
                    Paragraph(abstract, styles['BodyText']),
                    Spacer(1, 12 * 5)
                ])

    if elements:
        file_name = f"arxiv_papers_{timestamp}.pdf"
        pdf = SimpleDocTemplate(file_name, pagesize=letter)
        pdf.build(elements)
        print("PDF created successfully!")
    else:
        print("No matching papers found.")

def main():
    print("Welcome to the ArXiv Paper Fetcher!")
    print("You can search for up to 5 subjects.")
    
    subjects = input("Enter the subjects separated by commas (e.g., 'Machine Learning, AI, Robotics'): ").split(',')
    subjects = [subject.strip() for subject in subjects if subject.strip()]  # Clean up input
    
    if len(subjects) == 0:
        print("No subjects entered. Exiting.")
        return
    
    try:
        fetch_arxiv_papers(*subjects)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()