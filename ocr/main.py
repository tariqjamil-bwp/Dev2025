# main.py

import streamlit as st
from ocr_tool import ocr_from_file, ocr_from_url

def main():
    st.title("OCR Application with Mistral AI")
    st.write("Upload a PDF/image file or provide a URL to extract text.")

    # Option to upload a file
    uploaded_file = st.file_uploader("Choose a PDF or image file", type=["pdf", "png", "jpg", "jpeg"])

    # Option to input a URL
    url = st.text_input("Or enter a URL")

    if st.button("Process"):
        if uploaded_file:
            with st.spinner("Processing file..."):
                try:
                    result = ocr_from_file(uploaded_file)
                    st.markdown(result)
                except Exception as e:
                    st.error(f"An error occurred while processing the file: {e}")
        elif url:
            with st.spinner("Processing URL..."):
                try:
                    result = ocr_from_url(url)
                    st.markdown(result)
                except Exception as e:
                    st.error(f"An error occurred while processing the URL: {e}")
        else:
            st.error("Please upload a file or enter a URL.")

if __name__ == "__main__":
    main()
