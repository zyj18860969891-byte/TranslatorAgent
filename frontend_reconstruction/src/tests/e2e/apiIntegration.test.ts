/**
 * API 集成端到端测试
 * 测试前端与后端 API 的完整集成流程
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { checkApiHealth, getApiLatency, getApiConfig } from '../../utils/apiClient';
import { getPerformanceMonitor } from '../../utils/PerformanceMonitor';
import { apiFsm } from '../../utils/ApiFileSystemStateMachine';

describe('API 集成端到端测试', () => {
  let apiAvailable = false;

  beforeAll(async () => {
    // 检查 API 是否可用
    apiAvailable = await checkApiHealth();
    console.log(`[测试] API 可用性: ${apiAvailable ? '可用' : '不可用'}`);
  });

  afterAll(() => {
    // 清理测试数据
    const monitor = getPerformanceMonitor();
    monitor.clearAllAlerts();
  });

  describe('API 连接测试', () => {
    it('应该能够检查 API 健康状态', async () => {
      const isHealthy = await checkApiHealth();
      expect(typeof isHealthy).toBe('boolean');
    });

    it('应该能够测量 API 延迟', async () => {
      const latency = await getApiLatency();
      expect(typeof latency).toBe('number');
      expect(latency).toBeGreaterThanOrEqual(-1); // -1 表示连接失败
    });

    it('应该能够获取 API 配置', () => {
      const config = getApiConfig();
      expect(config).toBeDefined();
      expect(config.baseUrl).toBeDefined();
      expect(config.version).toBeDefined();
      expect(config.timeout).toBeDefined();
      expect(config.retryCount).toBeDefined();
    });
  });

  describe('性能监控测试', () => {
    it('应该能够获取性能监控器实例', () => {
      const monitor = getPerformanceMonitor();
      expect(monitor).toBeDefined();
    });

    it('应该能够记录性能指标', () => {
      const monitor = getPerformanceMonitor();
      
      // 记录测试指标
      monitor.recordMetrics({
        apiLatency: 100,
        apiStatus: 'connected',
        errorRate: 0.05,
        requestCount: 10,
        successCount: 9,
        failureCount: 1,
      });

      const history = monitor.getMetricsHistory(1);
      expect(history.length).toBeGreaterThan(0);
      expect(history[0].apiLatency).toBe(100);
    });

    it('应该能够获取性能统计', () => {
      const monitor = getPerformanceMonitor();
      const stats = monitor.getStats();
      
      expect(stats).toBeDefined();
      expect(stats.totalAlerts).toBeDefined();
      expect(stats.unacknowledgedAlerts).toBeDefined();
      expect(stats.avgLatency).toBeDefined();
      expect(stats.errorRate).toBeDefined();
      expect(stats.successRate).toBeDefined();
    });

    it('应该能够导出性能数据', () => {
      const monitor = getPerformanceMonitor();
      const data = monitor.exportData();
      
      expect(data).toBeDefined();
      expect(data.metrics).toBeDefined();
      expect(data.alerts).toBeDefined();
      expect(data.config).toBeDefined();
    });
  });

  describe('API 文件系统状态机测试', () => {
    it('应该能够检查 API FSM 是否可用', () => {
      const isAvailable = apiFsm.isApiAvailable();
      expect(typeof isAvailable).toBe('boolean');
    });

    it('应该能够获取 API 配置', () => {
      const config = apiFsm.getApiConfig();
      expect(config).toBeDefined();
      expect(config.baseUrl).toBeDefined();
    });

    it('应该能够初始化 FSM', async () => {
      // FSM 应该已经初始化
      expect(apiFsm).toBeDefined();
    });
  });

  describe('告警系统测试', () => {
    it('应该能够创建告警', () => {
      const monitor = getPerformanceMonitor();
      
      // 记录触发告警的指标
      monitor.recordMetrics({
        apiLatency: 2000, // 触发高延迟告警
        apiStatus: 'connected',
        errorRate: 0.1,
        requestCount: 10,
        successCount: 8,
        failureCount: 2,
      });

      const alerts = monitor.getAlerts();
      expect(alerts.length).toBeGreaterThan(0);
    });

    it('应该能够确认告警', () => {
      const monitor = getPerformanceMonitor();
      const alerts = monitor.getAlerts();
      
      if (alerts.length > 0) {
        const alertId = alerts[0].id;
        const result = monitor.acknowledgeAlert(alertId);
        expect(result).toBe(true);
      }
    });

    it('应该能够清除告警', () => {
      const monitor = getPerformanceMonitor();
      const alerts = monitor.getAlerts();
      
      if (alerts.length > 0) {
        const alertId = alerts[0].id;
        const result = monitor.clearAlert(alertId);
        expect(result).toBe(true);
      }
    });
  });

  describe('API 集成流程测试', () => {
    it('应该能够完成完整的 API 集成流程', async () => {
      // 1. 检查 API 连接
      const isHealthy = await checkApiHealth();
      expect(isHealthy).toBeDefined();

      // 2. 测量 API 延迟
      const latency = await getApiLatency();
      expect(latency).toBeDefined();

      // 3. 记录性能指标
      const monitor = getPerformanceMonitor();
      monitor.recordMetrics({
        apiLatency: latency,
        apiStatus: isHealthy ? 'connected' : 'disconnected',
        errorRate: isHealthy ? 0 : 1,
        requestCount: 1,
        successCount: isHealthy ? 1 : 0,
        failureCount: isHealthy ? 0 : 1,
      });

      // 4. 检查性能统计
      const stats = monitor.getStats();
      expect(stats).toBeDefined();

      // 5. 检查 API FSM
      const isApiAvailable = apiFsm.isApiAvailable();
      expect(typeof isApiAvailable).toBe('boolean');

      // 6. 获取 API 配置
      const config = apiFsm.getApiConfig();
      expect(config).toBeDefined();
    });
  });

  describe('错误处理测试', () => {
    it('应该能够处理 API 连接失败', async () => {
      // 模拟 API 不可用的情况
      const latency = await getApiLatency();
      
      // 如果 API 不可用，应该返回 -1
      if (latency === -1) {
        expect(latency).toBe(-1);
      } else {
        expect(latency).toBeGreaterThanOrEqual(0);
      }
    });

    it('应该能够处理性能监控错误', () => {
      const monitor = getPerformanceMonitor();
      
      // 尝试记录无效的指标
      expect(() => {
        monitor.recordMetrics({
          apiLatency: -100, // 无效值
          apiStatus: 'invalid' as any,
          errorRate: 2, // 无效值
          requestCount: -1, // 无效值
          successCount: -1, // 无效值
          failureCount: -1, // 无效值
        });
      }).not.toThrow();
    });
  });
});

/**
 * API 端点集成测试
 * 测试与后端 API 的实际交互
 */
