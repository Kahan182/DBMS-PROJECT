# app/api/endpoints/chatbot.py

import os
import json
import traceback
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from groq import Groq

from app import security
from app.api.api import private_router
from app.chatbot.tools import tools, available_tools
from app.models.model import User

# --- Pydantic Models (No Changes) ---
class ChatTurn(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    content: str
    history: List[ChatTurn] = Field(default_factory=list)

class ChatResponse(BaseModel):
    response: str
    history: List[ChatTurn]

# --- Groq Client Setup ---
groq_api_key = os.getenv("GROQ_API_KEY") or "dummy_key"
client = Groq(api_key=groq_api_key)
LLM_MODEL = "llama-3.1-8b-instant" # Using the latest fast Llama 3.1 model

@private_router.post("/chatbot", response_model=ChatResponse, tags=["Chatbot"])
def chat_with_assistant(
    message: ChatMessage,
    db: Session = Depends(security.get_db),
    current_user: User = Depends(security.get_current_user)
):
    if not os.getenv("GROQ_API_KEY"):
        updated_history = message.history + [
            ChatTurn(role="user", content=message.content),
            ChatTurn(role="assistant", content="The AI Chatbot is currently unavailable because the GROQ_API_KEY environment variable is not configured. Please set a valid GROQ_API_KEY in your backend environment variables or a .env file to enable this feature.")
        ]
        return {
            "response": "The AI Chatbot is currently unavailable because the GROQ_API_KEY environment variable is not configured. Please set a valid GROQ_API_KEY in your backend environment variables or a .env file to enable this feature.",
            "history": updated_history
        }

    try:
        system_prompt = {"role": "system", "content": "You are a helpful, menu-driven inventory assistant..."}
        messages = [system_prompt] + [turn.dict() for turn in message.history] + [{"role": "user", "content": message.content}]
        
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            assistant_message_dict = response_message.model_dump()
            
            clean_assistant_message = {
                "role": "assistant",
                "content": assistant_message_dict.get("content"),
                "tool_calls": assistant_message_dict.get("tool_calls")
            }
            clean_assistant_message = {k: v for k, v in clean_assistant_message.items() if v is not None}
            
            messages.append(clean_assistant_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)
                
                if not function_to_call:
                    raise HTTPException(status_code=500, detail=f"Tool '{function_name}' not found.")

                function_args = json.loads(tool_call.function.arguments or "{}")
                
                if function_name == 'get_product_details':
                    function_response = function_to_call(db=db, **function_args)
                else:
                    function_response = function_to_call(db=db, current_user=current_user)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )
            
            second_response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
            )
            final_response_content = second_response.choices[0].message.content
        else:
            final_response_content = response_message.content

        updated_history = message.history + [
            ChatTurn(role="user", content=message.content),
            ChatTurn(role="assistant", content=final_response_content)
        ]
        return {"response": final_response_content, "history": updated_history}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")