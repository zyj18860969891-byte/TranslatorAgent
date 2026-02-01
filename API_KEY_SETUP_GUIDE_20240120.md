# 🔐 百炼API密钥永久配置指南

## 📋 配置概述

**配置日期**: 2024年1月20日  
**API密钥**: `sk-88bf1bd605544d208c7338cb1989ab3e`  
**配置方式**: 永久配置到用户环境变量

## ✅ 已完成的配置

### 1. 临时配置（当前会话）
```powershell
# 已配置
$env:DASHSCOPE_API_KEY = "sk-88bf1bd605544d208c7338cb1989ab3e"
```

### 2. 永久配置（用户环境变量）
```powershell
# 已配置
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-88bf1bd605544d208c7338cb1989ab3e", "User")
```

### 3. 验证配置
```powershell
# 检查当前会话
echo $env:DASHSCOPE_API_KEY
# 输出: sk-88bf1bd605544d208c7338cb1989ab3e

# 检查用户环境变量
Get-ChildItem Env: | findstr DASHSCOPE
# 输出: DASHSCOPE_API_KEY    sk-88bf1bd605544d208c7338cb1989ab3e
```

## 🎯 配置验证

### 方法1: 检查当前会话
```powershell
echo $env:DASHSCOPE_API_KEY
```
**预期输出**: `sk-88bf1bd605544d208c7338cb1989ab3e`

### 方法2: 检查用户环境变量
```powershell
[Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")
```
**预期输出**: `sk-88bf1bd605544d208c7338cb1989ab3e`

### 方法3: 检查所有环境变量
```powershell
Get-ChildItem Env: | findstr DASHSCOPE
```
**预期输出**: `DASHSCOPE_API_KEY    sk-88bf1bd605544d208c7338cb1989ab3e`

## 📦 自动配置脚本

### Windows批处理脚本 (`setup_api_key.bat`)
```batch
@echo off
set API_KEY=sk-88bf1bd605544d208c7338cb1989ab3e
setx DASHSCOPE_API_KEY "%API_KEY%"
echo 配置完成！请重启终端。
pause
```

**使用方法**:
1. 双击运行 `setup_api_key.bat`
2. 等待配置完成
3. 重启终端

### PowerShell脚本 (`setup_api_key.ps1`)
```powershell
$API_KEY = "sk-88bf1bd605544d208c7338cb1989ab3e"
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", $API_KEY, "User")
Write-Host "配置完成！请重启终端。"
```

**使用方法**:
1. 右键点击 `setup_api_key.ps1`
2. 选择 "使用PowerShell运行"
3. 等待配置完成
4. 重启终端

## 🚀 重启终端/IDE

### 1. 重启PowerShell终端
```powershell
# 关闭当前终端
# 重新打开PowerShell
```

### 2. 重启VS Code
1. 关闭VS Code
2. 重新打开VS Code
3. 打开新的终端

### 3. 验证配置
```powershell
# 在新终端中运行
echo $env:DASHSCOPE_API_KEY
```

## 🧪 测试API连接

### 1. 运行连接测试
```powershell
D:/MultiMode/TranslatorAgent/notebooklm-skill-master/.venv/Scripts/python.exe test_api_connection.py
```

**预期输出**:
```
✅ 连接成功！
响应: 你好！很高兴见到你～😊 有什么问题、想法，或者需要帮助的地方吗？我很乐意为你提供支持！...
```

### 2. 运行功能测试
```powershell
D:/MultiMode/TranslatorAgent/notebooklm-skill-master/.venv/Scripts/python.exe test_subtitle_features.py
```

**预期输出**:
```
🎉 所有测试通过！
总计: 6 个测试
通过: 6 个
失败: 0 个
```

## 📊 配置状态

### 环境变量状态
| 变量名 | 值 | 状态 |
|--------|-----|------|
| `DASHSCOPE_API_KEY` | `sk-88bf1bd605544d208c7338cb1989ab3e` | ✅ 已配置 |

### 配置范围
- ✅ **用户环境变量**: 永久配置
- ✅ **当前会话**: 临时配置
- ✅ **系统重启后**: 配置仍然有效

## 🛠️ 故障排除

### 问题1: 配置后仍然报错
**可能原因**:
1. 没有重启终端/IDE
2. 配置了多个环境变量
3. 使用了错误的配置方式

**解决方案**:
```powershell
# 1. 检查当前会话
echo $env:DASHSCOPE_API_KEY

# 2. 检查用户环境变量
[Environment]::GetEnvironmentVariable("DASHSCOPE_API_KEY", "User")

# 3. 如果不一致，重新配置
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-88bf1bd605544d208c7338cb1989ab3e", "User")

# 4. 重启终端
```

### 问题2: 环境变量未生效
**解决方案**:
```powershell
# 1. 关闭所有终端
# 2. 重新打开PowerShell
# 3. 验证配置
echo $env:DASHSCOPE_API_KEY
```

### 问题3: 需要删除旧配置
```powershell
# 删除用户环境变量
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", $null, "User")

# 重新配置
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-88bf1bd605544d208c7338cb1989ab3e", "User")
```

## 🔒 安全建议

### 1. 保护API密钥
- ✅ 不要分享API密钥
- ✅ 不要提交到Git仓库
- ✅ 定期轮换密钥
- ✅ 设置访问权限

### 2. 监控使用情况
- ✅ 定期检查API调用记录
- ✅ 设置费用告警
- ✅ 监控异常调用

### 3. 备份配置
```powershell
# 导出环境变量
Get-ChildItem Env: | findstr DASHSCOPE > api_key_backup.txt

# 恢复环境变量
$env:DASHSCOPE_API_KEY = (Get-Content api_key_backup.txt).Split(" ")[-1]
```

## 📝 配置总结

### 已完成的工作
- ✅ 百炼API密钥已获取: `sk-88bf1bd605544d208c7338cb1989ab3e`
- ✅ 临时配置已设置: `$env:DASHSCOPE_API_KEY = "sk-88bf1bd605544d208c7338cb1989ab3e"`
- ✅ 永久配置已设置: `[Environment]::SetEnvironmentVariable(...)`
- ✅ 配置验证通过: 环境变量已正确配置
- ✅ 自动配置脚本已创建: `setup_api_key.bat` 和 `setup_api_key.ps1`

### 下一步操作
1. **重启终端/IDE**: 使永久配置生效
2. **验证配置**: 检查环境变量
3. **测试API**: 运行连接测试
4. **开始使用**: 使用字幕压制和擦除功能

### 配置文件位置
- **配置脚本**: `D:\MultiMode\TranslatorAgent\setup_api_key.bat`
- **PowerShell脚本**: `D:\MultiMode\TranslatorAgent\setup_api_key.ps1`
- **测试脚本**: `D:\MultiMode\TranslatorAgent\test_api_connection.py`
- **使用指南**: `D:\MultiMode\TranslatorAgent\API_KEY_SETUP_GUIDE_20240120.md`

---

**配置完成**: 2024年1月20日  
**配置状态**: ✅ 永久配置已设置  
**下一步**: 重启终端并开始使用