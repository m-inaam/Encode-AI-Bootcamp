from openai import OpenAI

client = OpenAI()

def main():
  messages = [
    {
      "role": "system",
      "content": "Greetings! I'm your friendly AI chef, specializing in the vibrant cuisines of Korea, Japan, and China. Tell me, are you craving the bold flavors of kimchi, the delicate artistry of sushi, or the savory richness of a Chinese stir-fry? I'm here to guide you on a culinary adventure!"
    }
  ]

  while True:
    print("\n")
    user_cuisine = input("What type of cuisine are you interested in today (Korean, Japanese, or Chinese)? ").lower()
    user_input = input("Tell me the dish you'd like a recipe for, or ask for suggestions: ")

    messages.append({
      "role": "user",
      "content": user_input
    })

    model = "gpt-3.5-turbo"
    stream = client.chat.completions.create(
      model=model,
      messages=messages,
      stream=True
    )

    collected_messages = []
    for chunk in stream:
      chunk_message = chunk.choices[0].delta.content or ""
      print(chunk_message, end="")
      collected_messages.append(chunk_message)

    messages.append({
      "role": "system",
      "content": "".join(collected_messages)
    })

if __name__ == "__main__":
  main()