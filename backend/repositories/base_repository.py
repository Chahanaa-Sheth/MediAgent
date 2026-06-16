from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.exceptions import Logger


class BaseRepository:
    """Base repository class with common CRUD operations"""

    def __init__(self, collection):
        self.collection = collection
        self.logger = Logger(self.__class__.__name__)

    async def create(self, data: Dict[str, Any]) -> str:
        """Create a new document and return the inserted ID"""
        result = await self.collection.insert_one(data)
        self.logger.info("Document created", collection=self.collection.name, id=str(result.inserted_id))
        return str(result.inserted_id)

    async def read(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Read a single document"""
        result = await self.collection.find_one(query)
        if result:
            result['_id'] = str(result['_id'])
        return result

    async def read_many(self, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """Read multiple documents"""
        cursor = self.collection.find(query).limit(limit)
        results = []
        async for doc in cursor:
            doc['_id'] = str(doc['_id'])
            results.append(doc)
        return results

    async def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """Update a document"""
        update_data['updated_at'] = datetime.utcnow()
        result = await self.collection.update_one(query, {"$set": update_data})
        self.logger.info("Document updated", collection=self.collection.name, matched=result.matched_count)
        return result.matched_count > 0

    async def delete(self, query: Dict[str, Any]) -> bool:
        """Delete a document"""
        result = await self.collection.delete_one(query)
        self.logger.info("Document deleted", collection=self.collection.name, deleted=result.deleted_count)
        return result.deleted_count > 0

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Alias for read"""
        return await self.read(query)

    async def find_many(self, query: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
        """Alias for read_many"""
        return await self.read_many(query, limit)
