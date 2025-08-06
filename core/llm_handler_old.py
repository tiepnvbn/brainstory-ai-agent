from langchain_community.llms import Ollama
import os
import requests
import time

def generate_user_story(prompt: str) -> str:
    """Tạo user story với Ollama local - bảo mật tuyệt đối"""
    
    # Thử các model nhẹ theo thứ tự ưu tiên
    models_to_try = [
        "llama3.2:1b",     # Nhẹ nhất (1.3GB)
        "llama3.2:3b",     # Trung bình (2GB) 
        "qwen2:1.5b",      # Nhẹ, hiệu quả (0.9GB)
        "gemma2:2b",       # Google, nhẹ (1.6GB)
        "phi3:mini"        # Microsoft, rất nhẹ (2.3GB)
    ]
    
    for model in models_to_try:
        try:
            print(f"🔄 Đang thử model: {model}")
            result = generate_with_ollama(prompt, model)
            print(f"✅ Thành công với model: {model}")
            return result
        except Exception as e:
            print(f"❌ Model {model} lỗi: {str(e)}")
            continue
    
    # Fallback: Hướng dẫn cài đặt
    return generate_setup_guide(prompt)

def generate_with_ollama(prompt: str, model: str) -> str:
    """Kết nối với Ollama local"""
    
    # Kiểm tra Ollama service có chạy không
    if not check_ollama_running():
        raise Exception("Ollama service không chạy")
    
    # Kiểm tra model có tồn tại không
    if not check_model_exists(model):
        raise Exception(f"Model {model} chưa được tải")
    
    llm = Ollama(
        model=model, 
        options={
            "temperature": 0.3,
            "top_p": 0.9,
            "top_k": 40,
            "num_ctx": 2048
        }
    )
    
    instruction = f"""Bạn là chuyên gia Product Owner trong phát triển phần mềm Agile.
Nhiệm vụ: Tạo User Story chuyên nghiệp từ yêu cầu sau: "{prompt}"

Format trả về:
## 🎯 TIÊU ĐỀ USER STORY
Là [vai trò], tôi muốn [chức năng] để [mục đích/lợi ích].

## 📝 MÔ TẢ CHI TIẾT
[Mô tả chi tiết tính năng và ngữ cảnh sử dụng]

## 💼 GIÁ TRỊ KINH DOANH
- [Lợi ích 1]
- [Lợi ích 2] 
- [Lợi ích 3]

## ✅ TIÊU CHÍ CHẤP NHẬN (ACCEPTANCE CRITERIA)
- [ ] Given [điều kiện], When [hành động], Then [kết quả mong đợi]
- [ ] Given [điều kiện], When [hành động], Then [kết quả mong đợi]
- [ ] Given [điều kiện], When [hành động], Then [kết quả mong đợi]

## 📏 ƯỚC LƯỢNG
- Story Points: [1-13]
- Priority: [High/Medium/Low]
"""
    
    return llm.invoke(instruction)

def check_ollama_running() -> bool:
    """Kiểm tra Ollama service có đang chạy không"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_model_exists(model: str) -> bool:
    """Kiểm tra model có tồn tại trong Ollama không"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return any(m['name'].startswith(model.split(':')[0]) for m in models)
    except:
        pass
    return False

