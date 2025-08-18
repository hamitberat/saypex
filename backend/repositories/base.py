from typing import TypeVar, Generic, List, Optional, Dict, Any
from abc import ABC, abstractmethod
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
import logging
from datetime import datetime

from ..models.base import BaseDocument
from ..core.database import get_database

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseDocument)


class BaseRepository(Generic[T], ABC):
    """Base repository with common CRUD operations and enterprise patterns"""
    
    def __init__(self, model_class: type[T], collection_name: str):
        self.model_class = model_class
        self.collection_name = collection_name
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get MongoDB collection with lazy initialization"""
        if self._collection is None:
            self._db = await get_database()
            self._collection = self._db[self.collection_name]
        return self._collection
    
    async def create(self, document: T, session=None) -> T:
        """Create a new document"""
        try:
            collection = await self.get_collection()
            document.created_at = datetime.utcnow()
            document.updated_at = datetime.utcnow()
            
            result = await collection.insert_one(
                document.dict(by_alias=True, exclude_unset=True),
                session=session
            )
            
            document.id = result.inserted_id
            logger.info(f"Created {self.model_class.__name__} with ID: {result.inserted_id}")
            return document
            
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            raise
    
    def _convert_objectids_to_strings(self, doc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId fields to strings for Pydantic compatibility"""
        if not doc_data:
            return doc_data
        
        # Convert _id to string
        if '_id' in doc_data and isinstance(doc_data['_id'], ObjectId):
            doc_data['_id'] = str(doc_data['_id'])
        
        # Convert other ObjectId fields to strings
        for key, value in doc_data.items():
            if isinstance(value, ObjectId):
                doc_data[key] = str(value)
            elif isinstance(value, list):
                # Handle lists that might contain ObjectIds
                doc_data[key] = [str(item) if isinstance(item, ObjectId) else item for item in value]
        
        return doc_data
    
    async def get_by_id(self, document_id: str) -> Optional[T]:
        """Get document by ID"""
        try:
            collection = await self.get_collection()
            doc_data = await collection.find_one({"_id": ObjectId(document_id)})
            
            if doc_data:
                doc_data = self._convert_objectids_to_strings(doc_data)
                return self.model_class(**doc_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {document_id}: {e}")
            return None
    
    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get document by specific field"""
        try:
            collection = await self.get_collection()
            doc_data = await collection.find_one({field: value})
            
            if doc_data:
                doc_data = self._convert_objectids_to_strings(doc_data)
                return self.model_class(**doc_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by {field}: {e}")
            return None
    
    async def find_many(
        self, 
        filter_dict: Dict[str, Any] = None,
        sort_by: str = "created_at",
        sort_order: int = DESCENDING,
        limit: int = 50,
        offset: int = 0
    ) -> List[T]:
        """Find multiple documents with filtering, sorting, and pagination"""
        try:
            collection = await self.get_collection()
            filter_dict = filter_dict or {}
            
            cursor = collection.find(filter_dict).sort(sort_by, sort_order).skip(offset).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Convert ObjectIds to strings for each document
            converted_docs = [self._convert_objectids_to_strings(doc) for doc in documents]
            return [self.model_class(**doc) for doc in converted_docs]
            
        except Exception as e:
            logger.error(f"Error finding {self.model_class.__name__} documents: {e}")
            return []
    
    async def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """Count documents matching filter"""
        try:
            collection = await self.get_collection()
            filter_dict = filter_dict or {}
            return await collection.count_documents(filter_dict)
            
        except Exception as e:
            logger.error(f"Error counting {self.model_class.__name__} documents: {e}")
            return 0
    
    async def update_by_id(
        self, 
        document_id: str, 
        update_data: Dict[str, Any],
        session=None
    ) -> Optional[T]:
        """Update document by ID with optimistic locking"""
        try:
            collection = await self.get_collection()
            
            # Add updated timestamp and increment version
            update_data["updated_at"] = datetime.utcnow()
            
            # Get current document for version check
            current_doc = await collection.find_one({"_id": ObjectId(document_id)})
            if not current_doc:
                return None
            
            current_version = current_doc.get("version", 1)
            
            # Update with version check (optimistic locking)
            result = await collection.find_one_and_update(
                {
                    "_id": ObjectId(document_id),
                    "version": current_version
                },
                {
                    "$set": {**update_data, "version": current_version + 1},
                },
                return_document=True,
                session=session
            )
            
            if result:
                logger.info(f"Updated {self.model_class.__name__} with ID: {document_id}")
                return self.model_class(**result)
            else:
                logger.warning(f"Version conflict updating {self.model_class.__name__} ID: {document_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__} by ID {document_id}: {e}")
            return None
    
    async def delete_by_id(self, document_id: str, session=None) -> bool:
        """Delete document by ID"""
        try:
            collection = await self.get_collection()
            result = await collection.delete_one(
                {"_id": ObjectId(document_id)},
                session=session
            )
            
            if result.deleted_count > 0:
                logger.info(f"Deleted {self.model_class.__name__} with ID: {document_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__} by ID {document_id}: {e}")
            return False
    
    async def soft_delete_by_id(self, document_id: str, deleted_by: str = None) -> bool:
        """Soft delete document by ID"""
        update_data = {
            "is_deleted": True,
            "deleted_at": datetime.utcnow(),
            "deleted_by": deleted_by
        }
        
        result = await self.update_by_id(document_id, update_data)
        return result is not None
    
    async def bulk_create(self, documents: List[T], session=None) -> List[T]:
        """Bulk create documents"""
        try:
            collection = await self.get_collection()
            
            # Prepare documents with timestamps
            now = datetime.utcnow()
            docs_data = []
            for doc in documents:
                doc.created_at = now
                doc.updated_at = now
                docs_data.append(doc.dict(by_alias=True, exclude_unset=True))
            
            result = await collection.insert_many(docs_data, session=session)
            
            # Update document IDs
            for i, doc in enumerate(documents):
                doc.id = result.inserted_ids[i]
            
            logger.info(f"Bulk created {len(documents)} {self.model_class.__name__} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error bulk creating {self.model_class.__name__} documents: {e}")
            raise
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        try:
            collection = await self.get_collection()
            cursor = collection.aggregate(pipeline)
            documents = await cursor.to_list(length=None)
            
            # Convert ObjectIds to strings for each document
            converted_docs = [self._convert_objectids_to_strings(doc) for doc in documents]
            return converted_docs
            
        except Exception as e:
            logger.error(f"Error executing aggregation on {self.model_class.__name__}: {e}")
            return []
    
    async def text_search(
        self, 
        query: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[T]:
        """Perform text search on collection"""
        try:
            collection = await self.get_collection()
            
            cursor = collection.find(
                {"$text": {"$search": query}}
            ).sort([("score", {"$meta": "textScore"})]).skip(offset).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            return [self.model_class(**doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error performing text search on {self.model_class.__name__}: {e}")
            return []