import requests
from io import BytesIO
import streamlit as st
from PyPDF4 import PdfFileReader
import re


def process_pdf_file(pdf_file):
    """
    Process the PDF file and return the pages and highlighted occurrences of keywords.
    """
    pdf_reader = PdfFileReader(pdf_file)
    num_pages = pdf_reader.getNumPages()
    pages = []
    for i in range(num_pages):
        page = pdf_reader.getPage(i)
        text = page.extractText()
        pages.append(text)

    # Highlight the occurrences of the keywords
    keywords = st.sidebar.text_input("Enter keywords (separated by commas)")
    highlights = {}
    if keywords:
        keywords_list = keywords.split(",")
        for keyword in keywords_list:
            occurrences = []
            for i, page in enumerate(pages):
                # Find all paragraphs that contain the keyword
                paragraphs = page.split("\n\n")
                for j, paragraph in enumerate(paragraphs):
                    if re.search(r"\b{}\b".format(keyword), paragraph, re.IGNORECASE):
                        occurrences.append((i + 1, j + 1, paragraph))

            highlights[keyword] = occurrences

    return pages, highlights


def display_highlights(highlights):
    """
    Display the highlighted occurrences of keywords in a formatted table.
    """
    for keyword, occurrences in highlights.items():
        st.write(f"Occurrences of '{keyword}' in the annual report:")
        table_data = []
        for occurrence in occurrences:
            table_data.append([occurrence[0], occurrence[1], occurrence[2]])
        st.table(table_data)


def paginate_report(pages):
    """
    Paginate the annual report.
    """
    page_num = st.slider("Page", min_value=1, max_value=len(pages))
    st.write(pages[page_num - 1])


def main():
    st.set_page_config(page_title="Annual Report Parser", layout="wide")

    # Create a sidebar for inputs
    st.sidebar.title("Annual Report Parser")
    file_option = st.sidebar.radio("Choose file upload option", ("Upload a file", "Use a URL"))

    if file_option == "Upload a file":
        # File uploader
        uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            pages, highlights = process_pdf_file(uploaded_file)
            display_highlights(highlights)
            paginate_report(pages)

    else:
        # URL input
        pdf_url = st.sidebar.text_input("Enter PDF URL")
        if pdf_url:
            # Download the PDF file from the URL
            response = requests.get(pdf_url)
            if response.status_code == 200:
                pdf_data = response.content
                pdf_file = BytesIO(pdf_data)

                # Process the annual report file
                pages, highlights = process_pdf_file(pdf_file)
                display_highlights(highlights)
                paginate_report(pages)
            else:
                st.sidebar.error("Error downloading PDF file from URL.")

    # Add a search button
    st.sidebar.button("Search")


if __name__ == '__main__':
    main()
