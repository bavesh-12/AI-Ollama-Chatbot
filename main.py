from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
from memory_manager import ConversationMemory, ConversationStore
from ai_client import generate_response, summarize_document
import aiofiles
import asyncio

conversation_store = ConversationStore()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

try:
    from rag import add_document_to_memory, clear_memory, retrieve_memory
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

app = FastAPI(title="AI Chat Interface")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, conversation_id: str = None):
    if not conversation_id:
        memory = ConversationMemory()
        return RedirectResponse(f"/?conversation_id={memory.conversation_id}")
    
    memory = ConversationMemory(conversation_id)
    all_conversations = conversation_store.get_all_conversations()
    conversation_messages = memory.get_conversation_history()
    conversation_info = memory.get_conversation_info()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "messages": conversation_messages,
            "conversations": all_conversations,
            "current_conversation": conversation_info,
            "conversation_id": conversation_id,
            "rag_available": RAG_AVAILABLE
        }
    )

@app.post("/send_message")
async def send_message(
    request: Request,
    conversation_id: str = Form(...),
    prompt: str = Form(None),
    files: list[UploadFile] = File(None)
):
    memory = ConversationMemory(conversation_id)
    
    files_processed = False
    
    if files:
        for file in files:
            if file and file.filename:
                safe_filename = file.filename.replace('/', '_').replace('\\', '_')
                file_path = os.path.join(UPLOAD_DIR, safe_filename)
                
                try:
                    async with aiofiles.open(file_path, 'wb') as out_file:
                        content = await file.read()
                        await out_file.write(content)
                    
                    if RAG_AVAILABLE:
                        chunks_added, file_hash, extracted_text = add_document_to_memory(conversation_id, file_path, safe_filename)
                        
                        if chunks_added > 0 and extracted_text and len(extracted_text.strip()) > 10:
                            memory.add_message("system", f"📄 Added {safe_filename} to memory ({chunks_added} chunks)")
                            files_processed = True
                        else:
                            memory.add_message("system", f"⚠️ Could not extract text from {safe_filename}")
                            files_processed = True
                    else:
                        memory.add_message("system", f"📄 Uploaded {safe_filename}")
                        files_processed = True
                        
                except Exception as e:
                    memory.add_message("system", f"❌ Error uploading {safe_filename}: {str(e)}")
    
    if prompt and prompt.strip():
        rag_context = ""
        
        if RAG_AVAILABLE:
            try:
                results = retrieve_memory(conversation_id, prompt, k=3)
                if results:
                    rag_context = "Relevant document information:\n"
                    for i, result in enumerate(results, 1):
                        source = result['metadata']['source']
                        text = result['text'][:300]
                        rag_context += f"[From {source}]: {text}...\n"
            except:
                pass
        
        context = memory.get_recent_context(max_messages=6)
        
        full_prompt = prompt
        if rag_context:
            full_prompt = f"{rag_context}\n\nQuestion: {prompt}"
        
        response = await generate_response(full_prompt, context, use_rag=RAG_AVAILABLE)
        
        memory.add_message("user", prompt)
        memory.add_message("assistant", response)
    
    elif not files_processed and not prompt:
        raise HTTPException(status_code=400, detail="Please type a message or attach a file")
    
    return RedirectResponse(f"/?conversation_id={conversation_id}", status_code=303)

@app.post("/clear_memory")
async def clear_memory_endpoint(conversation_id: str = Form(...)):
    if RAG_AVAILABLE:
        clear_memory(conversation_id)
        memory = ConversationMemory(conversation_id)
        memory.add_message("system", "🗑️ Document memory cleared")
    
    return RedirectResponse(f"/?conversation_id={conversation_id}", status_code=303)

@app.get("/new_chat")
async def new_chat():
    memory = ConversationMemory()
    return RedirectResponse(f"/?conversation_id={memory.conversation_id}")

@app.get("/switch_chat/{conversation_id}")
async def switch_chat(conversation_id: str):
    return RedirectResponse(f"/?conversation_id={conversation_id}")

@app.post("/delete_chat/{conversation_id}")
async def delete_chat(conversation_id: str):
    success = conversation_store.delete_conversation(conversation_id)
    if RAG_AVAILABLE:
        clear_memory(conversation_id)
    return {"success": success}