"""
Vector Database Integration cho BrainStory AI Agent
Sử dụng ChromaDB để lưu trữ và tìm kiếm dữ liệu từ GitHub và Rally
"""

import chromadb
import os
from datetime import datetime
from pathlib import Path
from .data_connector import DataConnector


class VectorDBConnector:
    def __init__(self, db_path="./chroma_db"):
        """
        Khởi tạo Vector Database Connector
        
        Args:
            db_path: Đường dẫn đến thư mục lưu trữ ChromaDB
        """
        self.db_path = db_path
        self.client = None
        self.collections = {}
        self.is_initialized = False
        
    def initialize(self):
        """Khởi tạo ChromaDB và các collections"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            Path(self.db_path).mkdir(parents=True, exist_ok=True)
            
            # Khởi tạo ChromaDB client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Tạo collections
            self._setup_collections()
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"Vector DB initialization error: {e}")
            return False
    
    def _setup_collections(self):
        """Setup các collections cần thiết"""
        collections_config = {
            "github_data": {
                "name": "github_data",
                "metadata": {"hnsw:space": "cosine"}
            },
            "rally_data": {
                "name": "rally_data", 
                "metadata": {"hnsw:space": "cosine"}
            },
            "user_stories": {
                "name": "user_stories",
                "metadata": {"hnsw:space": "cosine"}
            }
        }
        
        for key, config in collections_config.items():
            try:
                # Kiểm tra collection đã tồn tại chưa
                try:
                    collection = self.client.get_collection(config["name"])
                except:
                    # Tạo collection mới
                    collection = self.client.create_collection(
                        name=config["name"],
                        metadata=config["metadata"]
                    )
                
                self.collections[key] = collection
                
            except Exception as e:
                print(f"Error setting up collection {config['name']}: {e}")
    
    def add_github_context(self, repo_owner, repo_name, context_data):
        """
        Thêm context từ GitHub vào vector database
        
        Args:
            repo_owner: Owner của repository
            repo_name: Tên repository  
            context_data: Dữ liệu context từ GitHub
        """
        if not self.is_initialized or "github_data" not in self.collections:
            return False
            
        try:
            collection = self.collections["github_data"]
            
            documents = []
            ids = []
            metadatas = []
            
            # Thêm repository info
            if context_data.get('repo_info'):
                repo_info = context_data['repo_info']
                doc_text = f"""
                Repository: {repo_owner}/{repo_name}
                Description: {repo_info.get('description', '')}
                Language: {repo_info.get('language', '')}
                README: {repo_info.get('readme', '')[:1000]}...
                """
                
                documents.append(doc_text)
                ids.append(f"repo_{repo_owner}_{repo_name}")
                metadatas.append({
                    "type": "repository",
                    "owner": repo_owner,
                    "name": repo_name,
                    "updated_at": datetime.now().isoformat()
                })
            
            # Thêm issues/PRs
            if context_data.get('issues'):
                for i, issue in enumerate(context_data['issues'][:10]):  # Giới hạn 10 issues
                    doc_text = f"""
                    Issue #{issue.get('number', '')}: {issue.get('title', '')}
                    State: {issue.get('state', '')}
                    Body: {issue.get('body', '')[:500]}...
                    Labels: {', '.join([label.get('name', '') for label in issue.get('labels', [])])}
                    """
                    
                    documents.append(doc_text)
                    ids.append(f"issue_{repo_owner}_{repo_name}_{issue.get('number', i)}")
                    metadatas.append({
                        "type": "issue",
                        "repo_owner": repo_owner,
                        "repo_name": repo_name,
                        "number": issue.get('number', i),
                        "state": issue.get('state', ''),
                        "updated_at": datetime.now().isoformat()
                    })
            
            # Thêm vào collection
            if documents:
                collection.add(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas
                )
                
                return True
                
        except Exception as e:
            print(f"Error adding GitHub context: {e}")
            
        return False
    
    def add_rally_context(self, context_data):
        """
        Thêm context từ Rally vào vector database
        
        Args:
            context_data: Dữ liệu context từ Rally
        """
        if not self.is_initialized or "rally_data" not in self.collections:
            return False
            
        try:
            collection = self.collections["rally_data"]
            
            documents = []
            ids = []
            metadatas = []
            
            # Thêm stories
            if context_data.get('stories'):
                for story in context_data['stories'][:10]:  # Giới hạn 10 stories
                    doc_text = f"""
                    Story {story.get('FormattedID', '')}: {story.get('Name', '')}
                    State: {story.get('ScheduleState', '')}
                    Description: {story.get('Description', '')[:500]}...
                    Iteration: {story.get('Iteration', {}).get('Name', '') if story.get('Iteration') else ''}
                    """
                    
                    documents.append(doc_text)
                    ids.append(f"story_{story.get('FormattedID', '')}")
                    metadatas.append({
                        "type": "user_story",
                        "formatted_id": story.get('FormattedID', ''),
                        "state": story.get('ScheduleState', ''),
                        "updated_at": datetime.now().isoformat()
                    })
            
            # Thêm vào collection
            if documents:
                collection.add(
                    documents=documents,
                    ids=ids,
                    metadatas=metadatas
                )
                
                return True
                
        except Exception as e:
            print(f"Error adding Rally context: {e}")
            
        return False
    
    def search_relevant_context(self, query, context_type="all", limit=5):
        """
        Tìm kiếm context liên quan dựa trên query
        
        Args:
            query: Câu query tìm kiếm
            context_type: Loại context ("github", "rally", "all")
            limit: Số lượng kết quả tối đa
            
        Returns:
            List các context liên quan
        """
        if not self.is_initialized:
            return []
            
        results = []
        
        try:
            collections_to_search = []
            
            if context_type == "all":
                collections_to_search = ["github_data", "rally_data"]
            elif context_type == "github":
                collections_to_search = ["github_data"]
            elif context_type == "rally":
                collections_to_search = ["rally_data"]
            
            for collection_name in collections_to_search:
                if collection_name in self.collections:
                    collection = self.collections[collection_name]
                    
                    search_results = collection.query(
                        query_texts=[query],
                        n_results=limit
                    )
                    
                    # Format results
                    if search_results.get('documents') and search_results['documents'][0]:
                        for i, doc in enumerate(search_results['documents'][0]):
                            metadata = search_results['metadatas'][0][i] if search_results.get('metadatas') else {}
                            distance = search_results['distances'][0][i] if search_results.get('distances') else 1.0
                            
                            results.append({
                                'text': doc,
                                'metadata': metadata,
                                'similarity': 1 - distance,  # Convert distance to similarity
                                'source': collection_name
                            })
            
            # Sort by similarity
            results = sorted(results, key=lambda x: x['similarity'], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error searching context: {e}")
            return []
    
    def store_generated_story(self, story_content, metadata=None):
        """
        Lưu trữ user story đã được tạo
        
        Args:
            story_content: Nội dung user story
            metadata: Metadata bổ sung
        """
        if not self.is_initialized or "user_stories" not in self.collections:
            return False
            
        try:
            collection = self.collections["user_stories"]
            
            story_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            story_metadata = {
                "created_at": datetime.now().isoformat(),
                "type": "generated_story"
            }
            
            if metadata:
                story_metadata.update(metadata)
            
            collection.add(
                documents=[story_content],
                ids=[story_id],
                metadatas=[story_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error storing generated story: {e}")
            return False
    
    def get_stats(self):
        """Lấy thống kê về vector database"""
        if not self.is_initialized:
            return {}
            
        stats = {}
        for name, collection in self.collections.items():
            try:
                stats[name] = collection.count()
            except:
                stats[name] = 0
                
        return stats
    
    def clear_collection(self, collection_name):
        """Xóa toàn bộ dữ liệu trong collection"""
        try:
            if collection_name in self.collections:
                collection = self.collections[collection_name]
                
                # Lấy tất cả IDs trong collection
                result = collection.get()
                if result['ids']:
                    # Xóa tất cả documents
                    collection.delete(ids=result['ids'])
                    print(f"🗑️ Đã xóa {len(result['ids'])} documents từ collection '{collection_name}'")
                    return True
                else:
                    print(f"Collection '{collection_name}' đã trống")
                    return True
                
        except Exception as e:
            print(f"❌ Lỗi xóa collection: {e}")
            return False
