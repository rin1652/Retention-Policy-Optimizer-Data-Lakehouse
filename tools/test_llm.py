import os
import sys
from dotenv import load_dotenv

# Try to import providers
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

def test_gemini_connection(model, timeout):
    if not genai:
        print("Error: google-genai is not installed.")
        return

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        print("Error: Missing GEMINI_API_KEY in environment or .env file.")
        return

    print(f"Testing connection to Gemini using model: {model} with timeout {timeout}s...")
    client = genai.Client(api_key=api_key)
    
    try:
        response = client.models.generate_content(
            model=model,
            contents="Hello, this is a test. Please respond with exactly 'OK' and nothing else.",
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=10,
                system_instruction="You are a helpful assistant."
            )
        )
        print("Success! Gemini responded:")
        print(response.text)
    except Exception as e:
        print(f"Error calling Gemini API: {type(e).__name__} - {e}")

def test_fpt_connection(model, timeout):
    if not openai:
        print("Error: openai is not installed. FPT usually provides an OpenAI-compatible API.")
        return

    api_key = os.getenv("FPT_API_KEY")
    base_url = os.getenv("FPT_API_BASE", "https://api.fpt.ai/v1")

    if not api_key or api_key == "YOUR_FPT_API_KEY_HERE":
        print("Error: Missing FPT_API_KEY in environment or .env file.")
        return

    print(f"Testing connection to FPT using model: {model} at {base_url} with timeout {timeout}s...")
    client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, this is a test. Please respond with exactly 'OK' and nothing else."}
            ],
            max_tokens=10,
            temperature=0.0
        )
        print("Success! FPT responded:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling FPT API: {type(e).__name__} - {e}")

def test_llm_connection():
    load_dotenv()
    
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))

    if provider == "gemini":
        test_gemini_connection(model, timeout)
    elif provider == "fpt":
        test_fpt_connection(model, timeout)
    elif provider == "openai":
        # Similar to FPT but without custom base_url
        print("OpenAI provider not explicitly implemented in this test script yet.")
    else:
        print(f"Unknown LLM_PROVIDER: {provider}")

if __name__ == "__main__":
    test_llm_connection()
