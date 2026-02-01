#!/usr/bin/env python3
"""
上下文管理模块

基于 NotebookLM 文档驱动开发
文档: context-compression-SKILL.md, context-degradation-SKILL.md, context-fundamentals-SKILL.md, context-optimization-SKILL.md, dynamic-context-discovery-skill.md

功能:
- 上下文存储和管理
- 上下文压缩算法
- 上下文优化策略
- 上下文检索机制
- 动态上下文发现
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
import sqlite3
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextType(Enum):
    """上下文类型"""
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    METADATA = "metadata"
    USER = "user"
    SYSTEM = "system"
    TEMPORAL = "temporal"


class ContextPriority(Enum):
    """上下文优先级"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ContextItem:
    """上下文项"""
    id: str
    content: Any
    context_type: ContextType
    priority: ContextPriority
    timestamp: datetime
    expiration: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "context_type": self.context_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "expiration": self.expiration.isoformat() if self.expiration else None,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "tags": list(self.tags)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextItem':
        """从字典创建"""
        return cls(
            id=data["id"],
            content=data["content"],
            context_type=ContextType(data["context_type"]),
            priority=ContextPriority(data["priority"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            expiration=datetime.fromisoformat(data["expiration"]) if data.get("expiration") else None,
            metadata=data.get("metadata", {}),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            tags=set(data.get("tags", []))
        )


class ContextCompression:
    """上下文压缩算法"""
    
    @staticmethod
    def compress_text(text: str, compression_ratio: float = 0.5) -> str:
        """压缩文本"""
        if compression_ratio >= 1.0:
            return text
        
        # 更智能的文本压缩
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return text
        
        # 保留前几个句子
        keep_count = max(1, int(len(sentences) * compression_ratio))
        important_sentences = sentences[:keep_count]
        
        # 确保压缩后的文本比原文短
        compressed = '. '.join(important_sentences)
        if len(compressed) >= len(text):
            # 如果压缩后没有变短，则截取部分文本
            max_length = max(1, int(len(text) * compression_ratio))
            compressed = text[:max_length]
        
        return compressed + '.' if compressed and not compressed.endswith('.') else compressed
    
    @staticmethod
    def compress_context_list(context_list: List[ContextItem], 
                           max_items: int = 100,
                           compression_ratio: float = 0.7) -> List[ContextItem]:
        """压缩上下文列表"""
        if len(context_list) <= max_items:
            return context_list
        
        # 按优先级和时间排序（优先级高的在前，时间新的在前）
        sorted_context = sorted(
            context_list,
            key=lambda x: (-x.priority.value, -x.timestamp.timestamp())
        )
        
        # 直接限制数量
        compressed_context = sorted_context[:max_items]
        
        return compressed_context
    
    @staticmethod
    def create_context_summary(context_list: List[ContextItem]) -> str:
        """创建上下文摘要"""
        if not context_list:
            return ""
        
        # 按类型分组
        type_groups = {}
        for ctx in context_list:
            ctx_type = ctx.context_type.value
            if ctx_type not in type_groups:
                type_groups[ctx_type] = []
            type_groups[ctx_type].append(ctx)
        
        # 生成摘要
        summary = []
        for ctx_type, items in type_groups.items():
            count = len(items)
            latest_time = max(item.timestamp for item in items)
            summary.append(f"{ctx_type}: {count} items (latest: {latest_time.strftime('%Y-%m-%d %H:%M')})")
        
        return "; ".join(summary)


class ContextOptimizer:
    """上下文优化器"""
    
    def __init__(self):
        self.optimization_strategies = {
            "temporal_decay": self._temporal_decay_optimization,
            "access_frequency": self._access_frequency_optimization,
            "relevance_scoring": self._relevance_scoring_optimization,
            "size_management": self._size_management_optimization
        }
    
    def optimize_context(self, context_list: List[ContextItem], 
                        strategies: List[str] = None,
                        max_size: int = 1000) -> List[ContextItem]:
        """优化上下文"""
        if strategies is None:
            strategies = ["temporal_decay", "access_frequency", "size_management"]
        
        optimized_context = context_list.copy()
        
        for strategy in strategies:
            if strategy in self.optimization_strategies:
                optimized_context = self.optimization_strategies[strategy](optimized_context)
        
        # 确保不超过最大大小
        if len(optimized_context) > max_size:
            optimized_context = ContextCompression.compress_context_list(
                optimized_context, max_size
            )
        
        return optimized_context
    
    def _temporal_decay_optimization(self, context_list: List[ContextItem]) -> List[ContextItem]:
        """时间衰减优化"""
        current_time = datetime.now()
        decay_threshold = timedelta(days=7)  # 7天前的上下文衰减
        
        return [
            ctx for ctx in context_list
            if current_time - ctx.timestamp <= decay_threshold
        ]
    
    def _access_frequency_optimization(self, context_list: List[ContextItem]) -> List[ContextItem]:
        """访问频率优化"""
        # 保留访问频率高的上下文
        threshold = 1  # 至少访问1次
        
        return [
            ctx for ctx in context_list
            if ctx.access_count >= threshold
        ]
    
    def _relevance_scoring_optimization(self, context_list: List[ContextItem]) -> List[ContextItem]:
        """相关性评分优化"""
        # 简单的相关性评分：优先级 + 访问频率
        scored_context = []
        for ctx in context_list:
            score = ctx.priority.value + (ctx.access_count * 0.1)
            scored_context.append((ctx, score))
        
        # 按评分排序，保留前80%
        scored_context.sort(key=lambda x: x[1], reverse=True)
        keep_count = max(1, int(len(scored_context) * 0.8))
        
        return [ctx for ctx, _ in scored_context[:keep_count]]
    
    def _size_management_optimization(self, context_list: List[ContextItem]) -> List[ContextItem]:
        """大小管理优化"""
        # 按大小管理，保留最重要的上下文
        return ContextCompression.compress_context_list(context_list, 500)


class ContextStorage:
    """上下文存储"""
    
    def __init__(self, storage_path: str = "context_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # 初始化SQLite数据库
        self.db_path = self.storage_path / "context.db"
        self._init_database()
        
        # 内存缓存
        self.cache: Dict[str, ContextItem] = {}
        self.cache_size = 1000
        
        logger.info(f"Context storage initialized at {self.storage_path}")
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 创建上下文表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_items (
                id TEXT PRIMARY KEY,
                content BLOB,
                context_type TEXT,
                priority INTEGER,
                timestamp TEXT,
                expiration TEXT,
                metadata TEXT,
                access_count INTEGER,
                last_accessed TEXT,
                tags TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON context_items(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON context_items(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_type ON context_items(context_type)')
        
        conn.commit()
        conn.close()
    
    def _get_cache_key(self, context_id: str) -> str:
        """获取缓存键"""
        return f"context_{context_id}"
    
    def _add_to_cache(self, context_item: ContextItem):
        """添加到缓存"""
        cache_key = self._get_cache_key(context_item.id)
        self.cache[cache_key] = context_item
        
        # 如果缓存超过大小限制，删除最旧的项
        if len(self.cache) > self.cache_size:
            oldest_key = min(self.cache.keys(), 
                            key=lambda k: self.cache[k].last_accessed or datetime.min)
            del self.cache[oldest_key]
    
    def _get_from_cache(self, context_id: str) -> Optional[ContextItem]:
        """从缓存获取"""
        cache_key = self._get_cache_key(context_id)
        if cache_key in self.cache:
            context_item = self.cache[cache_key]
            context_item.access_count += 1
            context_item.last_accessed = datetime.now()
            return context_item
        return None
    
    async def store_context(self, context_item: ContextItem) -> bool:
        """存储上下文"""
        try:
            # 序列化内容
            content_bytes = pickle.dumps(context_item.content)
            
            # 存储到数据库
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO context_items 
                (id, content, context_type, priority, timestamp, expiration, metadata, access_count, last_accessed, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                context_item.id,
                content_bytes,
                context_item.context_type.value,
                context_item.priority.value,
                context_item.timestamp.isoformat(),
                context_item.expiration.isoformat() if context_item.expiration else None,
                json.dumps(context_item.metadata),
                context_item.access_count,
                context_item.last_accessed.isoformat() if context_item.last_accessed else None,
                json.dumps(list(context_item.tags))
            ))
            
            conn.commit()
            conn.close()
            
            # 添加到缓存
            self._add_to_cache(context_item)
            
            logger.info(f"Context stored: {context_item.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False
    
    async def retrieve_context(self, context_id: str) -> Optional[ContextItem]:
        """检索上下文"""
        try:
            # 先从缓存获取
            cached_item = self._get_from_cache(context_id)
            if cached_item:
                return cached_item
            
            # 从数据库获取
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM context_items WHERE id = ?', (context_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                context_item = ContextItem(
                    id=row[0],
                    content=pickle.loads(row[1]),
                    context_type=ContextType(row[2]),
                    priority=ContextPriority(row[3]),
                    timestamp=datetime.fromisoformat(row[4]),
                    expiration=datetime.fromisoformat(row[5]) if row[5] else None,
                    metadata=json.loads(row[6]) if row[6] else {},
                    access_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    tags=set(json.loads(row[9])) if row[9] else set()
                )
                
                # 更新访问信息
                context_item.access_count += 1
                context_item.last_accessed = datetime.now()
                
                # 添加到缓存
                self._add_to_cache(context_item)
                
                logger.info(f"Context retrieved: {context_id}")
                return context_item
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return None
    
    async def search_context(self, 
                           context_type: Optional[ContextType] = None,
                           tags: Optional[Set[str]] = None,
                           priority_min: Optional[int] = None,
                           priority_max: Optional[int] = None,
                           time_start: Optional[datetime] = None,
                           time_end: Optional[datetime] = None,
                           limit: int = 100) -> List[ContextItem]:
        """搜索上下文"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 构建查询
            query = "SELECT * FROM context_items WHERE 1=1"
            params = []
            
            if context_type:
                query += " AND context_type = ?"
                params.append(context_type.value)
            
            if tags:
                query += " AND tags LIKE ?"
                for tag in tags:
                    params.append(f'%"{tag}"%')
            
            if priority_min is not None:
                query += " AND priority >= ?"
                params.append(priority_min)
            
            if priority_max is not None:
                query += " AND priority <= ?"
                params.append(priority_max)
            
            if time_start:
                query += " AND timestamp >= ?"
                params.append(time_start.isoformat())
            
            if time_end:
                query += " AND timestamp <= ?"
                params.append(time_end.isoformat())
            
            query += " ORDER BY priority DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            # 转换为ContextItem对象
            context_items = []
            for row in rows:
                context_item = ContextItem(
                    id=row[0],
                    content=pickle.loads(row[1]),
                    context_type=ContextType(row[2]),
                    priority=ContextPriority(row[3]),
                    timestamp=datetime.fromisoformat(row[4]),
                    expiration=datetime.fromisoformat(row[5]) if row[5] else None,
                    metadata=json.loads(row[6]) if row[6] else {},
                    access_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    tags=set(json.loads(row[9])) if row[9] else set()
                )
                context_items.append(context_item)
            
            logger.info(f"Context search returned {len(context_items)} items")
            return context_items
            
        except Exception as e:
            logger.error(f"Failed to search context: {e}")
            return []
    
    async def delete_context(self, context_id: str) -> bool:
        """删除上下文"""
        try:
            # 从缓存删除
            cache_key = self._get_cache_key(context_id)
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            # 从数据库删除
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM context_items WHERE id = ?', (context_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info(f"Context deleted: {context_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete context: {e}")
            return False
    
    async def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 总数
            cursor.execute('SELECT COUNT(*) FROM context_items')
            total_count = cursor.fetchone()[0]
            
            # 按类型统计
            cursor.execute('''
                SELECT context_type, COUNT(*) 
                FROM context_items 
                GROUP BY context_type
            ''')
            type_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 按优先级统计
            cursor.execute('''
                SELECT priority, COUNT(*) 
                FROM context_items 
                GROUP BY priority
            ''')
            priority_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # 最近访问统计
            cursor.execute('''
                SELECT COUNT(*) 
                FROM context_items 
                WHERE last_accessed >= ?
            ''', (datetime.now() - timedelta(days=1),))
            recent_access = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_count": total_count,
                "type_stats": type_stats,
                "priority_stats": priority_stats,
                "recent_access": recent_access,
                "cache_size": len(self.cache)
            }
            
        except Exception as e:
            logger.error(f"Failed to get context stats: {e}")
            return {}


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, storage_path: str = "context_storage"):
        self.storage = ContextStorage(storage_path)
        self.compression = ContextCompression()
        self.optimizer = ContextOptimizer()
        
        # 上下文管理配置
        self.max_context_size = 1000
        self.compression_ratio = 0.7
        self.auto_optimize = True
        self.optimization_interval = 3600  # 1小时
        
        # 启动自动优化任务
        self._start_auto_optimization()
        
        logger.info("Context manager initialized")
    
    def _start_auto_optimization(self):
        """启动自动优化任务"""
        async def auto_optimize():
            while True:
                await asyncio.sleep(self.optimization_interval)
                if self.auto_optimize:
                    await self.optimize_all_context()
        
        asyncio.create_task(auto_optimize())
    
    async def add_context(self, 
                         content: Any,
                         context_type: ContextType,
                         priority: ContextPriority = ContextPriority.MEDIUM,
                         expiration: Optional[datetime] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         tags: Optional[Set[str]] = None) -> str:
        """添加上下文"""
        # 生成唯一ID
        content_str = str(content) if isinstance(content, (str, int, float, bool)) else json.dumps(content)
        context_id = hashlib.md5(content_str.encode()).hexdigest()
        
        # 创建上下文项
        context_item = ContextItem(
            id=context_id,
            content=content,
            context_type=context_type,
            priority=priority,
            timestamp=datetime.now(),
            expiration=expiration,
            metadata=metadata or {},
            tags=tags or set()
        )
        
        # 存储上下文
        await self.storage.store_context(context_item)
        
        logger.info(f"Context added: {context_id}")
        return context_id
    
    async def get_context(self, context_id: str) -> Optional[ContextItem]:
        """获取上下文"""
        return await self.storage.retrieve_context(context_id)
    
    async def search_context(self, **kwargs) -> List[ContextItem]:
        """搜索上下文"""
        return await self.storage.search_context(**kwargs)
    
    async def delete_context(self, context_id: str) -> bool:
        """删除上下文"""
        return await self.storage.delete_context(context_id)
    
    async def get_all_context(self, limit: int = 1000) -> List[ContextItem]:
        """获取所有上下文"""
        return await self.storage.search_context(limit=limit)
    
    async def optimize_all_context(self) -> List[ContextItem]:
        """优化所有上下文"""
        all_context = await self.get_all_context()
        
        if not all_context:
            return []
        
        # 应用优化策略
        optimized_context = self.optimizer.optimize_context(
            all_context,
            strategies=["temporal_decay", "access_frequency", "relevance_scoring"],
            max_size=self.max_context_size
        )
        
        # 更新存储
        for context_item in optimized_context:
            await self.storage.store_context(context_item)
        
        # 删除不再需要的上下文
        context_ids_to_delete = set(ctx.id for ctx in all_context) - set(ctx.id for ctx in optimized_context)
        for context_id in context_ids_to_delete:
            await self.delete_context(context_id)
        
        logger.info(f"Context optimized: {len(all_context)} -> {len(optimized_context)}")
        return optimized_context
    
    async def create_context_summary(self) -> str:
        """创建上下文摘要"""
        all_context = await self.get_all_context()
        return self.compression.create_context_summary(all_context)
    
    async def get_context_stats(self) -> Dict[str, Any]:
        """获取上下文统计信息"""
        return await self.storage.get_context_stats()
    
    async def compress_context(self, context_ids: List[str], compression_ratio: float = None) -> List[ContextItem]:
        """压缩指定上下文"""
        if compression_ratio is None:
            compression_ratio = self.compression_ratio
        
        context_items = []
        for context_id in context_ids:
            context_item = await self.get_context(context_id)
            if context_item:
                context_items.append(context_item)
        
        return self.compression.compress_context_list(context_items, compression_ratio=compression_ratio)
    
    async def find_similar_context(self, 
                                 query_content: Any,
                                 context_type: Optional[ContextType] = None,
                                 limit: int = 10) -> List[ContextItem]:
        """查找相似上下文"""
        # 获取候选上下文
        candidates = await self.search_context(context_type=context_type, limit=100)
        
        # 简单的相似性计算（基于内容哈希）
        query_hash = hashlib.md5(str(query_content).encode()).hexdigest()
        
        similar_context = []
        for ctx in candidates:
            ctx_hash = hashlib.md5(str(ctx.content).encode()).hexdigest()
            if ctx_hash == query_hash:
                similar_context.append(ctx)
        
        # 按优先级和访问频率排序
        similar_context.sort(key=lambda x: (x.priority.value, x.access_count), reverse=True)
        
        return similar_context[:limit]


# 使用示例
if __name__ == "__main__":
    async def main():
        # 创建上下文管理器
        context_manager = ContextManager()
        
        # 添加一些测试上下文
        await context_manager.add_context(
            content="Hello, world!",
            context_type=ContextType.TEXT,
            priority=ContextPriority.HIGH,
            tags={"greeting", "english"}
        )
        
        await context_manager.add_context(
            content="这是一个测试",
            context_type=ContextType.TEXT,
            priority=ContextPriority.MEDIUM,
            tags={"test", "chinese"}
        )
        
        # 搜索上下文
        results = await context_manager.search_context(tags={"greeting"})
        print(f"搜索结果: {len(results)} 项")
        
        # 获取统计信息
        stats = await context_manager.get_context_stats()
        print(f"统计信息: {stats}")
        
        # 创建摘要
        summary = await context_manager.create_context_summary()
        print(f"上下文摘要: {summary}")
    
    # 运行示例
    asyncio.run(main())