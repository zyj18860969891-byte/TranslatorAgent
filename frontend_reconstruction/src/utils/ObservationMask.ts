// 观察值掩码工具 - 防止大数据观察值塞满聊天窗口导致上下文崩溃

export interface ObservationMaskConfig {
  maxDisplayLength: number;
  maxLines: number;
  maskPattern: string;
  enableTruncation: boolean;
  enableCompression: boolean;
}

export interface MaskedObservation {
  original: string;
  masked: string;
  size: number;
  isMasked: boolean;
  metadata: {
    type: string;
    timestamp: string;
    source: string;
  };
}

export class ObservationMask {
  private config: ObservationMaskConfig;

  constructor(config?: Partial<ObservationMaskConfig>) {
    this.config = {
      maxDisplayLength: config?.maxDisplayLength || 500,
      maxLines: config?.maxLines || 10,
      maskPattern: config?.maskPattern || '...',
      enableTruncation: config?.enableTruncation ?? true,
      enableCompression: config?.enableCompression ?? true,
      ...config
    };
  }

  // 掩码观察值
  mask(observation: string, metadata?: Partial<MaskedObservation['metadata']>): MaskedObservation {
    const size = observation.length;
    const isLarge = size > this.config.maxDisplayLength;
    
    if (!isLarge || !this.config.enableTruncation) {
      return {
        original: observation,
        masked: observation,
        size,
        isMasked: false,
        metadata: {
          type: 'raw',
          timestamp: new Date().toISOString(),
          source: 'direct',
          ...metadata
        }
      };
    }

    // 截断大文本
    const truncated = this.truncate(observation);
    
    // 如果启用压缩，进一步处理
    const masked = this.config.enableCompression 
      ? this.compress(truncated)
      : truncated;

    return {
      original: observation,
      masked,
      size,
      isMasked: true,
      metadata: {
        type: 'compressed',
        timestamp: new Date().toISOString(),
        source: 'masked',
        ...metadata
      }
    };
  }

  // 截断文本
  private truncate(text: string): string {
    const lines = text.split('\n');
    
    if (lines.length > this.config.maxLines) {
      const head = lines.slice(0, Math.floor(this.config.maxLines / 2)).join('\n');
      const tail = lines.slice(-Math.floor(this.config.maxLines / 2)).join('\n');
      return `${head}\n${this.config.maskPattern} (${lines.length - this.config.maxLines} 行省略)\n${tail}`;
    }

    if (text.length > this.config.maxDisplayLength) {
      const head = text.substring(0, this.config.maxDisplayLength / 2);
      const tail = text.substring(text.length - this.config.maxDisplayLength / 2);
      return `${head}\n${this.config.maskPattern} (${text.length - this.config.maxDisplayLength} 字符省略)\n${tail}`;
    }

    return text;
  }

  // 压缩文本
  private compress(text: string): string {
    // 移除多余的空格和换行
    let compressed = text.replace(/\s+/g, ' ').trim();
    
    // 如果仍然很长，添加压缩标记
    if (compressed.length > this.config.maxDisplayLength) {
      compressed = compressed.substring(0, this.config.maxDisplayLength) + '...';
    }
    
    return compressed;
  }

  // 创建路径引用（用于大数据）
  createPathReference(filePath: string, size: number): string {
    const sizeStr = this.formatSize(size);
    return `📁 ${filePath} (${sizeStr})`;
  }

  // 创建进度引用
  createProgressReference(current: number, total: number, message: string): string {
    const percentage = Math.round((current / total) * 100);
    return `📊 ${message} (${percentage}%)`;
  }

  // 格式化大小
  private formatSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // 批量掩码多个观察值
  maskBatch(observations: string[], metadata?: Partial<MaskedObservation['metadata']>): MaskedObservation[] {
    return observations.map(obs => this.mask(obs, metadata));
  }

  // 恢复掩码的观察值
  restore(maskedObservation: MaskedObservation): string {
    return maskedObservation.original;
  }

  // 获取统计信息
  getStats(observations: MaskedObservation[]): {
    total: number;
    masked: number;
    totalSize: number;
    savedSize: number;
  } {
    const total = observations.length;
    const masked = observations.filter(o => o.isMasked).length;
    const totalSize = observations.reduce((sum, o) => sum + o.size, 0);
    const savedSize = observations.reduce((sum, o) => {
      if (o.isMasked) {
        return sum + (o.size - o.masked.length);
      }
      return sum;
    }, 0);

    return { total, masked, totalSize, savedSize };
  }
}

// 全局观察值掩码实例
export const observationMask = new ObservationMask({
  maxDisplayLength: 500,
  maxLines: 10,
  maskPattern: '...',
  enableTruncation: true,
  enableCompression: true
});