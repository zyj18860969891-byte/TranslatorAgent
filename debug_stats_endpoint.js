#!/usr/bin/env node

/**
 * 调试任务统计端点
 */

const RAILWAY_BACKEND_URL = 'http://localhost:8000';

async function debugStatsEndpoint() {
  try {
    console.log('🔍 调试任务统计端点...');
    
    // 首先获取所有任务
    console.log('\n📋 获取所有任务...');
    const tasksResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log('任务列表状态码:', tasksResponse.status);
    
    if (tasksResponse.ok) {
      const tasksData = await tasksResponse.json();
      console.log('任务数量:', tasksData.data?.length || 0);
      console.log('任务详情:', tasksData.data);
    }
    
    // 然后测试统计端点
    console.log('\n📊 测试任务统计端点...');
    const statsResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/stats`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log('统计端点状态码:', statsResponse.status);
    console.log('CORS头:', statsResponse.headers.get('access-control-allow-origin'));
    
    if (statsResponse.ok) {
      const statsData = await statsResponse.json();
      console.log('✅ 成功:', statsData);
    } else {
      const errorText = await statsResponse.text();
      console.log('❌ 错误:', statsResponse.status, errorText);
    }
    
    // 测试带模块参数的统计
    console.log('\n📊 测试带模块参数的任务统计...');
    const moduleStatsResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/stats?module=translation`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log('模块统计状态码:', moduleStatsResponse.status);
    
    if (moduleStatsResponse.ok) {
      const moduleStatsData = await moduleStatsResponse.json();
      console.log('✅ 模块统计成功:', moduleStatsData);
    } else {
      const errorText = await moduleStatsResponse.text();
      console.log('❌ 模块统计错误:', moduleStatsResponse.status, errorText);
    }
    
  } catch (error) {
    console.error('❌ 调试失败:', error);
  }
}

debugStatsEndpoint();