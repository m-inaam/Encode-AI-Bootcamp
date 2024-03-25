# Multilingual Recipe Search Engine
Given a list of ingredients in some language X, the engine returns the closest matching recipe in language X. The recipe can originally be written in any [supported language](https://docs.cohere.ai/docs/supported-languages)!

### Motivation
Ever had a bunch of ingredients and you didn't know what recipe to cook using them? And what if you only knew the ingredients in a specific language? 
Many people* face these problems. Traditional search engines (Google, Bing, etc.) fail to return recipes because they only look for recipes written in the same language as the query.

**But what if you can search for any recipe in any language? We did just that.**

*Think of students, refugees, and people on a minimal budget.

### How it works
We used Cohere's multilingual model to embed a list of ingredients into an embedding space called `recipes_index.ann`. 
For any query, we embed the query and search that embedding space for its approximate nearest neighbor.
We then use `reduced_recipes_dataset.csv` to get the recipe details.
Finally, we use Google translate to translate those recipe details back into the input's language.

`reduced_recipes_dataset.csv` is the first 100K recipes from the [RecipeNLG dataset](https://github.com/Glorf/recipenlg).

### Further Details
This is an MVP made for [Multilingual Semantic Search Hackathon](https://lablab.ai/event/multilingual-semantic-search-hackathon) by team Flavor Fuse.
