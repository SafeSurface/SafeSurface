from typing import List
from app.utils.logger import setup_logger

logger = setup_logger("memory.embeddings")

class EmbeddingService:
    """提供本地化的文本向量化服务"""
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            # 使用轻量级、速度快的本地模型，其输出维度为 384
            self.model = SentenceTransformer('all-MiniLM-L6-v2') 
            self.dimension = 384
            logger.info("Local SentenceTransformer (all-MiniLM-L6-v2) loaded successfully.")
        except ImportError:
            logger.warning("sentence-transformers not found! Please run `pip install sentence-transformers`")
            self.model = None
            self.dimension = 384
            
    def embed_text(self, text: str) -> List[float]:
        """将任意文本转化为浮点向量"""
        if self.model:
            return self.model.encode(text).tolist()
        else:
            # 降级模式：当尚未安装依赖时生成一个随机 Mock 向量防崩溃
            import numpy as np
            logger.debug(f"Using mock embedding for text (length: {len(text)})")
            return np.random.rand(self.dimension).tolist()

embedding_service = EmbeddingService()