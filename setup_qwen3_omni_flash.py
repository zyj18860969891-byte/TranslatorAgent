#!/usr/bin/env python3
"""
Qwen3-Omni-Flash 集成配置脚本
用于将 Qwen3-Omni-Flash 模型集成到 OpenManus TranslatorAgent 中
"""

import os
import sys
import toml
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Qwen3OmniFlashConfig:
    """Qwen3-Omni-Flash 配置管理器"""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self.backup_path = Path(f"{config_path}.backup")
        
    def backup_config(self) -> bool:
        """备份现有配置文件"""
        try:
            if self.config_path.exists():
                self.backup_path.write_text(self.config_path.read_text())
                print(f"✅ 配置文件已备份到: {self.backup_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ 备份配置文件失败: {e}")
            return False
    
    def add_qwen3_provider(self) -> bool:
        """添加 Qwen3-Omni-Flash Provider 到配置文件"""
        try:
            # 读取现有配置
            if self.config_path.exists():
                config = toml.load(self.config_path)
            else:
                config = {"llm": {"providers": []}}
            
            # 检查是否已存在
            existing_providers = config.get("llm", {}).get("providers", [])
            for provider in existing_providers:
                if provider.get("name") == "aliyun-dashscope":
                    print("⚠️  Qwen3-Omni-Flash Provider 已存在")
                    return True
            
            # 添加新的 Provider
            new_provider = {
                "name": "aliyun-dashscope",
                "base_url": "https://dashscope.aliyuncs.com/api/v1",
                "api_key": "${DASHSCOPE_API_KEY}",
                "model": "qwen3-omni-flash-realtime"
            }
            
            if "llm" not in config:
                config["llm"] = {}
            if "providers" not in config["llm"]:
                config["llm"]["providers"] = []
            
            config["llm"]["providers"].append(new_provider)
            
            # 写入配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(config, f)
            
            print("✅ Qwen3-Omni-Flash Provider 已添加到配置文件")
            return True
            
        except Exception as e:
            print(f"❌ 添加 Provider 失败: {e}")
            return False
    
    def check_api_key(self) -> bool:
        """检查 DASHSCOPE_API_KEY 环境变量"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key:
            print("✅ DASHSCOPE_API_KEY 环境变量已设置")
            return True
        else:
            print("❌ DASHSCOPE_API_KEY 环境变量未设置")
            print("请设置环境变量：")
            print("Windows: set DASHSCOPE_API_KEY=您的 sk-xxx 密钥")
            print("Linux/macOS: export DASHSCOPE_API_KEY='您的 sk-xxx 密钥'")
            return False
    
    def create_environment_setup_script(self) -> bool:
        """创建环境设置脚本"""
        try:
            script_content = """@echo off
