# 🧠 BrainStory AI Agent

**Intelligent User Story Generator with Enterprise Integration**

BrainStory AI Agent là một công cụ AI thông minh giúp tạo User Stories chi tiết từ yêu cầu nghiệp vụ, tích hợp với GitHub Enterprise và Rally để cung cấp context phong phú và chính xác.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)
![ChromaDB](https://img.shields.io/badge/chromadb-vector--database-purple.svg)

## 🌟 Tính năng chính

### 🎯 **AI-Powered User Story Generation**
- Tạo User Stories chi tiết từ mô tả ngắn gọn
- Sử dụng local AI models (Ollama) để đảm bảo bảo mật
- Fallback mode thông minh khi không có AI models

### 🏢 **Enterprise Integration**
- **GitHub Enterprise**: Kết nối với Cox Automotive GitHub Enterprise (ghe.coxautoinc.com)
- **Rally**: Tích hợp với Rally Project Management (rally1.rallydev.com)
- **Secure**: Tất cả dữ liệu được xử lý local

### 💾 **Vector Database**
- ChromaDB để lưu trữ và tìm kiếm context
- Semantic search cho dữ liệu liên quan
- Persistent storage cho learning liên tục

### 🔍 **Smart Context Enhancement**
- Tự động thu thập context từ GitHub issues, PRs, repository info
- Lấy dữ liệu từ Rally user stories, features, defects
- Vector search trong historical data

## 🏗️ Kiến trúc hệ thống

```
BrainStory AI Agent
├── app/
│   └── main.py              # Streamlit web interface
├── core/
│   ├── llm_handler.py       # AI processing với Ollama
│   ├── data_connector.py    # GitHub & Rally integration
│   └── vector_db.py         # ChromaDB vector database
├── connectors/
│   ├── github_connector.py  # GitHub API wrapper
│   ├── rally_connector.py   # Rally API wrapper
│   └── slack_connector.py   # Slack integration (future)
├── scripts/
│   ├── start_vector_db.py   # Vector database setup
│   ├── populate_demo_data.py # Demo data population
│   └── run_agent.py         # Main runner script
└── chroma_db/               # Vector database storage
```

## 🚀 Quick Start

### 1. **Clone Repository**
```bash
git clone <repository-url>
cd brainstory_ai_agent
```

### 2. **Setup Python Environment**
```bash
# Tạo virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. **Environment Configuration**
Tạo file `.env` trong thư mục gốc:

```env
# GitHub Enterprise Configuration
GITHUB_URL=https://ghe.coxautoinc.com
GITHUB_TOKEN=your_github_enterprise_token

# Rally Configuration  
RALLY_API_KEY=your_rally_api_key

# Slack (Optional)
SLACK_TOKEN=your_slack_token
```

### 4. **Setup Vector Database**
```bash
# Khởi tạo ChromaDB
python scripts/start_vector_db.py

# Populate demo data (optional)
python scripts/populate_demo_data.py
```

### 5. **Setup Local AI (Optional but Recommended)**
```bash
# Install Ollama
# Windows: Download từ https://ollama.ai
# macOS: brew install ollama

# Pull AI models (chọn một trong các models sau)
ollama pull llama3.2:1b      # Lightest (1.3GB)
ollama pull qwen2:1.5b       # Fast & efficient (0.9GB)
ollama pull gemma2:2b        # Google model (1.6GB)
ollama pull phi3:mini        # Microsoft model (2.3GB)
```

### 6. **Run Application**
```bash
# Start Streamlit app
streamlit run app/main.py

# Hoặc sử dụng script runner
python scripts/run_agent.py
```

🌐 **Open browser**: http://localhost:8501

## 📖 Hướng dẫn sử dụng

### 🎯 **Tab 1: Tạo User Story**

1. **Nhập yêu cầu**: Mô tả ngắn gọn feature cần tạo User Story
2. **Chọn context source**: 
   - GitHub Enterprise repository
   - Rally workspace/project
   - Hoặc không sử dụng context
3. **Generate**: AI sẽ tạo User Story chi tiết với:
   - User Story format chuẩn
   - Acceptance Criteria
   - Priority và Story Points estimate
   - Dependencies (nếu có)

**Ví dụ input**: "Tạo tính năng đăng nhập bằng Google OAuth"
**Output**: User Story đầy đủ với AC, technical considerations, security requirements

### 📊 **Tab 2: GitHub Enterprise Data**

1. **Repository Explorer**: 
   - Nhập `owner/repository-name`
   - Xem repository info, README, main language
2. **Issues & PRs**: Browse recent issues và pull requests
3. **File Structure**: Khám phá cấu trúc project

### 🏢 **Tab 3: Rally Data**

1. **User Stories**: Xem các User Stories trong workspace/project
2. **Features**: Browse các Features đang phát triển
3. **Defects**: Theo dõi bugs và issues từ Rally

### 🔍 **Tab 4: Vector Search**

1. **Semantic Search**: Tìm kiếm trong historical data
2. **Filter by Source**: GitHub, Rally, hoặc tất cả
3. **Relevance Scoring**: Kết quả được sắp xếp theo độ liên quan

## 🔧 Configuration

### GitHub Enterprise Setup

1. **Generate Personal Access Token**:
   - Đăng nhập vào https://ghe.coxautoinc.com
   - Settings → Developer Settings → Personal Access Tokens
   - Generate token với scopes: `repo`, `read:org`

2. **Add to .env**:
   ```env
   GITHUB_URL=https://ghe.coxautoinc.com
   GITHUB_TOKEN=ghp_your_token_here
   ```

### Rally API Setup

1. **Get API Key**:
   - Đăng nhập Rally → Profile → API Keys
   - Generate new API key

2. **Add to .env**:
   ```env
   RALLY_API_KEY=your_rally_api_key_here
   ```

### Ollama Models Configuration

**Recommended models** (theo thứ tự ưu tiên):

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `llama3.2:1b` | 1.3GB | ⚡⚡⚡ | ⭐⭐⭐ | Quick responses |
| `qwen2:1.5b` | 0.9GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced |
| `gemma2:2b` | 1.6GB | ⚡⚡ | ⭐⭐⭐⭐ | Google quality |
| `phi3:mini` | 2.3GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Microsoft, highest quality |

## 🛠️ Development

### Project Structure
```
├── app/                    # Frontend Streamlit app
├── core/                   # Core business logic
├── connectors/            # External service integrations  
├── scripts/               # Utility scripts
├── chroma_db/            # Vector database storage
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

### Adding New Features

1. **New Connector**: Add to `connectors/` folder
2. **Core Logic**: Extend `core/` modules
3. **UI Components**: Update `app/main.py`
4. **Vector DB**: Use `core/vector_db.py` for storage

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_URL` | Yes | GitHub Enterprise URL |
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `RALLY_API_KEY` | Yes | Rally API Key |
| `SLACK_TOKEN` | No | Slack Bot Token (future feature) |

## 🐛 Troubleshooting

### Common Issues

**1. Ollama Models Not Found**
```bash
# Check Ollama service
ollama list

# Pull missing models
ollama pull llama3.2:1b
```

**2. GitHub API Connection Error**
- Verify `GITHUB_TOKEN` có quyền truy cập repository
- Check GitHub Enterprise URL format
- Ensure token chưa expired

**3. Rally API Authentication Error**
- Verify `RALLY_API_KEY` in .env file
- Check Rally permissions cho workspace/project
- Test connection với Rally web interface

**4. ChromaDB Issues**
```bash
# Reset vector database
rm -rf chroma_db/
python scripts/start_vector_db.py
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=1
streamlit run app/main.py

# Or run debug scripts
python scripts/debug_rally.py
python scripts/test_github_connection.py
```

## 📊 Performance

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for Ollama models + 500MB for app
- **Network**: Stable connection cho GitHub/Rally APIs

### Optimization Tips
1. **Use smaller AI models** cho faster responses
2. **Enable vector DB caching** để giảm API calls
3. **Limit context data** để tránh prompt quá dài

## 🔒 Security

### Data Privacy
- ✅ **Local AI Processing**: Ollama models chạy local
- ✅ **No External AI APIs**: Không gửi data đến OpenAI/Claude
- ✅ **Encrypted Storage**: ChromaDB local storage
- ✅ **Secure Tokens**: Environment variables cho credentials

### Best Practices
1. **Rotate API tokens** định kỳ
2. **Use limited scope tokens** (chỉ cần thiết)
3. **Don't commit .env** file vào git
4. **Regular security updates** cho dependencies

## 📈 Roadmap

### V1.1 (Next Release)
- [ ] Slack integration cho notifications
- [ ] Advanced filtering cho vector search  
- [ ] Bulk User Story generation
- [ ] Export functionality (PDF, DOCX)

### V1.2 (Future)
- [ ] JIRA integration
- [ ] Custom AI model training
- [ ] Team collaboration features
- [ ] Analytics dashboard

## 🤝 Contributing

1. **Fork** the repository
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: GitHub Issues tracker
- **Documentation**: This README + inline code comments
- **Team**: Cox Automotive Development Team

---

**Made with ❤️ for Cox Automotive by BrainStory AI Team**

🚀 **Happy User Story Generation!** 🚀