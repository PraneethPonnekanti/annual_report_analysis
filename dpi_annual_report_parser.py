import requests
from io import BytesIO
import streamlit as st
from PyPDF2 import PdfFileReader
import re

def process_pdf_file(pdf_file):
    """
    Process the PDF file and return the pages and highlighted occurrences of keywords.
    """
    num_pages = pdf_file.getNumPages()
    pages = []
    for i in range(num_pages):
        page = pdf_file.getPage(i)
        text = page.extractText()
        pages.append(text)

    # Highlight the occurrences of the keywords
    keywords = st.text_input("Enter keywords (separated by commas)")
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
                        occurrences.append((i+1, j+1, paragraph))

            highlights[keyword] = occurrences

    return pages, highlights


def main():
    st.title("Annual Report Parser")

    # File upload option
    file_option = st.radio("Choose file upload option", ("Upload a file", "Use a URL"))

    if file_option == "Upload a file":
        # File uploader
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            pdf_file = PdfFileReader(uploaded_file)
            pages, highlights = process_pdf_file(pdf_file)

            # Display the highlighted occurrences of keywords
            for keyword, occurrences in highlights.items():
                st.write(f"Occurrences of '{keyword}' in the annual report:")
                for occurrence in occurrences:
                    st.write(f"Page {occurrence[0]}")
                    st.write(occurrence[2], unsafe_allow_html=True)

            # Paginate the annual report
            page_num = st.slider("Page", min_value=1, max_value=len(pages))
            st.write(pages[page_num-1])

    else:
        # URL input
        pdf_url = st.text_input("Enter PDF URL")
        if pdf_url:
            # Download the PDF file from the URL
            response = requests.get(pdf_url)
            if response.status_code == 200:
                pdf_data = response.content
                pdf_file = PdfFileReader(BytesIO(pdf_data))

                # Process the annual report file
                pages, highlights = process_pdf_file(pdf_file)

                # Display the highlighted occurrences of keywords
                for keyword, occurrences in highlights.items():
                    st.write(f"Occurrences of '{keyword}' in the annual report:")
                    for occurrence in occurrences:
                        st.write(f"Page {occurrence[0]}")
                        st.write(occurrence[2], unsafe_allow_html=True)

                # Paginate the annual report
                page_num = st.slider("Page", min_value=1, max_value=len(pages))
                st.write(pages[page_num-1])
            else:
                st.error("Error downloading PDF file from URL.")


if __name__ == '__main__':
    main()
