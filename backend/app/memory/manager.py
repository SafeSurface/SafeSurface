from typing import Dict, List, Any
from app.memory.vector_store import VectorStoreManager
from app.memory.embeddings import embedding_service
from app.utils.logger import setup_logger

logger = setup_logger("memory.manager")

class MultiLevelMemoryManager:
    """分层记忆管理器：统筹情节记忆 (Episodic) 和长期知识 (Long-Term/RAG)"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 自动计算位于 backend/data 目录下的默认路径
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, "data", "memory.db")
        self.vsm = VectorStoreManager(db_path=db_path)
        self.dimension = embedding_service.dimension
        
    def add_episodic_memory(self, session_id: str, content: str, metadata: Dict = None):
        """存储单次会话中的关键事件或探测结论（情节记忆）"""
        metadata = metadata or {}
        metadata['session_id'] = session_id
        vector = embedding_service.embed_text(content)
        
        # 存入专门的 'episodic' 集合
        store = self.vsm.get_store("episodic", dimension=self.dimension)
        item_id = self.vsm.add_memory(content, vector, "episodic", metadata)
        logger.info(f"Added episodic memory for session {session_id}: {item_id}")

    def add_long_term_knowledge(self, content: str, metadata: Dict = None):
        """存储跨会话的通用漏洞知识、Payload 库（长时记忆/RAG库）"""
        vector = embedding_service.embed_text(content)
        
        # 存入专门的 'long_term' 集合
        store = self.vsm.get_store("long_term", dimension=self.dimension)
        item_id = self.vsm.add_memory(content, vector, "long_term", metadata)
        logger.info(f"Added long-term knowledge to RAG store: {item_id}")

    def retrieve_context(self, query: str, session_id: str = None, limit: int = 3, threshold: float = 0.3) -> Dict[str, List[str]]:
        """根据当前意图 (query) 同步检索相关联的近过去事实以及长时知识补丁"""
        query_vector = embedding_service.embed_text(query)
        
        # 1. 召回相关的攻击打点经验
        episodic_results = self.vsm.search_memories(query_vector, memory_type="episodic", limit=limit)
        episodic_context = []
        for item, score in episodic_results:
            if score > threshold:
                # 只召回同一 session 的记忆或者跨 session 但极度相关的底层关联
                if not session_id or item.metadata.get('session_id') == session_id:
                    episodic_context.append(item.content)
            
        # 2. 召回 RAG 漏洞知识库
        long_term_results = self.vsm.search_memories(query_vector, memory_type="long_term", limit=limit)
        long_term_context = [item.content for (item, score) in long_term_results if score > threshold]
        
        return {
            "episodic": episodic_context,
            "long_term": long_term_context
        }

# 全局单例实例化
memory_manager = MultiLevelMemoryManager()