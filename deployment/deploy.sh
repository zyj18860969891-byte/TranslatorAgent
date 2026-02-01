#!/bin/bash

# Translator Agent 部署脚本

set -e

echo "=========================================="
echo "Translator Agent 部署脚本"
echo "=========================================="

# 检查环境变量
if [ -z "$MODELSCOPE_API_KEY" ]; then
    echo "错误: 请设置 MODELSCOPE_API_KEY 环境变量"
    exit 1
fi

# 配置
PROJECT_NAME="translator-agent"
DOCKER_IMAGE="translator-agent:latest"
NAMESPACE="translator-agent"

# 步骤1: 构建Docker镜像
echo "步骤1: 构建Docker镜像..."
docker build -t $DOCKER_IMAGE -f deployment/Dockerfile .
echo "✅ Docker镜像构建完成"

# 步骤2: 创建Kubernetes命名空间
echo "步骤2: 创建Kubernetes命名空间..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
echo "✅ 命名空间创建完成"

# 步骤3: 创建Secret
echo "步骤3: 创建Secret..."
kubectl create secret generic translator-secrets \
    --from-literal=modelscope-api-key=$MODELSCOPE_API_KEY \
    --namespace=$NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Secret创建完成"

# 步骤4: 部署应用
echo "步骤4: 部署应用..."
kubectl apply -f deployment/kubernetes-deployment.yml -n $NAMESPACE
echo "✅ 应用部署完成"

# 步骤5: 等待部署完成
echo "步骤5: 等待部署完成..."
kubectl wait --for=condition=available --timeout=300s deployment/translator-agent -n $NAMESPACE
echo "✅ 部署完成"

# 步骤6: 获取服务信息
echo "步骤6: 获取服务信息..."
SERVICE_IP=$(kubectl get svc translator-agent-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$SERVICE_IP" ]; then
    SERVICE_IP=$(kubectl get svc translator-agent-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    echo "服务集群IP: $SERVICE_IP"
else
    echo "服务外部IP: $SERVICE_IP"
fi

# 步骤7: 验证部署
echo "步骤7: 验证部署..."
sleep 10
if curl -f http://$SERVICE_IP/health > /dev/null 2>&1; then
    echo "✅ 部署验证通过"
else
    echo "⚠️ 部署验证失败，请检查日志"
    kubectl logs -n $NAMESPACE deployment/translator-agent
fi

echo ""
echo "=========================================="
echo "部署完成!"
echo "=========================================="
echo "API地址: http://$SERVICE_IP"
echo "API文档: http://$SERVICE_IP/api/docs"
echo "健康检查: http://$SERVICE_IP/health"
echo ""
echo "查看日志: kubectl logs -n $NAMESPACE deployment/translator-agent"
echo "查看状态: kubectl get all -n $NAMESPACE"
echo "=========================================="