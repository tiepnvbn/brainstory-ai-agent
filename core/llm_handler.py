from langchain_community.llms import Ollama
import os
import requests
import time
from .vector_db import VectorDBConnector

# Khởi tạo Vector DB connector
vector_db = VectorDBConnector()

def generate_user_story(prompt: str, context_data: dict = None) -> str:
    """Tao user story voi Ollama local - bao mat tuyet doi"""
    
    # Khởi tạo vector DB nếu chưa
    if not vector_db.is_initialized:
        vector_db.initialize()
    
    # Tìm kiếm context liên quan từ vector DB
    relevant_context = []
    if vector_db.is_initialized:
        relevant_context = vector_db.search_relevant_context(prompt, limit=3)
    
    # Kết hợp context data từ API và vector DB
    if context_data or relevant_context:
        enhanced_prompt = enhance_prompt_with_context(prompt, context_data, relevant_context)
    else:
        enhanced_prompt = prompt
    
    # Lưu context vào vector DB nếu có
    if context_data and vector_db.is_initialized:
        store_context_to_vector_db(context_data)
    
    # Thu cac model nhe theo thu tu uu tien
    models_to_try = [
        "llama3.2:1b",     # Nhe nhat (1.3GB)
        "llama3.2:3b",     # Trung binh (2GB) 
        "qwen2:1.5b",      # Nhe, hieu qua (0.9GB)
        "gemma2:2b",       # Google, nhe (1.6GB)
        "phi3:mini"        # Microsoft, rat nhe (2.3GB)
    ]
    
    generated_story = None
    for model in models_to_try:
        try:
            print(f"Dang thu model: {model}")
            result = generate_with_ollama(enhanced_prompt, model)
            print(f"Thanh cong voi model: {model}")
            generated_story = result
            break
        except Exception as e:
            print(f"Model {model} loi: {str(e)}")
            continue
    
    # Fallback: Huong dan cai dat
    if not generated_story:
        generated_story = generate_setup_guide(enhanced_prompt)
    
    # Lưu generated story vào vector DB
    if generated_story and vector_db.is_initialized:
        vector_db.store_generated_story(generated_story, {
            "prompt": prompt,
            "has_context": bool(context_data)
        })
    
    return generated_story

def store_context_to_vector_db(context_data):
    """Lưu context data vào vector database"""
    try:
        if "github" in context_data:
            github_data = context_data["github"]
            repo_owner = github_data.get("repo_owner", "unknown")
            repo_name = github_data.get("repo_name", "unknown")
            
            vector_db.add_github_context(repo_owner, repo_name, {
                "repo_info": github_data.get("repository_info"),
                "issues": github_data.get("issues", [])
            })
        
        if "rally" in context_data:
            rally_data = context_data["rally"]
            vector_db.add_rally_context({
                "stories": rally_data.get("user_stories", [])
            })
            
    except Exception as e:
        print(f"Error storing context to vector DB: {e}")

def enhance_prompt_with_context(prompt: str, context_data: dict = None, relevant_context: list = None) -> str:
    """Ket hop prompt voi du lieu tu GitHub/Rally va vector DB"""
    enhanced = f"YEU CAU CHINH: {prompt}\n\n"
    
    # Thêm context từ vector DB (dữ liệu lịch sử)
    if relevant_context:
        enhanced += "DU LIEU LIEN QUAN TU DATABASE:\n"
        for i, ctx in enumerate(relevant_context[:3], 1):
            source = ctx.get('source', 'unknown')
            similarity = ctx.get('similarity', 0)
            text_preview = ctx.get('text', '')[:200] + "..."
            enhanced += f"  {i}. [{source}] (độ liên quan: {similarity:.2f})\n"
            enhanced += f"     {text_preview}\n\n"
    
    # Thêm context data hiện tại
    if context_data:
        # Them du lieu GitHub neu co
        if "github" in context_data:
            github_data = context_data["github"]
            enhanced += "DU LIEU HIEN TAI TU GITHUB:\n"
            
            if "repository_info" in github_data:
                repo = github_data["repository_info"]
                enhanced += f"- Repository: {repo.get('name')} ({repo.get('language')})\n"
                enhanced += f"- Mo ta: {repo.get('description', 'Khong co')}\n"
        
        if "issues" in github_data and github_data["issues"]:
            enhanced += f"- Co {len(github_data['issues'])} issues:\n"
            for issue in github_data["issues"][:3]:  # Chi lay 3 issues dau
                enhanced += f"  + #{issue['number']}: {issue['title']}\n"
        
        enhanced += "\n"
    
    # Them du lieu Rally neu co
    if "rally" in context_data:
        rally_data = context_data["rally"]
        enhanced += "DU LIEU TU RALLY:\n"
        
        if "user_stories" in rally_data and rally_data["user_stories"]:
            enhanced += f"- Co {len(rally_data['user_stories'])} user stories:\n"
            for story in rally_data["user_stories"][:3]:
                enhanced += f"  + {story['formatted_id']}: {story['name']} ({story['state']})\n"
        
        if "features" in rally_data and rally_data["features"]:
            enhanced += f"- Co {len(rally_data['features'])} features:\n"
            for feature in rally_data["features"][:2]:
                enhanced += f"  + {feature['formatted_id']}: {feature['name']}\n"
        
        enhanced += "\n"
    
    enhanced += "TASK: Tao User Story chi tiet dua tren yeu cau chinh va du lieu context tren."
    
    return enhanced

