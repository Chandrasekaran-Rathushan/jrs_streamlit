import streamlit as st
import pandas as pd
import math

def show():
    query_params = st.experimental_get_query_params()
    company = query_params.get("company")[0]

    st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: end;
        } 
    </style>
    """,unsafe_allow_html=True
    )

    subheader_col, analyze_col = st.columns(2)

    with subheader_col:
        subheader_col.subheader(f'{company}')
    
    with analyze_col:
        if analyze_col.button("Analyze"):
            st.experimental_set_query_params(page="analyze_employer", company=company)
            st.experimental_rerun()

    wait = st.markdown("<h3 style='color: red;'>Please wait ...</h3>", unsafe_allow_html=True)
    df = pd.read_csv('./data/glassdoor_reviews.csv')
   

    def is_nan_float(val):
        return 0 if math.isnan(val) else val
    
    def is_nan_str(val):
            if(val == '' or val == ' '):
                 return 'Not Available'
            
            if(type(val).__name__ == 'float' or val is None):
                 return 'Not Available' if math.isnan(val) else val
            return val

    filtered_df = df[df['firm'] == company]

    html_code = """<div class='reviews' style='display: grid;grid-template-columns: auto auto auto;padding: 10px;column-gap: 15px;'>"""

    if len(filtered_df) == 0:
        st.write("No reviews found for the selected employer.")
    else:
        for i, row in filtered_df.iterrows():
            html_code += f"""<div style="border: 1px solid #dee2e6; padding: 15px; margin-bottom: 15px;" class="review">
                            <div style="background-color: #fff; padding-bottom: 0;display: flex;justify-content: space-between;" class="review-header">
                                <p style="margin-bottom: 0; color: #6c757d;" class="job_title"><b>{is_nan_str(row["job_title"])}</b></p>
                                <p class="location" style="margin-bottom: 0; color: #6c757d;">{is_nan_str(row["location"])}</p>
                            </div>
                            <hr style="border-top: 1px solid #a44; margin: 10px 0;">
                            <div style="padding: 0;" class="review-body">
                                <div style="display: flex; justify-content: space-between;" class="review-stat-1">
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="overall_rating">{is_nan_float(row["overall_rating"])}</p>
                                        <p style="margin-bottom: 0;">Overall Rating</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="work_life_balance">{is_nan_float(row["work_life_balance"])}</p>
                                        <p style="margin-bottom: 0;">Work-Life Balance</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="culture_values">{is_nan_float(row["culture_values"])}</p>
                                        <p style="margin-bottom: 0;">Culture and Values</p>
                                    </div>
                                </div>
                                <hr style="border-top: 1px solid #dee2e6; margin: 10px 0;">
                                <div style="display: flex; justify-content: space-between;" class="review-stat-2">
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="diversity_inclusion">{is_nan_float(row["diversity_inclusion"])}</p>
                                        <p style="margin-bottom: 0;">Diversity & Inclusion</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="career_opp">{is_nan_float(row["career_opp"])}</p>
                                        <p style="margin-bottom: 0;">Career Opportunities</p>
                                    </div>
                                    <div style="text-align: center;">
                                        <p style="font-weight: bold; margin-bottom: 0;" class="comp_benefits">{is_nan_float(row["comp_benefits"])}</p>
                                        <p style="margin-bottom: 0;">Compensation and Benefits</p>
                                    </div>
                                </div>
                                <hr style="border-top: 1px solid #dee2e6; margin: 10px 0;">
                                <div class="review-details">
                                    <h6 style="margin-bottom: 5px; color: #6c757d;">Headline:</h6>
                                    <p style="margin-bottom: 10px;" class="headline">{row["headline"]}</p>
                                    <h6 style="margin-bottom: 5px; color: #6c757d;">Pros:</h6>
                                    <p style="margin-bottom: 10px;" class="pros">{row["pros"]}</p>
                                    <h6 style="margin-bottom: 5px; color: #6c757d;">Cons:</h6>
                                    <p style="margin-bottom: 0;" class="cons">{row["cons"]}</p>
                                </div>
                            </div>
                        </div>"""
                    
        st.markdown(html_code, unsafe_allow_html=True)

        wait.empty()