import google.genai as genai
import asyncio

GEMINI_API_KEY = "AIzaSyClIAyoPQm63VuiuXmwRBS2ASA2szCvN18"

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    client = None

async def generate_response(prompt: str, context: str = None, use_rag: bool = False) -> str:
    if not client:
        return "API not configured. Check your API key."
    
    full_prompt = prompt
    if context:
        full_prompt = f"Previous conversation:\n{context}\n\nCurrent query: {prompt}"
    
    try:
        response = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model="gemini-1.5-flash-latest",
                contents=full_prompt,
                config={"temperature": 0.7}
            )
        )
        
        if response.text:
            return response.text.strip()
    except Exception:
        try:
            response = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model="gemma-3-4b-it",
                    contents=full_prompt,
                    config={"temperature": 0.7}
                )
            )
            
            if response.text:
                return response.text.strip()
        except Exception:
            pass
    
    return "Unable to get response."

async def summarize_document(file_content: str, filename: str) -> str:
    if not client:
        return f"Document '{filename}' uploaded."
    
    if len(file_content) < 50:
        return "Document processed."
    
    try:
        summary_prompt = f"Summarize this document briefly:\n\nFilename: {filename}\n\nContent: {file_content[:3000]}"
        response = await asyncio.to_thread(
            lambda: client.models.generate_content(
                model="gemini-1.5-flash-latest",
                contents=summary_prompt
            )
        )
        return response.text.strip() if response.text else "Document added to memory."
    except:
        return f"Document '{filename}' uploaded and processed."