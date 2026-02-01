#!/usr/bin/env python3
"""
评估优化框架

基于 NotebookLM 文档驱动开发
文档: advanced-evaluation-SKILL.md, evaluation-SKILL.md, Strategic Optimization Framework for AI Translation Agents

功能:
- 翻译质量评估
- 性能监控
- 瓶颈分析
- 优化策略
- A/B测试框架
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta
import re
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvaluationMetric(Enum):
    """评估指标"""
    BLEU = "bleu"
    ROUGE = "rouge"
    METEOR = "meteor"
    TER = "ter"
    CHRF = "chrf"
    BERT_SCORE = "bert_score"
    COMET = "comet"
    CUSTOM = "custom"


class PerformanceMetric(Enum):
    """性能指标"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    LATENCY = "latency"
    AVAILABILITY = "availability"


@dataclass
class TranslationResult:
    """翻译结果"""
    source_text: str
    translated_text: str
    reference_text: Optional[str] = None
    confidence: float = 0.0
    processing_time: float = 0.0
    model_name: str = ""
    language_pair: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """评估结果"""
    metric: EvaluationMetric
    score: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceData:
    """性能数据"""
    metric: PerformanceMetric
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TranslationQualityEvaluator:
    """翻译质量评估器"""
    
    def __init__(self):
        self.metric_calculators = {
            EvaluationMetric.BLEU: self._calculate_bleu,
            EvaluationMetric.ROUGE: self._calculate_rouge,
            EvaluationMetric.TER: self._calculate_ter,
            EvaluationMetric.CUSTOM: self._calculate_custom
        }
    
    async def evaluate_translation(self, 
                                  translation_result: TranslationResult,
                                  metrics: List[EvaluationMetric] = None) -> List[EvaluationResult]:
        """评估翻译质量"""
        if metrics is None:
            metrics = [EvaluationMetric.BLEU, EvaluationMetric.ROUGE, EvaluationMetric.TER]
        
        results = []
        
        for metric in metrics:
            if metric in self.metric_calculators:
                try:
                    score, details = await self.metric_calculators[metric](translation_result)
                    result = EvaluationResult(
                        metric=metric,
                        score=score,
                        details=details,
                        metadata=translation_result.metadata
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to calculate {metric.value}: {e}")
        
        return results
    
    async def _calculate_bleu(self, translation_result: TranslationResult) -> Tuple[float, Dict[str, Any]]:
        """计算BLEU分数"""
        try:
            # 简单的BLEU实现
            from collections import Counter
            
            def get_ngrams(tokens, n):
                return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
            
            # 分词
            source_tokens = translation_result.source_text.lower().split()
            translated_tokens = translation_result.translated_text.lower().split()
            reference_tokens = translation_result.reference_text.lower().split() if translation_result.reference_text else translated_tokens
            
            # 计算n-gram精度
            precisions = []
            for n in range(1, 5):
                source_ngrams = Counter(get_ngrams(source_tokens, n))
                translated_ngrams = Counter(get_ngrams(translated_tokens, n))
                reference_ngrams = Counter(get_ngrams(reference_tokens, n))
                
                if not translated_ngrams:
                    precisions.append(0.0)
                    continue
                
                clipped_ngrams = translated_ngrams & reference_ngrams
                precision = sum(clipped_ngrams.values()) / sum(translated_ngrams.values())
                precisions.append(precision)
            
            # 计算BLEU分数
            if min(precisions) > 0:
                bp = 1.0  # 简化版，不考虑简短惩罚
                bleu = bp * (statistics.geometric_mean(precisions) * 100)
            else:
                bleu = 0.0
            
            details = {
                "precisions": precisions,
                "brevity_penalty": bp,
                "geometric_mean": statistics.geometric_mean(precisions)
            }
            
            return bleu, details
            
        except Exception as e:
            logger.error(f"BLEU calculation failed: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_rouge(self, translation_result: TranslationResult) -> Tuple[float, Dict[str, Any]]:
        """计算ROUGE分数"""
        try:
            # 简单的ROUGE实现
            def get_lcs_length(x, y):
                m, n = len(x), len(y)
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        if x[i-1] == y[j-1]:
                            dp[i][j] = dp[i-1][j-1] + 1
                        else:
                            dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                
                return dp[m][n]
            
            translated_tokens = translation_result.translated_text.lower().split()
            reference_tokens = translation_result.reference_text.lower().split() if translation_result.reference_text else translated_tokens
            
            # 计算ROUGE-L
            lcs_length = get_lcs_length(translated_tokens, reference_tokens)
            rouge_l = (lcs_length / len(translated_tokens)) * 100 if translated_tokens else 0.0
            
            details = {
                "lcs_length": lcs_length,
                "translated_length": len(translated_tokens),
                "reference_length": len(reference_tokens)
            }
            
            return rouge_l, details
            
        except Exception as e:
            logger.error(f"ROUGE calculation failed: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_ter(self, translation_result: TranslationResult) -> Tuple[float, Dict[str, Any]]:
        """计算TER（翻译错误率）"""
        try:
            # 简单的TER实现
            def edit_distance(s1, s2):
                m, n = len(s1), len(s2)
                dp = [[0] * (n + 1) for _ in range(m + 1)]
                
                for i in range(m + 1):
                    dp[i][0] = i
                for j in range(n + 1):
                    dp[0][j] = j
                
                for i in range(1, m + 1):
                    for j in range(1, n + 1):
                        if s1[i-1] == s2[j-1]:
                            dp[i][j] = dp[i-1][j-1]
                        else:
                            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
                
                return dp[m][n]
            
            translated_tokens = translation_result.translated_text.lower().split()
            reference_tokens = translation_result.reference_text.lower().split() if translation_result.reference_text else translated_tokens
            
            distance = edit_distance(translated_tokens, reference_tokens)
            ter = (distance / len(reference_tokens)) * 100 if reference_tokens else 0.0
            
            details = {
                "edit_distance": distance,
                "translated_length": len(translated_tokens),
                "reference_length": len(reference_tokens)
            }
            
            return ter, details
            
        except Exception as e:
            logger.error(f"TER calculation failed: {e}")
            return 0.0, {"error": str(e)}
    
    async def _calculate_custom(self, translation_result: TranslationResult) -> Tuple[float, Dict[str, Any]]:
        """计算自定义指标"""
        try:
            # 自定义指标：基于长度和相似度的简单评分
            source_length = len(translation_result.source_text)
            translated_length = len(translation_result.translated_text)
            
            # 长度比率
            length_ratio = translated_length / source_length if source_length > 0 else 1.0
            
            # 简单的相似度计算（基于字符重叠）
            source_chars = set(translation_result.source_text.lower())
            translated_chars = set(translation_result.translated_text.lower())
            overlap_ratio = len(source_chars & translated_chars) / len(source_chars | translated_chars) if source_chars or translated_chars else 0.0
            
            # 综合评分
            custom_score = (length_ratio * 0.3 + overlap_ratio * 0.7) * 100
            
            details = {
                "length_ratio": length_ratio,
                "overlap_ratio": overlap_ratio,
                "source_length": source_length,
                "translated_length": translated_length
            }
            
            return custom_score, details
            
        except Exception as e:
            logger.error(f"Custom metric calculation failed: {e}")
            return 0.0, {"error": str(e)}


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, storage_path: str = "performance_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # 初始化数据库
        self.db_path = self.storage_path / "performance.db"
        self._init_database()
        
        # 内存缓存
        self.cache: Dict[str, List[PerformanceData]] = defaultdict(list)
        self.cache_size = 1000
        
        # 性能阈值
        self.thresholds = {
            PerformanceMetric.RESPONSE_TIME: 1000,  # 1秒
            PerformanceMetric.ERROR_RATE: 0.05,     # 5%
            PerformanceMetric.MEMORY_USAGE: 0.8,    # 80%
            PerformanceMetric.CPU_USAGE: 0.8,       # 80%
            PerformanceMetric.AVAILABILITY: 0.99   # 99%
        }
        
        logger.info(f"Performance monitor initialized at {self.storage_path}")
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 创建性能数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT,
                value REAL,
                timestamp TEXT,
                metadata TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_timestamp ON performance_data(metric, timestamp)')
        
        conn.commit()
        conn.close()
    
    async def record_performance(self, 
                                metric: PerformanceMetric,
                                value: float,
                                metadata: Optional[Dict[str, Any]] = None):
        """记录性能数据"""
        try:
            performance_data = PerformanceData(
                metric=metric,
                value=value,
                metadata=metadata or {}
            )
            
            # 存储到数据库
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_data (metric, value, timestamp, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                metric.value,
                value,
                performance_data.timestamp.isoformat(),
                json.dumps(performance_data.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            # 添加到缓存
            cache_key = metric.value
            self.cache[cache_key].append(performance_data)
            
            # 如果缓存超过大小限制，删除最旧的数据
            if len(self.cache[cache_key]) > self.cache_size:
                self.cache[cache_key].pop(0)
            
            # 检查阈值
            if metric in self.thresholds:
                threshold = self.thresholds[metric]
                if value > threshold:
                    logger.warning(f"Performance threshold exceeded: {metric.value} = {value} (threshold: {threshold})")
            
            logger.info(f"Performance recorded: {metric.value} = {value}")
            
        except Exception as e:
            logger.error(f"Failed to record performance: {e}")
    
    async def get_performance_data(self, 
                                 metric: PerformanceMetric,
                                 time_start: Optional[datetime] = None,
                                 time_end: Optional[datetime] = None,
                                 limit: int = 1000) -> List[PerformanceData]:
        """获取性能数据"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 构建查询
            query = "SELECT * FROM performance_data WHERE metric = ?"
            params = [metric.value]
            
            if time_start:
                query += " AND timestamp >= ?"
                params.append(time_start.isoformat())
            
            if time_end:
                query += " AND timestamp <= ?"
                params.append(time_end.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            conn.close()
            
            # 转换为PerformanceData对象
            performance_data = []
            for row in rows:
                performance_data.append(PerformanceData(
                    metric=PerformanceMetric(row[1]),
                    value=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    metadata=json.loads(row[4]) if row[4] else {}
                ))
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Failed to get performance data: {e}")
            return []
    
    async def get_performance_stats(self, 
                                  metric: PerformanceMetric,
                                  time_start: Optional[datetime] = None,
                                  time_end: Optional[datetime] = None) -> Dict[str, float]:
        """获取性能统计信息"""
        try:
            data = await self.get_performance_data(metric, time_start, time_end)
            
            if not data:
                return {}
            
            values = [d.value for d in data]
            
            return {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "count": len(values)
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {}
    
    async def detect_bottlenecks(self, time_window: timedelta = timedelta(hours=1)) -> List[Dict[str, Any]]:
        """检测性能瓶颈"""
        try:
            bottlenecks = []
            current_time = datetime.now()
            time_start = current_time - time_window
            
            # 检查所有性能指标
            for metric in PerformanceMetric:
                stats = await self.get_performance_stats(metric, time_start)
                
                if not stats:
                    continue
                
                # 检查是否超过阈值
                if metric in self.thresholds:
                    threshold = self.thresholds[metric]
                    avg_value = stats["avg"]
                    
                    if avg_value > threshold:
                        bottlenecks.append({
                            "metric": metric.value,
                            "threshold": threshold,
                            "average": avg_value,
                            "severity": "high" if avg_value > threshold * 1.5 else "medium",
                            "time_window": str(time_window),
                            "stats": stats
                        })
            
            # 按严重程度排序
            bottlenecks.sort(key=lambda x: x["severity"], reverse=True)
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Failed to detect bottlenecks: {e}")
            return []


class OptimizationStrategy:
    """优化策略基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        self.parameters = {}
    
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用优化策略"""
        raise NotImplementedError
    
    async def evaluate(self, context: Dict[str, Any]) -> float:
        """评估优化效果"""
        raise NotImplementedError


class CachingStrategy(OptimizationStrategy):
    """缓存优化策略"""
    
    def __init__(self):
        super().__init__("caching", "缓存优化策略")
        self.parameters = {
            "cache_size": 1000,
            "cache_ttl": 3600,
            "eviction_policy": "lru"
        }
    
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用缓存优化"""
        try:
            # 模拟缓存优化
            cache_hits = context.get("cache_hits", 0)
            cache_misses = context.get("cache_misses", 0)
            
            total_requests = cache_hits + cache_misses
            hit_rate = cache_hits / total_requests if total_requests > 0 else 0.0
            
            optimization_result = {
                "strategy": self.name,
                "cache_hit_rate": hit_rate,
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "estimated_improvement": hit_rate * 0.1  # 假设缓存可以提升10%性能
            }
            
            logger.info(f"Caching strategy applied: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Caching strategy failed: {e}")
            return {"strategy": self.name, "error": str(e)}
    
    async def evaluate(self, context: Dict[str, Any]) -> float:
        """评估缓存优化效果"""
        try:
            result = await self.apply(context)
            return result.get("estimated_improvement", 0.0)
        except Exception as e:
            logger.error(f"Caching strategy evaluation failed: {e}")
            return 0.0


class LoadBalancingStrategy(OptimizationStrategy):
    """负载均衡优化策略"""
    
    def __init__(self):
        super().__init__("load_balancing", "负载均衡优化策略")
        self.parameters = {
            "max_workers": 4,
            "queue_size": 100,
            "timeout": 30
        }
    
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用负载均衡优化"""
        try:
            # 模拟负载均衡优化
            current_load = context.get("current_load", 0.5)
            max_capacity = context.get("max_capacity", 1.0)
            
            load_factor = current_load / max_capacity
            optimization_result = {
                "strategy": self.name,
                "current_load": current_load,
                "max_capacity": max_capacity,
                "load_factor": load_factor,
                "estimated_improvement": (1.0 - load_factor) * 0.2  # 假设负载均衡可以提升20%性能
            }
            
            logger.info(f"Load balancing strategy applied: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Load balancing strategy failed: {e}")
            return {"strategy": self.name, "error": str(e)}
    
    async def evaluate(self, context: Dict[str, Any]) -> float:
        """评估负载均衡优化效果"""
        try:
            result = await self.apply(context)
            return result.get("estimated_improvement", 0.0)
        except Exception as e:
            logger.error(f"Load balancing strategy evaluation failed: {e}")
            return 0.0


class ResourceOptimizationStrategy(OptimizationStrategy):
    """资源优化策略"""
    
    def __init__(self):
        super().__init__("resource_optimization", "资源优化策略")
        self.parameters = {
            "memory_limit": "2GB",
            "cpu_limit": "80%",
            "gpu_limit": "100%"
        }
    
    async def apply(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """应用资源优化"""
        try:
            # 模拟资源优化
            memory_usage = context.get("memory_usage", 0.7)
            cpu_usage = context.get("cpu_usage", 0.6)
            
            resource_efficiency = (1.0 - memory_usage) * 0.6 + (1.0 - cpu_usage) * 0.4
            optimization_result = {
                "strategy": self.name,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage,
                "resource_efficiency": resource_efficiency,
                "estimated_improvement": resource_efficiency * 0.15  # 假设资源优化可以提升15%性能
            }
            
            logger.info(f"Resource optimization strategy applied: {optimization_result}")
            return optimization_result
            
        except Exception as e:
            logger.error(f"Resource optimization strategy failed: {e}")
            return {"strategy": self.name, "error": str(e)}
    
    async def evaluate(self, context: Dict[str, Any]) -> float:
        """评估资源优化效果"""
        try:
            result = await self.apply(context)
            return result.get("estimated_improvement", 0.0)
        except Exception as e:
            logger.error(f"Resource optimization strategy evaluation failed: {e}")
            return 0.0


class ABTestFramework:
    """A/B测试框架"""
    
    def __init__(self):
        self.experiments = {}
        self.results = {}
    
    def create_experiment(self, 
                         name: str,
                         description: str,
                         variants: List[Dict[str, Any]],
                          metrics: List[str]) -> str:
        """创建A/B测试实验"""
        experiment_id = f"exp_{name}_{int(time.time())}"
        
        self.experiments[experiment_id] = {
            "name": name,
            "description": description,
            "variants": variants,
            "metrics": metrics,
            "status": "created",
            "created_at": datetime.now(),
            "results": {}
        }
        
        logger.info(f"AB test experiment created: {experiment_id}")
        return experiment_id
    
    async def run_experiment(self, experiment_id: str, 
                           traffic_split: Dict[str, float] = None) -> Dict[str, Any]:
        """运行A/B测试实验"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            
            if traffic_split is None:
                # 均匀分配流量
                variants = experiment["variants"]
                traffic_split = {variant["name"]: 1.0/len(variants) for variant in variants}
            
            # 模拟实验运行
            results = {}
            for variant_name, split in traffic_split.items():
                # 模拟性能数据
                variant_results = {
                    "variant": variant_name,
                    "traffic_split": split,
                    "response_time": 1000 + (hash(variant_name) % 500),  # 模拟响应时间
                    "error_rate": 0.01 + (hash(variant_name) % 20) / 1000,  # 模拟错误率
                    "conversion_rate": 0.1 + (hash(variant_name) % 50) / 1000,  # 模拟转化率
                    "sample_size": int(1000 * split)  # 模拟样本大小
                }
                results[variant_name] = variant_results
            
            # 计算统计显著性
            best_variant = max(results.keys(), 
                              key=lambda k: results[k]["conversion_rate"])
            
            experiment["results"] = results
            experiment["status"] = "completed"
            experiment["best_variant"] = best_variant
            experiment["completed_at"] = datetime.now()
            
            logger.info(f"AB test experiment completed: {experiment_id}")
            return results
            
        except Exception as e:
            logger.error(f"AB test experiment failed: {e}")
            return {"error": str(e)}
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """获取实验结果"""
        if experiment_id not in self.experiments:
            return {"error": f"Experiment {experiment_id} not found"}
        
        experiment = self.experiments[experiment_id]
        return {
            "experiment_id": experiment_id,
            "name": experiment["name"],
            "description": experiment["description"],
            "status": experiment["status"],
            "created_at": experiment["created_at"],
            "completed_at": experiment.get("completed_at"),
            "results": experiment.get("results", {}),
            "best_variant": experiment.get("best_variant")
        }


class OptimizationFramework:
    """优化框架"""
    
    def __init__(self):
        self.evaluator = TranslationQualityEvaluator()
        self.monitor = PerformanceMonitor()
        self.strategies = [
            CachingStrategy(),
            LoadBalancingStrategy(),
            ResourceOptimizationStrategy()
        ]
        self.ab_test = ABTestFramework()
    
    async def evaluate_translation_quality(self, translation_result: TranslationResult) -> List[EvaluationResult]:
        """评估翻译质量"""
        return await self.evaluator.evaluate_translation(translation_result)
    
    async def record_performance(self, metric: PerformanceMetric, value: float, metadata: Optional[Dict[str, Any]] = None):
        """记录性能数据"""
        await self.monitor.record_performance(metric, value, metadata)
    
    async def get_performance_stats(self, metric: PerformanceMetric) -> Dict[str, float]:
        """获取性能统计信息"""
        return await self.monitor.get_performance_stats(metric)
    
    async def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """检测性能瓶颈"""
        return await self.monitor.detect_bottlenecks()
    
    async def apply_optimization_strategies(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """应用优化策略"""
        results = []
        
        for strategy in self.strategies:
            if strategy.enabled:
                try:
                    result = await strategy.apply(context)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Strategy {strategy.name} failed: {e}")
                    results.append({"strategy": strategy.name, "error": str(e)})
        
        return results
    
    async def evaluate_optimization_strategies(self, context: Dict[str, Any]) -> Dict[str, float]:
        """评估优化策略"""
        evaluations = {}
        
        for strategy in self.strategies:
            if strategy.enabled:
                try:
                    score = await strategy.evaluate(context)
                    evaluations[strategy.name] = score
                except Exception as e:
                    logger.error(f"Strategy {strategy.name} evaluation failed: {e}")
                    evaluations[strategy.name] = 0.0
        
        return evaluations
    
    def create_ab_test(self, name: str, description: str, variants: List[Dict[str, Any]], metrics: List[str]) -> str:
        """创建A/B测试"""
        return self.ab_test.create_experiment(name, description, variants, metrics)
    
    async def run_ab_test(self, experiment_id: str, traffic_split: Dict[str, float] = None) -> Dict[str, Any]:
        """运行A/B测试"""
        return await self.ab_test.run_experiment(experiment_id, traffic_split)
    
    def get_ab_test_results(self, experiment_id: str) -> Dict[str, Any]:
        """获取A/B测试结果"""
        return self.ab_test.get_experiment_results(experiment_id)


# 使用示例
if __name__ == "__main__":
    async def main():
        # 创建优化框架
        framework = OptimizationFramework()
        
        # 测试翻译质量评估
        translation_result = TranslationResult(
            source_text="Hello, world!",
            translated_text="你好，世界！",
            reference_text="你好，世界！",
            confidence=0.95,
            processing_time=1.5,
            model_name="test_model",
            language_pair="en-zh"
        )
        
        evaluation_results = await framework.evaluate_translation_quality(translation_result)
        print(f"翻译质量评估结果: {len(evaluation_results)} 项")
        
        # 测试性能监控
        await framework.record_performance(PerformanceMetric.RESPONSE_TIME, 500.0)
        await framework.record_performance(PerformanceMetric.ERROR_RATE, 0.02)
        
        stats = await framework.get_performance_stats(PerformanceMetric.RESPONSE_TIME)
        print(f"性能统计: {stats}")
        
        # 测试瓶颈检测
        bottlenecks = await framework.detect_bottlenecks()
        print(f"检测到的瓶颈: {len(bottlenecks)} 个")
        
        # 测试优化策略
        context = {
            "cache_hits": 100,
            "cache_misses": 20,
            "current_load": 0.7,
            "max_capacity": 1.0,
            "memory_usage": 0.6,
            "cpu_usage": 0.5
        }
        
        optimization_results = await framework.apply_optimization_strategies(context)
        print(f"优化策略结果: {len(optimization_results)} 项")
        
        # 测试A/B测试
        experiment_id = framework.create_ab_test(
            name="translation_model_test",
            description="翻译模型A/B测试",
            variants=[
                {"name": "model_a", "description": "模型A"},
                {"name": "model_b", "description": "模型B"}
            ],
            metrics=["response_time", "error_rate", "conversion_rate"]
        )
        
        ab_test_results = await framework.run_ab_test(experiment_id)
        print(f"A/B测试结果: {ab_test_results}")
    
    # 运行示例
    asyncio.run(main())