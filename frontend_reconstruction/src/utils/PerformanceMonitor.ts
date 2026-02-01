/**
 * 性能监控器
 * 实时监控 API 性能指标并触发告警
 */

export interface PerformanceMetrics {
  timestamp: number;
  apiLatency: number;
  apiStatus: 'connected' | 'disconnected' | 'degraded';
  errorRate: number;
  requestCount: number;
  successCount: number;
  failureCount: number;
  memoryUsage?: number;
}

export interface AlertRule {
  id: string;
  name: string;
  condition: (metrics: PerformanceMetrics) => boolean;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  cooldown?: number; // 冷却时间（毫秒）
}

export interface Alert {
  id: string;
  ruleId: string;
  timestamp: number;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  metrics: PerformanceMetrics;
  acknowledged: boolean;
}

export interface PerformanceConfig {
  samplingInterval: number; // 采样间隔（毫秒）
  maxHistory: number; // 最大历史记录数
  alertEnabled: boolean; // 是否启用告警
  alertCooldown: number; // 默认告警冷却时间
}

// 默认配置
const DEFAULT_CONFIG: PerformanceConfig = {
  samplingInterval: 30000, // 30秒
  maxHistory: 100,
  alertEnabled: true,
  alertCooldown: 60000, // 1分钟
};

// 默认告警规则
const DEFAULT_ALERT_RULES: AlertRule[] = [
  {
    id: 'high_latency',
    name: '高延迟告警',
    condition: (metrics) => metrics.apiLatency > 1000,
    severity: 'warning',
    message: 'API 响应延迟过高 (>1000ms)',
    cooldown: 120000, // 2分钟
  },
  {
    id: 'api_disconnected',
    name: 'API 断开告警',
    condition: (metrics) => metrics.apiStatus === 'disconnected',
    severity: 'error',
    message: 'API 连接已断开',
    cooldown: 30000, // 30秒
  },
  {
    id: 'high_error_rate',
    name: '高错误率告警',
    condition: (metrics) => metrics.errorRate > 0.3,
    severity: 'error',
    message: 'API 错误率过高 (>30%)',
    cooldown: 180000, // 3分钟
  },
  {
    id: 'critical_latency',
    name: '严重延迟告警',
    condition: (metrics) => metrics.apiLatency > 5000,
    severity: 'critical',
    message: 'API 响应严重延迟 (>5000ms)',
    cooldown: 60000, // 1分钟
  },
  {
    id: 'api_degraded',
    name: 'API 降级告警',
    condition: (metrics) => metrics.apiStatus === 'degraded',
    severity: 'warning',
    message: 'API 已降级到本地存储',
    cooldown: 90000, // 1.5分钟
  },
  {
    id: 'low_success_rate',
    name: '低成功率告警',
    condition: (metrics) => {
      const total = metrics.requestCount;
      if (total === 0) return false;
      const successRate = metrics.successCount / total;
      return successRate < 0.7;
    },
    severity: 'warning',
    message: 'API 成功率过低 (<70%)',
    cooldown: 180000, // 3分钟
  },
];

export class PerformanceMonitor {
  private config: PerformanceConfig;
  private metricsHistory: PerformanceMetrics[] = [];
  private alerts: Alert[] = [];
  private alertRules: AlertRule[];
  private alertCooldowns: Map<string, number> = new Map();
  private listeners: Set<(alert: Alert) => void> = new Set();
  private samplingInterval: any = null;

