import os

import streamlit as st

import subprocess

import time

from utils.modal import Modal

import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, pairwise_distances
import math


#import trained tfidx vectorizer and data
DATA_PATH = './data'

data = pd.read_csv(f'{DATA_PATH}/recommendation_data.csv')

with open(f'{DATA_PATH}/recommendation_tfidf_vectorizer.pkl',  'rb') as tfidf_vectorizer_file:
    tfidf_vectorizer = pickle.load(tfidf_vectorizer_file)

with open(f'{DATA_PATH}/recommendation_tfidf_matrix.pkl',  'rb') as tfidf_matrix_file:
    tfidf_matrix = pickle.load(tfidf_matrix_file)

# Define the columns to use for recommendations
cols = ['title', 'description', 'requirement', 'qualifications', 'city', 'district', 'province']

# ---------------------------------------------------

def get_recommendations(title, description='', requirement='', qualifications='', city='', district='', province='', n=5):
    # Create a new DataFrame with the input job information
    input_df = pd.DataFrame({
        'description': [description.lower()],
        'requirement': [requirement.lower()],
        'qualifications': [qualifications.lower()],
        'city': [city.lower()],
        'district': [district.lower()],
        'province': [province.lower()],
        'title': [title.lower()]
    })

    # Calculate the TF-IDF matrix for the input DataFrame
    input_tfidf = tfidf_vectorizer.transform(input_df[cols].fillna('').apply(lambda x: ' '.join(x), axis=1))

    # Calculate the cosine similarity scores between the input job and all jobs in the merged DataFrame
    cosine_similarity_scores = cosine_similarity(input_tfidf, tfidf_matrix).flatten()

    # Calculate the pairwise similarity scores between the input job and all jobs in the merged DataFrame
    pairwise_similarity_scores = pairwise_distances(input_tfidf, tfidf_matrix, metric='cosine').flatten()
    # pairwise_similarity_scores = 1 - pairwise_similarity_scores

    # Normalize pairwise distances to range [0, 1]
    max_distance = pairwise_similarity_scores.max()
    normalized_distances = 1 - (pairwise_similarity_scores / max_distance)

    # Calculate the final scores as a combination of hybrid scores and similarity scores
    final_scores = data['hybrid_score'].values.tolist() * cosine_similarity_scores * normalized_distances

    # Get the indices of the top N jobs with the highest final scores
    top_indices = final_scores.argsort()[::-1][:n]

    # Get the titles and scores of the top N jobs
    top_n_jobs = data.iloc[top_indices]

    # Return a DataFrame of the top N recommendations
    return top_n_jobs[
        ['title', 'company_name','description', 'requirement', 'qualifications', 
         'district', 'province', 'cosine_similarity_score', 'pairwise_distance_score', 'sentiment_score', 'hybrid_score']
            ]

def is_nan_str(val):
    if(type(val).__name__ == 'float' or val is None or val == ''):
            return '' if math.isnan(val) else val
    return val

