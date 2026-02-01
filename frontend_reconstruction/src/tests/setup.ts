/**
 * 测试环境设置
 * 配置测试所需的全局环境
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// 扩展 Vitest 的 expect 方法
expect.extend(matchers);

// 每个测试后清理 DOM
afterEach(() => {
  cleanup();
});

// 模拟全局对象
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// 模拟 localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
(window as any).localStorage = localStorageMock;

// 模拟 fetch
(window as any).fetch = vi.fn();

// 模拟 performance
(window as any).performance = {
  now: () => Date.now(),
};

// 模拟 URL
(window as any).URL = {
  createObjectURL: () => 'mock-url',
  revokeObjectURL: () => {},
};