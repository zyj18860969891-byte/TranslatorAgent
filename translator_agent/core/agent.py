#!/usr/bin/env python3
"""
智能体系统模块

基于 NotebookLM 文档驱动开发
文档: OpenManus_架构详解.md, multi-agent-patterns-SKILL.md, bdi-mental-states-SKILL.md

功能:
- 智能体基类
- BDI 心理状态建模
- 多智能体协作
- 意图识别与工具编排
"""

import abc
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """智能体状态"""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    DONE = "done"


class ToolType(Enum):
    """工具类型"""
    TRANSLATION = "translation"
    VIDEO_PROCESSING = "video_processing"
    SUBTITLE_EXTRACTION = "subtitle_extraction"
    EMOTION_ANALYSIS = "emotion_analysis"
    FILE_OPERATION = "file_operation"
    API_CALL = "api_call"


@dataclass
class Tool:
    """工具定义"""
    name: str
    tool_type: ToolType
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Awaitable[Any]]
    enabled: bool = True


@dataclass
class BDIState:
    """BDI (Belief-Desire-Intention) 心理状态"""
    # Belief (信念) - 对世界的认知
    beliefs: Dict[str, Any] = field(default_factory=dict)
    
    # Desire (愿望) - 目标和期望
    desires: List[str] = field(default_factory=list)
    
    # Intention (意图) - 当前计划和行动
    intentions: List[str] = field(default_factory=list)
    
    # 情感状态
    emotions: List[str] = field(default_factory=list)
    
    # 上下文记忆
    memory: Dict[str, Any] = field(default_factory=dict)
    
    def update_belief(self, key: str, value: Any):
        """更新信念"""
        self.beliefs[key] = value
        logger.info(f"Belief updated: {key} = {value}")
    
    def add_desire(self, desire: str):
        """添加愿望"""
        if desire not in self.desires:
            self.desires.append(desire)
            logger.info(f"Desire added: {desire}")
    
    def add_intention(self, intention: str):
        """添加意图"""
        if intention not in self.intentions:
            self.intentions.append(intention)
            logger.info(f"Intention added: {intention}")
    
    def clear_intentions(self):
        """清空意图"""
        self.intentions.clear()
        logger.info("Intentions cleared")
    
    def add_emotion(self, emotion: str):
        """添加情感"""
        if emotion not in self.emotions:
            self.emotions.append(emotion)
            logger.info(f"Emotion added: {emotion}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "beliefs": self.beliefs,
            "desires": self.desires,
            "intentions": self.intentions,
            "emotions": self.emotions,
            "memory": self.memory
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BDIState':
        """从字典创建"""
        return cls(
            beliefs=data.get("beliefs", {}),
            desires=data.get("desires", []),
            intentions=data.get("intentions", []),
            emotions=data.get("emotions", []),
            memory=data.get("memory", {})
        )


@dataclass
class Task:
    """任务定义"""
    task_id: str
    description: str
    priority: int = 1  # 1-10, 10 is highest
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(abc.ABC):
    """智能体基类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.bdi = BDIState()
        self.tools: Dict[str, Tool] = {}
        self.tasks: Dict[str, Task] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 注册默认工具
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        # 可以在子类中重写
        pass
    
    def register_tool(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
        self.logger.info(f"Tool registered: {tool.name}")
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        if not tool.enabled:
            raise ValueError(f"Tool '{tool_name}' is disabled")
        
        self.logger.info(f"Executing tool: {tool_name}")
        
        try:
            result = await tool.func(**kwargs)
            self.logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Tool {tool_name} failed: {e}")
            raise
    
    @abc.abstractmethod
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考（意图识别和规划）"""
        pass
    
    @abc.abstractmethod
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """行动（执行任务）"""
        pass
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """运行智能体"""
        self.status = AgentStatus.THINKING
        self.logger.info(f"{self.name} is thinking...")
        
        # 思考阶段
        think_result = await self.think(context)
        
        # 更新 BDI 状态
        if "beliefs" in think_result:
            for key, value in think_result["beliefs"].items():
                self.bdi.update_belief(key, value)
        
        if "desires" in think_result:
            for desire in think_result["desires"]:
                self.bdi.add_desire(desire)
        
        if "intentions" in think_result:
            for intention in think_result["intentions"]:
                self.bdi.add_intention(intention)
        
        # 行动阶段
        self.status = AgentStatus.WORKING
        self.logger.info(f"{self.name} is acting...")
        
        act_result = await self.act(context)
        
        # 更新状态
        self.status = AgentStatus.DONE
        self.logger.info(f"{self.name} finished")
        
        return {
            "think_result": think_result,
            "act_result": act_result,
            "bdi_state": self.bdi.to_dict()
        }
    
    def save_state(self, path: str):
        """保存状态"""
        state = {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "bdi": self.bdi.to_dict(),
            "tasks": {tid: asdict(task) for tid, task in self.tasks.items()}
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"State saved to {path}")
    
    def load_state(self, path: str):
        """加载状态"""
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.name = state["name"]
        self.description = state["description"]
        self.status = AgentStatus(state["status"])
        self.bdi = BDIState.from_dict(state["bdi"])
        
        self.logger.info(f"State loaded from {path}")


class TranslatorAgent(BaseAgent):
    """翻译器智能体"""
    
    def __init__(self, translator_client, model_client):
        super().__init__(
            name="TranslatorAgent",
            description="负责翻译任务的智能体，协调翻译引擎和上下文管理"
        )
        
        self.translator_client = translator_client
        self.model_client = model_client
        
        # 更新 BDI 状态
        self.bdi.update_belief("translation_engine", "mimo-v2-flash")
        self.bdi.update_belief("supported_languages", ["en", "zh", "ja", "ko", "fr", "de", "es"])
        self.bdi.add_desire("提供高质量翻译")
        self.bdi.add_desire("保持术语一致性")
        self.bdi.add_desire("注入情感温度")
    
    def _register_default_tools(self):
        """注册翻译相关工具"""
        # 翻译工具
        self.register_tool(Tool(
            name="translate_text",
            tool_type=ToolType.TRANSLATION,
            description="翻译文本",
            parameters={
                "text": "str",
                "source_lang": "str",
                "target_lang": "str"
            },
            func=self._translate_text_func
        ))
        
        # 情感分析工具
        self.register_tool(Tool(
            name="analyze_emotion",
            tool_type=ToolType.EMOTION_ANALYSIS,
            description="分析文本情感",
            parameters={
                "text": "str"
            },
            func=self._analyze_emotion_func
        ))
    
    async def _translate_text_func(self, text: str, source_lang: str, target_lang: str) -> str:
        """翻译文本函数"""
        try:
            # 使用 ModelScope 客户端翻译
            translated = await self.model_client.translate(text, source_lang, target_lang)
            return translated
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            raise
    
    async def _analyze_emotion_func(self, text: str) -> Dict[str, Any]:
        """分析情感函数"""
        try:
            # 这里可以调用情感分析模型
            # 暂时返回模拟结果
            return {"emotions": ["neutral"], "confidence": [1.0]}
        except Exception as e:
            self.logger.error(f"Emotion analysis failed: {e}")
            raise
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考翻译任务"""
        text = context.get("text", "")
        source_lang = context.get("source_lang", "en")
        target_lang = context.get("target_lang", "zh")
        
        # 分析文本
        beliefs = {
            "text_length": len(text),
            "source_lang": source_lang,
            "target_lang": target_lang,
            "has_context": "context" in context
        }
        
        desires = [
            f"将 {source_lang} 翻译为 {target_lang}",
            "保持翻译质量"
        ]
        
        intentions = [
            "分析文本情感",
            "调用翻译引擎",
            "后处理翻译结果"
        ]
        
        return {
            "beliefs": beliefs,
            "desires": desires,
            "intentions": intentions
        }
    
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行翻译"""
        text = context.get("text", "")
        source_lang = context.get("source_lang", "en")
        target_lang = context.get("target_lang", "zh")
        
        results = {}
        
        # 1. 分析情感（如果启用）
        if context.get("enable_emotion_analysis", False):
            try:
                emotion_result = await self.execute_tool("analyze_emotion", text=text)
                results["emotion"] = emotion_result
                self.bdi.add_emotion(emotion_result.get("emotions", ["neutral"])[0])
            except Exception as e:
                self.logger.warning(f"Emotion analysis skipped: {e}")
        
        # 2. 翻译文本
        try:
            translated = await self.execute_tool(
                "translate_text",
                text=text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            results["translated_text"] = translated
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            results["error"] = str(e)
        
        # 3. 后处理（如果需要）
        if context.get("enable_post_process", True):
            # 这里可以添加后处理逻辑
            pass
        
        return results


class VideoTranslatorAgent(BaseAgent):
    """视频翻译智能体"""
    
    def __init__(self, video_processor, model_client, translator_agent):
        super().__init__(
            name="VideoTranslatorAgent",
            description="负责视频翻译的智能体，协调视频处理和翻译"
        )
        
        self.video_processor = video_processor
        self.model_client = model_client
        self.translator_agent = translator_agent
        
        # 更新 BDI 状态
        self.bdi.update_belief("video_processing_enabled", True)
        self.bdi.update_belief("subtitle_extraction_enabled", True)
        self.bdi.update_belief("emotion_injection_enabled", True)
        self.bdi.add_desire("生成高质量视频翻译")
        self.bdi.add_desire("保持时间轴同步")
        self.bdi.add_desire("优化视频质量")
    
    def _register_default_tools(self):
        """注册视频处理工具"""
        # 视频处理工具
        self.register_tool(Tool(
            name="process_video",
            tool_type=ToolType.VIDEO_PROCESSING,
            description="处理视频文件",
            parameters={
                "video_path": "str",
                "enable_subtitle_extraction": "bool",
                "enable_subtitle_erasure": "bool"
            },
            func=self._process_video_func
        ))
        
        # 字幕翻译工具
        self.register_tool(Tool(
            name="translate_subtitles",
            tool_type=ToolType.TRANSLATION,
            description="翻译字幕",
            parameters={
                "subtitles": "List[SubtitleSegment]",
                "source_lang": "str",
                "target_lang": "str"
            },
            func=self._translate_subtitles_func
        ))
    
    async def _process_video_func(self, video_path: str, 
                                  enable_subtitle_extraction: bool = True,
                                  enable_subtitle_erasure: bool = False) -> Dict[str, Any]:
        """处理视频函数"""
        try:
            results = await self.video_processor.process_video(
                video_path=video_path,
                model_client=self.model_client,
                enable_subtitle_extraction=enable_subtitle_extraction,
                enable_subtitle_erasure=enable_subtitle_erasure
            )
            return results
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            raise
    
    async def _translate_subtitles_func(self, subtitles: List[Any], 
                                       source_lang: str, 
                                       target_lang: str) -> List[Any]:
        """翻译字幕函数"""
        try:
            # 使用翻译器智能体翻译字幕
            translated = await self.translator_agent.video_processor.translate_subtitles(
                subtitles=subtitles,
                translator=self.translator_agent.translator_client,
                source_lang=source_lang,
                target_lang=target_lang
            )
            return translated
        except Exception as e:
            self.logger.error(f"Subtitle translation failed: {e}")
            raise
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考视频翻译任务"""
        video_path = context.get("video_path", "")
        
        # 分析任务
        beliefs = {
            "video_path": video_path,
            "has_video": bool(video_path),
            "enable_subtitle_extraction": context.get("enable_subtitle_extraction", True),
            "enable_emotion_analysis": context.get("enable_emotion_analysis", True)
        }
        
        desires = [
            "提取视频字幕",
            "翻译字幕文本",
            "注入情感信息",
            "生成翻译后视频"
        ]
        
        intentions = [
            "提取视频帧",
            "检测字幕",
            "分析情感",
            "翻译字幕",
            "擦除原字幕",
            "压制新字幕"
        ]
        
        return {
            "beliefs": beliefs,
            "desires": desires,
            "intentions": intentions
        }
    
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行视频翻译"""
        video_path = context.get("video_path", "")
        
        results = {}
        
        # 1. 处理视频
        try:
            video_results = await self.execute_tool(
                "process_video",
                video_path=video_path,
                enable_subtitle_extraction=context.get("enable_subtitle_extraction", True),
                enable_subtitle_erasure=context.get("enable_subtitle_erasure", False)
            )
            results.update(video_results)
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            return {"error": str(e)}
        
        # 2. 翻译字幕
        if "subtitles" in video_results:
            try:
                translated_subtitles = await self.execute_tool(
                    "translate_subtitles",
                    subtitles=video_results["subtitles"],
                    source_lang=context.get("source_lang", "en"),
                    target_lang=context.get("target_lang", "zh")
                )
                results["translated_subtitles"] = translated_subtitles
            except Exception as e:
                self.logger.error(f"Subtitle translation failed: {e}")
                results["translation_error"] = str(e)
        
        return results


class SupervisorAgent(BaseAgent):
    """主管智能体（协调多个子智能体）"""
    
    def __init__(self, translator_agent: TranslatorAgent, video_agent: VideoTranslatorAgent):
        super().__init__(
            name="SupervisorAgent",
            description="主管智能体，协调翻译器和视频翻译器"
        )
        
        self.translator_agent = translator_agent
        self.video_agent = video_agent
        self.sub_agents = {
            "translator": translator_agent,
            "video_translator": video_agent
        }
        
        # 更新 BDI 状态
        self.bdi.update_belief("coordinator_mode", "supervisor")
        self.bdi.update_belief("active_agents", ["translator", "video_translator"])
        self.bdi.add_desire("协调多个智能体完成复杂任务")
        self.bdi.add_desire("优化任务分配")
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考任务分配"""
        task_type = context.get("task_type", "unknown")
        
        # 意图识别
        if "video" in task_type.lower() or "video_path" in context:
            target_agent = "video_translator"
            task_desc = "视频翻译任务"
        elif "text" in task_type.lower() or "text" in context:
            target_agent = "translator"
            task_desc = "文本翻译任务"
        else:
            target_agent = "translator"
            task_desc = "通用翻译任务"
        
        beliefs = {
            "task_type": task_type,
            "target_agent": target_agent,
            "task_description": task_desc
        }
        
        desires = [
            f"分配任务到 {target_agent}",
            "确保任务顺利完成"
        ]
        
        intentions = [
            f"调用 {target_agent}",
            "监控执行状态",
            "收集结果"
        ]
        
        return {
            "beliefs": beliefs,
            "desires": desires,
            "intentions": intentions
        }
    
    async def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务分配"""
        target_agent_name = context.get("target_agent")
        
        if not target_agent_name:
            # 自动选择目标智能体
            if "video_path" in context:
                target_agent_name = "video_translator"
            else:
                target_agent_name = "translator"
        
        if target_agent_name not in self.sub_agents:
            raise ValueError(f"Unknown agent: {target_agent_name}")
        
        target_agent = self.sub_agents[target_agent_name]
        
        self.logger.info(f"Delegating task to {target_agent_name}")
        
        # 执行任务
        try:
            result = await target_agent.run(context)
            return {
                "target_agent": target_agent_name,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Task delegation failed: {e}")
            return {
                "target_agent": target_agent_name,
                "error": str(e),
                "status": "failed"
            }


# 使用示例
if __name__ == "__main__":
    async def main():
        # 模拟客户端
        class MockTranslatorClient:
            async def translate_async(self, text: str, source_lang: str, target_lang: str) -> str:
                return f"[翻译] {text}"
        
        class MockModelClient:
            async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
                return f"[ModelScope] {text}"
            
            async def analyze_emotion(self, audio_path: str) -> Dict[str, Any]:
                return {"emotions": ["neutral"], "confidence": [1.0]}
        
        class MockVideoProcessor:
            async def process_video(self, video_path: str, model_client, **kwargs) -> Dict[str, Any]:
                return {"frames": [], "subtitles": []}
        
        # 创建智能体
        translator_client = MockTranslatorClient()
        model_client = MockModelClient()
        video_processor = MockVideoProcessor()
        
        translator_agent = TranslatorAgent(translator_client, model_client)
        video_agent = VideoTranslatorAgent(video_processor, model_client, translator_client)
        supervisor = SupervisorAgent(translator_agent, video_agent)
        
        # 测试文本翻译
        print("=== 测试文本翻译 ===")
        text_result = await translator_agent.run({
            "text": "Hello, world!",
            "source_lang": "en",
            "target_lang": "zh",
            "enable_emotion_analysis": True
        })
        print(f"翻译结果: {text_result}")
        
        # 测试视频翻译
        print("\n=== 测试视频翻译 ===")
        video_result = await supervisor.run({
            "task_type": "video_translation",
            "video_path": "./test_video.mp4",
            "source_lang": "en",
            "target_lang": "zh"
        })
        print(f"视频翻译结果: {video_result}")
    
    # 运行示例
    asyncio.run(main())
