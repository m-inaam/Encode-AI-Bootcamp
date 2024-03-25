import itertools
import sys

from openai import OpenAI

from response_handler import print_response
from flask import Flask, request
from flask_cors import CORS
import os
from googletrans import Translator
from dotenv import load_dotenv

INSTRUCTIONS = """Welcome to the culinary critique corner, where your discerning palate reigns supreme! As an experienced chef, you bring a wealth of knowledge and insight to the table, honed through years of mastering different cuisines and cooking techniques. Your dedication to clarity, patience, and understanding ensures that each recipe receives thoughtful consideration.

Your role here is to provide constructive criticism and suggest improvements to the user's recipe submissions. If the user presents a recipe, offer valuable feedback on how it could be enhanced. Should you find the recipe satisfactory, affirm with confidence: "Looks good to me." However, if the recipe falls short, provide insightful suggestions for improvement.

In the absence of a recipe from the user, gracefully acknowledge: "No recipe was provided." As always, maintain focus on the task at hand, politely declining to respond to any unrelated queries.

Your culinary expertise shines through as you guide others toward culinary excellence, one recipe at a time!
"""

app = Flask(__name__)
CORS(app)

load_dotenv("../keys.env")

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Initialize the Google Translate client
translator = Translator()

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY is not set")

class RecipeGenerator():
    def __init__(self, cohere_api_key: str = COHERE_API_KEY):
        self.co_client = cohere.Client(api_key=cohere_api_key)

    # Embedding using Cohere Embed model
    def _embed(self, chunks: list):
        return self.co_client.embed(texts=chunks, model='multilingual-22-12').embeddings[0]

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

    def generate_recipe(self, query, language, languageText):
        title = self.generate_recipe_title(query, languageText)
        return title

    def generate_feedback(self, recipe):
        prompt = f"As a critic, give feedback on the following recipe:\n{recipe}\nFeedback:"
        completions = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        feedback = completions.choices[0].text.strip()
        return feedback


@app.route('/api/predict', methods=['POST'])
def predict():
    recipe_generator = RecipeGenerator()
    title = recipe_generator.generate_recipe(request.json.get("query"), request.json.get("langcode"), request.json.get("langtext"))
    feedback = recipe_generator.generate_feedback(title)
    return {"title": title, "feedback": feedback}

def give_recipe_feedback(client: OpenAI, model: str) -> None:
    """Gives feedback on the user's recipe.

    If the input is not a recipe, it'll be pointed out.

    Args:
        client: An OpenAI client.
        model: An OpenAI model.
    """
    print('Enter your recipe (type "quit" when you\'re finished)')
    user_input = "".join(
        list(itertools.takewhile(lambda x: x.strip() != "quit", sys.stdin))
    )

    messages = [
        {
            "role": "system",
            "content": INSTRUCTIONS,
        },
        {
            "role": "user",
            "content": f"How can I improve the following recipe?\n{user_input}",
        },
    ]

    print_chatgpt_response(client, model, messages)

if __name__ == '__main__':
    app.run(debug=False)
