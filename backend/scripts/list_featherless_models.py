import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("FEATHERLESS_API_KEY"),
    base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
)

models = client.models.list()

for model in models.data:
    model_id = getattr(model, "id", None)

    if not model_id:
        continue

    if any(keyword.lower() in model_id.lower() for keyword in ["qwen", "mistral", "llama", "deepseek"]):
        print(model_id)