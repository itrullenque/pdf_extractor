import pandas as pd
import os

output_folder = "downloaded_pdfs_pubmed"
list_downloaded_files = []
for file in os.listdir(output_folder):
    file_pmid = int(file.split("_")[0])
    list_downloaded_files.append(file_pmid)

df = pd.DataFrame(list_downloaded_files, columns=["PMID"])

excel_output_path = os.path.join(output_folder, "downloaded_files.xlsx")
df.to_excel(excel_output_path, index=False)
