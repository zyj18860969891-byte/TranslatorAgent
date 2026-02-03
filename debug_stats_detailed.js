#!/usr/bin/env node

/**
 * 详细调试任务统计问题
 */

const RAILWAY_BACKEND_URL = 'http://localhost:8000';

async function debugStatsDetailed() {
  try {
    console.log('🔍 详细调试任务统计问题...');
    
    // 创建一个任务
    console.log('\n📝 创建测试任务...');
    const taskRequest = {
      module: 'translation',
      taskName: '详细统计调试任务',
      instructions: '详细调试统计功能'
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
    console.log(`✅ 任务创建成功: ${taskId}`);
    
    // 获取任务列表
    console.log('\n📋 获取任务列表...');
    const listResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    if (!listResponse.ok) {
      throw new Error(`获取任务列表失败: ${listResponse.status}`);
    }
    
    const listData = await listResponse.json();
    console.log(`✅ 任务列表获取成功，数量: ${listData.data?.length || 0}`);
    
    // 手动计算统计信息
    console.log('\n📊 手动计算统计信息...');
    const tasks = listData.data || [];
    const manualStats = {
      totalTasks: tasks.length,
      completedTasks: tasks.filter(t => t.status === 'completed').length,
      failedTasks: tasks.filter(t => t.status === 'failed').length,
      processingTasks: tasks.filter(t => t.status === 'processing' || t.status === 'queued').length
    };
    
    console.log('手动统计:', manualStats);
    
    // 测试任务统计端点
    console.log('\n📊 测试任务统计端点...');
    const statsResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/stats`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`统计端点状态码: ${statsResponse.status}`);
    console.log(`CORS头: ${statsResponse.headers.get('access-control-allow-origin')}`);
    
    if (statsResponse.ok) {
      const statsData = await statsResponse.json();
      console.log('✅ 统计端点成功:', statsData);
    } else {
      const errorText = await statsResponse.text();
      console.log('❌ 统计端点错误:', statsResponse.status, errorText);
      
      // 尝试解析错误信息
      try {
        const errorData = JSON.parse(errorText);
        console.log('错误详情:', errorData);
      } catch (e) {
        console.log('错误文本:', errorText);
      }
    }
    
    // 测试带参数的统计端点
    console.log('\n📊 测试带参数的统计端点...');
    const paramStatsResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/stats?module=translation`, {
      method: 'GET',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`参数统计状态码: ${paramStatsResponse.status}`);
    
    if (paramStatsResponse.ok) {
      const paramStatsData = await paramStatsResponse.json();
      console.log('✅ 参数统计成功:', paramStatsData);
    } else {
      const errorText = await paramStatsResponse.text();
      console.log('❌ 参数统计错误:', paramStatsResponse.status, errorText);
    }
    
  } catch (error) {
    console.error('❌ 调试失败:', error);
  }
}

debugStatsDetailed();