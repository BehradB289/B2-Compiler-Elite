import os
import sys
import time
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import litellm


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BG_RED = '\033[41m'


logging.getLogger("uvicorn.access").disabled = True
logging.getLogger("litellm").setLevel(logging.ERROR)


app = FastAPI(
    title="BehradB2 Elite Compiler",
    description="سرور کامپایلر آبشاری با قابلیت دیباگ خودکار و مقاومت در برابر قطعی",
    version="4.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VALID_API_KEY = "sk-33c30ed152582727-i4wntx-55470e71"
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def verify_api_key(auth_header: str = Depends(api_key_header)):
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    token = auth_header.replace("Bearer ", "").strip()
    if token != VALID_API_KEY:
        print(f"{Colors.BG_RED}{Colors.BOLD} ⚠️ UNAUTHORIZED ACCESS ATTEMPT ⚠️ {Colors.ENDC} Token: {token[:10]}...")
        raise HTTPException(status_code=403, detail="Invalid API Key for BehradB2 System")
    return token


COMPILER_ELITE_FALLBACKS = [
    {"name": "DeepSeek V4 Pro", "id": "nvidia/deepseek-ai/deepseek-v4-pro"},
    {"name": "Claude Sonnet 4.6", "id": "anthropic/claude-3-5-sonnet-20241022"},
    {"name": "Qwen 2.5 Coder 32B", "id": "cloudflare/@cf/qwen/qwen2.5-coder-32b-instruct"},
    {"name": "Gemini 1.5 Pro", "id": "gemini/gemini-1.5-pro"},
    {"name": "Llama 3.3 70B", "id": "groq/llama-3.3-70b-versatile"}
]


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.5
    max_tokens: Optional[int] = 8192
    stream: Optional[bool] = False


async def safe_stream_generator(response_generator, model_name: str, start_time: float):
    """مدیریت استریم و محاسبه زمان اجرای موفق"""
    token_count = 0
    try:
        for chunk in response_generator:
            if chunk:
                token_count += 1
                yield f"data: {chunk.model_dump_json()}\n\n"
        
        elapsed = time.time() - start_time
        yield "data: [DONE]\n\n"
        print(f"{Colors.GREEN}│ ✅ STREAM COMPLETE: {model_name} ({token_count} tokens in {elapsed:.2f}s){Colors.ENDC}")
        print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.RED}│ ❌ STREAM INTERRUPTED: {str(e)}{Colors.ENDC}")
        yield f"data: {{\"error\": \"Stream interrupted: {str(e)}\"}}\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    api_key: str = Depends(verify_api_key)
):
    req_model = request.model.strip()
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    
    user_query = "No user prompt found"
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_query = msg.content.replace("\n", " ")[:70] + "..."
            break

    print(f"\n{Colors.CYAN}┌─────────────────────────────────────────────────────────────┐{Colors.ENDC}")
    print(f"{Colors.CYAN}│ 📥 INCOMING REQUEST {Colors.ENDC}")
    print(f"{Colors.CYAN}│ 🤖 Target Model: {Colors.BOLD}{Colors.YELLOW}{req_model}{Colors.ENDC}")
    print(f"{Colors.CYAN}│ 💬 Prompt: {user_query}{Colors.ENDC}")
    print(f"{Colors.CYAN}├─────────────────────────────────────────────────────────────┤{Colors.ENDC}")

    
    if "b2-compiler-elite" in req_model.lower():
        last_error = None
        start_process_time = time.time()
        
        for attempt, model_info in enumerate(COMPILER_ELITE_FALLBACKS):
            layer_num = attempt + 1
            model_id = model_info["id"]
            friendly_name = model_info["name"]
            
            print(f"{Colors.BLUE}│ 🔄 Layer {layer_num}/5 | Engaging: {friendly_name} ...{Colors.ENDC}")
            
            try:
                
                response = litellm.completion(
                    model=f"openai/{model_id}", 
                    api_base="http://localhost:20128/v1", 
                    api_key=VALID_API_KEY, 
                    messages=formatted_messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=request.stream,
                    timeout=20.0 
                )
                
                
                if request.stream:
                    return StreamingResponse(
                        safe_stream_generator(response, friendly_name, start_process_time),
                        media_type="text/event-stream"
                    )
                
                
                elapsed = time.time() - start_process_time
                print(f"{Colors.GREEN}│ ✅ SUCCESS: Generated by {friendly_name} in {elapsed:.2f}s{Colors.ENDC}")
                print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
                return response

            except Exception as e:
                
                error_msg = str(e)
                short_error = error_msg[:60] + "..." if len(error_msg) > 60 else error_msg
                print(f"{Colors.RED}│ ⚠️ FAILED: {friendly_name} -> {short_error}{Colors.ENDC}")
                last_error = error_msg
                continue 

       
        print(f"{Colors.BG_RED}{Colors.BOLD} 💥 CRITICAL FAILURE: All 5 Elite Models Failed! 💥 {Colors.ENDC}")
        print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
        raise HTTPException(
            status_code=503, 
            detail=f"B2-Compiler-Elite cascade exhausted. Last error: {last_error}"
        )


    else:
        start_process_time = time.time()
        try:
            print(f"{Colors.BLUE}│ ➡️ Executing direct passthrough for: {req_model}{Colors.ENDC}")
            
            safe_model_name = req_model if req_model.startswith("openai/") else f"openai/{req_model}"
            
            response = litellm.completion(
                model=safe_model_name,
                api_base="http://localhost:20128/v1", 
                api_key=VALID_API_KEY,
                messages=formatted_messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
            
            if request.stream:
                return StreamingResponse(
                    safe_stream_generator(response, req_model, start_process_time),
                    media_type="text/event-stream"
                )
                
            elapsed = time.time() - start_process_time
            print(f"{Colors.GREEN}│ ✅ SUCCESS: Response ready in {elapsed:.2f}s{Colors.ENDC}")
            print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
            return response
            
        except Exception as e:
            print(f"{Colors.RED}│ ❌ CRITICAL ERROR: {str(e)}{Colors.ENDC}")
            print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────┘{Colors.ENDC}\n")
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=======================================================================")
    print(" 🚀 BEHRADB2 AUTONOMOUS COMPILER & FALLBACK ROUTER IS ONLINE 🚀")
    print("=======================================================================")
    print(f" {Colors.GREEN}📍 New Endpoint :{Colors.ENDC} http://localhost:20129/v1")
    print(f" {Colors.GREEN}🔑 API Key      :{Colors.ENDC} {VALID_API_KEY}")
    print(f" {Colors.GREEN}🧠 Cascade Name :{Colors.ENDC} B2-Compiler-Elite")
    print(f"\n {Colors.YELLOW}⚡ Aider Setup Command:{Colors.ENDC}")
    print(f" aider --openai --openai-api-base http://localhost:20129/v1 \\")
    print(f"       --openai-api-key {VALID_API_KEY} \\")
    print(f"       --model B2-Compiler-Elite")
    print(f"{Colors.CYAN}======================================================================={Colors.ENDC}")
    
    
    uvicorn.run(app, host="0.0.0.0", port=20129, log_level="critical")
