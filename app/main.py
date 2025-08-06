import streamlit as st
import sys
import os

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_handler import generate_user_story
from core.data_connector import data_connector
from core.vector_db import VectorDBConnector

# Khởi tạo vector database
@st.cache_resource
def init_vector_db():
    vdb = VectorDBConnector()
    vdb.initialize()
    return vdb

vector_db = init_vector_db()

st.set_page_config(
    page_title="BrainStory AI Agent",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 BrainStory AI Agent - Cox Automotive Integration")

# Sidebar cho cấu hình
st.sidebar.header("⚙️ Cấu hình kết nối")
st.sidebar.info("🏢 GitHub Enterprise: ghe.coxautoinc.com")
st.sidebar.info("🏢 Rally: rally1.rallydev.com")

# Vector Database Stats
st.sidebar.header("💾 Vector Database")
if vector_db.is_initialized:
    db_stats = vector_db.get_stats()
    st.sidebar.success("✅ ChromaDB đang hoạt động")
    for collection, count in db_stats.items():
        st.sidebar.metric(f"📊 {collection}", count)
else:
    st.sidebar.error("❌ Vector DB chưa khởi tạo")

# Tab chính
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Tạo User Story", "📊 GitHub Data", "🏢 Rally Data", "🔍 Vector Search"])

with tab1:
    st.header("Tạo User Story từ yêu cầu")
    
    # Tùy chọn nguồn dữ liệu
    data_source = st.selectbox(
        "Chọn nguồn dữ liệu:",
        ["Nhập thủ công", "Từ GitHub Issues", "Từ Rally Features", "Kết hợp tất cả"]
    )
    
    if data_source == "Nhập thủ công":
        input_text = st.text_area("Nhập yêu cầu tính năng, email hoặc ghi chú:")
        
        if st.button("🚀 Tạo User Story"):
            if input_text:
                with st.spinner("Đang tạo user story..."):
                    result = generate_user_story(input_text)
                    st.success("✅ Đã tạo user story!")
                    st.markdown(result)
            else:
                st.warning("Vui lòng nhập yêu cầu!")
    
    elif data_source == "Từ GitHub Issues":
        repo_input = st.text_input("Nhập GitHub Enterprise repository (vd: team/project):")
        
        if st.button("🔍 Lấy Issues từ GitHub Enterprise"):
            if repo_input:
                with st.spinner("Đang lấy dữ liệu từ GitHub Enterprise..."):
                    github_data = data_connector.get_github_data(repo_input)
                    
                    if "error" in github_data:
                        st.error(github_data["error"])
                    else:
                        st.success(f"✅ Tìm thấy {len(github_data['issues'])} issues")
                        
                        # Hiển thị danh sách issues để chọn
                        if github_data["issues"]:
                            selected_issues = st.multiselect(
                                "Chọn issues để tạo User Story:",
                                options=range(len(github_data["issues"])),
                                format_func=lambda x: f"#{github_data['issues'][x]['number']} - {github_data['issues'][x]['title']}"
                            )
                            
                            if st.button("🎯 Tạo User Story từ Issues đã chọn"):
                                if selected_issues:
                                    combined_text = "\n".join([
                                        f"Issue #{github_data['issues'][i]['number']}: {github_data['issues'][i]['title']}\n{github_data['issues'][i]['body']}"
                                        for i in selected_issues
                                    ])
                                    
                                    with st.spinner("Đang tạo user story từ GitHub issues..."):
                                        result = generate_user_story(combined_text)
                                        st.success("✅ Đã tạo user story từ GitHub Enterprise!")
                                        st.markdown(result)
                                else:
                                    st.warning("Vui lòng chọn ít nhất 1 issue!")
            else:
                st.warning("Vui lòng nhập repository!")

with tab2:
    st.header("📊 Dữ liệu GitHub Enterprise")
    
    repo_input_tab2 = st.text_input("Repository GitHub Enterprise:", key="repo_tab2", placeholder="team/project-name")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Lấy thông tin Repository"):
            if repo_input_tab2:
                with st.spinner("Đang lấy dữ liệu từ GitHub Enterprise..."):
                    github_data = data_connector.get_github_data(repo_input_tab2, include_prs=True)
                    
                    if "error" in github_data:
                        st.error(github_data["error"])
                    else:
                        # Thông tin repository
                        repo_info = github_data["repository_info"]
                        st.subheader("ℹ️ Thông tin Repository")
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("⭐ Stars", repo_info.get("stars", 0))
                        with col_b:
                            st.metric("🔀 Forks", repo_info.get("forks", 0))
                        with col_c:
                            st.metric("🐛 Open Issues", repo_info.get("open_issues", 0))
                        
                        st.write(f"**Mô tả:** {repo_info.get('description', 'Không có mô tả')}")
                        st.write(f"**Ngôn ngữ chính:** {repo_info.get('language', 'Không xác định')}")
                        
                        # Issues
                        st.subheader("🐛 Issues")
                        issues = github_data["issues"]
                        if issues:
                            for issue in issues[:10]:  # Hiển thị 10 issues đầu
                                with st.expander(f"#{issue['number']} - {issue['title']} ({issue['state']})"):
                                    st.write(f"**Labels:** {', '.join(issue['labels'])}")
                                    st.write(f"**Mô tả:** {issue['body'][:200]}...")
                        else:
                            st.info("Không có issues nào")
                        
                        # Pull Requests
                        st.subheader("🔀 Pull Requests")
                        prs = github_data["pull_requests"]
                        if prs:
                            for pr in prs[:5]:  # Hiển thị 5 PRs đầu
                                with st.expander(f"#{pr['number']} - {pr['title']} ({pr['state']})"):
                                    st.write(f"**Mô tả:** {pr['body'][:200]}...")
                        else:
                            st.info("Không có pull requests nào")
            else:
                st.warning("Vui lòng nhập repository!")

with tab3:
    st.header("🏢 Dữ liệu Rally")
    
    col1, col2 = st.columns(2)
    
    with col1:
        workspace_input = st.text_input("Workspace ID (tùy chọn):")
    with col2:
        project_input = st.text_input("Project ID (tùy chọn):")
    
    if st.button("📈 Lấy dữ liệu Rally"):
        with st.spinner("Đang lấy dữ liệu từ Rally..."):
            rally_data = data_connector.get_rally_data(workspace_input, project_input)
            
            if "error" in rally_data:
                st.error(rally_data["error"])
            else:
                # User Stories
                st.subheader("📝 User Stories")
                stories = rally_data["user_stories"]
                if stories:
                    for story in stories[:10]:
                        with st.expander(f"{story['formatted_id']} - {story['name']} ({story['state']})"):
                            st.write(f"**Plan Estimate:** {story['plan_estimate']} points")
                            st.write(f"**Owner:** {story['owner'] or 'Chưa assign'}")
                            st.write(f"**Mô tả:** {story['description'][:200]}...")
                else:
                    st.info("Không có user stories nào")
                
                # Features
                st.subheader("🚀 Features")
                features = rally_data["features"]
                if features:
                    for feature in features[:5]:
                        with st.expander(f"{feature['formatted_id']} - {feature['name']} ({feature['state']})"):
                            st.write(f"**Mô tả:** {feature['description'][:200]}...")
                else:
                    st.info("Không có features nào")
                
                # Defects
                st.subheader("🐛 Defects")
                defects = rally_data["defects"]
                if defects:
                    for defect in defects[:5]:
                        with st.expander(f"{defect['formatted_id']} - {defect['name']} ({defect['state']})"):
                            st.write(f"**Severity:** {defect['severity']}")
                            st.write(f"**Mô tả:** {defect['description'][:200]}...")
                else:
                    st.info("Không có defects nào")

with tab4:
    st.header("🔍 Vector Database Search")
    st.info("Tìm kiếm trong dữ liệu đã lưu trữ từ GitHub và Rally")
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Nhập từ khóa tìm kiếm:",
            placeholder="Ví dụ: authentication, login, user management..."
        )
    
    with col2:
        search_type = st.selectbox(
            "Nguồn dữ liệu:",
            ["all", "github", "rally"],
            format_func=lambda x: {"all": "Tất cả", "github": "GitHub", "rally": "Rally"}[x]
        )
    
    if st.button("🔍 Tìm kiếm", type="primary"):
        if search_query.strip():
            with st.spinner("Đang tìm kiếm..."):
                if vector_db.is_initialized:
                    results = vector_db.search_relevant_context(
                        search_query, 
                        context_type=search_type, 
                        limit=10
                    )
                    
                    if results:
                        st.subheader(f"📊 Tìm thấy {len(results)} kết quả liên quan")
                        
                        for i, result in enumerate(results, 1):
                            with st.expander(f"#{i} - {result['source']} (độ liên quan: {result['similarity']:.3f})"):
                                # Metadata
                                metadata = result.get('metadata', {})
                                if metadata:
                                    st.json(metadata)
                                
                                # Content
                                st.text_area(
                                    "Nội dung:",
                                    result['text'],
                                    height=100,
                                    disabled=True
                                )
                    else:
                        st.warning("Không tìm thấy kết quả nào phù hợp")
                else:
                    st.error("Vector database chưa được khởi tạo")
        else:
            st.warning("Vui lòng nhập từ khóa tìm kiếm")
    
    # Database management
    st.subheader("⚙️ Quản lý Database")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Refresh Stats"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear GitHub Data"):
            if vector_db.is_initialized:
                vector_db.clear_collection("github_data")
                st.success("Đã xóa dữ liệu GitHub")
                st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Rally Data"):
            if vector_db.is_initialized:
                vector_db.clear_collection("rally_data")
                st.success("Đã xóa dữ liệu Rally")
                st.rerun()
    
    # Show detailed stats
    if vector_db.is_initialized:
        st.subheader("📈 Chi tiết Database")
        stats = vector_db.get_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("GitHub Data", stats.get('github_data', 0))
        
        with col2:
            st.metric("Rally Data", stats.get('rally_data', 0))
        
        with col3:
            st.metric("Generated Stories", stats.get('user_stories', 0))

# Footer
st.sidebar.markdown("---")
st.sidebar.info("🔐 Tất cả dữ liệu được xử lý local để đảm bảo bảo mật")
st.sidebar.info("💾 ChromaDB lưu trữ vector embeddings cho tìm kiếm nhanh")
