# Translator Agent 部署指南

## 概述

本指南提供Translator Agent的完整部署方案，包括Docker部署、Kubernetes部署和开发环境配置。

## 前置要求

### 系统要求
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.20+ (可选)
- Python 3.9+
- FFmpeg (视频处理)

### 环境变量
```bash
# 必需的环境变量
export MODELSCOPE_API_KEY="your_modelscope_api_key"

# 可选的环境变量
export CACHE_SIZE=1000
export MAX_WORKERS=4
export DEBUG=false
```

## Docker部署

### 1. 快速启动

```bash
# 进入部署目录
cd deployment

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f translator-agent

# 停止服务
docker-compose down
```

### 2. 开发环境

```bash
# 使用开发配置
docker-compose -f docker-compose.dev.yml up -d

# 开发环境包含：
# - Translator Agent (端口8000)
# - Redis (端口6379)
# - Redis Commander (端口8081)
# - Portainer (端口9000)
```

### 3. 自定义配置

创建 `.env` 文件：
```bash
MODELSCOPE_API_KEY=your_api_key_here
CACHE_SIZE=2000
MAX_WORKERS=8
```

然后启动：
```bash
docker-compose --env-file .env up -d
```

## Kubernetes部署

### 1. 准备工作

```bash
# 确保Kubernetes集群已配置
kubectl config current-context

# 创建命名空间
kubectl create namespace translator-agent
```

### 2. 部署应用

```bash
# 使用部署脚本
chmod +x deploy.sh
./deploy.sh

# 或者手动部署
kubectl apply -f kubernetes-deployment.yml -n translator-agent
```

### 3. 验证部署

```bash
# 查看Pod状态
kubectl get pods -n translator-agent

# 查看Service
kubectl get svc -n translator-agent

# 查看日志
kubectl logs -n translator-agent deployment/translator-agent

# 端口转发（本地访问）
kubectl port-forward svc/translator-agent-service 8000:80 -n translator-agent
```

### 4. 扩展和管理

```bash
# 扩展副本数
kubectl scale deployment translator-agent --replicas=3 -n translator-agent

# 查看HPA
kubectl get hpa -n translator-agent

# 查看资源使用
kubectl top pods -n translator-agent
```

## Nginx反向代理

### 配置说明

`nginx.conf` 提供了以下功能：
- 反向代理到Translator Agent
- API端点路由
- 健康检查
- 错误处理

### 使用Nginx

```bash
# 使用Docker Compose启动Nginx
docker-compose up -d nginx

# 或者手动启动Nginx
nginx -c $(pwd)/nginx.conf
```

## 生产环境部署

### 1. 安全配置

```bash
# 创建SSL证书
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/translator.key \
    -out ssl/translator.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=Translator/CN=translator.example.com"

# 更新nginx.conf以使用SSL
```

### 2. 监控配置

```bash
# 查看应用日志
docker logs translator-agent

# 查看系统资源
docker stats translator-agent

# 查看Kubernetes资源
kubectl top pods -n translator-agent
```

### 3. 备份和恢复

```bash
# 备份数据
docker cp translator-agent:/app/context_storage ./backup/context_storage
docker cp translator-agent:/app/performance_storage ./backup/performance_storage

# 恢复数据
docker cp ./backup/context_storage translator-agent:/app/
docker cp ./backup/performance_storage translator-agent:/app/
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -ano | findstr :8000
   
   # 修改端口
   export PORT=8001
   ```

2. **环境变量缺失**
   ```bash
   # 检查环境变量
   echo $MODELSCOPE_API_KEY
   
   # 设置环境变量
   export MODELSCOPE_API_KEY="your_key"
   ```

3. **Docker权限问题**
   ```bash
   # 添加用户到docker组
   sudo usermod -aG docker $USER
   
   # 重新登录
   newgrp docker
   ```

4. **Kubernetes部署失败**
   ```bash
   # 查看详细错误
   kubectl describe pod -n translator-agent
   kubectl logs -n translator-agent deployment/translator-agent
   ```

### 日志查看

```bash
# Docker日志
docker logs translator-agent
docker logs -f translator-agent

# Kubernetes日志
kubectl logs -n translator-agent deployment/translator-agent
kubectl logs -f -n translator-agent deployment/translator-agent

# 查看特定Pod日志
kubectl get pods -n translator-agent
kubectl logs <pod-name> -n translator-agent
```

## 性能优化

### 1. 资源限制

```yaml
# 在docker-compose.yml中
resources:
  limits:
    memory: 2G
    cpus: '1.0'
  reservations:
    memory: 512M
    cpus: '0.5'
```

### 2. 缓存配置

```bash
# 增加缓存大小
export CACHE_SIZE=5000

# 使用Redis缓存
# 在docker-compose.yml中启用Redis服务
```

### 3. 并发配置

```bash
# 增加工作进程
export MAX_WORKERS=8

# 调整UVICORN配置
# 在run_api.py中修改uvicorn.run参数
```

## 监控和告警

### 1. 健康检查

```bash
# 检查应用健康状态
curl http://localhost:8000/health

# 检查API端点
curl http://localhost:8000/api/info
```

### 2. 性能监控

```bash
# 查看性能统计
curl http://localhost:8000/api/v1/tasks/stats

# 查看系统状态
curl http://localhost:8000/api/v1/system/status
```

### 3. 日志监控

```bash
# 实时日志
docker logs -f translator-agent

# 日志分析
docker logs translator-agent | grep "ERROR"
docker logs translator-agent | grep "WARNING"
```

## 更新和维护

### 1. 更新应用

```bash
# 停止服务
docker-compose down

# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build --no-cache

# 启动服务
docker-compose up -d
```

### 2. 数据迁移

```bash
# 备份数据
docker cp translator-agent:/app/context_storage ./backup/
docker cp translator-agent:/app/performance_storage ./backup/

# 恢复数据
docker cp ./backup/context_storage translator-agent:/app/
docker cp ./backup/performance_storage translator-agent:/app/
```

### 3. 清理

```bash
# 清理Docker资源
docker system prune -f
docker volume prune -f

# 清理Kubernetes资源
kubectl delete all -n translator-agent
kubectl delete namespace translator-agent
```

## 安全建议

1. **使用HTTPS**
   - 配置SSL证书
   - 使用Let's Encrypt

2. **访问控制**
   - 使用API密钥
   - 实现认证和授权

3. **网络隔离**
   - 使用VPC
   - 配置防火墙规则

4. **数据加密**
   - 加密敏感数据
   - 定期轮换密钥

## 性能基准

### 测试环境
- CPU: 4核
- 内存: 8GB
- 网络: 1Gbps

### 预期性能
- API响应时间: < 100ms
- 并发处理: 100+ 请求/秒
- 视频处理: 10-20秒/分钟视频
- 内存使用: < 2GB

## 支持和反馈

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 项目文档
- 技术支持邮箱

---

**版本**: 1.0.0  
**最后更新**: 2026-01-20  
**维护者**: Translator Agent Team