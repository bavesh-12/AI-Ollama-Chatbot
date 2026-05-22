import json
import os
from datetime import datetime
import uuid
import google.genai as genai

GEMINI_API_KEY = 

try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
except:
    gemini_client = None
    GEMINI_AVAILABLE = False

def generate_chat_title(prompt: str) -> str:
    if not prompt or len(prompt.strip()) < 3:
        return "New Chat"
    
    clean_prompt = prompt.strip()
    
    if len(clean_prompt) <= 40:
        words = clean_prompt.split()
        if len(words) <= 5:
            title = " ".join(word.capitalize() for word in words[:5])
            return title if title else "New Chat"
    
    try:
        if GEMINI_AVAILABLE and gemini_client:
            summary_prompt = f"Create a very short, concise title (max 5 words) for this chat query: '{clean_prompt[:200]}'. Return only the title with each word capitalized, no quotes, no explanations."
            
            response = gemini_client.models.generate_content(
                model="gemini-1.5-flash-latest",
                contents=summary_prompt,
                config={"temperature": 0.3}
            )
            
            if response.text:
                title = response.text.strip()
                if title and len(title) > 0:
                    words = title.split()
                    title = " ".join(word.capitalize() for word in words[:5])
                    return title if len(title) <= 40 else " ".join(word.capitalize() for word in clean_prompt.split()[:3])
    except:
        pass
    
    words = clean_prompt.split()
    if len(words) >= 3:
        keywords = []
        for word in words[:5]:
            if len(word) > 2 and word.lower() not in ['the', 'and', 'for', 'with', 'this', 'that', 'what', 'how', 'why', 'when']:
                keywords.append(word.capitalize())
        
        if keywords:
            title = " ".join(keywords[:4])
            if len(title) <= 40:
                return title
    
    first_words = " ".join(word.capitalize() for word in words[:3])
    return first_words if first_words else "New Chat"

class ConversationMemory:
    def __init__(self, conversation_id: str = None):
        self.conversations_dir = "conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
        
        if conversation_id:
            self.conversation_id = conversation_id
            self.filepath = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        else:
            self.conversation_id = str(uuid.uuid4())[:8]
            self.filepath = os.path.join(self.conversations_dir, f"{self.conversation_id}.json")
            self._create_new_conversation()
    
    def _create_new_conversation(self):
        conversation_data = {
            "id": self.conversation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "title": "New Chat",
            "messages": []
        }
        self._save_conversation(conversation_data)
    
    def add_message(self, role: str, content: str):
        conversation = self._load_conversation()
        
        message = {
            "id": len(conversation["messages"]) + 1,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        conversation["messages"].append(message)
        
        if role == "user" and len(conversation["messages"]) == 1:
            title = generate_chat_title(content)
            conversation["title"] = title
        
        conversation["updated_at"] = datetime.now().isoformat()
        self._save_conversation(conversation)
    
    def get_conversation_history(self, limit: int = None):
        conversation = self._load_conversation()
        messages = conversation["messages"]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_recent_context(self, max_messages: int = 10):
        messages = self.get_conversation_history(limit=max_messages)
        
        context_lines = []
        for msg in messages:
            if msg["role"] == "user":
                context_lines.append(f"User: {msg['content']}")
            else:
                context_lines.append(f"Assistant: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def get_conversation_info(self):
        conversation = self._load_conversation()
        return {
            "id": conversation["id"],
            "title": conversation["title"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "message_count": len(conversation["messages"])
        }
    
    def _load_conversation(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "id": self.conversation_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "title": "New Chat",
                "messages": []
            }
    
    def _save_conversation(self, conversation):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)

class ConversationStore:
    def __init__(self):
        self.conversations_dir = "conversations"
        os.makedirs(self.conversations_dir, exist_ok=True)
    
    def get_all_conversations(self):
        conversations = []
        
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.conversations_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'id' not in data:
                            data['id'] = filename.replace('.json', '')
                        conversations.append(data)
                except:
                    continue
        
        conversations.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return conversations
    
    def delete_conversation(self, conversation_id: str):
        filepath = os.path.join(self.conversations_dir, f"{conversation_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
