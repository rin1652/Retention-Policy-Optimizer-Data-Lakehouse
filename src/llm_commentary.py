import os
import json
import logging
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

def get_prompt_template() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "report-commentary.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logging.warning(f"Could not read prompt template: {e}")
        return "Given the experiment metrics below, summarize the result in 3–5 sentences. Respond in Vietnamese."

def generate_commentary(metrics_json: dict, run_id: str) -> dict:
    """
    Nhận metrics JSON và tạo 3-5 câu nhận xét qua LLM thật.
    - LLM chỉ diễn giải số đo, không điều khiển logic.
    - Lưu các thông tin log: model, prompt, response, status và run ID.
    - Xử lý timeout/error và trả về trạng thái thiếu nhận xét.
    """
    load_dotenv()
    
    provider = os.getenv("LLM_PROVIDER", "fpt").lower()
    model = os.getenv("LLM_MODEL", "DeepSeek-V4-Flash")
    timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    
    prompt_template = get_prompt_template()
    metrics_str = json.dumps(metrics_json, indent=2, ensure_ascii=False)
    
    full_prompt = f"{prompt_template}\n\nMetrics:\n{metrics_str}"
    
    result = {
        "run_id": run_id,
        "model": model,
        "provider": provider,
        "prompt": full_prompt,
        "response": None,
        "status": "pending",
        "error_message": None
    }
    
    try:
        if provider == "gemini":
            if not genai:
                raise ImportError("Thư viện google-genai chưa được cài đặt")
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
                raise ValueError("GEMINI_API_KEY chưa được cấu hình")
                
            client = genai.Client(api_key=api_key)
            # API Gemini của SDK mới có thể chưa nhận timeout trong config trực tiếp, 
            # tuy nhiên lỗi kết nối nếu quá thời gian sẽ raise exception.
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    system_instruction="Bạn là chuyên gia phân tích dữ liệu Data Lakehouse. Hãy trả lời bằng tiếng Việt."
                )
            )
            result["response"] = response.text
            result["status"] = "success"
            
        elif provider in ["fpt", "openai"]:
            if not openai:
                raise ImportError("Thư viện openai chưa được cài đặt")
            
            api_key = os.getenv("FPT_API_KEY") if provider == "fpt" else os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("FPT_API_BASE") if provider == "fpt" else None
            
            if not api_key or api_key == "YOUR_FPT_API_KEY_HERE":
                raise ValueError(f"{'FPT_API_KEY' if provider == 'fpt' else 'OPENAI_API_KEY'} chưa được cấu hình")
                
            client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia phân tích dữ liệu Data Lakehouse. Hãy trả lời bằng tiếng Việt."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.0
            )
            result["response"] = response.choices[0].message.content
            result["status"] = "success"
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
            
    except Exception as e:
        error_name = type(e).__name__
        if "timeout" in str(e).lower() or "Timeout" in error_name:
            result["status"] = "timeout"
        else:
            result["status"] = "error"
        result["error_message"] = f"{error_name}: {str(e)}"
        logging.error(f"Lỗi gọi LLM: {result['error_message']}")
        
    return result
