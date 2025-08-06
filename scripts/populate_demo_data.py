#!/usr/bin/env python3
"""
Demo script để populate dữ liệu mẫu vào ChromaDB Vector Database
"""

import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.start_vector_db import VectorDBManager
from datetime import datetime


def populate_demo_data():
    """Thêm dữ liệu demo vào vector database"""
    
    print("🚀 Bắt đầu populate dữ liệu demo...")
    
    # Khởi tạo Vector DB Manager
    db_manager = VectorDBManager()
    
    if not db_manager.initialize_db():
        print("❌ Không thể khởi tạo database")
        return
    
    # Demo GitHub data
    print("\n📊 Thêm dữ liệu GitHub demo...")
    add_github_demo_data(db_manager)
    
    # Demo Rally data  
    print("\n🏢 Thêm dữ liệu Rally demo...")
    add_rally_demo_data(db_manager)
    
    # Demo User Stories
    print("\n📝 Thêm User Stories demo...")
    add_user_stories_demo_data(db_manager)
    
    print("\n✅ Hoàn thành populate dữ liệu demo!")
    
    # Show final stats
    print("\n📈 Thống kê cuối cùng:")
    stats = db_manager.get_database_stats()
    for collection, count in stats.items():
        print(f"  - {collection}: {count} documents")


def add_github_demo_data(db_manager):
    """Thêm dữ liệu GitHub demo"""
    
    # Demo repository info
    repo_data = {
        'name': 'cox-automotive-platform',
        'description': 'Main platform for Cox Automotive applications with microservices architecture',
        'language': 'TypeScript',
        'topics': ['microservices', 'nodejs', 'typescript', 'kubernetes'],
        'readme': '''# Cox Automotive Platform

A comprehensive platform for automotive services including:
- Vehicle inventory management
- Customer relationship management  
- Financial services integration
- Real-time pricing and analytics

## Architecture
- Microservices with Node.js/TypeScript
- Kubernetes orchestration
- PostgreSQL and Redis
- GraphQL API Gateway

## Key Features
- User authentication and authorization
- Vehicle search and filtering
- Inventory management
- Customer portal
- Dealer management system'''
    }
    
    if "github_repos" in db_manager.collections:
        collection = db_manager.collections["github_repos"]
        
        doc_text = f"""
        Repository: cox-automotive/cox-automotive-platform
        Description: {repo_data['description']}
        Language: {repo_data['language']}
        Topics: {', '.join(repo_data['topics'])}
        README: {repo_data['readme']}
        """
        
        collection.add(
            documents=[doc_text],
            ids=["repo_cox-automotive_platform"],
            metadatas=[{
                "type": "repository",
                "owner": "cox-automotive",
                "name": "cox-automotive-platform",
                "language": repo_data['language'],
                "created_at": "2023-01-15T10:00:00Z",
                "updated_at": datetime.now().isoformat()
            }]
        )
        
        print("✅ Đã thêm repository demo")
    
    # Demo issues
    demo_issues = [
        {
            "number": 123,
            "title": "Implement OAuth2 authentication for customer portal",
            "body": "Need to implement secure OAuth2 authentication flow for customer portal login. Should support Google, Facebook, and Cox Automotive SSO.",
            "state": "open",
            "labels": [{"name": "enhancement"}, {"name": "security"}, {"name": "authentication"}]
        },
        {
            "number": 124,
            "title": "Add vehicle search filters for advanced queries",
            "body": "Customers need ability to filter vehicles by make, model, year, price range, mileage, and features. Should support multiple filters simultaneously.",
            "state": "open", 
            "labels": [{"name": "feature"}, {"name": "search"}, {"name": "frontend"}]
        },
        {
            "number": 125,
            "title": "Fix inventory sync issues with dealer systems",
            "body": "Vehicle inventory is not syncing properly with dealer management systems. Causing discrepancies in available inventory.",
            "state": "in-progress",
            "labels": [{"name": "bug"}, {"name": "integration"}, {"name": "inventory"}]
        }
    ]
    
    if "github_issues" in db_manager.collections:
        collection = db_manager.collections["github_issues"]
        
        documents = []
        ids = []
        metadatas = []
        
        for issue in demo_issues:
            doc_text = f"""
            Title: {issue['title']}
            Body: {issue['body']}
            State: {issue['state']}
            Labels: {', '.join([label['name'] for label in issue['labels']])}
            """
            
            documents.append(doc_text)
            ids.append(f"issue_cox-automotive_platform_{issue['number']}")
            metadatas.append({
                "type": "issue",
                "repo_owner": "cox-automotive",
                "repo_name": "cox-automotive-platform",
                "number": issue['number'],
                "state": issue['state'],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": datetime.now().isoformat()
            })
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"✅ Đã thêm {len(demo_issues)} GitHub issues demo")