def generate_setup_guide(prompt: str) -> str:
    """Tạo hướng dẫn cài đặt khi không thể kết nối Ollama"""
    return f"""
## 📋 User Story (Demo Mode)

**Yêu cầu nhận được:** {prompt}

---

### 🎯 **Tiêu đề:**
Là một người dùng, tôi muốn {prompt[:50]}... để có thể cải thiện trải nghiệm sử dụng.

### 📝 **Mô tả ngắn:**
Tính năng này sẽ giúp người dùng thực hiện việc {prompt[:30]}... một cách dễ dàng và hiệu quả hơn.

### 💼 **Mục tiêu kinh doanh:**
- Tăng trải nghiệm người dùng
- Cải thiện hiệu suất hệ thống  
- Đáp ứng nhu cầu thực tế của khách hàng

### ✅ **Tiêu chí chấp nhận:**
- [ ] Giao diện thân thiện và dễ sử dụng
- [ ] Hoạt động ổn định trên các thiết bị khác nhau
- [ ] Có validation và xử lý lỗi phù hợp
- [ ] Được test kỹ lưỡng trước khi release

def generate_setup_guide(prompt: str) -> str:
    """Tạo user story chi tiết cho demo khi không có AI model"""
    
    # Phân tích prompt để tạo response thông minh hơn
    prompt_lower = prompt.lower()
    
    # Xác định vai trò từ prompt
    role = "người dùng"
    if any(word in prompt_lower for word in ["admin", "quản trị", "manager"]):
        role = "quản trị viên"
    elif any(word in prompt_lower for word in ["dev", "developer", "lập trình"]):
        role = "lập trình viên"
    elif any(word in prompt_lower for word in ["khách hàng", "customer", "client"]):
        role = "khách hàng"
    
    # Xác định độ ưu tiên
    priority = "Medium"
    if any(word in prompt_lower for word in ["khẩn cấp", "urgent", "gấp", "quan trọng"]):
        priority = "High"
    elif any(word in prompt_lower for word in ["không gấp", "thường", "bình thường"]):
        priority = "Low"
    
    # Ước lượng story points dựa trên độ phức tạp
    story_points = "5"
    if any(word in prompt_lower for word in ["đơn giản", "simple", "dễ"]):
        story_points = "3"
    elif any(word in prompt_lower for word in ["phức tạp", "complex", "khó", "tích hợp"]):
        story_points = "8"
    
    return f"""
## 🎯 TIÊU ĐỀ USER STORY
Là một **{role}**, tôi muốn **{prompt[:60]}...** để có thể cải thiện quy trình làm việc và trải nghiệm sử dụng.

## 📝 MÔ TẢ CHI TIẾT  
Tính năng này sẽ giúp {role} thực hiện việc {prompt[:40]}... một cách hiệu quả và thuận tiện hơn. 
Hệ thống cần đảm bảo tính bảo mật, hiệu suất cao và giao diện thân thiện với người dùng.

## 💼 GIÁ TRỊ KINH DOANH
- **Tăng hiệu suất:** Giảm thời gian thực hiện công việc lên đến 30%
- **Cải thiện UX:** Nâng cao trải nghiệm người dùng và độ hài lòng
- **Tối ưu quy trình:** Đơn giản hóa các bước thực hiện công việc
- **Bảo mật dữ liệu:** Đảm bảo an toàn thông tin nhạy cảm

## ✅ TIÊU CHÍ CHẤP NHẬN (ACCEPTANCE CRITERIA)
- [ ] **Given** người dùng truy cập hệ thống, **When** thực hiện chức năng, **Then** hệ thống phản hồi trong vòng 2 giây
- [ ] **Given** dữ liệu được nhập vào, **When** validate, **Then** hiển thị thông báo lỗi rõ ràng nếu có
- [ ] **Given** chức năng hoạt động, **When** có lỗi xảy ra, **Then** hệ thống tự khôi phục hoặc báo lỗi
- [ ] **Given** tính năng hoàn thành, **When** test trên các device, **Then** hoạt động ổn định trên desktop/mobile

## 📏 ƯỚC LƯỢNG
- **Story Points:** {story_points}
- **Priority:** {priority}
- **Estimated Time:** {int(story_points) * 2} hours

---
CANH BAO: DEMO MODE - AI LOCAL CAN THIET CHO BAO MAT

BAO MAT: De bao ve du lieu nhay cam, ban can AI local:

**Cach 1: Ollama (Khuyen nghi)**
```bash
# Tai Ollama tu: https://ollama.ai/download
# Sau khi cai dat:
ollama pull qwen2:1.5b    # Model nhe nhat (0.9GB)
# hoac
ollama pull llama3.2:1b   # Model thay the (1.3GB)
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
