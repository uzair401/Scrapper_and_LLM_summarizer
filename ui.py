import streamlit as st
from scrapper import site_scrapper
st.title("Scrapper + AI Summarizer")

#Actual frontend
url_field = st.text_input("Enter the URL")

if st.button("Scrape and Summarize"):
    st.write(f"Scraping and summarizing content from")
    result = site_scrapper(url_field)
    print(result)