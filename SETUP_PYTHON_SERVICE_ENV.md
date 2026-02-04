# 设置Python处理服务环境变量指南

## 当前状态

✅ Python处理服务已成功部署到Railway
- 服务名称: `intuitive-bravery`
- 服务URL: `https://intuitive-bravery.railway.app`
- 状态: 运行中

⚠️ 需要设置环境变量以启用真实的AI处理功能

## 需要设置的环境变量

在Railway控制台中为Python处理服务设置以下环境变量：

### 1. DASHSCOPE_API_KEY (必需)
```
DASHSCOPE_API_KEY=your_actual_dashscope_api_key_here
```

### 2. ALLOWED_ORIGINS (可选，建议设置)
```
ALLOWED_ORIGINS=https://translator-agent-rosy.vercel.app,https://translatoragent-production.up.railway.app
```

### 3. 其他可选配置
```
PYTHONUNBUFFERED=1
DEBUG=false
```

## 设置步骤

### 方法1：通过Railway Web控制台（推荐）

1. 访问 https://railway.app/dashboard
2. 登录您的账户
3. 找到项目: `TranslatorAgent`
4. 点击服务: `intuitive-bravery`
5. 进入 "Variables" 标签页
6. 添加上述环境变量
7. 点击 "Save" 保存
8. 重启服务（如果需要）

### 方法2：通过Railway CLI

```bash
# 设置环境变量
cd processing_service
railway variables set DASHSCOPE_API_KEY=your_actual_dashscope_api_key_here
railway variables set ALLOWED_ORIGINS=https://translator-agent-rosy.vercel.app,https://translatoragent-production.up.railway.app

# 重启服务
railway restart
```

## 验证设置

设置完成后，运行以下命令验证：

```bash
# 检查环境变量
railway variables list

# 查看服务日志
railway logs --tail 20

# 测试服务健康状态
curl https://intuitive-bravery.railway.app/health
```

## 预期结果

设置DASHSCOPE_API_KEY后：
- ✅ Python服务将使用真实的Qwen3模型进行任务处理
- ✅ 不再显示"Qwen3组件未安装，将使用模拟处理"警告
- ✅ 任务处理将返回真实的AI生成结果

## 故障排除

### 问题：服务启动失败
- 检查DASHSCOPE_API_KEY是否正确
- 查看Railway日志中的错误信息
- 确认API密钥有足够的权限

### 问题：CORS错误
- 确保ALLOWED_ORIGINS包含正确的域名
- 检查后端CORS配置

### 问题：连接超时
- 确认服务URL正确
- 检查网络连接
- 查看Railway服务状态

## 下一步

设置环境变量后：
1. 重新运行部署状态检查: `python check_deployment_status.py`
2. 测试完整的任务处理流程
3. 验证前端能够成功调用Python服务
4. 修复Vercel前端404问题

---

**重要提醒**: 请将 `your_actual_dashscope_api_key_here` 替换为您的实际DashScope API密钥。