  constructor(config?: Partial<PerformanceConfig>, rules?: AlertRule[]) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.alertRules = rules || DEFAULT_ALERT_RULES;
  }

  /**
   * 启动监控
   */
  start(): void {
    if (this.samplingInterval) {
      return; // 已经启动
    }

    console.log('[PerformanceMonitor] 监控已启动');
    
    this.samplingInterval = setInterval(() => {
      this.sampleMetrics();
    }, this.config.samplingInterval);
  }

  /**
   * 停止监控
   */
  stop(): void {
    if (this.samplingInterval) {
      clearInterval(this.samplingInterval);
      this.samplingInterval = null;
      console.log('[PerformanceMonitor] 监控已停止');
    }
  }

  /**
   * 记录性能指标
   */
  recordMetrics(metrics: Omit<PerformanceMetrics, 'timestamp'>): void {
    const fullMetrics: PerformanceMetrics = {
      ...metrics,
      timestamp: Date.now(),
    };

    // 添加到历史记录
    this.metricsHistory.push(fullMetrics);
    
    // 限制历史记录数量
    if (this.metricsHistory.length > this.config.maxHistory) {
      this.metricsHistory = this.metricsHistory.slice(-this.config.maxHistory);
    }

    // 检查告警规则
    if (this.config.alertEnabled) {
      this.checkAlertRules(fullMetrics);
    }

    // 触发采样（如果需要实时监控）
    this.sampleMetrics();
  }

  /**
   * 采样当前指标
   */
  private sampleMetrics(): void {
    if (this.metricsHistory.length === 0) {
      return;
    }
    
    // 计算统计信息
    const recentMetrics = this.metricsHistory.slice(-10); // 最近10个样本
    const avgLatency = recentMetrics.reduce((sum, m) => sum + m.apiLatency, 0) / recentMetrics.length;
    const errorRate = recentMetrics.reduce((sum, m) => sum + m.errorRate, 0) / recentMetrics.length;
    const totalRequests = recentMetrics.reduce((sum, m) => sum + m.requestCount, 0);
    const totalSuccess = recentMetrics.reduce((sum, m) => sum + m.successCount, 0);
    const successRate = totalRequests > 0 ? totalSuccess / totalRequests : 1;

    // 输出监控信息
    console.log(`[PerformanceMonitor] 采样 - 延迟: ${avgLatency.toFixed(0)}ms, 错误率: ${(errorRate * 100).toFixed(1)}%, 成功率: ${(successRate * 100).toFixed(1)}%`);
  }

  /**
   * 检查告警规则
   */
  private checkAlertRules(metrics: PerformanceMetrics): void {
    const now = Date.now();

    for (const rule of this.alertRules) {
      // 检查条件是否满足
      if (!rule.condition(metrics)) {
        continue;
      }

      // 检查冷却时间
      const lastAlertTime = this.alertCooldowns.get(rule.id) || 0;
      const cooldown = rule.cooldown || this.config.alertCooldown;
      
      if (now - lastAlertTime < cooldown) {
        continue; // 还在冷却期
      }

      // 创建告警
      const alert: Alert = {
        id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        ruleId: rule.id,
        timestamp: now,
        severity: rule.severity,
        message: rule.message,
        metrics: { ...metrics },
        acknowledged: false,
      };

      // 添加到告警列表
      this.alerts.push(alert);
      
      // 更新冷却时间
      this.alertCooldowns.set(rule.id, now);

      // 限制告警数量
      if (this.alerts.length > 50) {
        this.alerts = this.alerts.slice(-50);
      }

      // 输出告警信息
      this.logAlert(alert);

      // 通知监听器
      this.notifyListeners(alert);
    }
  }

  /**
   * 记录告警
   */
  private logAlert(alert: Alert): void {
    const prefix = `[PerformanceMonitor] 告警 [${alert.severity.toUpperCase()}]`;
    const message = `${prefix} ${alert.message}`;
    
    switch (alert.severity) {
      case 'info':
        console.info(message);
        break;
      case 'warning':
        console.warn(message);
        break;
      case 'error':
      case 'critical':
        console.error(message);
        break;
    }
  }

  /**
   * 通知监听器
   */
  private notifyListeners(alert: Alert): void {
    this.listeners.forEach(listener => {
      try {
        listener(alert);
      } catch (error) {
        console.error('[PerformanceMonitor] 通知监听器失败:', error);
      }
    });
  }

  /**
   * 添加告警监听器
   */
  addListener(listener: (alert: Alert) => void): void {
    this.listeners.add(listener);
  }

  /**
   * 移除告警监听器
   */
  removeListener(listener: (alert: Alert) => void): void {
    this.listeners.delete(listener);
  }

  /**
   * 确认告警
   */
  acknowledgeAlert(alertId: string): boolean {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      return true;
    }
    return false;
  }

  /**
   * 清除告警
   */
  clearAlert(alertId: string): boolean {
    const index = this.alerts.findIndex(a => a.id === alertId);
    if (index !== -1) {
      this.alerts.splice(index, 1);
      return true;
    }
    return false;
  }

  /**
   * 清除所有告警
   */
  clearAllAlerts(): void {
    this.alerts = [];
  }

  /**
   * 获取当前告警
   */
  getAlerts(filter?: { severity?: Alert['severity']; acknowledged?: boolean }): Alert[] {
    let alerts = [...this.alerts];

    if (filter?.severity) {
      alerts = alerts.filter(a => a.severity === filter.severity);
    }

    if (filter?.acknowledged !== undefined) {
      alerts = alerts.filter(a => a.acknowledged === filter.acknowledged);
    }

    // 按时间倒序排序
    return alerts.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * 获取未确认的告警
   */
  getUnacknowledgedAlerts(): Alert[] {
    return this.getAlerts({ acknowledged: false });
  }

  /**
   * 获取历史指标
   */
  getMetricsHistory(limit?: number): PerformanceMetrics[] {
    if (limit) {
      return this.metricsHistory.slice(-limit);
    }
    return [...this.metricsHistory];
  }

  /**
   * 获取统计信息
   */
  getStats(): {
    totalAlerts: number;
    unacknowledgedAlerts: number;
    recentMetrics: PerformanceMetrics[];
    avgLatency: number;
    errorRate: number;
    successRate: number;
  } {
    const recentMetrics = this.metricsHistory.slice(-10);
    const avgLatency = recentMetrics.length > 0
      ? recentMetrics.reduce((sum, m) => sum + m.apiLatency, 0) / recentMetrics.length
      : 0;
    
    const errorRate = recentMetrics.length > 0
      ? recentMetrics.reduce((sum, m) => sum + m.errorRate, 0) / recentMetrics.length
      : 0;
    
    const totalRequests = recentMetrics.reduce((sum, m) => sum + m.requestCount, 0);
    const totalSuccess = recentMetrics.reduce((sum, m) => sum + m.successCount, 0);
    const successRate = totalRequests > 0 ? totalSuccess / totalRequests : 1;

    return {
      totalAlerts: this.alerts.length,
      unacknowledgedAlerts: this.getUnacknowledgedAlerts().length,
      recentMetrics,
      avgLatency,
      errorRate,
      successRate,
    };
  }

  /**
   * 重置监控器
   */
  reset(): void {
    this.stop();
    this.metricsHistory = [];
    this.alerts = [];
    this.alertCooldowns.clear();
    this.listeners.clear();
  }

  /**
   * 导出数据
   */
  exportData(): {
    metrics: PerformanceMetrics[];
    alerts: Alert[];
    config: PerformanceConfig;
  } {
    return {
      metrics: this.metricsHistory,
      alerts: this.alerts,
      config: this.config,
    };
  }

  /**
   * 导入数据
   */
  importData(data: {
    metrics?: PerformanceMetrics[];
    alerts?: Alert[];
    config?: PerformanceConfig;
  }): void {
    if (data.metrics) {
      this.metricsHistory = data.metrics.slice(-this.config.maxHistory);
    }
    if (data.alerts) {
      this.alerts = data.alerts.slice(-50);
    }
    if (data.config) {
      this.config = { ...this.config, ...data.config };
    }
  }
}

// 全局性能监控器实例
let globalMonitor: PerformanceMonitor | null = null;

/**
 * 获取全局性能监控器
 */
export function getPerformanceMonitor(): PerformanceMonitor {
  if (!globalMonitor) {
    globalMonitor = new PerformanceMonitor();
  }
  return globalMonitor;
}

/**
 * 初始化全局性能监控器
 */
export function initializePerformanceMonitor(config?: Partial<PerformanceConfig>): PerformanceMonitor {
  if (globalMonitor) {
    globalMonitor.reset();
  }
  globalMonitor = new PerformanceMonitor(config);
  return globalMonitor;
}

/**
 * 销毁全局性能监控器
 */
export function destroyPerformanceMonitor(): void {
  if (globalMonitor) {
    globalMonitor.reset();
    globalMonitor = null;
  }
}