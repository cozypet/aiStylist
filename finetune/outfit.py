from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from numpy.linalg import norm
import requests
import openai
import pymongo
import os
import json
import numpy as np
import pandas as pd

# Set OpenAI API Key
openai.api_key = os.environ['OPENAI_API_KEY']

# Define the URL
#url = "https://en.wikipedia.org/wiki/Markets_in_Financial_Instruments_Directive_2014#Directive_2014/65/EU_/_Regulation_(EU)_No_600/2014"

# Connect to MongoDB server
def connect_mongodb():
    mongo_url = "mongodb+srv://han:han@cluster0.bofm7.mongodb.net/test?retryWrites=true&w=majority"
    client = pymongo.MongoClient(mongo_url)
    db = client["produit"]
    collection = db["products"]
    return collection

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

# def data_prep():
#     # Load data
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     text = soup.get_text()
#     content_div = soup.find('div', {'class': 'mw-parser-output'})

#     # Remove unwanted elements from div
#     unwanted_tags = ['sup', 'span', 'table', 'ul', 'ol']
#     for tag in unwanted_tags:
#         for match in content_div.findAll(tag):
#             match.extract()
#     article_text = content_div.get_text()

#     # Split data
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=100,
#         chunk_overlap=20,
#         separators=["\n\n", "\n", "(?<=\. )", " ", ""],
#         length_function=len,
#     )
#     texts = text_splitter.create_documents([article_text])

#     # Calculate embeddings
#     text_chunks = [text.page_content for text in texts]
#     df = pd.DataFrame({'text_chunks': text_chunks})
#     df['ada_embedding'] = df.text_chunks.apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))

#     # Store into MongoDB
#     collection = connect_mongodb()
#     df_dict = df.to_dict(orient='records')
#     collection.insert_many(df_dict)

#     print("Data loaded successfully")

def find_similar_documents(embedding):
    collection = connect_mongodb()
    documents = list(collection.aggregate([
        {
            "$search": {
                "index": "vector-docEmbedding-euclidean",
                "knnBeta": {
                    "vector": embedding,
                    "path": "docEmbedding",
                    "k": 10,
                },
            }
        },
        {"$project": {"_id": 0, "name": 1, "subcategory": 1}},
    ]))
    return documents

def qna(users_question):
    llm = OpenAI(temperature=1)
    question_embedding = get_embedding(text="Chapeau de parasol de casquette de baseball en denim lavé à bordure", model="text-embedding-ada-002")


    context = ""
    documents = find_similar_documents(question_embedding)
        
    df = pd.DataFrame(documents)

    for index, row in df[0:10].iterrows():
        print(row)
        context = context + " " + row.name
    print(context)
    template = """
    You are a fashin stylist who loves to help people! Given the following context sections, answer the
    question using only the given context. Give the details with sending context, the list of names of product prices, and id. 
    And prepare a situation how I will put these articles on.
    show me the context section in the answer.

    Context sections:
    {context}

    Question:
    {users_question}

    Answer:
    """

    prompt = PromptTemplate(template=template, input_variables=[
                            "context", "users_question"])

    prompt_text = prompt.format(context=context, users_question=users_question)

    #response = llm(prompt_text)

    #print(response)

while True:
    #data_prep()
    users_input = input("What's your outfit style today?\n")
    qna(users_input)
