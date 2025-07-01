import streamlit as st
import requests
from scrapper import site_scrapper, extract_body_content, clean_body_content
from linkedin import initialize_linkedin_auth, handle_linkedin_callback, post_to_linkedin
from configuration import FASTAPI_URL

st.set_page_config(page_title="AI Web Scraper with LinkedIn", layout="wide")
st.title("AI Web Scraper by Uzair")

handle_linkedin_callback()

if 'scraped_result' not in st.session_state:
    st.session_state.scraped_result = None

col1, col2 = st.columns([2,1])

with col1:
    url = st.text_input("Enter Website URL")
    prompt = st.text_area("What do you want to know about this website?")

with col2:
    st.subheader("LinkedIn Integration")
    if 'linkedin_access_token' in st.session_state:
        profile = st.session_state.get('linkedin_profile', {})
        name = f"{profile.get('localizedFirstName','')} {profile.get('localizedLastName','')}"
        st.success(f"Connected as {name}")
        if st.button("Disconnect LinkedIn"):
            for key in ['linkedin_access_token', 'linkedin_profile', 'linkedin_person_urn']:
                st.session_state.pop(key, None)
            st.rerun()
    else:
        if st.button("Connect to LinkedIn"):
            auth = initialize_linkedin_auth()
            redirect_url = auth.get_authorization_url()
            st.markdown(f"""
                <meta http-equiv="refresh" content="0; url={redirect_url}">
                <p>Redirecting to LinkedIn...</p>
            """, unsafe_allow_html=True)


if st.button("Scrape and Analyze"):
    if url and prompt:
        try:
            html = site_scrapper(url)
            body = extract_body_content(html)
            cleaned = clean_body_content(body)
            st.text_area("Scraped Content", cleaned, height=300)
            response = requests.post(f"{FASTAPI_URL}/ask", json={"prompt": prompt, "data": cleaned})
            response.raise_for_status()
            analysis = response.json().get("response", "")
            st.session_state.scraped_result = {'url': url, 'prompt': prompt, 'analysis': analysis}
            st.write("**Analysis Result:**")
            st.write(analysis)
        except Exception as e:
            st.error(f"Scraping failed: {e}")
    else:
        st.warning("Please enter both URL and prompt")

if st.session_state.scraped_result and 'linkedin_access_token' in st.session_state:
    st.subheader("Share to LinkedIn")
    post_content = f"""🔍 Just analyzed a website!

URL: {st.session_state.scraped_result['url']}
Prompt: {st.session_state.scraped_result['prompt']}

Insights:
{st.session_state.scraped_result['analysis'][:500]}{'...' if len(st.session_state.scraped_result['analysis']) > 500 else ''}

#AI #Scraping #LinkedIn
"""
    edited = st.text_area("Edit your LinkedIn post", value=post_content, height=200)
    if st.button("Post to LinkedIn"):
        success, result = post_to_linkedin(edited, st.session_state['linkedin_access_token'], st.session_state['linkedin_person_urn'])
        if success:
            st.success("✅ Posted successfully!")
            st.balloons()
            st.session_state.scraped_result = None
        else:
            st.error(f"Failed: {result}")
