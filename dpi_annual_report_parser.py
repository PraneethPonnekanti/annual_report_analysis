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
    Display the highlighted occurrences of keywords in a beautifully formatted table.
    """
    if highlights:
        # Create a DataFrame from the highlights list
        df = pd.DataFrame(highlights, columns=["keyword", "page_number", "paragraph_number", "paragraph_text"])

        # Group the DataFrame by keyword
        groups = df.groupby("keyword")

        # Display the highlights for each keyword
        for keyword, group in groups:
            st.write(f"Occurrences of '{keyword}' in the annual report:")
            st.dataframe(group[["page_number", "paragraph_number", "paragraph_text"]], width=800, height=400)

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
       # Search button
    st.sidebar.button("Parse PDF")
   # if st.sidebar.button("Search"):
    #    keywords = st.text_input("Enter keywords (separated by commas)")
     #   if keywords:
      #      pages, highlights = process_pdf_file(BytesIO(pdf_data))
       #     display_highlights(highlights)


if __name__ == '__main__':
    main()
