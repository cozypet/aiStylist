import os
import openai
import json
import pymongo

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Get the embedding for a given text using OpenAI's API.
    """
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

def connect_mongodb():
    """
    Connect to the MongoDB server and return the collection.
    """
    mongo_url = "mongodb+srv://han:han@cluster0.bofm7.mongodb.net/test?retryWrites=true&w=majority"
    client = pymongo.MongoClient(mongo_url)
    db = client["produit"]
    collection = db["products"]
    return collection

def find_similar_documents(embedding):
    """
    Find similar documents in MongoDB based on the provided embedding.
    """
    collection = connect_mongodb()
    documents = list(collection.aggregate([
        {
            "$search": {
                "index": "vector-docEmbedding-cosine",
                "knnBeta": {
                    "vector": embedding,
                    "path": "docEmbedding",
                    "k": 1,
                },
            }
        },
        {"$project": {"_id": 0, "name": 1, "subcategory" :1, "model" :1, "id":1 }}
    ]))
    return documents

def migistylist(user_style):
    """
    Get outfit suggestions and product list based on user input.
    """
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Migi is a fashion stylist with a modern and edgy style. You give outfit suggestion based on user content. Your answer has two parts: 1. the proposed outfit 2. product list in JSON format. Here is an example of output, you should follow strictly the format but not the content: ```{\"outfit\": \"```{suggested outfit}```\",\"product_list\": {\"```{category of product}```}\": \"```{product descriptions}```}\",\"```{category of product}```\": \"```{product descriptions}```\",\"```{category of product}```\": \"```{product descriptions}```\",\"```{category of product}```\": \"```{product descriptions}```\",\"situation\": \"```{picture the situation with this outfit}```\"```"},
            {"role": "user", "content": f"```{user_style}```"}
        ]
    )

    # Extract content and parse as JSON
    content_json = json.loads(completion['choices'][0]['message']['content'])

    # Extract "outfit suggestion"
    outfit = content_json['outfit']

    # Extract "product_list"
    product_list = content_json['product_list']
    
    print("Here is the outfit suggestion")
    print(json.dumps(outfit, indent=2))

    # Print the extracted "product_list"
    print("Here is the list of your recommended products")
    print(json.dumps(product_list, indent=2))

    return product_list 

def product_Recommandation(product_list):
    """
    Recommend products based on the provided list.
    """
    for key, value in product_list.items():
        result = f"{key}: {value}\n"
        product_embedding = get_embedding(result)
        print(f"{key}: {value}")
        documents = find_similar_documents(product_embedding)
        for document in documents:
            print(str(document) + "\n")

if __name__ == "__main__":
    while True:
        users_input = input("What is your outfit style today?\n")
        product_list = migistylist(users_input)
        product_Recommandation(product_list)
