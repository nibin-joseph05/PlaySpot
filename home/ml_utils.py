from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



def load_faq_data(file_path='home/data/faq.xlsx'):
    """
    Load FAQ data from the Excel file and return it as a list of dictionaries.
    """
    try:
        data = pd.read_excel(file_path, header=None)
        print("Loaded data:", data.head())      
        data = data.dropna(axis=1, how='all')
        print(f"Columns after cleaning: {data.shape[1]}")  
        if data.shape[1] == 5:
            data.columns = ['Unused1', 'Unused2', 'Question', 'Answer', 'Category']
            data = data[['Question', 'Answer']]
        elif data.shape[1] == 3:
            data.columns = ['Unused1', 'Unused2', 'Question']
            data = data[['Question']]
            data['Answer'] = ''
        data['Question'] = data['Question'].fillna('')
        data['Answer'] = data['Answer'].fillna('')
        data['Question'] = data['Question'].str.replace('"', '', regex=False)
        data['Answer'] = data['Answer'].str.replace('"', '', regex=False)
        faq_list = data[['Question', 'Answer']].to_dict(orient='records')
        if not faq_list:
            raise ValueError("FAQ data is empty.")
        return faq_list
    except Exception as e:
        print(f"Error loading FAQ data: {e}")
        return []


def get_best_match(user_query, faq_data):
    """
    Match the user query with the most relevant FAQ question using cosine similarity.
    """
    print(f"Received query: {user_query}")  
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    
    if any(greeting in user_query.lower() for greeting in greetings):
        return "Hello! How can I assist you today?"

    try:
        questions = [faq['Question'] for faq in faq_data]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(questions)

        query_vec = vectorizer.transform([user_query])
        similarity = cosine_similarity(query_vec, tfidf_matrix)
        best_match_idx = similarity.argmax()

        if max(similarity[0]) < 0.3:
            return "I'm sorry, I couldn't find an answer to your question. Please contact support for further assistance."

        return faq_data[best_match_idx]['Answer']
    except Exception as e:
        print(f"Error in query matching: {e}")
        return "An error occurred while processing your query."
