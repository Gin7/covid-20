"""
This script downloads and converts the confirmed cases PDF data into a CSV file.
"""

import csv

import PyPDF2
import requests
from bs4 import BeautifulSoup

FIX_STRINGS = [
    ["CIUDAD DE\n \nMÉXICO", "CIUDAD DE MÉXICO"],
    ["CIUDAD\n \nDE MÉXICO", "CIUDAD DE MÉXICO"],
    ["Estados\n \nUnidos", "Estados Unidos"]
]

URL = "https://www.gob.mx/salud/documentos/coronavirus-covid-19-comunicado-tecnico-diario-238449"


def main():
    """Calls our other functions."""

    download_pdf()
    extract_pdf()


def download_pdf():
    """Locates and downloads the PDF file."""

    # Load the documents directory website and parse it with BeautifulSoup.
    with requests.get(URL) as response:

        soup = BeautifulSoup(response.text, "html.parser")

        # Iterate over all the anchor tags.
        for link in soup.find_all("a"):

            # Once we find the one we are interested in, we download it and break the loop.
            if "casos_positivos" in link["href"]:
                print("Downloading PDF file...")

                with requests.get("https://www.gob.mx" + link["href"]) as pdf_response:

                    with open("./casos_confirmados.pdf", "wb") as pdf_file:
                        pdf_file.write(pdf_response.content)
                        print("PDF file downloaded.")

                break


def extract_pdf():
    """Extracts and cleans the data from the recently downloaded PDF file.

    It then saves it into a CSV file.
    """

    # Initialize the PDF reader.
    reader = PyPDF2.PdfFileReader(open("./casos_confirmados.pdf", "rb"))

    # Initialize our data list with a header row (8 columns).
    data_list = [["numero_caso", "estado", "sexo", "edad",
                  "fecha_inicio_sintomas", "estatus", "procedencia", "fecha_llegada_mexico"]]

    # Iterate over each page.
    for i in range(reader.numPages):
        print("Processing page:", i+1, "of", reader.numPages)

        # Extract the raw text.
        page_data = reader.getPage(i).extractText()

        # Fix some small inconsistencies with the text.
        for fixer in FIX_STRINGS:
            page_data = page_data.replace(fixer[0], fixer[1])

        # Split the text into chunks and remove empty ones.
        page_data = [item.replace("\n", "")
                     for item in page_data.split("\n ") if item != " "]

        # Only on the first page the starting chunk is the 10th one.
        if i == 0:
            start_index = 9
        else:
            start_index = 0

        # Iterate over our chunks, 8 at a time (8 columns).
        for j in range(start_index, len(page_data), 8):

            # Create a list with the current chunk plus the next seven.
            temp_list = page_data[j:j+8]

            # Add the previous list to the data list if it's not empty.
            if len(temp_list) == 8 and temp_list[0] != "":
                data_list.append(temp_list)

    # Finally, save the data list to CSV.
    with open("casos_confirmados.csv", "w", encoding="utf-8", newline="") as csv_file:
        csv.writer(csv_file).writerows(data_list)
        print("PDF converted.")


if __name__ == "__main__":

    main()
""
