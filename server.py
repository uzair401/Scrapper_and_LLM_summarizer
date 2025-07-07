import os
import re
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
app = FastAPI()

def evaluate_response(user_prompt, response, extracted_data):
    eval_prompt = f"""Rate this AI response quality from 0.0 to 1.0:

User Query: {user_prompt}
AI Response: {response}
Data Available: {extracted_data[:1000]}...

Rate accuracy and relevance. Respond only with JSON:
{{"accuracy": 0.0-1.0, "relevance": 0.0-1.0, "overall": 0.0-1.0, "needs_retry": true/false}}"""

    try:
        eval_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=eval_prompt
        )

        json_match = re.search(r'\{.*\}', eval_response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass

    low_quality_signs = ["don't have enough", "cannot answer", "insufficient", "not enough details"]
    has_low_quality = any(sign in response.lower() for sign in low_quality_signs)

    return {
        "accuracy": 0.3 if has_low_quality else 0.7,
        "relevance": 0.4 if has_low_quality else 0.7,
        "overall": 0.35 if has_low_quality else 0.7,
        "needs_retry": has_low_quality or len(response) < 100
    }

def stream_generate_response(user_prompt, extracted_data, is_retry=False, previous_response=""):
    if is_retry:
        prompt = f"""Your previous response was low quality. Improve it using the provided data.

Previous Response: {previous_response}

User Query: {user_prompt}
Data: {extracted_data}

Provide a better, more detailed response using specific information from the data."""
    else:
        prompt = f"""You are an intelligent web content analyzer. Analyze the data and answer the user query accurately.

Data: {extracted_data}
User Query: {user_prompt}

Provide a comprehensive response based strictly on the provided data. Use specific examples and details from the data."""

    response_stream = client.models.stream_generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    for chunk in response_stream:
        yield chunk.text.encode()

@app.post("/ask")
async def ask(req: Request):
    data = await req.json()
    user_prompt = data.get("prompt")
    extracted_data = data.get("data", "")

    if not user_prompt:
        return {"error": "Prompt required"}

    return StreamingResponse(stream_generate_response(user_prompt, extracted_data), media_type="text/plain")
