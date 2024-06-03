import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from zenrows import ZenRowsClient
from urllib.parse import urlparse

#zen row client
zen_row_client = ZenRowsClient("25710735fe41553568fc11d0b9963e0accc2debc")

def download_pdf(url, output_folder, filename):
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"Error: {e}")
        return False
    #Finding the DOI link
    soup = BeautifulSoup(response.content, 'html.parser')
    doi_link = soup.find('a', {'class': 'id-link', 'ref': lambda x: x and 'linksrc=article_id_link' in x})

    if doi_link:
        doi_url = doi_link['href']
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
                    "Accept" :"*/*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'DNT': '1',
                    'Upgrade-Insecure-Requests': '1'}
        try:
            response = requests.get(doi_url, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False

        if response.status_code == 200:
            doi_soup = BeautifulSoup(response.content, 'html.parser')
            if "www.ncbi.nlm.nih.gov" in response.url:
                result = ncbi_nlm_nih_gov(doi_soup,output_folder, filename, headers)
                return result
            elif "www.quintessence-publishing.com" in response.url:
                result = quintessence_publishing(doi_soup,output_folder, filename, headers)
                return result
            elif "pubs.rsc.org" in response.url:
                result = pubs_rsc_org(response, doi_soup,output_folder, filename, headers)
                return result
            elif "academic.oup.com" in response.url:
                result = academic_oup_com(response, doi_soup,output_folder, filename, headers)
                return result
            elif "linkinghub.elsevier.com" in response.url:
                url = "https://www.sciencedirect.com/science/article/abs/"
                parsed_url = urlparse(response.url)
                path_segments = parsed_url.path.split('/')
                last_two_segments = '/'.join(path_segments[-2:])
                science_direct_url = url + last_two_segments
                try:
                    response = zen_row_client.get(science_direct_url)
                except Exception as e:
                    print(f"Error: {e}")
                    return False
                doi_soup = BeautifulSoup(response.content, 'html.parser')
                result = science_direct(response, doi_soup,output_folder, filename, headers)
                return result
            elif "link.springer.com" in response.url:
                result = springer_link(response, doi_soup, output_folder, filename, headers)
                return result
            elif "bmcoralhealth.biomedcentral.com" in response.url:
                result = bmcoralhealth_biomedcentral(response, doi_soup, output_folder, filename, headers)
                return result
            elif "medscimonit.com" in response.url:
                result = medscimonit(response, doi_soup, output_folder, filename, headers)
                return result
            elif "www.swissdentaljournal.org" in response.url:
                result = swiss_dental_journal(doi_soup, output_folder, filename, headers)
                return result
            else:
                result = ncbi_nlm_nih_gov(doi_soup,output_folder, filename, headers)
                return result
        else:
            if response.status_code == 403:
                if "onlinelibrary.wiley.com" in response.url:
                    try:
                        response = zen_row_client.get(response.url)
                        doi_soup = BeautifulSoup(response.content, 'html.parser')
                        result = one_library_wiley(doi_soup, output_folder, filename, headers)
                        return result
                    except Exception as e:
                        print(f"Error: {e}")
                        return False
                else:
                    return False
            else:
                return False


def process_csv(csv_file, output_folder):
    df = pd.read_csv(csv_file, delimiter=';')
    total_count = len(df)
    success_count = 0

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for _, row in df.iterrows():
        #pubmed_id = row['PMID']
        pubmed_id = 38750491
        title = row['Title']
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
        filename = f"{pubmed_id}_{title}"
        filename = truncate_filename(filename)
        success = download_pdf(url, output_folder, filename)

        if success:
            success_count += 1
            print(f"Downloaded PDF for PubMed ID: {pubmed_id}")
        else:
            print(f"PDF not available for PubMed ID: {pubmed_id}")

    print(f"\nSummary:")
    print(f"Total publications: {total_count}")
    print(f"PDFs downloaded: {success_count}")
    print(f"PDFs not available: {total_count - success_count}")

def truncate_filename(filename, max_length=60):
    if len(filename) > max_length:
        truncated_filename = filename[:max_length]
        if ' ' in truncated_filename:
            truncated_filename = truncated_filename[:truncated_filename.rfind(' ')]
        return truncated_filename
    else:
        return filename
    
def ncbi_nlm_nih_gov(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('a', class_='int-view')
    if pdf_link:
        pdf_url = 'https://www.ncbi.nlm.nih.gov' + pdf_link['href']
        try:
            pdf_response = requests.get(pdf_url,headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if pdf_response.status_code == 200 and pdf_response.headers['Content-Type'] == 'application/pdf':
            write_result = write_pdf(pdf_response, output_folder, filename)
            if write_result:
                return write_result
            else:
                return False
        else: 
            print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}") 
            return False
    else:
        return False
    
def one_library_wiley(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('a', class_='coolBar__ctrl pdf-download')
    if pdf_link:
        pdf_url = 'https://onlinelibrary.wiley.com' + pdf_link['href']
        try:
            pdf_response = zen_row_client.get(pdf_url)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if pdf_response.status_code == 200:
            new_soup = BeautifulSoup(pdf_response.content, 'html.parser')
            #print("Parsed HTML:", new_soup.prettify())
            new_pdf_link = new_soup.find('a', class_='btn--bordered__light')
            if new_pdf_link:
                new_pdf_link = 'https://onlinelibrary.wiley.com' + new_pdf_link['href']
                try:
                    new_pdf_response = zen_row_client.get(new_pdf_link)
                except Exception as e:
                    print(f"Error: {e}")
                    return False
                write_result = write_pdf(new_pdf_response, output_folder, filename)
                if write_result:
                    return write_result
                else:
                    return False
            else:
                new_pdf_link = new_soup.find('div', class_='accessDenialslot')
                if new_pdf_link:
                    return False
                else:
                    return False
        else:  
            print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
            return False
    else:
        return False

def quintessence_publishing(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('a', {'class': 'u-article-teaser__full-text'})
    if pdf_link:
        pdf_url = 'https://www.quintessence-publishing.com' + pdf_link['href']
        try:
            pdf_response = requests.get(pdf_url, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if pdf_response.status_code == 200:
            write_result = write_pdf(pdf_response, output_folder, filename)
            return write_result
        else:
            print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
            return False
    else:   
        return False 
    
def pubs_rsc_org(response, doi_soup, output_folder, filename,headers):
    new_url = response.url
    parsed_url = urlparse(new_url)
    path = parsed_url.path
    parts = path.split('/')
    desired_parts = parts[4:]  
    result = '/'.join(desired_parts)
    pdf_url = 'https://pubs.rsc.org/en/content/articlepdf/' + result
    try:
        pdf_response = requests.get(pdf_url, headers=headers)
    except Exception as e:
        print(f"Error: {e}")
        return False
    new_url = pdf_response.url
    if new_url.split('/')[-1] == "unauth":
        return False
    if pdf_response.status_code == 200 and pdf_response.headers.get('Content-Type') == 'application/pdf':
        write_result = write_pdf(pdf_response, output_folder, filename)
        if write_result:
            return write_result
        else:
            return False
    else:
        print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
        return False
    
def academic_oup_com(response, doi_soup,output_folder, filename,headers):
    currency_wrap = doi_soup.find_all('div', class_="purchase-currency")
    if currency_wrap:
        return False
    else:
        pdf_link = doi_soup.find('a', class_="get-access get-access-jumplink at-get-access-jumplink js-no-access-jumplink")
        if pdf_link:
            pdf_url = response.url + pdf_link['href']
            if pdf_link['href'] == "#no-access-message":
                return False
            else:
                try:
                    pdf_response = requests.get(pdf_url, headers=headers)
                except Exception as e:
                    print(f"Error: {e}")
                    return False
                if pdf_response.status_code == 200:
                    write_result = write_pdf(pdf_response, output_folder, filename)
                    return write_result
                else:
                    print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
                    return False
        else:   
            return False 
        
def science_direct(response, doi_soup,output_folder, filename,headers):
    access_link = doi_soup.find('li', class_="accessbar-item-hide-from-initial accessbar-item-hide-from-xs accessbar-item-show-from-md PurchasePDF")
    if access_link:
        return False
    else:
        access_link = doi_soup.find('li', class_="ViewPDF")
        if access_link:
            pdf_url = access_link.find('a', class_="link-button accessbar-utility-component accessbar-utility-link link-button-primary link-button-icon-left")
            if pdf_url and "href" in pdf_url.attrs and pdf_url['href'] != "":
                pdf_url = 'https://www.sciencedirect.com/science/' + pdf_url['href']
                try:
                    pdf_response = zen_row_client.get(pdf_url)
                except Exception as e:
                    print(f"Error: {e}")
                    return False
                if pdf_response.status_code == 200:
                    write_result = write_pdf(pdf_response, output_folder, filename)
                    return write_result
                else:
                    print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
                    return False
            else:   
                return False
            
def springer_link(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('a', class_='u-button u-button--full-width u-button--primary u-justify-content-space-between c-pdf-download__link')
    if pdf_link:
        pdf_url = 'link.springer.com/' + pdf_link['href']
        try:
            pdf_response = requests.get(pdf_url, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if pdf_response.status_code == 200:
            write_result = write_pdf(pdf_response, output_folder, filename)
            return write_result
        else:
            print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
            return False
    else:   
        return False

def bmcoralhealth_biomedcentral(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('a', class_='u-button u-button--full-width u-button--primary u-justify-content-space-between c-pdf-download__link')
    if pdf_link:
        pdf_url = pdf_link['href']
        try:
            pdf_response = requests.get(pdf_url, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if pdf_response.status_code == 200:
            write_result = write_pdf(pdf_response, output_folder, filename)
            return write_result
        else:
            print(f"Error: PDF download failed for {filename}. Status code: {pdf_response.status_code}")
            return False
    else:   
        return False 
    
def medscimonit(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('form', {'id': 'form2'})
    if pdf_link:
        pdf_url = pdf_link['action']
        id_jour = pdf_link.find('input', {'name': 'ID_JOUR'})['value']
        id_art = pdf_link.find('input', {'name': 'idArt'})['value']
        base_url = "https://medscimonit.com" 
        full_url = f"{base_url}{pdf_url}"
        payload = {
            'ID_JOUR': id_jour,
            'idArt': id_art
        }
        # Send POST request to download the PDF
        try:
            response_post = requests.post(full_url, data=payload)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if response_post.status_code == 200:
            write_result = write_pdf(response_post, output_folder, filename)
            return write_result
        else:
            print(f"Error: PDF download failed for {filename}. Status code: {response_post.status_code}")
            return False
    else:   
        return False 
    
def swiss_dental_journal(doi_soup,output_folder, filename,headers):
    pdf_link = doi_soup.find('a', class_="obj_galley_link pdf")
    if pdf_link:
        pdf_url = pdf_link['href']
        try:
            new_pdf_response = requests.get(pdf_url, headers=headers)
        except Exception as e:
            print(f"Error: {e}")
            return False
        if new_pdf_response.status_code == 200:
            new_soup = BeautifulSoup(new_pdf_response.content, 'html.parser')
            download = new_soup.find('a', class_="download")
            if download:
                download_url = download['href']
                try:
                    download_url_response = requests.get(download_url, headers=headers)
                except Exception as e:
                    print(f"Error: {e}")
                    return False
                if download_url_response.status_code == 200:
                    write_result = write_pdf(download_url_response, output_folder, filename)
                    return write_result
                else:
                    print(f"Error: PDF download failed for {filename}. Status code: {download_url_response.status_code}")
                    return False
            else:   
                return False
        else: 
            print(f"Error: PDF download failed for {filename}. Status code: {new_pdf_response.status_code}")  
            return False  
    else:   
        return False     
    
def write_pdf(pdf_response, output_folder, filename):
    output_path = os.path.join(output_folder, f"{filename}.pdf")
    with open(output_path, 'wb') as file:
        file.write(pdf_response.content)
    return True

# Load the CSV file and process each row
csv_file = 'csv-halitosis-set (2).csv'
output_folder = 'downloaded_pdfs'
processor_result = process_csv(csv_file, output_folder)