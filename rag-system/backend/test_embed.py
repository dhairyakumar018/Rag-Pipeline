from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Testing generate_content")
    res = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello world"
    )
    print("Success generate_content:", res.text)
except Exception as e:
    print("Error generate_content:", e)

try:
    print("Testing embed_content with task_type")
    from google.genai import types
    res = client.models.embed_content(
        model="gemini-embedding-2",
        contents="Hello world",
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    print("Success embed_content task_type")
except Exception as e:
    print("Error embed_content task_type:", e)