def add_rally_demo_data(db_manager):
    """Thêm dữ liệu Rally demo"""
    
    demo_stories = [
        {
            "FormattedID": "US1001",
            "Name": "Customer login with social authentication",
            "Description": "As a customer, I want to login using my Google or Facebook account so that I can quickly access the platform without creating a new password.",
            "ScheduleState": "In-Progress",
            "Iteration": {"Name": "Sprint 23"},
            "Owner": {"_refObjectName": "John Smith"}
        },
        {
            "FormattedID": "US1002", 
            "Name": "Advanced vehicle search functionality",
            "Description": "As a customer, I want to search for vehicles using multiple filters (make, model, year, price, mileage) so that I can find vehicles that match my specific criteria.",
            "ScheduleState": "Defined",
            "Iteration": {"Name": "Sprint 24"},
            "Owner": {"_refObjectName": "Sarah Johnson"}
        },
        {
            "FormattedID": "US1003",
            "Name": "Real-time inventory synchronization",
            "Description": "As a dealer, I want the platform to sync with my inventory management system in real-time so that customers see accurate vehicle availability.",
            "ScheduleState": "Accepted",
            "Iteration": {"Name": "Sprint 22"},
            "Owner": {"_refObjectName": "Mike Davis"}
        }
    ]
    
    if "rally_stories" in db_manager.collections:
        collection = db_manager.collections["rally_stories"]
        
        documents = []
        ids = []
        metadatas = []
        
        for story in demo_stories:
            doc_text = f"""
            Story ID: {story['FormattedID']}
            Name: {story['Name']}
            Description: {story['Description']}
            State: {story['ScheduleState']}
            Iteration: {story['Iteration']['Name']}
            Owner: {story['Owner']['_refObjectName']}
            """
            
            documents.append(doc_text)
            ids.append(f"rally_story_{story['FormattedID']}")
            metadatas.append({
                "type": "user_story",
                "formatted_id": story['FormattedID'],
                "state": story['ScheduleState'],
                "created_date": "2024-01-15T10:00:00Z",
                "updated_at": datetime.now().isoformat()
            })
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"✅ Đã thêm {len(demo_stories)} Rally stories demo")


def add_user_stories_demo_data(db_manager):
    """Thêm generated user stories demo"""
    
    demo_generated_stories = [
        {
            "content": """**User Story:** Customer Vehicle Wishlist Management

**As a** registered customer
**I want to** save vehicles to a personal wishlist
**So that** I can easily track and compare vehicles I'm interested in

**Acceptance Criteria:**
- Customer can add vehicles to wishlist from search results or vehicle detail page
- Customer can view all saved vehicles in their wishlist
- Customer can remove vehicles from wishlist
- Wishlist persists across login sessions
- Customer can share wishlist with family members
- Maximum 50 vehicles per wishlist

**Priority:** High
**Story Points:** 5
**Dependencies:** Customer authentication system must be implemented""",
            "prompt": "Create a user story for vehicle wishlist functionality",
            "has_context": True
        },
        {
            "content": """**User Story:** Dealer Inventory Upload

**As a** dealer administrator  
**I want to** bulk upload my vehicle inventory via CSV file
**So that** I can quickly update hundreds of vehicles without manual entry

**Acceptance Criteria:**
- Support CSV file upload with standard vehicle fields
- Validate data format and show errors before processing
- Process uploads in background with progress indicator
- Send email notification when upload is complete
- Support images upload via ZIP file
- Handle duplicate VIN detection
- Generate upload summary report

**Priority:** High
**Story Points:** 8
**Dependencies:** File storage system, background job processing""",
            "prompt": "Create a user story for dealer inventory management",
            "has_context": False
        }
    ]
    
    if "user_stories" in db_manager.collections:
        collection = db_manager.collections["user_stories"]
        
        documents = []
        ids = []
        metadatas = []
        
        for i, story in enumerate(demo_generated_stories, 1):
            documents.append(story['content'])
            ids.append(f"story_demo_{i}")
            metadatas.append({
                "created_at": datetime.now().isoformat(),
                "type": "generated_story",
                "prompt": story['prompt'],
                "has_context": story['has_context']
            })
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        
        print(f"✅ Đã thêm {len(demo_generated_stories)} generated stories demo")


if __name__ == "__main__":
    populate_demo_data()
