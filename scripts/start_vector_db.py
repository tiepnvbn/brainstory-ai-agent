#!/usr/bin/env python3
"""
ChromaDB Vector Database Setup và Management Script
Sử dụng để setup vector database cho việc lưu trữ và tìm kiếm dữ liệu từ GitHub và Rally
"""

import chromadb
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_connector import DataConnector


class VectorDBManager:
    def __init__(self, db_path="./chroma_db"):
        """
        Khởi tạo ChromaDB Manager
        
        Args:
            db_path: Đường dẫn đến thư mục lưu trữ ChromaDB
        """
        self.db_path = db_path
        self.client = None
        self.collections = {}
        
    def initialize_db(self):
        """Khởi tạo ChromaDB client và tạo collections"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # Khởi tạo ChromaDB client
            self.client = chromadb.PersistentClient(path=self.db_path)
            print(f"✅ Đã khởi tạo ChromaDB tại: {self.db_path}")
            
            # Tạo collections cho các loại dữ liệu khác nhau
            self._create_collections()
            
            return True
        except Exception as e:
            print(f"❌ Lỗi khởi tạo ChromaDB: {e}")
            return False
    
    def _create_collections(self):
        """Tạo các collections cho GitHub và Rally data"""
        collections_config = {
            "github_issues": {
                "name": "github_issues",
                "metadata": {"hnsw:space": "cosine"},
                "description": "GitHub Issues và Pull Requests"
            },
            "github_repos": {
                "name": "github_repos", 
                "metadata": {"hnsw:space": "cosine"},
                "description": "GitHub Repository information"
            },
            "rally_stories": {
                "name": "rally_stories",
                "metadata": {"hnsw:space": "cosine"}, 
                "description": "Rally User Stories"
            },
            "rally_features": {
                "name": "rally_features",
                "metadata": {"hnsw:space": "cosine"},
                "description": "Rally Features"
            },
            "rally_defects": {
                "name": "rally_defects",
                "metadata": {"hnsw:space": "cosine"},
                "description": "Rally Defects"
            }
        }
        
        for collection_key, config in collections_config.items():
            try:
                # Kiểm tra xem collection đã tồn tại chưa
                try:
                    collection = self.client.get_collection(config["name"])
                    print(f"📦 Collection '{config['name']}' đã tồn tại")
                except:
                    # Tạo collection mới nếu chưa tồn tại
                    collection = self.client.create_collection(
                        name=config["name"],
                        metadata=config["metadata"]
                    )
                    print(f"✅ Đã tạo collection '{config['name']}' - {config['description']}")
                
                self.collections[collection_key] = collection
                
            except Exception as e:
                print(f"❌ Lỗi tạo collection '{config['name']}': {e}")
    
    def add_github_data(self, repo_owner, repo_name, force_refresh=False):
        """
        Thêm dữ liệu GitHub vào vector database
        
        Args:
            repo_owner: Tên owner của repository
            repo_name: Tên repository
            force_refresh: Có force làm mới dữ liệu không
        """
        try:
            print(f"🔄 Đang thu thập dữ liệu GitHub từ {repo_owner}/{repo_name}...")
            
            # Khởi tạo data connector
            connector = DataConnector()
            
            # Lấy thông tin repository
            repo_info = connector._get_repo_info(repo_owner, repo_name)
            if repo_info:
                self._add_repo_to_vector_db(repo_info, repo_owner, repo_name)
            
            # Lấy issues và PRs
            issues = connector._get_github_issues(repo_owner, repo_name)
            if issues:
                self._add_issues_to_vector_db(issues, repo_owner, repo_name)
                
            print(f"✅ Đã thêm dữ liệu GitHub {repo_owner}/{repo_name} vào vector database")
            
        except Exception as e:
            print(f"❌ Lỗi thêm dữ liệu GitHub: {e}")
    
    def _add_repo_to_vector_db(self, repo_info, repo_owner, repo_name):
        """Thêm thông tin repository vào vector database"""
        if "github_repos" not in self.collections:
            return
            
        collection = self.collections["github_repos"]
        
        # Tạo document text từ repo info
        doc_text = f"""
        Repository: {repo_owner}/{repo_name}
        Description: {repo_info.get('description', 'No description')}
        Language: {repo_info.get('language', 'Unknown')}
        Topics: {', '.join(repo_info.get('topics', []))}
        README: {repo_info.get('readme', 'No README')}
        """
        
        doc_id = f"repo_{repo_owner}_{repo_name}"
        
        # Thêm vào collection
        collection.add(
            documents=[doc_text],
            ids=[doc_id],
            metadatas=[{
                "type": "repository",
                "owner": repo_owner,
                "name": repo_name,
                "language": repo_info.get('language', 'Unknown'),
                "created_at": repo_info.get('created_at', ''),
                "updated_at": datetime.now().isoformat()
            }]
        )
        
        print(f"📦 Đã thêm repository {repo_owner}/{repo_name} vào vector DB")
    
    def _add_issues_to_vector_db(self, issues, repo_owner, repo_name):
        """Thêm GitHub issues/PRs vào vector database"""
        if "github_issues" not in self.collections:
            return
            
        collection = self.collections["github_issues"]
        
        documents = []
        ids = []
        metadatas = []
        
        for issue in issues:
            # Tạo document text từ issue
            doc_text = f"""
            Title: {issue.get('title', '')}
            Body: {issue.get('body', '')}
            State: {issue.get('state', '')}
            Labels: {', '.join([label.get('name', '') for label in issue.get('labels', [])])}
            """
            
            doc_id = f"issue_{repo_owner}_{repo_name}_{issue.get('number', 0)}"
            
            documents.append(doc_text)
            ids.append(doc_id)
            metadatas.append({
                "type": "issue" if not issue.get('pull_request') else "pull_request",
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "number": issue.get('number', 0),
                "state": issue.get('state', ''),
                "created_at": issue.get('created_at', ''),
                "updated_at": datetime.now().isoformat()
            })
        
        if documents:
            # Thêm batch vào collection
            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"📝 Đã thêm {len(documents)} issues/PRs từ {repo_owner}/{repo_name} vào vector DB")
    
    def add_rally_data(self, story_ids=None, force_refresh=False):
        """
        Thêm dữ liệu Rally vào vector database
        
        Args:
            story_ids: List các story IDs cần thêm (None để lấy tất cả)
            force_refresh: Có force làm mới dữ liệu không
        """
        try:
            print("🔄 Đang thu thập dữ liệu Rally...")
            
            # Khởi tạo data connector
            connector = DataConnector()
            
            # Lấy Rally stories
            stories = connector._get_rally_stories(story_ids)
            if stories:
                self._add_rally_stories_to_vector_db(stories)
                
            print("✅ Đã thêm dữ liệu Rally vào vector database")
            
        except Exception as e:
            print(f"❌ Lỗi thêm dữ liệu Rally: {e}")
    
    def _add_rally_stories_to_vector_db(self, stories):
        """Thêm Rally stories vào vector database"""
        if "rally_stories" not in self.collections:
            return
            
        collection = self.collections["rally_stories"]
        
        documents = []
        ids = []
        metadatas = []
        
        for story in stories:
            # Tạo document text từ story
            doc_text = f"""
            Story ID: {story.get('FormattedID', '')}
            Name: {story.get('Name', '')}
            Description: {story.get('Description', '')}
            State: {story.get('ScheduleState', '')}
            Iteration: {story.get('Iteration', {}).get('Name', '') if story.get('Iteration') else ''}
            Owner: {story.get('Owner', {}).get('_refObjectName', '') if story.get('Owner') else ''}
            """
            
            doc_id = f"rally_story_{story.get('FormattedID', '')}"
            
            documents.append(doc_text)
            ids.append(doc_id)
            metadatas.append({
                "type": "user_story",
                "formatted_id": story.get('FormattedID', ''),
                "state": story.get('ScheduleState', ''),
                "created_date": story.get('CreationDate', ''),
                "updated_at": datetime.now().isoformat()
            })
        
        if documents:
            # Thêm batch vào collection
            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"📋 Đã thêm {len(documents)} Rally stories vào vector DB")
    
    def search_similar(self, query, collection_name, limit=5):
        """
        Tìm kiếm dữ liệu tương tự trong vector database
        
        Args:
            query: Câu query tìm kiếm
            collection_name: Tên collection để tìm kiếm
            limit: Số lượng kết quả tối đa
            
        Returns:
            List kết quả tìm kiếm
        """
        try:
            if collection_name not in self.collections:
                print(f"❌ Collection '{collection_name}' không tồn tại")
                return []
                
            collection = self.collections[collection_name]
            
            # Thực hiện tìm kiếm
            results = collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            return results
            
        except Exception as e:
            print(f"❌ Lỗi tìm kiếm: {e}")
            return []
    
    def get_database_stats(self):
        """Lấy thống kê database"""
        stats = {}
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = count
            except:
                stats[name] = 0
                
        return stats
    
    def clear_collection(self, collection_name):
        """Xóa toàn bộ dữ liệu trong collection"""
        try:
            if collection_name in self.collections:
                # ChromaDB không có method clear, nên ta phải delete và recreate
                self.client.delete_collection(collection_name)
                print(f"🗑️ Đã xóa collection '{collection_name}'")
                
                # Tạo lại collection
                self._create_collections()
                
        except Exception as e:
            print(f"❌ Lỗi xóa collection: {e}")


def main():
    """Main function để chạy script"""
    print("🚀 Khởi động ChromaDB Vector Database Manager")
    print("=" * 50)
    
    # Khởi tạo Vector DB Manager
    db_manager = VectorDBManager()
    
    # Initialize database
    if not db_manager.initialize_db():
        print("❌ Không thể khởi tạo database")
        return
    
    print("\n📊 Database Stats:")
    stats = db_manager.get_database_stats()
    for collection, count in stats.items():
        print(f"  - {collection}: {count} documents")
    
    print("\n🎯 Vector Database đã sẵn sàng!")
    print("Bạn có thể:")
    print("1. Thêm dữ liệu GitHub: db_manager.add_github_data('owner', 'repo')")
    print("2. Thêm dữ liệu Rally: db_manager.add_rally_data()")
    print("3. Tìm kiếm: db_manager.search_similar('query', 'collection_name')")
    
    return db_manager


if __name__ == "__main__":
    main()
