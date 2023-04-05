import streamlit as st
import pandas as pd

def show():
    df = pd.read_csv('C:/Users/rathu/OneDrive/Desktop/JRS/glassdoor_reviews.csv')
    companies = df['firm'].unique().tolist()

    st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: center;
        } 
        div[data-testid="column"]:nth-of-type(3)
        {
            text-align: end;
        } 
    </style>
    """,unsafe_allow_html=True
    )

    subheader_col, home_col, lgoutbtn_col = st.columns(3)

    with subheader_col:
        subheader_col.subheader(f'Companies')

    with home_col:
        if home_col.button("Home"):
            st.experimental_set_query_params(page="home")
            st.experimental_rerun()

    with lgoutbtn_col:
        if lgoutbtn_col.button("Log out"):
            st.session_state.clear()
            st.session_state.logged_in = False
            st.write("Logging out...")
       
            st.experimental_set_query_params(page="login")
            # Reload the app with the new query parameters
            st.experimental_rerun()

    company = st.text_input("Company name")

    base_url = st.get_option('server.baseUrlPath')

    if company and company != '':
        if company not in companies:
            st.write("No company found")
        else:
            company_link = f'{base_url}/?page=review_employer&company={company}'
            st.markdown(f'<div class="card mb-3"><div class="card-body"><a href="{company_link}" id="company_link_{company}" class="card-title">{company}</a></div></div>', unsafe_allow_html=True)
    else:
        if len(companies) == 0:
            st.write("No companies found.")
        else:
            for i, company in enumerate(companies):
                company_link = f'{base_url}/?page=review_employer&company={company}'
              
                html_code = f"""
                    <div style="margin: 0 0 3px 0"><div class="card-body"><a href="{company_link}" id="company_link_{company}" class="card-title"><span>{i+1}) </span> {company}</a></div></div>
                """
                st.write(html_code, unsafe_allow_html=True)

