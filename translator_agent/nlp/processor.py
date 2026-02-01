#!/usr/bin/env python3
"""
NLP 处理模块 - 文本预处理和后处理

基于 NotebookLM 文档驱动开发
文档: context-compression-SKILL.md, context-optimization-SKILL.md

功能:
- 文本清洗
- 分词和标记化
- 语言检测
- 文本规范化
- 后处理优化
"""

import re
import unicodedata
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Language(Enum):
    """支持的语言枚举"""
    ENGLISH = "en"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"
    ITALIAN = "it"
    RUSSIAN = "ru"
    PORTUGUESE = "pt"


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def clean_text(self, text: str, remove_extra_spaces: bool = True) -> str:
        """文本清洗"""
        # 移除控制字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # 移除多余的空白字符
        if remove_extra_spaces:
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        # 规范化 Unicode
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def detect_language(self, text: str) -> Language:
        """检测文本语言"""
        # 简单的语言检测（基于字符范围）
        if re.search(r'[\u4e00-\u9fff]', text):
            return Language.CHINESE
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return Language.JAPANESE
        elif re.search(r'[\uac00-\ud7af]', text):
            return Language.KOREAN
        elif re.search(r'[\u0400-\u04ff]', text):
            return Language.RUSSIAN
        elif re.search(r'[\u00C0-\u00FF]', text):
            # 欧洲语言
            if re.search(r'[äöüß]', text, re.IGNORECASE):
                return Language.GERMAN
            elif re.search(r'[àâçéèêëîïôùûüÿ]', text, re.IGNORECASE):
                return Language.FRENCH
            elif re.search(r'[áéíóúñ]', text, re.IGNORECASE):
                return Language.SPANISH
            elif re.search(r'[àèéìòù]', text, re.IGNORECASE):
                return Language.ITALIAN
            elif re.search(r'[áâãàçéêíóôõú]', text, re.IGNORECASE):
                return Language.PORTUGUESE
        else:
            # 默认为英语
            return Language.ENGLISH
    
    def tokenize(self, text: str, language: Optional[Language] = None) -> List[str]:
        """分词"""
        if language is None:
            language = self.detect_language(text)
        
        if language == Language.CHINESE:
            # 中文分词（简单版本）
            return self._tokenize_chinese(text)
        elif language == Language.JAPANESE:
            # 日文分词（简单版本）
            return self._tokenize_japanese(text)
        elif language == Language.KOREAN:
            # 韩文分词（简单版本）
            return self._tokenize_korean(text)
        else:
            # 西方语言分词
            return self._tokenize_western(text)
    
    def _tokenize_chinese(self, text: str) -> List[str]:
        """中文分词（简单版本）"""
        # 简单的基于标点的分词
        tokens = re.split(r'[，。！？；：、\s]+', text)
        return [t for t in tokens if t]
    
    def _tokenize_japanese(self, text: str) -> List[str]:
        """日文分词（简单版本）"""
        # 简单的基于标点的分词
        tokens = re.split(r'[。！？；：、\s]+', text)
        return [t for t in tokens if t]
    
    def _tokenize_korean(self, text: str) -> List[str]:
        """韩文分词（简单版本）"""
        # 简单的基于空格的分词
        tokens = re.split(r'\s+', text)
        return [t for t in tokens if t]
    
    def _tokenize_western(self, text: str) -> List[str]:
        """西方语言分词"""
        # 基于空格和标点的分词
        tokens = re.split(r'[.,!?;:\s]+', text)
        return [t for t in tokens if t]
    
    def normalize_text(self, text: str, language: Optional[Language] = None) -> str:
        """文本规范化"""
        if language is None:
            language = self.detect_language(text)
        
        # 基础清洗
        text = self.clean_text(text)
        
        # 语言特定的规范化
        if language == Language.CHINESE:
            text = self._normalize_chinese(text)
        elif language == Language.ENGLISH:
            text = self._normalize_english(text)
        
        return text
    
    def _normalize_chinese(self, text: str) -> str:
        """中文规范化"""
        # 全角转半角
        text = unicodedata.normalize('NFKC', text)
        
        # 规范化标点
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('‘', "'").replace('’', "'")
        text = text.replace('—', '-').replace('–', '-')
        
        return text
    
    def _normalize_english(self, text: str) -> str:
        """英文规范化"""
        # 规范化引号
        text = text.replace('“', '"').replace('”', '"')
        text = text.replace('‘', "'").replace('’', "'")
        
        # 规范化破折号
        text = text.replace('—', '-').replace('–', '-')
        
        return text
    
    def post_process(self, text: str, original_text: str, target_lang: Language) -> str:
        """后处理"""
        # 基础清洗
        text = self.clean_text(text)
        
        # 语言特定的后处理
        if target_lang == Language.CHINESE:
            text = self._post_process_chinese(text, original_text)
        elif target_lang == Language.ENGLISH:
            text = self._post_process_english(text, original_text)
        
        return text
    
    def _post_process_chinese(self, text: str, original_text: str) -> str:
        """中文后处理"""
        # 移除多余的标点
        text = re.sub(r'[，。！？；：、]+', lambda m: m.group(0)[0], text)
        
        # 规范化标点
        text = text.replace(',,', ',').replace('..', '.')
        text = text.replace('!!', '!').replace('??', '?')
        
        return text
    
    def _post_process_english(self, text: str, original_text: str) -> str:
        """英文后处理"""
        # 规范化空格
        text = re.sub(r'\s+', ' ', text)
        
        # 规范化标点
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # 首字母大写（如果是句子）
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text
    
    def compress_text(self, text: str, max_length: int = 1000) -> str:
        """文本压缩（基于上下文压缩技能）"""
        if len(text) <= max_length:
            return text
        
        # 简单的压缩策略：保留关键信息
        sentences = re.split(r'[。！？.!?]+', text)
        
        compressed = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if current_length + len(sentence) + 1 <= max_length:
                compressed.append(sentence)
                current_length += len(sentence) + 1
            else:
                break
        
        return ' '.join(compressed)
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（基于词频）
        tokens = self.tokenize(text)
        
        # 计算词频
        freq = {}
        for token in tokens:
            if len(token) > 1:  # 过滤单字符
                freq[token] = freq.get(token, 0) + 1
        
        # 按频率排序
        keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return [k for k, v in keywords[:top_k]]


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, max_context_length: int = 5000):
        self.max_context_length = max_context_length
        self.contexts: Dict[str, List[str]] = {}
        self.processor = TextProcessor()
    
    def add_context(self, key: str, text: str):
        """添加上下文"""
        if key not in self.contexts:
            self.contexts[key] = []
        
        # 压缩文本
        compressed = self.processor.compress_text(text, self.max_context_length // 10)
        self.contexts[key].append(compressed)
        
        # 保持上下文长度
        if len(self.contexts[key]) > 10:
            self.contexts[key] = self.contexts[key][-10:]
    
    def get_context(self, key: str) -> str:
        """获取上下文"""
        if key not in self.contexts:
            return ""
        
        return " ".join(self.contexts[key])
    
    def clear_context(self, key: str):
        """清空上下文"""
        if key in self.contexts:
            self.contexts[key].clear()
    
    def clear_all(self):
        """清空所有上下文"""
        self.contexts.clear()


# 使用示例
if __name__ == "__main__":
    processor = TextProcessor()
    
    # 测试文本清洗
    text = "Hello,   world!  这是一个  测试。"
    cleaned = processor.clean_text(text)
    print(f"清洗后: {cleaned}")
    
    # 测试语言检测
    lang = processor.detect_language(text)
    print(f"检测语言: {lang}")
    
    # 测试分词
    tokens = processor.tokenize(text)
    print(f"分词结果: {tokens}")
    
    # 测试关键词提取
    keywords = processor.extract_keywords(text, top_k=5)
    print(f"关键词: {keywords}")
    
    # 测试上下文管理
    context_manager = ContextManager()
    context_manager.add_context("test", "这是一个测试上下文。")
    context_manager.add_context("test", "这是另一个测试上下文。")
    print(f"上下文: {context_manager.get_context('test')}")
