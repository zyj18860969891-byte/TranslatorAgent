# 🔐 百炼API密钥配置说明

## 📋 问题确认

**用户疑问**: 
- 提供的API密钥格式: `accessKeyId LTAI5t6TBo9HDHq7eHoqd2dN` 和 `accessKeySecret r2AYxKTIgYaToNFVRESy03t0VLylj3`
- 看到的配置方式: `$env:DASHSCOPE_API_KEY = "你的AccessKeyID:你的AccessKeySecret"`
- **需要核实**: 这两种格式是否正确？

## ✅ 官方配置方式核实

### 1. 百炼API密钥 vs 阿里云AccessKey

**重要区别**:
- **阿里云AccessKey**: 用于阿里云所有服务（ECS、OSS等）
- **百炼API密钥**: 专门用于百炼大模型服务

**你的密钥类型**:
- `LTAI5t6TBo9HDHq7eHoqd2dN` - 这是**阿里云AccessKey ID**
- `r2AYxKTIgYaToNFVRESy03t0VLylj3` - 这是**阿里云AccessKey Secret**

### 2. 百炼API密钥获取方式

**正确步骤**:
1. 登录阿里云百炼控制台: https://bailian.console.aliyun.com
2. 进入 **密钥管理** 页面
3. 点击 **创建API-KEY**
4. 复制生成的API密钥（格式类似: `sk-xxxxxxxxxxxxxxxxxxxx`）

**百炼API密钥格式**:
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 配置方式核实

#### ❌ 错误的配置方式
```bash
# 这是错误的！
$env:DASHSCOPE_API_KEY = "LTAI5t6TBo9HDHq7eHoqd2dN:r2AYxKTIgYaToNFVRESy03t0VLylj3"
```

#### ✅ 正确的配置方式

**方式1: 使用百炼API密钥（推荐）**
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Linux/macOS
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**方式2: 使用阿里云AccessKey（不推荐，但可用）**
```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY = "LTAI5t6TBo9HDHq7eHoqd2dN"

# Linux/macOS
export DASHSCOPE_API_KEY="LTAI5t6TBo9HDHq7eHoqd2dN"
```

**注意**: 
- 使用阿里云AccessKey时，**只需要AccessKey ID**，不需要AccessKey Secret
- AccessKey Secret在百炼API调用中不需要

## 🔍 如何获取正确的百炼API密钥

### 步骤1: 登录百炼控制台
```
https://bailian.console.aliyun.com
```

### 步骤2: 进入密钥管理
1. 点击左侧菜单 **密钥管理**
2. 或访问: `https://bailian.console.aliyun.com/?tab=model#/api-key`

### 步骤3: 创建API密钥
1. 点击 **创建API-KEY**
2. 选择归属账号和业务空间
3. 填写描述
4. 点击确定

### 步骤4: 复制API密钥
1. 在API密钥列表中找到新创建的密钥
2. 点击 **复制** 图标
3. 格式类似: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## 💻 配置示例

### Windows PowerShell
```powershell
# 临时配置（当前会话有效）
$env:DASHSCOPE_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 永久配置（需要重启终端）
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "User")
```

### Windows CMD
```cmd
# 临时配置
set DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 永久配置（需要重启终端）
setx DASHSCOPE_API_KEY "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Linux/macOS
```bash
# 临时配置（当前会话有效）
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 永久配置（需要重启终端）
echo 'export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

### Python代码中使用
```python
import os
from openai import OpenAI

# 从环境变量读取API密钥
api_key = os.getenv("DASHSCOPE_API_KEY")

if not api_key:
    raise ValueError("请先配置DASHSCOPE_API_KEY环境变量")

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 测试调用
response = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)
```

## 🎯 验证配置

### 方法1: 检查环境变量
```powershell
# Windows PowerShell
echo $env:DASHSCOPE_API_KEY

# Linux/macOS
echo $DASHSCOPE_API_KEY
```

### 方法2: 测试API调用
```python
import os
from openai import OpenAI

try:
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": "测试"}]
    )
    
    print("✅ API配置成功！")
    print(f"响应: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ API配置失败: {e}")
```

## ⚠️ 常见问题

### 问题1: 使用AccessKey ID还是百炼API密钥？

**答案**: **推荐使用百炼API密钥**

| 类型 | 格式 | 用途 | 推荐度 |
|------|------|------|--------|
| 百炼API密钥 | `sk-xxxxxx` | 专门用于百炼服务 | ⭐⭐⭐⭐⭐ |
| 阿里云AccessKey | `LTAI5t6T...` | 用于所有阿里云服务 | ⭐⭐⭐ |

### 问题2: AccessKey Secret需要配置吗？

**答案**: **不需要**

百炼API调用只需要AccessKey ID，不需要AccessKey Secret。

### 问题3: 配置后仍然报错？

**可能原因**:
1. 没有重启终端/IDE
2. 环境变量配置错误
3. 使用了错误的密钥格式

**解决方案**:
1. 重启VS Code或终端
2. 重新配置环境变量
3. 确保使用百炼API密钥格式

## 📊 密钥类型对比

| 特性 | 阿里云AccessKey | 百炼API密钥 |
|------|----------------|-------------|
| **格式** | `LTAI5t6T...` | `sk-xxxxxxxxxx` |
| **用途** | 所有阿里云服务 | 仅百炼服务 |
| **安全性** | 较低（权限广泛） | 较高（专用于AI） |
| **获取方式** | 阿里云控制台 | 百炼控制台 |
| **推荐使用** | ❌ 不推荐 | ✅ 推荐 |

## 🎯 最终建议

### 1. 立即行动
- ✅ 登录百炼控制台获取API密钥
- ✅ 配置 `DASHSCOPE_API_KEY` 环境变量
- ✅ 重启终端/IDE

### 2. 最佳实践
- ✅ 使用百炼API密钥（`sk-xxxxxx`格式）
- ✅ 不要将密钥写入代码
- ✅ 定期轮换密钥
- ✅ 设置访问权限

### 3. 安全提醒
- ⚠️ 不要分享API密钥
- ⚠️ 不要提交到Git仓库
- ⚠️ 定期检查使用记录
- ⚠️ 及时删除不再使用的密钥

---

**总结**: 
- ❌ 你提供的格式（AccessKey ID:Secret）**不正确**
- ✅ 应该使用百炼API密钥（`sk-xxxxxx`格式）
- ✅ 配置时**只需要密钥本身**，不需要前缀