def show():
    hide_sidebar_close = """
        <style>
        .e1fqkh3o2 {visibility: hidden;}
        </style>
        """
    st.markdown(hide_sidebar_close, unsafe_allow_html=True)

    name = st.session_state.user['name']
    fname = st.session_state.user['fname']
    lname = st.session_state.user['lname']
    email = st.session_state.user['email']
    picture_url = st.session_state.user['picture_url']


    st.sidebar.columns(3)[1].image(picture_url)
   
    fname_col, lname_col = st.sidebar.columns(2)

    with fname_col:
        fname_col.text_input(label='First Name', placeholder='First Name', value=fname)
    with lname_col:
        lname_col.text_input(label='Last Name', placeholder='Last Name', value=lname)
        
    st.sidebar.text_input(label='Email', placeholder='Email', value=email, disabled=True)

    jobtitles = data['title'].unique().tolist()
    job_title = st.sidebar.selectbox('Job title' , jobtitles)

    employement_types = ['Full time', 'Part time', 'Contract', 'Temporary', 'Internship']
    employement_type = st.sidebar.selectbox('Full/Part/Contract/Intern/Temporary' , employement_types)

    work_cultures = ['Hybrid', 'Work from home', 'On-site']
    work_culture = st.sidebar.selectbox('Hybrid/WFH/On-site' , work_cultures)

    experience = st.sidebar.slider("Experience (in years)", 0, 50, 1)

    education_options = ["BSc in Computer Science", "BSc Software Engineering", "BEngSoftware Engineering", "BSc in Electrical Engineering", "BSc in Information Technology", "MSc in Computer Science", "MSc in Software Engineering ", "MSc in Information Technology", 'Other']
    education = st.sidebar.multiselect('Education', education_options)

    if education == 'Other':
        education_c = st.sidebar.text_area('Education', placeholder='Education')
        if education_c:
            education = education_c

    qualifications = st.sidebar.text_area('Qualifications', placeholder='Qualifications')

    locations = data['province'].unique().tolist()
    location = st.sidebar.selectbox('Location' , locations)

    skill_options = ['Java', 'C', 'C++', 'C#', 'Python', 'SQL' , 'MySql', 'PHP', 'Kotlin', 'MongoDB', 
                     'oracle', 'Postgresql', 'Android', 'Html', 'Css', 'JavaScript', 'JQuery', 'Ruby', 
                     'Scala', 'Swift', 'TypeScript', 'Perl', 'Golang', 'F#', 'SpringBoot', 'CodeIgniter', 
                     'Laravel', 'Reactjs', 'Vue.js', 'Angular', 'react native', 'flutter', 'javafx', 'java swing', 
                     'ASP.Net core', 'R', 'Django', 'Flask', 'AWS', 'Azure', 'Node.js', 'Express.js', 'Backbone.js',
                     'Next.js' ]
    skills = st.sidebar.multiselect('Skills', skill_options, max_selections=8)

    search_btn =  st.sidebar.button("Search")

    if search_btn:
        pass


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

    subheader_col, companies_col, lgoutbtn_col = st.columns(3)

    with subheader_col:
        subheader_col.subheader('Dashboard')
    
    with companies_col:

        if companies_col.button("Companies"):
            st.experimental_set_query_params(page="companies")
            st.experimental_rerun()

    with lgoutbtn_col:
        if lgoutbtn_col.button("Log out"):
            st.session_state.clear()
            st.session_state.logged_in = False
            st.write("Logging out...")
       
            st.experimental_set_query_params(page="login")
            # Reload the app with the new query parameters
            st.experimental_rerun()

            

    if st.session_state.initial_run:
        backdrop = st.markdown("""<div style="position: fixed;top: 0;left: 0;height: 100%;width: 100%;background-color: rgba(0, 0, 0, 0.5);z-index: 0;"></div>""", 
                            unsafe_allow_html=True)
   

        modal = Modal(title='Initializing...', show_footer=False, show_close_header_btn=False, height=250)
        modal_spinner = """
                        <div class="d-flex justify-content-center">
                            <div class="spinner-grow text-primary me-2" style="width: 3rem; height: 3rem;" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <div class="spinner-grow text-danger me-2" style="width: 3rem; height: 3rem;" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <div class="spinner-grow text-warning me-2" style="width: 3rem; height: 3rem;" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                """

        modal.add_element(modal_spinner)
        modal.show_modal()

        time.sleep(1)

    try:
        pass
    except FileNotFoundError:
        pass

    finally:
        if st.session_state.initial_run:
            modal.close()
            backdrop.empty()
            st.session_state.initial_run = False

    # job_title
    # employement_type
    # work_culture
    # education
    # qualifications
    # location
    # skills


    job_title = job_title.strip()

    skills_str = ", ".join(skills)
    education = education.strip() if type(education) is not list else education
    if type(education) is not list:
        education = education[:-1] if education.endswith('.') else education
    qualifications = qualifications.strip()
    qualifications = qualifications[:-1] if qualifications.endswith('.') else qualifications

    # Sample job titles to test recommendation function
    title = f'{job_title}'.lower()
    description = f"""I am seeking a {employement_type} {job_title} position with {experience}+ year of experience in {skills_str}, and am willing to work {work_culture} as needed.""".lower()
    requirement = f"""{education} and a skilled {job_title} with over {experience}+ years of experience in {skills_str} is actively seeking a {employement_type} position that will enable them to utilize their skills and knowledge to drive the success of the organization. They are also willing and available to work {work_culture} as needed to support the goals and objectives of the team.""".lower()
    qualifications = f"""{education}. {qualifications}. {experience}+ years of experience in software development using {skills_str}. I am available to work {employement_type} hours and am open to working {work_culture} at your location.""".lower()
    district = f"""{location}""".lower()

    print(f"""
    job_title = {job_title}
    employement_type = {employement_type}
    work_culture = {work_culture}
    education = {education}
    qualifications = {qualifications}
    location = {location}
    skills = {skills}
    """)

    # Recommend top 5 similar jobs for each title
    n = 10
    st.write(f"\nTop {n} similar jobs for '{title}':\n")

    recommendations = get_recommendations(
        title=title,
        description=description,
        requirement=requirement,
        qualifications=qualifications,
        district=district, 
        n=n
    )

    html_code = """<div class='recommendations' style='display: grid;grid-template-columns: auto auto;padding: 10px;column-gap: 20px;'>"""

    if len(recommendations) == 0:
        st.write("No recommendations found.")
    else:
        for i, row in recommendations.iterrows():


            html_code = f"""
                        {html_code}
                        <div style="border: 1px solid #dee2e6; padding: 15px; margin-bottom: 15px;">
                            <div style="padding: 0;">
                                <hr style="border-top: 1px solid #dee2e6; margin: 10px 0;">
                                <div style="display: flex; justify-content: space-between;">
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;"class="overall_rating">{row["title"]}</p>
                                        <p style="margin-bottom: 0;">Title</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="work_life_balance">{row["company_name"]}</p>
                                        <p style="margin-bottom: 0;">Company</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="culture_values">{row["district"]}, {row["province"]}</p>
                                        <p style="margin-bottom: 0;">Location</p>
                                    </div>
                                </div>
                                <hr style="border-top: 1px solid #dee2e6; margin: 10px 0;">
                                <div style="display: flex; justify-content: space-between;">
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="similarity_score">{round(row["cosine_similarity_score"], 2)}</p>
                                        <p style="margin-bottom: 0;">Similarity Score</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="sentiment_score">{round(row["sentiment_score"], 2)}</p>
                                        <p style="margin-bottom: 0;">Sentiment Score</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="hybrid_score">{round(row["hybrid_score"], 2)}</p>
                                        <p style="margin-bottom: 0;">Recommendation Score</p>
                                    </div>
                                </div>
                                <hr style="border-top: 1px solid #dee2e6; margin: 10px 0;">
                                <div>
                                    <h6 style="margin-bottom: 5px; color: #6c757d;">Description:</h6>
                                    <p style="margin-bottom: 10px;" class="headline">{is_nan_str(row["description"])}</p>
                                    <h6 style="margin-bottom: 5px; color: #6c757d;">Requirement:</h6>
                                    <p style="margin-bottom: 10px;" class="pros">{is_nan_str(row["requirement"])}</p>
                                    <h6 style="margin-bottom: 5px; color: #6c757d;">Qualifications:</h6>
                                    <p style="margin-bottom: 0;" class="cons">{is_nan_str(row["qualifications"])}</p>
                                </div>
                            </div>
                        </div>
                    """

        st.markdown(html_code, unsafe_allow_html=True, )


    # Log out button
    if not st.session_state.logged_in:
        st.experimental_set_query_params(page="login")
        # Reload the app with the new query parameters
        st.experimental_rerun()