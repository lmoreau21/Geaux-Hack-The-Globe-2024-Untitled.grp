import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

def download_pdfs(url, folder_path):
    # Ensure the folder exists
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path, exist_ok=True)

    # Fetch the content of the page
    response = requests.get(url, verify=False)
    # Make sure the request was successful
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <a> tags with href ending in ".pdf"
    pdf_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]

    for link in pdf_links:
        # Extract filename and create local path
        filename = os.path.join(folder_path, link.split('/')[-1])
        print(f"Downloading {filename}...")

        # Download PDF
        with requests.get(link, stream=True, verify=False) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    print("Download completed.")

# URL to scrape
url = 'https://ldh.la.gov/page/medicaid-eligibility-manual'

# Folder to save PDFs
folder_path = r'C:\Users\lmore\OneDrive\Documents\GitHub\Geaux-Hack-The-Globed-2024-Untitled.grp\backend\backend\la_medicaid'

download_pdfs(url, folder_path)
