import cohere
import pandas as pd
import numpy as np
import openai

from flask import Flask, request
from flask_cors import CORS
import os
from typing import List

from googletrans import Translator
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Success!</p>"

load_dotenv("../keys.env")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Initialize the Google Translate client
translator = Translator()

COHERE_SIZE_VECTOR = 768  # small model

if not QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY is not set")

if not QDRANT_HOST:
    raise ValueError("QDRANT_HOST is not set")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set")

if not openai.api_key:
    raise ValueError("COHERE_API_KEY is not set")


class SearchClient():
    def __init__(
        self,
        preload = True,
        qdrant_api_key: str = QDRANT_API_KEY,
        qdrant_host: str = QDRANT_HOST,
        cohere_api_key: str = COHERE_API_KEY,
        collection_name: str = "recipe_ingredients",
        COHERE_SIZE_VECTOR : int = COHERE_SIZE_VECTOR,  # default model
        ):
        '''
        Params: preload = If True, loads existing qdrant container to avoido overwrite.
        '''
        self.qdrant_client = QdrantClient(url=qdrant_host, api_key=qdrant_api_key)
        self.collection_name = collection_name

        if not preload:
          # create new collection
          self.qdrant_client.recreate_collection(
              collection_name=self.collection_name,
              on_disk_payload=True,
              vectors_config=models.VectorParams(
                  size=COHERE_SIZE_VECTOR, distance=models.Distance.COSINE
              ),
          )

        self.co_client = cohere.Client(api_key=cohere_api_key)

    # Qdrant requires data in float format
    def _float_vector(self, vector: List[float]):
        return list(map(float, vector))

    # Embedding using Cohere Embed model
    def _embed(self, chunks: List[str]):
        # Inference
          return self.co_client.embed(texts=chunks, model='multilingual-22-12').embeddings[0]

    # Search using text query
    def search(self, query_text: str, limit: int=1):
        query_vector = self._embed(query_text)

        search_result =  self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=self._float_vector(query_vector),
            limit=limit,
        )
        # return payload dict
        return search_result[0].payload

    def generate_recipe_title(self, ingredients, languageText):
        prompt = f"Generate a recipe title in {languageText} for the following ingredients: " + ", ".join(str(ingredients))
        completions = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=60,
            n=1,
            stop=None,
            temperature=0.5,
        )
        title = completions.choices[0].text.strip()
        return title

    def search_recipes(self, query, language, languageText):
        """
        Searches for recipes given a query and a language.
        The language parameter takes a language code (ISO-639) as argument.
        """
        match_recipe = self.search([query])
        # ingredients with measurements
        ingredients = match_recipe["ingredients"]
        # Generate the recipe title
        title = self.generate_recipe_title(ingredients, languageText)
        # Generate the recipe procedure
        procedure = match_recipe["steps"]
        ing_header = "Ingredients"
        direc_header = "Directions"
        if language != "en":
            # Translate the recipe to query language
            # list
            ingredients = [t.text for t in translator.translate(ingredients, src="en", dest=language)]
            procedure = [t.text for t in translator.translate(procedure, src="en", dest=language)]
            ing_header = translator.translate(ing_header, src="en", dest=language).text
            direc_header = translator.translate(direc_header, src="en", dest=language).text
        
        # make readable
        procedure = '\n'.join(str(i) + '. ' + j for i, j in enumerate(procedure, 1))
        procedure = f"\n\n{direc_header}:\n" + procedure
        ingredients = '\n '.join(ingredients)
        ingredients = f"\n{ing_header}:\n" + ingredients
        return title, procedure, ingredients
    

@app.route('/api/predict', methods=['POST'])
def predict():
    client = SearchClient()
    title, steps, ingredients = client.search_recipes(request.json.get("query"), request.json.get("langcode"), request.json.get("langtext"))
    bot = title + ingredients + steps
    return {"bot": bot}
    
if __name__ == '__main__':
    app.run(debug=False)