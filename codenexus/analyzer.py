import os

import streamlit as st
from streamlit.url_util import get_hostname
from urllib.parse import urlparse, parse_qs

import pandas as pd

from selenium import webdriver
from bs4 import BeautifulSoup
import math
import re
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import string
import pickle
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from utils.modal import Modal

#import trained tfidx vectorizer and data
# DATA_PATH = os.path.normpath(os.path.abspath('data'))

# data = pd.read_csv(f'{DATA_PATH}/recommendation_data.csv')

def get_data_from_site(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(20)

    # Navigate to the Glassdoor page with the desired filters
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    time.sleep(10)

    # Use Beautiful Soup to parse the page source
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # find all the divs with class "review"
    reviews_div = soup.find('div', {'class': 'reviews'})

    # find all the divs with class "review"
    review_divs = soup.find_all('div', {'class': 'review'})

    job_titles = []
    locations = []
    overall_ratings = []
    work_life_balances = []
    culture_valuess = []
    diversity_inclusions = []
    career_opps = []
    comp_benefits_list = []
    headlines = []
    pros_list = []
    cons_list = []

    overall_ratings_ = []
    work_life_balances_ = []
    culture_valuess_ = []
    diversity_inclusions_ = []
    career_opps_ = []
    comp_benefits_list_ = []

    # loop through each review div and extract the relevant information
    for review_div in review_divs:
        job_title = review_div.find('p', {'class': 'job_title'}).text.strip()
        location = review_div.find('p', {'class': 'location'}).text.strip()
        overall_rating = review_div.find('p', {'class': 'overall_rating'}).text.strip()
        work_life_balance = review_div.find('p', {'class': 'work_life_balance'}).text.strip()
        culture_values = review_div.find('p', {'class': 'culture_values'}).text.strip()
        diversity_inclusion = review_div.find('p', {'class': 'diversity_inclusion'}).text.strip()
        career_opp = review_div.find('p', {'class': 'career_opp'}).text.strip()
        comp_benefits = review_div.find('p', {'class': 'comp_benefits'}).text.strip()
        headline = review_div.find('p', {'class': 'headline'}).text.strip()
        pros = review_div.find('p', {'class': 'pros'}).text.strip()
        cons = review_div.find('p', {'class': 'cons'}).text.strip()
        
        job_titles.append(job_title)
        locations.append(location)
        overall_ratings.append(overall_rating)
        work_life_balances.append(work_life_balance)
        culture_valuess.append(culture_values)
        diversity_inclusions.append(diversity_inclusion)
        career_opps.append(career_opp)
        comp_benefits_list.append(comp_benefits)
        headlines.append(headline)
        pros_list.append(pros)
        cons_list.append(cons)

        overall_ratings_ = [float(i) for i in overall_ratings]
        work_life_balances_ = [float(i) for i in work_life_balances]
        culture_valuess_ = [float(i) for i in culture_valuess]
        diversity_inclusions_ = [float(i) for i in diversity_inclusions]
        career_opps_ = [float(i) for i in career_opps]
        comp_benefits_list_ = [float(i) for i in comp_benefits_list]

    # create an array of columns
    columns = ["job_title","location","overall_rating","work_life_balance","culture_values",
            "diversity_inclusion","career_opp","comp_benefits","headline","pros","cons"]

    # create a dictionary of data for each column
    data = {
        'job_title': job_titles,
        'location': locations,
        'overall_rating': overall_ratings_,
        'work_life_balance': work_life_balances_,
        'culture_values': culture_valuess_,
        'diversity_inclusion': diversity_inclusions_,
        'career_opp': career_opps_,
        'comp_benefits': comp_benefits_list_, 
        'headline': headlines,
        'pros': pros_list,
        'cons': cons_list
    }

    # create a DataFrame from the columns and data
    df = pd.DataFrame(data, columns=columns)

    df['review'] = df[['headline', 'pros', 'cons']].apply(
        lambda row: '.'.join(row.values.astype(str)),
        axis=1
    )
    
    # Calculate lexicon scores
    sid = SentimentIntensityAnalyzer()
    df['lexicon_sentiment_score'] = df['review'].apply(lambda x: sid.polarity_scores(x)['compound'])

    stop_words = set(stopwords.words('english'))

    def get_wordnet_pos(tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN


    def clean_text(text):
        text = text.lower().strip()
        text = re.sub("\[\s*\w*\s*\]", "", text)
        dictionary = "abc".maketrans('', '', string.punctuation)
        text = text.translate(dictionary)
        text = re.sub("\S*\d\S*", "", text)

        words = [word for word in text.split() if word.isalpha()
                and word not in stop_words]
        stop_words_removed = " ".join(words)

        word_pos_tags = nltk.pos_tag(word_tokenize(
            stop_words_removed))  # Get position tags

        lemmatizer = WordNetLemmatizer()

        # Map the position tag and lemmatize the word/token
        words = [lemmatizer.lemmatize(tag[0], get_wordnet_pos(
            tag[1])) for idx, tag in enumerate(word_pos_tags)]

        return " ".join(words)
    
    df["cleaned_review"] = df.review.apply(lambda x: clean_text(x))

    with open('./data/recommendation_tfidf_vectorizer.pkl', 'rb') as tfidx_vectorizer_file:
        tfidf_vectorizer = pickle.load(tfidx_vectorizer_file)

    with open('./data/sentiment-classification-svc-model.pkl', 'rb') as svm_model_file:
        model = pickle.load(svm_model_file)
    
    predicted_labels = model.predict(tfidf_vectorizer.transform(df['cleaned_review']))
    df['user_sentiment'] = predicted_labels

    df['weighted_sentiment_score'] = df['lexicon_sentiment_score'].copy()
    df.loc[predicted_labels == 1, 'weighted_sentiment_score'] = (df.loc[predicted_labels == 1, 'lexicon_sentiment_score'] * 0.75) + (1 * 0.25)
    df.loc[predicted_labels == 0, 'weighted_sentiment_score'] = (df.loc[predicted_labels == 0, 'lexicon_sentiment_score'] * 0.75) + (-1 * 0.25)

    # Calculate word base sentiment score and overall sentiment score
    words_df = pd.read_csv(f'./data/pos_neg.csv')

    pos_words = set(words_df['positive'].values.tolist())
    neg_words = set(words_df['negative'].values.tolist())

    # Define a function to count the number of positive and negative words in a sentence
    def count_pos_neg_words(sentence):
        pos_words = 0
        neg_words = 0
        # tokens = nltk.word_tokenize(sentence)
        tokens = sentence.split(" ")
        for token in tokens:
            ss = sid.polarity_scores(token)
            if ss['compound'] > 0:
                pos_words += 1
            elif ss['compound'] < 0:
                neg_words += 1
        return pos_words, neg_words, len(tokens)


    # Apply the function to each review
    df[['pos_count', 'neg_count', 'tot_count']] = df['cleaned_review'].apply(
        lambda x: pd.Series(count_pos_neg_words(x)))

    # Calculate the word base sentiment score
    df['word_base_sentiment_score'] = (((df['pos_count'] - df['neg_count']) / df['tot_count']) + ((df['tot_count'] - df['neg_count']) / df['tot_count'])) / 2

    # Calculate the overall sentiment score
    df['overall_sentiment_score'] = (
                                    (0.1 * df['word_base_sentiment_score']) 
                                    + (0.1 * (((df['work_life_balance'] + df['culture_values'] + df['diversity_inclusion'] + df['career_opp'] + df['comp_benefits']) / 25) * 100)) 
                                    + (0.8 * df['weighted_sentiment_score'])
                                    ) / (0.1 + 0.1 + 0.9) * 10.0
    
    avg_ratings = df[['overall_rating', 'work_life_balance',
                                           'culture_values', 'diversity_inclusion',
                                            'career_opp', 'comp_benefits', 'lexicon_sentiment_score',
                                            'weighted_sentiment_score', 'word_base_sentiment_score',
                                            'overall_sentiment_score']].mean()
    driver.quit()
    return avg_ratings


def show():
    query_params = st.experimental_get_query_params()
    company = ''

    if query_params.get("company") is not None:
        company = query_params.get("company")[0]

    if query_params.get("page")[0] == "analyze_employer" and company is None or company == '' :
        url = st.text_input("url")
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        company = query_params['company'][0]

    st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(2)
        {
            text-align: center;
        } 
        div[data-testid="column"]:nth-of-type(3)
        {
            text-align: center;
        } 
        div[data-testid="column"]:nth-of-type(4)
        {
            text-align: end;
        } 
    </style>
    """,unsafe_allow_html=True
    )


    subheader_col, home_col, companies_col, lgoutbtn_col = st.columns(4)

    with subheader_col:
        subheader_col.subheader(f'Analyze {company}')

    with home_col:
        if home_col.button("Home"):
            st.experimental_set_query_params(page="home")
            st.experimental_rerun()
    
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

    hostname = st.get_option('browser.serverAddress')
    port = st.get_option('browser.serverPort')

    url_ = f"https://jrs-streamlit-c5xok5423q-ew.a.run.app/?page=review_employer&company={company}"
    # url_ = f"http://{hostname}:{port}/?page=review_employer&company={company}"
    
    st.write(url_)

    backdrop = st.markdown("""<div style="position: fixed;top: 0;left: 0;height: 100%;width: 100%;background-color: rgba(0, 0, 0, 0.5);z-index: 0;"></div>""", 
                           unsafe_allow_html=True)
   

    modal = Modal(title='Analyzing...', show_footer=False, show_close_header_btn=False, height=250)
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

    analytics = get_data_from_site(url=url_)

    st.dataframe(analytics, use_container_width=True)

    modal.close()
    backdrop.empty()