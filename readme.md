# PDF Downloader

This Python script downloads PDF files from various scientific journal websites based on the information provided in a CSV file. The script utilizes the `requests` library to send HTTP requests, `BeautifulSoup` for parsing HTML content, `pandas` for reading the CSV file, and `ZenRows` for handling certain website requests.

## Supported Scientific Journals

The script supports downloading PDF files from the following scientific journals:

- NCBI NLM NIH (https://www.ncbi.nlm.nih.gov/)
- Wiley Online Library (https://onlinelibrary.wiley.com/)
- Quintessence Publishing (https://www.quintessence-publishing.com/)
- Royal Society of Chemistry (https://pubs.rsc.org/)
- Oxford Academic (https://academic.oup.com/)
- ScienceDirect (https://www.sciencedirect.com/)
- Springer Link (https://link.springer.com/)
- BMC Oral Health (https://bmcoralhealth.biomedcentral.com/)
- Medical Science Monitor (https://medscimonit.com/)
- Swiss Dental Journal (https://www.swissdentaljournal.org/)

## Prerequisites

Before running the script, make sure you have the following dependencies installed:

- Python 3.x
- `requests` library
- `beautifulsoup4` library
- `pandas` library
- `zenrows` library

You can install the required libraries using pip.

## Configuration

1. Obtain a ZenRows API key by signing up at [ZenRows](https://www.zenrows.com/) and replace the placeholder API key in the script with your actual API key:

```python
zen_row_client = ZenRowsClient("25710735fe41553568fc11d0b9963e0accc2debc") - you can use the default one that is already hardcoded.

2. Prepare a CSV file containing the necessary information for downloading the PDF files. The CSV file should have the following columns:

PMID: PubMed ID of the publication
Title: Title of the publication

Example CSV file (csv-halitosis-set (2).csv).

3. Usage

Place the CSV file in the same directory as the main.py script.
Open a terminal or command prompt and navigate to the directory containing the script.
Run the script using the following command: python main.py

The script will process each row in the CSV file and attempt to download the corresponding PDF file from the respective journal website.
The downloaded PDF files will be saved in the downloaded_pdfs directory, which will be created if it doesn't exist.
After the script finishes executing, it will display a summary of the total publications processed, the number of PDFs downloaded successfully, and the number of PDFs that were not available for download.

Limitations

The script relies on the structure and layout of the supported journal websites as of the date of development. If the websites undergo significant changes, the script may need to be updated accordingly.
Some journal websites may require additional authentication or have access restrictions that prevent the script from downloading the PDF files.
The script assumes that the CSV file follows the specified format and contains the necessary information for each publication.
```