echo 设置 DASHSCOPE_API_KEY 环境变量
setx DASHSCOPE_API_KEY "您的 sk-xxx 密钥"
echo 环境变量已设置，请重启终端使配置生效
pause
"""
            
            with open("setup_qwen3_env.bat", 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print("✅ 环境设置脚本已创建: setup_qwen3_env.bat")
            return True
            
        except Exception as e:
            print(f"❌ 创建环境设置脚本失败: {e}")
            return False
    
    def create_test_script(self) -> bool:
        """创建测试脚本"""
        try:
            test_script = '''#!/usr/bin/env python3
"""
Qwen3-Omni-Flash 测试脚本
"""

import os
import requests
import json
from pathlib import Path

def test_qwen3_connection():
    """测试 Qwen3-Omni-Flash 连接"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ DASHSCOPE_API_KEY 环境变量未设置")
        return False
    
    url = "https://dashscope.aliyuncs.com/api/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "qwen3-omni-flash-realtime",
        "messages": [
            {
                "role": "user",
                "content": "请简单介绍一下自己"
            }
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Qwen3-Omni-Flash 连接成功")
            print(f"响应: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            return True
        else:
            print(f"❌ 连接失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试连接时发生错误: {e}")
        return False

if __name__ == "__main__":
    print("测试 Qwen3-Omni-Flash 连接...")
    success = test_qwen3_connection()
    if success:
        print("🎉 测试成功！")
    else:
        print("💡 请检查配置和环境变量")
'''
            
            with open("test_qwen3_connection.py", 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            print("✅ 测试脚本已创建: test_qwen3_connection.py")
            return True
            
        except Exception as e:
            print(f"❌ 创建测试脚本失败: {e}")
            return False
    
    def create_integration_guide(self) -> bool:
        """创建集成指南"""
        try:
            guide_content = '''# Qwen3-Omni-Flash 集成指南

## 快速开始

### 1. 设置环境变量
运行 `setup_qwen3_env.bat` 脚本设置环境变量，或手动设置：
```bash
set DASHSCOPE_API_KEY=您的 sk-xxx 密钥
```

### 2. 测试连接
```bash
python test_qwen3_connection.py
```

### 3. 验证配置
检查 `config.toml` 文件是否包含 Qwen3-Omni-Flash Provider

## 字幕提取功能使用

### 1. 上传视频文件
- 在详情页点击"上传"按钮
- 选择要处理的视频文件
- 文件将保存到 `tasks/[task_id]/` 目录

### 2. 处理流程
1. 系统自动检测字幕变化帧
2. 使用 Qwen3-Omni-Flash 进行 OCR 识别
3. 生成 SRT 字幕文件
4. 显示处理进度

### 3. 结果查看
- 生成的 SRT 文件保存在 `tasks/[task_id]/output/`
- 可在详情页直接预览和下载

## 高级功能

### 情感分析
- 系统自动识别角色情绪
- 情感标签注入翻译提示词
- 生成更具情感共鸣的译文

### 多模态处理
- 支持文本、图像、音频、视频输入
- 统一处理流程，减少信息损耗

## 故障排除

### 常见问题
1. **API 连接失败**
   - 检查 DASHSCOPE_API_KEY 是否正确
   - 确认网络连接正常
   - 查看 API 配置

2. **字幕提取不准确**
   - 确保视频质量良好
   - 检查字幕格式
   - 尝试不同的处理参数

3. **性能问题**
   - 监控 API 调用限制
   - 优化视频处理参数
   - 清理临时文件

### 日志查看
- 查看 `logs/` 目录下的日志文件
- 检查错误信息和调试信息

## 技术支持

如需更多帮助，请参考：
- [Qwen3-Omni-Flash 官方文档](https://help.aliyun.com/zh/dashscope/)
- [OpenManus TranslatorAgent 文档](https://github.com/OpenManus/TranslatorAgent)
'''
            
            with open("Qwen3_Integration_Guide.md", 'w', encoding='utf-8') as f:
                f.write(guide_content)
            
            print("✅ 集成指南已创建: Qwen3_Integration_Guide.md")
            return True
            
        except Exception as e:
            print(f"❌ 创建集成指南失败: {e}")
            return False
    
    def setup_complete(self) -> bool:
        """完成完整的设置流程"""
        print("🚀 开始 Qwen3-Omni-Flash 集成设置...")
        
        # 1. 备份配置
        if not self.backup_config():
            return False
        
        # 2. 检查 API 密钥
        if not self.check_api_key():
            self.create_environment_setup_script()
            print("💡 请先设置 DASHSCOPE_API_KEY 环境变量")
            return False
        
        # 3. 添加 Provider
        if not self.add_qwen3_provider():
            return False
        
        # 4. 创建测试脚本
        if not self.create_test_script():
            return False
        
        # 5. 创建集成指南
        if not self.create_integration_guide():
            return False
        
        print("🎉 Qwen3-Omni-Flash 集成设置完成！")
        print("📋 下一步操作：")
        print("1. 运行 test_qwen3_connection.py 测试连接")
        print("2. 查看 Qwen3_Integration_Guide.md 了解使用方法")
        print("3. 重启 OpenManus TranslatorAgent")
        
        return True

def main():
    """主函数"""
    print("Qwen3-Omni-Flash 集成配置工具")
    print("=" * 40)
    
    config = Qwen3OmniFlashConfig()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # 仅测试连接
            config.check_api_key()
            config.create_test_script()
            os.system("python test_qwen3_connection.py")
        elif sys.argv[1] == "--help":
            print("使用方法：")
            print("python setup_qwen3_omni_flash.py     # 完整设置")
            print("python setup_qwen3_omni_flash.py --test  # 仅测试连接")
            print("python setup_qwen3_omni_flash.py --help  # 显示帮助")
        else:
            print("未知参数，使用 --help 查看帮助")
    else:
        # 完整设置
        success = config.setup_complete()
        if not success:
            print("❌ 设置失败，请检查错误信息")
            sys.exit(1)

if __name__ == "__main__":
    main()