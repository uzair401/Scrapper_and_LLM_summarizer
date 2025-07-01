import requests
import streamlit as st
from urllib.parse import urlencode
import secrets
from configuration import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI

class LinkedInAuth:
    def __init__(self):
        self.client_id = LINKEDIN_CLIENT_ID
        self.client_secret = LINKEDIN_CLIENT_SECRET
        self.redirect_uri = LINKEDIN_REDIRECT_URI
        self.auth_base_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.api_base_url = "https://api.linkedin.com/v2"

    def get_authorization_url(self):
        state = secrets.token_urlsafe(32)
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'w_member_social'
        }
        return f"{self.auth_base_url}?{urlencode(params)}"

    def exchange_code_for_token(self, code, state):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.token_url, data=data)
        if not response.ok:
            st.error(response.text)
        response.raise_for_status()
        return response.json()['access_token']

    def get_user_profile(self, access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_url = f"{self.api_base_url}/me"
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def create_post(self, access_token, content, person_urn):
        url = "https://api.linkedin.com/rest/posts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "LinkedIn-Version": "202405",
            "Content-Type": "application/json"
        }
        data = {
            "author": person_urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "lifecycleState": "PUBLISHED"
        }
        response = requests.post(url, headers=headers, json=data)
        if not response.ok:
            st.error(response.text)
        response.raise_for_status()
        return response.json()

def initialize_linkedin_auth():
    return LinkedInAuth()

def handle_linkedin_callback():
    query_params = st.query_params
    st.write("🔁 LinkedIn Redirect Response:", query_params)
    if 'code' in query_params and 'state' in query_params:
        code, state = query_params['code'][0], query_params['state'][0]
        linkedin_auth = initialize_linkedin_auth()
        try:
            token = linkedin_auth.exchange_code_for_token(code, state)
            st.session_state['linkedin_access_token'] = token
            profile = linkedin_auth.get_user_profile(token)
            st.session_state['linkedin_profile'] = profile
            st.session_state['linkedin_person_urn'] = f"urn:li:person:{profile['id']}"
            st.experimental_set_query_params()
            st.success("✅ LinkedIn connected.")
            st.rerun()
        except Exception as e:
            st.error(f"LinkedIn auth failed: {e}")

def post_to_linkedin(content, access_token, person_urn):
    try:
        linkedin_auth = initialize_linkedin_auth()
        result = linkedin_auth.create_post(access_token, content, person_urn)
        return True, result
    except Exception as e:
        return False, str(e)