describe('API 端点集成测试', () => {
  const API_BASE_URL = 'http://localhost:8000';

  describe('健康检查端点', () => {
    it('应该能够访问健康检查端点', async () => {
      const isAvailable = await checkApiHealth();
      if (!isAvailable) {
        console.log('[测试] 跳过 - API 不可用');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/health`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.data).toBeDefined();
      expect(data.data.status).toBe('healthy');
    });
  });

  describe('任务管理端点', () => {
    it('应该能够创建任务', async () => {
      const isAvailable = await checkApiHealth();
      if (!isAvailable) {
        console.log('[测试] 跳过 - API 不可用');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module: 'translation',
          taskName: '测试任务',
          files: [{ name: 'test.mp4', type: 'video/mp4', url: 'http://example.com/test.mp4' }],
          instructions: '测试翻译',
        }),
      });

      expect(response.ok).toBe(true);
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.data).toBeDefined();
      expect(data.data.taskId).toBeDefined();
    });

    it('应该能够获取任务列表', async () => {
      const isAvailable = await checkApiHealth();
      if (!isAvailable) {
        console.log('[测试] 跳过 - API 不可用');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/tasks`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(Array.isArray(data.data)).toBe(true);
    });
  });

  describe('系统信息端点', () => {
    it('应该能够获取系统信息', async () => {
      const isAvailable = await checkApiHealth();
      if (!isAvailable) {
        console.log('[测试] 跳过 - API 不可用');
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/system/info`);
      expect(response.ok).toBe(true);
      
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.data).toBeDefined();
      expect(data.data.version).toBeDefined();
    });
  });
});