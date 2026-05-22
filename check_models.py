import google.genai as genai

API_KEY = 

client = genai.Client(api_key=API_KEY)

print("Available models in your account:")
models = client.models.list()
for model in models:
    print(f"- {model.name}")
