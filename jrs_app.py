import streamlit as st

from codenexus import login, home, review_employer, companies, analyzer

from requests_oauthlib import OAuth2Session

import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from urllib.parse import urlencode, urlunparse, urlparse

filename = "/data/client_det.pickle"
os.makedirs(os.path.dirname(filename), exist_ok=True)

from linkedin_api import Linkedin

import pickle


def is_logged_in():
    is_logged_in = False
    try:
        is_logged_in = st.session_state.logged_in
    except:
        pass
    return is_logged_in

# Define the Streamlit app
def app():
    # Set the app title
    st.set_page_config(page_title="LinkedIn Login",
                       page_icon=":guardsman:", layout="wide")
    
    # Get the current query parameters
    query_params = st.experimental_get_query_params()

    # Define the LinkedIn OAuth endpoints
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'


    # Define your client ID and client secret
    client_id = '86fnoq3p9reokj'
    client_secret = 'unD661syK3kHMdPt'
    redirect_uri = 'http://localhost:8501/?page=home'

    # Create an OAuth2Session instance with the client ID and secret
    linkedin = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope="r_emailaddress,r_liteprofile")


    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    
    if "page" not in query_params:
        st.experimental_set_query_params(page="home")
        st.experimental_rerun()

    if not is_logged_in() and query_params.get("page")[0] == "home" and "code" not in query_params:
        st.experimental_set_query_params(page="login")
        st.experimental_rerun()
    
    if query_params.get("page")[0] == "login":
        st.experimental_set_query_params(page="login")
        login.show(linkedin)

    elif query_params.get("page")[0] == "home":
        if "user" not in st.session_state and "code" in query_params:
            _, sp_c, _ = st.columns(3)

            with sp_c:
                with st.spinner('Initializing....'):

                    code = query_params["code"][0]
                    state = query_params["state"][0]

                    token_url_params_string = urlencode({ 'page': 'home' , 'client_id': client_id, 'client_secret': client_secret })
                    token_response = urlunparse(urlparse(token_url)._replace(query=token_url_params_string))

                    authorization_url_params_string = urlencode({ 'page': 'home' ,'code': code, 'state': state })
                    authorization_response = urlunparse(urlparse(redirect_uri)._replace(query=authorization_url_params_string))

                    token = linkedin.fetch_token(token_url=token_response, code=code, authorization_response=authorization_response, client_secret=client_secret)

                    st.session_state.code = code
                    st.session_state.token = token
                    st.session_state.logged_in = True
                    st.session_state.initial_run = True

                    profile = linkedin.get('https://api.linkedin.com/v2/me?projection=(id,firstName,lastName,emailAddress,profilePicture(displayImage~:playableStreams))').json()

                    profile_email = linkedin.get( 'https://api.linkedin.com/v2/clientAwareMemberHandles?q=members&projection=(elements*(true,EMAIL,handle~,emailAddress))').json()

                    fname =  profile['firstName']['localized']['en_US']
                    lname = profile['lastName']['localized']['en_US']
                    name = fname + ' ' + lname
                
                    picture_url = profile['profilePicture']['displayImage~']['elements'][0]['identifiers'][0]['identifier']
                    email = profile_email['elements'][0]['handle~']['emailAddress']

                    user = {'name': name, 'picture_url':picture_url, 'email': email, 'fname': fname, 'lname': lname }

                     # Enter your LinkedIn email address and password
                    USERNAME = 'cooldiana6@gmail.com'
                    PASSWORD = 'iamabadboy'

                    client = None

                    try:
                        with open('/data/client_det.pickle', 'rb') as f:
                            client = pickle.load(f)
                            f.close()
                    except FileNotFoundError:
                        print("****** NEED TO AUTHENTICATE ******")

                    if client is None:
                        # Create a LinkedIn API client object and login
                        client = Linkedin(USERNAME, PASSWORD)

                        with open('/data/client_det.pickle', 'wb') as f:
                            pickle.dump(client, f, pickle.HIGHEST_PROTOCOL)
                            f.close()

                    # Search for users matching the query
                    search_results = client.search_people(
                        keywords=name,
                        limit=1)
                    
                    # Extract the first user from the search results
                    searched_user = search_results[0]

                    # Extract the user's public profile URL from their profile data
                    profile_url = f"https://www.linkedin.com/in/{searched_user['public_id']}/"
                    public_userid =  searched_user['public_id']

                    user.update(profile_url=profile_url)
                    user.update(public_userid=public_userid)

                    st.session_state.user = user

                    st.experimental_set_query_params(page="home")
                    st.experimental_rerun()

        elif "user" in st.session_state:
            st.experimental_set_query_params(page="home")
            home.show()
            st.stop()
    
        else:
            st.experimental_set_query_params(page="login")
            login.show(linkedin)
            st.stop()
    
    elif query_params.get("page")[0] == "companies":
        st.experimental_set_query_params(page="companies")
        companies.show()

    elif query_params.get("page")[0] == "review_employer":
        st.experimental_set_query_params(page="review_employer", company=query_params.get("company")[0])
        review_employer.show()

    elif query_params.get("page")[0] == "analyze_employer":
        company = ''
        if query_params.get("company") is not None:
            company = query_params.get("company")[0]
        st.experimental_set_query_params(page="analyze_employer", company=company)
        analyzer.show()
    
   
        
if __name__ == "__main__":
    app()
