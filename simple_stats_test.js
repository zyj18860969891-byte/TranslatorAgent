#!/usr/bin/env node

/**
 * 简单的任务统计测试
 */

const RAILWAY_BACKEND_URL = 'http://localhost:8000';

async function simpleStatsTest() {
  try {
    console.log('🔍 简单任务统计测试...');
    
    // 创建一个任务
    console.log('\n📝 创建任务...');
    const taskRequest = {
      module: 'translation',
      taskName: '统计测试任务',
      instructions: '测试任务统计功能'
    };
    
    const createResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
      method: 'POST',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskRequest)
    });
    
    if (!createResponse.ok) {
      throw new Error(`任务创建失败: ${createResponse.status}`);
    }
    
    const createData = await createResponse.json();
    const taskId = createData.data?.taskId;
    console.log('✅ 任务创建成功:', taskId);
    
    // 直接测试任务统计端点
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
      console.log('✅ 统计端点成功:', statsData);
    } else {
      const errorText = await statsResponse.text();
      console.log('❌ 统计端点错误:', statsResponse.status, errorText);
    }
    
    // 测试带参数的统计
    console.log('\n📊 测试带参数的统计端点...');
    const paramStatsResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/stats?module=translation`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log('参数统计状态码:', paramStatsResponse.status);
    
    if (paramStatsResponse.ok) {
      const paramStatsData = await paramStatsResponse.json();
      console.log('✅ 参数统计成功:', paramStatsData);
    } else {
      const errorText = await paramStatsResponse.text();
      console.log('❌ 参数统计错误:', paramStatsResponse.status, errorText);
    }
    
  } catch (error) {
    console.error('❌ 测试失败:', error);
  }
}

simpleStatsTest();