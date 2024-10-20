import os
import re
import time

# from zenrows import ZenRowsClient
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


def download_pdf(url, output_folder, filename):
    try:
        response = session.get(url)
    except Exception as e:
        print(f"Error: {e}")
        return False
    # Finding the DOI link
    soup = BeautifulSoup(response.content, "html.parser")
    doi_link = soup.find(
        "a", {"class": "id-link", "ref": lambda x: x and "linksrc=article_id_link" in x}
    )

    if doi_link:
        doi_url = doi_link["href"]
        doi_url = doi_url.replace("doi.org", "sci-hub.ru")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }
        try:
            response = session.get(doi_url, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False

        if response.status_code == 200:
            doi_soup = BeautifulSoup(response.content, "html.parser")
            if "article not found" in response.text:
                return False
            else:
                pdf_embed = doi_soup.find("embed", id="pdf")
                if pdf_embed and "src" in pdf_embed.attrs:
                    pdf_url = pdf_embed["src"]
                    if pdf_url.startswith("//"):
                        pdf_url = "https:" + pdf_url
                    try:
                        pdf_response = session.get(pdf_url, headers=headers)
                        if pdf_response.status_code == 200:
                            pdf_path = os.path.join(output_folder, f"{filename}.pdf")
                            with open(pdf_path, "wb") as f:
                                f.write(pdf_response.content)
                            return True
                        else:
                            print(
                                f"Failed to download PDF. Status code: {pdf_response.status_code}"
                            )
                            return False
                    except Exception as e:
                        print(f"Error: {e}")
                        return False
                else:
                    print("PDF embed not found in the page")
                    return False
        else:
            print("DOI link not found")
            return False


def process_csv(csv_file, output_folder, list_downloaded_files, start=1):
    df = pd.read_csv(csv_file, delimiter=",", encoding="utf-8")
    total_count = len(df)
    success_count = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(df.columns)

    couter = 0
    for _, row in df.iterrows():
        couter += 1
        if couter < start:
            continue
        pubmed_id = row["PMID"]
        if pubmed_id in list_downloaded_files:
            continue
        title = row["Title"]
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
        filename = f"{pubmed_id}_{title}"
        filename = truncate_filename(filename)
        success = download_pdf(url, output_folder, filename)

        if success:
            success_count += 1
            print(
                f"Downloaded PDF for PubMed ID: {pubmed_id} , from {couter}/{total_count}"
            )
        else:
            print(
                f"PDF not available for PubMed ID: {pubmed_id}, from {couter}/{total_count}"
            )

    print(f"\nSummary:")
    print(f"Total publications: {total_count}")
    print(f"PDFs downloaded: {success_count}")
    print(f"PDFs not available: {total_count - success_count}")


def truncate_filename(filename, max_length=100):
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)
    if len(filename) > max_length:
        truncated_filename = filename[:max_length]
        if " " in truncated_filename:
            truncated_filename = truncated_filename[: truncated_filename.rfind(" ")]
        return truncated_filename
    else:
        return filename


# Load the CSV file and process each row
csv_file = "SearchV006_5876.csv"
output_folder = "papers_malodour_scihub"
list_downloaded_files = []
for file in os.listdir(output_folder):
    file_pmid = int(file.split("_")[0])
    list_downloaded_files.append(file_pmid)

processor_result = process_csv(csv_file, output_folder, list_downloaded_files)
