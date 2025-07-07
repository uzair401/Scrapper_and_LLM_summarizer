import streamlit as st
import requests
import json
from scrapper import site_scrapper, extract_body_content, clean_body_content
from configuration import FASTAPI_URL

st.set_page_config(page_title="AI Web Scraper", layout="wide")
st.title("AI Web Scraper by Uzair")

if 'scraped_result' not in st.session_state:
    st.session_state.scraped_result = None

if 'show_scraped' not in st.session_state:
    st.session_state.show_scraped = False

url = st.text_input("Enter Website URL")
prompt = st.text_area("What do you want to know about this website?")

if st.button("Scrape and Analyze"):
    if url and prompt:
        try:
            html = site_scrapper(url)
            body = extract_body_content(html)
            cleaned = clean_body_content(body)

            response = requests.post(f"{FASTAPI_URL}/ask", json={"prompt": prompt, "data": cleaned})
            response.raise_for_status()
            result_json = response.json()
            cleaned_response = result_json.get("response", "No response field found.")

            # Show AI analysis as markdown
            st.markdown("### AI Analysis")
            st.markdown(cleaned_response)

            # Save scraped data in session
            st.session_state.scraped_result = {
                'url': url,
                'prompt': prompt,
                'analysis': cleaned_response,
                'scraped_content': cleaned
            }
            st.session_state.show_scraped = False

        except Exception as e:
            st.error(f"Scraping failed: {e}")
    else:
        st.warning("Please enter both URL and prompt")

# Show 'Show Scraped Content' button if result exists
if st.session_state.scraped_result:
    if st.button("Show Scraped Content"):
        st.session_state.show_scraped = not st.session_state.show_scraped

    if st.session_state.show_scraped:
        st.markdown("### Scraped Content")
        st.text_area("", st.session_state.scraped_result['scraped_content'], height=300)
