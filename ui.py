import streamlit as st

st.title("Scrapper + AI Summarizer")

#Actual frontend
url_field = st.text_input("Enter the URL")

if st.button("Scrape and Summarize"):
    st.write(f"Scraping and summarizing content from")