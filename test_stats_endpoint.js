#!/usr/bin/env node

/**
 * 测试任务统计端点
 */

const RAILWAY_BACKEND_URL = 'http://localhost:8000';

async function testStatsEndpoint() {
  try {
    console.log('🔍 测试任务统计端点...');
    
    const response = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/stats`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log('状态码:', response.status);
    console.log('CORS头:', response.headers.get('access-control-allow-origin'));
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ 成功:', data);
    } else {
      const errorText = await response.text();
      console.log('❌ 错误:', response.status, errorText);
    }
  } catch (error) {
    console.error('❌ 测试失败:', error);
  }
}

testStatsEndpoint();