#!/usr/bin/env node

/**
 * 调试端点路由问题
 */

const RAILWAY_BACKEND_URL = 'http://localhost:8000';

async function debugEndpointRouting() {
  try {
    console.log('🔍 调试端点路由问题...');
    
    // 测试所有可用的端点
    const endpoints = [
      { method: 'GET', path: '/api/health', description: '健康检查' },
      { method: 'GET', path: '/api/v1/tasks', description: '任务列表' },
      { method: 'GET', path: '/api/v1/tasks/stats', description: '任务统计' },
      { method: 'GET', path: '/api/v1/system/info', description: '系统信息' }
    ];
    
    for (const endpoint of endpoints) {
      console.log(`\n🔄 测试 ${endpoint.method} ${endpoint.path} - ${endpoint.description}`);
      
      try {
        const response = await fetch(`${RAILWAY_BACKEND_URL}${endpoint.path}`, {
          method: endpoint.method,
          headers: {
            'Origin': 'https://translator-agent-sandy.vercel.app',
            'Content-Type': 'application/json'
          }
        });
        
        console.log(`   状态码: ${response.status}`);
        console.log(`   CORS头: ${response.headers.get('access-control-allow-origin')}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log(`   ✅ 成功: ${JSON.stringify(data.data).substring(0, 100)}...`);
        } else {
          const errorText = await response.text();
          console.log(`   ❌ 错误: ${response.status} - ${errorText}`);
        }
      } catch (error) {
        console.log(`   ❌ 异常: ${error.message}`);
      }
    }
    
    // 创建一个任务并测试相关端点
    console.log('\n📝 创建测试任务...');
    const taskRequest = {
      module: 'translation',
      taskName: '路由调试任务',
      instructions: '测试路由功能'
    };
    
    const createResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
      method: 'POST',
      headers: {
        'Origin': 'https://translator-agent-sandy.vercel.app',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskRequest)
    });
    
    if (createResponse.ok) {
      const createData = await createResponse.json();
      const taskId = createData.data?.taskId;
      console.log(`   ✅ 任务创建成功: ${taskId}`);
      
      // 测试任务相关端点
      const taskEndpoints = [
        { method: 'GET', path: `/api/v1/tasks/${taskId}`, description: '获取任务状态' },
        { method: 'POST', path: `/api/v1/tasks/${taskId}/process`, description: '处理任务' },
        { method: 'GET', path: `/api/v1/tasks/stats`, description: '任务统计（再次测试）' }
      ];
      
      for (const endpoint of taskEndpoints) {
        console.log(`\n🔄 测试 ${endpoint.method} ${endpoint.path} - ${endpoint.description}`);
        
        try {
          const response = await fetch(`${RAILWAY_BACKEND_URL}${endpoint.path}`, {
            method: endpoint.method,
            headers: {
              'Origin': 'https://translator-agent-sandy.vercel.app',
              'Content-Type': 'application/json'
            }
          });
          
          console.log(`   状态码: ${response.status}`);
          console.log(`   CORS头: ${response.headers.get('access-control-allow-origin')}`);
          
          if (response.ok) {
            const data = await response.json();
            console.log(`   ✅ 成功: ${JSON.stringify(data.data).substring(0, 100)}...`);
          } else {
            const errorText = await response.text();
            console.log(`   ❌ 错误: ${response.status} - ${errorText}`);
          }
        } catch (error) {
          console.log(`   ❌ 异常: ${error.message}`);
        }
      }
    } else {
      console.log('   ❌ 任务创建失败');
    }
    
  } catch (error) {
    console.error('❌ 调试失败:', error);
  }
}

debugEndpointRouting();