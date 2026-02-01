#!/usr/bin/env python3
"""
Qwen3模型配置验证脚本
用于验证模型配置、API Key和系统环境
"""

import os
import json
import sys
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qwen3_config_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Qwen3ConfigValidator:
    """Qwen3配置验证器"""
    
    def __init__(self, config_path: str = "model_config.json"):
        self.config_path = config_path
        self.config = {}
        self.validation_results = {
            "environment": {},
            "config_files": {},
            "api_connectivity": {},
            "model_availability": {},
            "system_requirements": {}
        }
        
    def validate_environment(self) -> Dict[str, Any]:
        """验证环境配置"""
        logger.info("开始验证环境配置...")
        
        results = {
            "python_version": False,
            "required_packages": {},
            "environment_variables": {},
            "disk_space": False,
            "memory": False
        }
        
        # 检查Python版本
        try:
            import sys
            python_version = sys.version_info
            if python_version >= (3, 8):
                results["python_version"] = True
                logger.info(f"Python版本检查通过: {python_version.major}.{python_version.minor}.{python_version.micro}")
            else:
                logger.error(f"Python版本过低: {python_version.major}.{python_version.minor}.{python_version.micro}，需要3.8+")
        except Exception as e:
            logger.error(f"Python版本检查失败: {e}")
        
        # 检查必需的包
        required_packages = [
            "dashscope",
            "opencv-python",
            "numpy",
            "requests",
            "PIL"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                results["required_packages"][package] = True
                logger.info(f"包 {package} 检查通过")
            except ImportError:
                results["required_packages"][package] = False
                logger.error(f"包 {package} 未安装")
        
        # 检查环境变量
        env_vars = [
            "DASHSCOPE_API_KEY",
            "DASHSCOPE_BASE_URL",
            "DASHSCOPE_TIMEOUT",
            "DASHSCOPE_MAX_RETRIES",
            "DASHSCOPE_RETRY_DELAY"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                results["environment_variables"][var] = True
                logger.info(f"环境变量 {var} 已配置")
            else:
                results["environment_variables"][var] = False
                logger.warning(f"环境变量 {var} 未配置")
        
        # 检查磁盘空间
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            if free > 1024 * 1024 * 1024:  # 至少1GB可用空间
                results["disk_space"] = True
                logger.info(f"磁盘空间检查通过: {free / (1024*1024*1024):.2f}GB可用")
            else:
                logger.warning(f"磁盘空间不足: {free / (1024*1024*1024):.2f}GB可用")
        except Exception as e:
            logger.error(f"磁盘空间检查失败: {e}")
        
        # 检查内存
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.available > 512 * 1024 * 1024:  # 至少512MB可用内存
                results["memory"] = True
                logger.info(f"内存检查通过: {memory.available / (1024*1024*1024):.2f}GB可用")
            else:
                logger.warning(f"内存不足: {memory.available / (1024*1024*1024):.2f}GB可用")
        except Exception as e:
            logger.error(f"内存检查失败: {e}")
        
        self.validation_results["environment"] = results
        return results
    
    def validate_config_files(self) -> Dict[str, Any]:
        """验证配置文件"""
        logger.info("开始验证配置文件...")
        
        results = {
            "model_config": False,
            "feature_config": False,
            "config_syntax": {},
            "config_values": {}
        }
        
        # 检查模型配置文件
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                
                results["model_config"] = True
                logger.info(f"模型配置文件 {self.config_path} 加载成功")
                
                # 验证配置语法
                config_syntax = self._validate_config_syntax()
                results["config_syntax"] = config_syntax
                
                # 验证配置值
                config_values = self._validate_config_values()
                results["config_values"] = config_values
            else:
                logger.error(f"模型配置文件 {self.config_path} 不存在")
        except Exception as e:
            logger.error(f"模型配置文件验证失败: {e}")
        
        # 检查功能配置文件
        feature_config_path = "feature_config.json"
        try:
            if os.path.exists(feature_config_path):
                with open(feature_config_path, 'r', encoding='utf-8') as f:
                    feature_config = json.load(f)
                
                results["feature_config"] = True
                logger.info(f"功能配置文件 {feature_config_path} 加载成功")
            else:
                logger.warning(f"功能配置文件 {feature_config_path} 不存在")
        except Exception as e:
            logger.error(f"功能配置文件验证失败: {e}")
        
        self.validation_results["config_files"] = results
        return results
    
    def _validate_config_syntax(self) -> Dict[str, Any]:
        """验证配置语法"""
        results = {
            "models_section": False,
            "required_fields": {},
            "json_syntax": True
        }
        
        try:
            # 检查models部分
            if "models" in self.config:
                results["models_section"] = True
                logger.info("models配置部分存在")
                
                # 检查必需字段
                required_fields = ["name", "type", "base_url", "api_key", "enabled"]
                for model_name, model_config in self.config["models"].items():
                    model_results = {}
                    for field in required_fields:
                        if field in model_config:
                            model_results[field] = True
                        else:
                            model_results[field] = False
                            logger.warning(f"模型 {model_name} 缺少字段: {field}")
                    
                    results["required_fields"][model_name] = model_results
            else:
                logger.error("配置文件中缺少models部分")
        except Exception as e:
            logger.error(f"配置语法验证失败: {e}")
            results["json_syntax"] = False
        
        return results
    
    def _validate_config_values(self) -> Dict[str, Any]:
        """验证配置值"""
        results = {
            "api_key_format": {},
            "url_format": {},
            "numeric_values": {}
        }
        
        try:
            for model_name, model_config in self.config["models"].items():
                # 检查API Key格式
                api_key = model_config.get("api_key", "")
                if api_key and api_key.startswith("${") and api_key.endswith("}"):
                    results["api_key_format"][model_name] = True
                    logger.info(f"模型 {model_name} API Key使用环境变量")
                elif api_key:
                    results["api_key_format"][model_name] = True
                    logger.info(f"模型 {model_name} API Key已配置")
                else:
                    results["api_key_format"][model_name] = False
                    logger.warning(f"模型 {model_name} API Key未配置")
                
                # 检查URL格式
                base_url = model_config.get("base_url", "")
                if base_url and base_url.startswith("http"):
                    results["url_format"][model_name] = True
                    logger.info(f"模型 {model_name} URL格式正确")
                else:
                    results["url_format"][model_name] = False
                    logger.warning(f"模型 {model_name} URL格式错误")
                
                # 检查数值配置
                numeric_fields = ["max_tokens", "temperature", "timeout"]
                model_numeric_results = {}
                for field in numeric_fields:
                    value = model_config.get(field)
                    if isinstance(value, (int, float)) and value > 0:
                        model_numeric_results[field] = True
                    else:
                        model_numeric_results[field] = False
                        logger.warning(f"模型 {model_name} {field} 值无效")
                
                results["numeric_values"][model_name] = model_numeric_results
        except Exception as e:
            logger.error(f"配置值验证失败: {e}")
        
        return results
    
    def validate_api_connectivity(self) -> Dict[str, Any]:
        """验证API连接性"""
        logger.info("开始验证API连接性...")
        
        results = {
            "base_url_accessible": False,
            "authentication": {},
            "rate_limits": {}
        }
        
        try:
            import requests
            
            # 检查基础URL可访问性
            base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com")
            try:
                response = requests.get(f"{base_url}/api/v1/models", timeout=10)
                if response.status_code == 200:
                    results["base_url_accessible"] = True
                    logger.info(f"基础URL {base_url} 可访问")
                else:
                    logger.warning(f"基础URL {base_url} 返回状态码: {response.status_code}")
            except Exception as e:
                logger.error(f"基础URL访问失败: {e}")
            
            # 检查认证
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if api_key:
                try:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(
                        f"{base_url}/api/v1/services/aigc/text-generation/generation",
                        json={"model": "qwen-turbo", "input": {"text": "test"}},
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        results["authentication"]["success"] = True
                        logger.info("API认证成功")
                    elif response.status_code == 401:
                        results["authentication"]["success"] = False
                        results["authentication"]["error"] = "认证失败，API Key无效"
                        logger.error("API认证失败，API Key无效")
                    else:
                        results["authentication"]["success"] = False
                        results["authentication"]["error"] = f"认证请求失败: {response.status_code}"
                        logger.error(f"API认证请求失败: {response.status_code}")
                except Exception as e:
                    results["authentication"]["success"] = False
                    results["authentication"]["error"] = str(e)
                    logger.error(f"API认证检查失败: {e}")
            else:
                results["authentication"]["success"] = False
                results["authentication"]["error"] = "未配置API Key"
                logger.error("未配置API Key")
            
            # 检查速率限制
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                # 发送多个请求检查速率限制
                for i in range(3):
                    response = requests.post(
                        f"{base_url}/api/v1/services/aigc/text-generation/generation",
                        json={"model": "qwen-turbo", "input": {"text": f"test_{i}"}},
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 429:
                        results["rate_limits"]["limited"] = True
                        results["rate_limits"]["error"] = "达到速率限制"
                        logger.warning("达到API速率限制")
                        break
                    elif response.status_code != 200:
                        logger.warning(f"请求 {i+1} 失败: {response.status_code}")
                
                if "limited" not in results["rate_limits"]:
                    results["rate_limits"]["limited"] = False
                    logger.info("速率限制检查通过")
            except Exception as e:
                results["rate_limits"]["limited"] = False
                results["rate_limits"]["error"] = str(e)
                logger.error(f"速率限制检查失败: {e}")
        
        except ImportError:
            logger.error("未安装requests包，无法进行API连接性检查")
        except Exception as e:
            logger.error(f"API连接性检查失败: {e}")
        
        self.validation_results["api_connectivity"] = results
        return results
    
    def validate_model_availability(self) -> Dict[str, Any]:
        """验证模型可用性"""
        logger.info("开始验证模型可用性...")
        
        results = {
            "available_models": [],
            "unavailable_models": [],
            "model_details": {}
        }
        
        try:
            import requests
            
            base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com")
            api_key = os.getenv("DASHSCOPE_API_KEY")
            
            if not api_key:
                logger.error("未配置API Key，无法检查模型可用性")
                return results
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 获取可用模型列表
            try:
                response = requests.get(f"{base_url}/api/v1/models", headers=headers, timeout=10)
                if response.status_code == 200:
                    models_data = response.json()
                    
                    # 检查我们关心的模型
                    target_models = [
                        "qwen3-omni-flash-realtime",
                        "qwen3-vl-rerank",
                        "qwen3-embedding"
                    ]
                    
                    for model_id in target_models:
                        model_found = False
                        for model in models_data.get("models", []):
                            if model_id in model.get("model", ""):
                                model_found = True
                                results["available_models"].append(model_id)
                                results["model_details"][model_id] = {
                                    "name": model.get("name", ""),
                                    "model": model.get("model", ""),
                                    "type": model.get("type", ""),
                                    "description": model.get("description", "")
                                }
                                logger.info(f"模型 {model_id} 可用: {model.get('name', '')}")
                                break
                        
                        if not model_found:
                            results["unavailable_models"].append(model_id)
                            logger.warning(f"模型 {model_id} 不可用")
                
                else:
                    logger.error(f"获取模型列表失败: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
            
            except Exception as e:
                logger.error(f"模型可用性检查失败: {e}")
        
        except ImportError:
            logger.error("未安装requests包，无法进行模型可用性检查")
        except Exception as e:
            logger.error(f"模型可用性检查失败: {e}")
        
        self.validation_results["model_availability"] = results
        return results
    
    def validate_system_requirements(self) -> Dict[str, Any]:
        """验证系统要求"""
        logger.info("开始验证系统要求...")
        
        results = {
            "python_packages": {},
            "system_resources": {},
            "file_permissions": {}
        }
        
        try:
            # 检查Python包
            required_packages = {
                "dashscope": "DashScope SDK",
                "opencv-python": "OpenCV图像处理",
                "numpy": "NumPy数值计算",
                "requests": "HTTP请求库",
                "PIL": "图像处理库",
                "moviepy": "视频处理库",
                "transformers": "HuggingFace Transformers",
                "torch": "PyTorch深度学习框架"
            }
            
            for package, description in required_packages.items():
                try:
                    __import__(package.replace("-", "_"))
                    results["python_packages"][package] = True
                    logger.info(f"包 {package} ({description}) 可用")
                except ImportError:
                    results["python_packages"][package] = False
                    logger.warning(f"包 {package} ({description}) 未安装")
            
            # 检查系统资源
            try:
                import psutil
                
                # CPU
                cpu_count = psutil.cpu_count()
                results["system_resources"]["cpu_count"] = cpu_count
                logger.info(f"CPU核心数: {cpu_count}")
                
                # 内存
                memory = psutil.virtual_memory()
                results["system_resources"]["memory_total"] = memory.total
                results["system_resources"]["memory_available"] = memory.available
                logger.info(f"内存总量: {memory.total / (1024*1024*1024):.2f}GB")
                logger.info(f"可用内存: {memory.available / (1024*1024*1024):.2f}GB")
                
                # 磁盘
                disk = psutil.disk_usage('.')
                results["system_resources"]["disk_total"] = disk.total
                results["system_resources"]["disk_free"] = disk.free
                logger.info(f"磁盘总量: {disk.total / (1024*1024*1024):.2f}GB")
                logger.info(f"可用磁盘: {disk.free / (1024*1024*1024):.2f}GB")
                
            except Exception as e:
                logger.error(f"系统资源检查失败: {e}")
            
            # 检查文件权限
            try:
                # 测试文件写入权限
                test_file = "test_permission.tmp"
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                results["file_permissions"]["write"] = True
                logger.info("文件写入权限检查通过")
                
                # 测试目录创建权限
                test_dir = "test_permission_dir"
                os.makedirs(test_dir, exist_ok=True)
                os.rmdir(test_dir)
                results["file_permissions"]["directory"] = True
                logger.info("目录创建权限检查通过")
                
            except Exception as e:
                logger.error(f"文件权限检查失败: {e}")
                results["file_permissions"]["write"] = False
                results["file_permissions"]["directory"] = False
        
        except Exception as e:
            logger.error(f"系统要求验证失败: {e}")
        
        self.validation_results["system_requirements"] = results
        return results
    
    def generate_report(self) -> str:
        """生成验证报告"""
        logger.info("生成验证报告...")
        
        report = []
        report.append("=" * 60)
        report.append("Qwen3模型配置验证报告")
        report.append("=" * 60)
        report.append(f"验证时间: {os.popen('date /t').read().strip()}")
        report.append(f"验证路径: {os.getcwd()}")
        report.append("")
        
        # 环境验证结果
        report.append("1. 环境验证")
        report.append("-" * 40)
        env_results = self.validation_results["environment"]
        
        if env_results["python_version"]:
            report.append("✅ Python版本: 符合要求 (3.8+)")
        else:
            report.append("❌ Python版本: 不符合要求")
        
        installed_packages = sum(1 for v in env_results["required_packages"].values() if v)
        total_packages = len(env_results["required_packages"])
        report.append(f"📦 必需包: {installed_packages}/{total_packages} 已安装")
        
        configured_env_vars = sum(1 for v in env_results["environment_variables"].values() if v)
        total_env_vars = len(env_results["environment_variables"])
        report.append(f"🔧 环境变量: {configured_env_vars}/{total_env_vars} 已配置")
        
        if env_results["disk_space"]:
            report.append("💾 磁盘空间: 充足")
        else:
            report.append("⚠️ 磁盘空间: 不足")
        
        if env_results["memory"]:
            report.append("🧠 内存: 充足")
        else:
            report.append("⚠️ 内存: 不足")
        
        report.append("")
        
        # 配置文件验证结果
        report.append("2. 配置文件验证")
        report.append("-" * 40)
        config_results = self.validation_results["config_files"]
        
        if config_results["model_config"]:
            report.append("✅ 模型配置文件: 存在且格式正确")
        else:
            report.append("❌ 模型配置文件: 不存在或格式错误")
        
        if config_results["feature_config"]:
            report.append("✅ 功能配置文件: 存在且格式正确")
        else:
            report.append("⚠️ 功能配置文件: 不存在或格式错误")
        
        report.append("")
        
        # API连接性验证结果
        report.append("3. API连接性验证")
        report.append("-" * 40)
        api_results = self.validation_results["api_connectivity"]
        
        if api_results["base_url_accessible"]:
            report.append("✅ 基础URL: 可访问")
        else:
            report.append("❌ 基础URL: 不可访问")
        
        if api_results["authentication"].get("success"):
            report.append("✅ API认证: 成功")
        else:
            report.append(f"❌ API认证: 失败 - {api_results['authentication'].get('error', '未知错误')}")
        
        if api_results["rate_limits"].get("limited"):
            report.append("⚠️ 速率限制: 已达到限制")
        else:
            report.append("✅ 速率限制: 正常")
        
        report.append("")
        
        # 模型可用性验证结果
        report.append("4. 模型可用性验证")
        report.append("-" * 40)
        model_results = self.validation_results["model_availability"]
        
        available_count = len(model_results["available_models"])
        unavailable_count = len(model_results["unavailable_models"])
        report.append(f"📊 可用模型: {available_count}")
        report.append(f"📊 不可用模型: {unavailable_count}")
        
        for model in model_results["available_models"]:
            details = model_results["model_details"].get(model, {})
            report.append(f"✅ {model}: {details.get('name', '未知')}")
        
        for model in model_results["unavailable_models"]:
            report.append(f"❌ {model}: 不可用")
        
        report.append("")
        
        # 系统要求验证结果
        report.append("5. 系统要求验证")
        report.append("-" * 40)
        sys_results = self.validation_results["system_requirements"]
        
        installed_packages = sum(1 for v in sys_results["python_packages"].values() if v)
        total_packages = len(sys_results["python_packages"])
        report.append(f"📦 Python包: {installed_packages}/{total_packages} 已安装")
        
        if sys_results["file_permissions"].get("write") and sys_results["file_permissions"].get("directory"):
            report.append("✅ 文件权限: 正常")
        else:
            report.append("❌ 文件权限: 异常")
        
        report.append("")
        
        # 总结
        report.append("6. 总结")
        report.append("-" * 40)
        
        # 计算总体状态
        total_checks = 0
        passed_checks = 0
        
        for category in self.validation_results.values():
            if isinstance(category, dict):
                for key, value in category.items():
                    if isinstance(value, bool):
                        total_checks += 1
                        if value:
                            passed_checks += 1
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, bool):
                                total_checks += 1
                                if sub_value:
                                    passed_checks += 1
        
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        report.append(f"总体成功率: {success_rate:.1f}% ({passed_checks}/{total_checks})")
        
        if success_rate >= 80:
            report.append("🎉 系统状态: 良好，可以开始使用")
        elif success_rate >= 60:
            report.append("⚠️ 系统状态: 一般，建议修复问题后使用")
        else:
            report.append("❌ 系统状态: 较差，需要修复问题后使用")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_validation(self) -> Dict[str, Any]:
        """运行完整验证"""
        logger.info("开始运行Qwen3配置验证...")
        
        # 执行各项验证
        self.validate_environment()
        self.validate_config_files()
        self.validate_api_connectivity()
        self.validate_model_availability()
        self.validate_system_requirements()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告
        with open("qwen3_validation_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info("验证完成，报告已保存到 qwen3_validation_report.txt")
        
        # 打印报告
        print(report)
        
        return self.validation_results

def main():
    """主函数"""
    print("Qwen3模型配置验证工具")
    print("=" * 50)
    
    # 创建验证器
    validator = Qwen3ConfigValidator()
    
    # 运行验证
    try:
        results = validator.run_validation()
        
        # 返回适当的退出码
        if results["environment"]["python_version"] and results["api_connectivity"]["authentication"]["success"]:
            print("\n✅ 验证通过，系统可以正常使用")
            sys.exit(0)
        else:
            print("\n❌ 验证失败，请检查配置")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"验证过程中发生错误: {e}")
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()