"""
Qwen3模型集成模块
提供基于Qwen3模型的智能视频翻译系统
"""

__version__ = "1.0.0"
__author__ = "OpenManus Team"
__email__ = "team@openmanus.com"

from .subtitle_extractor import SubtitleExtractor
from .video_translator import VideoTranslator
from .emotion_analyzer import EmotionAnalyzer
from .batch_processor import BatchProcessor
from .subtitle_pressing import SubtitlePressing, SubtitlePressingManager
from .subtitle_erasure import SubtitleErasure, SubtitleErasureManager
from .config import load_config, check_model_availability

__all__ = [
    "SubtitleExtractor",
    "VideoTranslator", 
    "EmotionAnalyzer",
    "BatchProcessor",
    "SubtitlePressing",
    "SubtitlePressingManager",
    "SubtitleErasure",
    "SubtitleErasureManager",
    "load_config",
    "check_model_availability"
]

# 模块初始化
def initialize():
    """初始化Qwen3集成模块"""
    import logging
    import os
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Qwen3集成模块初始化中...")
    
    # 检查环境
    env_check = check_environment()
    if not env_check["success"]:
        logger.warning(f"环境检查失败: {env_check['error']}")
    
    # 检查配置
    config_check = check_configuration()
    if not config_check["success"]:
        logger.warning(f"配置检查失败: {config_check['error']}")
    
    # 检查模型可用性
    model_check = check_model_availability()
    logger.info(f"模型可用性: {len(model_check['available'])} 个可用, {len(model_check['unavailable'])} 个不可用")
    
    logger.info("Qwen3集成模块初始化完成")
    return True

def check_environment():
    """检查运行环境"""
    try:
        import sys
        import platform
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            return {
                "success": False,
                "error": f"Python版本过低: {sys.version_info.major}.{sys.version_info.minor}, 需要3.8+"
            }
        
        # 检查操作系统
        os_info = platform.system()
        if os_info not in ["Windows", "Linux", "Darwin"]:
            return {
                "success": False,
                "error": f"不支持的操作系统: {os_info}"
            }
        
        # 检查必需的包
        required_packages = [
            "dashscope",
            "opencv-python",
            "numpy",
            "requests",
            "PIL"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return {
                "success": False,
                "error": f"缺少必需的包: {', '.join(missing_packages)}"
            }
        
        return {"success": True}
        
    except Exception as e:
        return {
            "success": False,
            "error": f"环境检查失败: {str(e)}"
        }

def check_configuration():
    """检查配置文件"""
    try:
        from pathlib import Path
        
        # 检查配置文件
        config_files = [
            "model_config.json",
            "feature_config.json"
        ]
        
        missing_files = []
        for config_file in config_files:
            if not Path(config_file).exists():
                missing_files.append(config_file)
        
        if missing_files:
            return {
                "success": False,
                "error": f"缺少配置文件: {', '.join(missing_files)}"
            }
        
        # 尝试加载配置
        config = load_config()
        if not config:
            return {
                "success": False,
                "error": "配置文件格式错误"
            }
        
        return {"success": True}
        
    except Exception as e:
        return {
            "success": False,
            "error": f"配置检查失败: {str(e)}"
        }

def run_system_tests():
    """运行系统测试"""
    try:
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("开始运行系统测试...")
        
        test_results = []
        
        # 测试1: 环境检查
        env_test = check_environment()
        test_results.append(("环境检查", env_test["success"], env_test.get("error", "")))
        
        # 测试2: 配置检查
        config_test = check_configuration()
        test_results.append(("配置检查", config_test["success"], config_test.get("error", "")))
        
        # 测试3: 模型可用性检查
        model_test = check_model_availability()
        test_results.append(("模型可用性", len(model_test["available"]) > 0, 
                           f"可用: {len(model_test['available'])}, 不可用: {len(model_test['unavailable'])}"))
        
        # 测试4: 基础功能测试
        try:
            from .subtitle_extractor import SubtitleExtractor
            extractor = SubtitleExtractor()
            test_results.append(("字幕提取器初始化", True, ""))
        except Exception as e:
            test_results.append(("字幕提取器初始化", False, str(e)))
        
        # 打印测试结果
        logger.info("系统测试结果:")
        for test_name, success, message in test_results:
            status = "✅ 通过" if success else "❌ 失败"
            logger.info(f"  {test_name}: {status} - {message}")
        
        # 计算总体结果
        passed_tests = sum(1 for _, success, _ in test_results if success)
        total_tests = len(test_results)
        
        logger.info(f"总体结果: {passed_tests}/{total_tests} 测试通过")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"系统测试失败: {e}")
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "test_results": [],
            "error": str(e)
        }

# 自动初始化
initialize()