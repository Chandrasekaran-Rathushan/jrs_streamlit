import streamlit as st


def show(linkedin):
    st.subheader('Login')

    authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'

    if st.session_state.logged_in:
        st.write("Redirecting to home screen...")
        st.experimental_set_query_params(page="home")
        # Reload the app with the new query parameters
        st.experimental_rerun()

    else:
        authorization_url, _ = linkedin.authorization_url(authorization_base_url)
        st.write("Please log in with your LinkedIn account")
        st.markdown(f"Click <a href='{authorization_url}' target='_self'>here</a> to log in", True)