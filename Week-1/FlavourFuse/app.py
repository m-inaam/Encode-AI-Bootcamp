import streamlit as st
from openai import OpenAI

def main():
    st.title("FlavourFuse")

    with st.form(key='recipe_form'):
        dish = st.text_input("Type the name of the dish you want a recipe for:")
        cuisine_preference = st.selectbox("Select your preferred cuisine:", ["Any", "Italian", "Mexican", "Indian", "Chinese", "French", "Thai", "Japanese", "Mediterranean", "Other"])
        dietary_restrictions = st.multiselect("Any dietary restrictions? (optional)", ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free", "Other"])
        submit_button = st.form_submit_button(label='Get Recipe')

    if submit_button:
        client = OpenAI()
        messages = [
            {
                "role": "system",
                "content": "You are an experienced chef specializing in providing personalized recipes. Please provide the details of the dish you're interested in, including its name, your preferred cuisine, and any dietary restrictions. Your input will help me generate the best recipe for you.",
            },
            {
                "role": "user",
                "content": f"Suggest me a detailed recipe and the preparation steps for making {dish}. My preferred cuisine is {cuisine_preference}. Dietary restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}."
            }
        ]
        model = "gpt-3.5-turbo"

        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        collected_messages = []
        for chunk in stream:
            chunk_message = chunk.choices[0].delta.content or ""
            collected_messages.append(chunk_message)

        st.text_area("Recipe:", value="".join(collected_messages), height=400)

if __name__ == "__main__":
    main()