def generate_with_ollama(prompt: str, model: str) -> str:
    """Ket noi voi Ollama local"""
    
    # Kiem tra Ollama service co chay khong
    if not check_ollama_running():
        raise Exception("Ollama service khong chay")
    
    # Kiem tra model co ton tai khong
    if not check_model_exists(model):
        raise Exception(f"Model {model} chua duoc tai")
    
    llm = Ollama(
        model=model, 
        options={
            "temperature": 0.3,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 2048
        }
    )
    
    instruction = f"""Ban la chuyen gia Product Owner trong phat trien phan mem Agile.
Nhiem vu: Tao User Story chuyen nghiep tu yeu cau sau: "{prompt}"

Format tra ve:
## TIEU DE USER STORY
La [vai tro], toi muon [chuc nang] de [muc dich/loi ich].

## MO TA CHI TIET
[Mo ta chi tiet tinh nang va ngu canh su dung]

## GIA TRI KINH DOANH
- [Loi ich 1]
- [Loi ich 2] 
- [Loi ich 3]

## TIEU CHI CHAP NHAN (ACCEPTANCE CRITERIA)
- [ ] Given [dieu kien], When [hanh dong], Then [ket qua mong doi]
- [ ] Given [dieu kien], When [hanh dong], Then [ket qua mong doi]
- [ ] Given [dieu kien], When [hanh dong], Then [ket qua mong doi]

## UOC LUONG
- Story Points: [1-13]
- Priority: [High/Medium/Low]
"""
    
    return llm.invoke(instruction)

def check_ollama_running() -> bool:
    """Kiem tra Ollama service co dang chay khong"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_model_exists(model: str) -> bool:
    """Kiem tra model co ton tai trong Ollama khong"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return any(m['name'].startswith(model.split(':')[0]) for m in models)
    except:
        pass
    return False

def generate_setup_guide(prompt: str) -> str:
    """Tao user story chi tiet cho demo khi khong co AI model"""
    
    # Phan tich prompt de tao response thong minh hon
    prompt_lower = prompt.lower()
    
    # Xac dinh vai tro tu prompt
    role = "nguoi dung"
    if any(word in prompt_lower for word in ["admin", "quan tri", "manager"]):
        role = "quan tri vien"
    elif any(word in prompt_lower for word in ["dev", "developer", "lap trinh"]):
        role = "lap trinh vien"
    elif any(word in prompt_lower for word in ["khach hang", "customer", "client"]):
        role = "khach hang"
    
    # Xac dinh do uu tien
    priority = "Medium"
    if any(word in prompt_lower for word in ["khan cap", "urgent", "gap", "quan trong"]):
        priority = "High"
    elif any(word in prompt_lower for word in ["khong gap", "thuong", "binh thuong"]):
        priority = "Low"
    
    # Uoc luong story points dua tren do phuc tap
    story_points = "5"
    if any(word in prompt_lower for word in ["don gian", "simple", "de"]):
        story_points = "3"
    elif any(word in prompt_lower for word in ["phuc tap", "complex", "kho", "tich hop"]):
        story_points = "8"
    
    return f"""
## TIEU DE USER STORY
La mot **{role}**, toi muon **{prompt[:60]}...** de co the cai thien quy trinh lam viec va trai nghiem su dung.

## MO TA CHI TIET  
Tinh nang nay se giup {role} thuc hien viec {prompt[:40]}... mot cach hieu qua va thuan tien hon. 
He thong can dam bao tinh bao mat, hieu suat cao va giao dien than thien voi nguoi dung.

## GIA TRI KINH DOANH
- **Tang hieu suat:** Giam thoi gian thuc hien cong viec len den 30%
- **Cai thien UX:** Nang cao trai nghiem nguoi dung va do hai long
- **Toi uu quy trinh:** Don gian hoa cac buoc thuc hien cong viec
- **Bao mat du lieu:** Dam bao an toan thong tin nhay cam

## TIEU CHI CHAP NHAN (ACCEPTANCE CRITERIA)
- [ ] **Given** nguoi dung truy cap he thong, **When** thuc hien chuc nang, **Then** he thong phan hoi trong vong 2 giay
- [ ] **Given** du lieu duoc nhap vao, **When** validate, **Then** hien thi thong bao loi ro rang neu co
- [ ] **Given** chuc nang hoat dong, **When** co loi xay ra, **Then** he thong tu khoi phuc hoac bao loi
- [ ] **Given** tinh nang hoan thanh, **When** test tren cac device, **Then** hoat dong on dinh tren desktop/mobile

## UOC LUONG
- **Story Points:** {story_points}
- **Priority:** {priority}
- **Estimated Time:** {int(story_points) * 2} hours

---
CANH BAO: DEMO MODE - AI LOCAL CAN THIET CHO BAO MAT

BAO MAT: De bao ve du lieu nhay cam, ban can AI local:

**Cach 1: Ollama (Khuyen nghi)**
```bash
ollama pull qwen2:1.5b
ollama pull llama3.2:1b
```

**Cach 2: Su dung script tu dong**
```bash
powershell -ExecutionPolicy Bypass -File scripts/setup_ollama.ps1
```

**Loi ich AI Local:**
- TICK **100% Bao mat** - Du lieu khong roi khoi may
- TICK **Khong phu thuoc mang** - Hoat dong offline  
- TICK **Khong chi phi API** - Mien phi hoan toan
- TICK **Tuy chinh duoc** - Co the fine-tune model
"""
