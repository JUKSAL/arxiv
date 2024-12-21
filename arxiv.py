import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter



# Generate a timestamp
timestamp = datetime.now().strftime("%d%m%Y_%H%M")

def fetch_arxiv_papers(*subjects):
    if len(subjects) < 1 or len(subjects) > 5:
        raise ValueError("The number of subjects should be between 1 and 5")

    results = []
    for search_phrase in subjects:
        url = "https://arxiv.org/list/cs/new"  # URL of the arXiv new submissions page
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get the sample styles and create a custom style for the title
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='TitleStyle', fontSize=14, alignment=0, spaceAfter=12, textColor='navy'))
            styles.add(ParagraphStyle(name='LinkStyle', textColor='blue', alignment=0, spaceAfter=12))

            # Find and extract necessary details
            elements = []
            for dt, dd in zip(soup.find_all('dt'), soup.find_all('dd')):
                subjects_element = dd.find('div', class_='list-subjects')
                subjects = subjects_element.get_text(strip=True).replace('Subjects:', '') if subjects_element else "Subjects not found"

                # Check if the subjects contain the search phrase
                if search_phrase.lower() in subjects.lower():
                    title = dd.find('div', class_='list-title').get_text(strip=True).replace('Title:', '')
                    authors = dd.find('div', class_='list-authors').get_text(strip=True).replace('Authors:', '')
                    link = "https://arxiv.org" + dt.find('a', title='Abstract')['href']
                    abstract_element = dd.find('p', class_='mathjax')
                    abstract = abstract_element.get_text(strip=True) if abstract_element else "Abstract not found"

                    # Add the details to the elements list
                    elements.append(Paragraph(title, styles['TitleStyle']))
                    elements.append(Paragraph(authors, styles['Italic']))
                    elements.append(Paragraph(f'<link href="{link}">{link}</link>', styles['LinkStyle']))
                    elements.append(Paragraph(subjects, styles['BodyText']))
                    elements.append(Paragraph(abstract, styles['BodyText']))
                    elements.append(Spacer(1, 12*5))  # Adding a spacer of 5 rows
                        
             
            file_name = f"arxiv_papers_{timestamp}.pdf"

            # Use the file name in SimpleDocTemplate
            pdf = SimpleDocTemplate(file_name, pagesize=letter)
            pdf.build(elements)
            
            print("PDF created successfully!")
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    if results:
        return results
    else:
        
        return []
    
    
# You can test the script with this command:
# fetch_arxiv_papers("Information Retrieval")    