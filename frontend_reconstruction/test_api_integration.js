bushi// 简单的API集成测试脚本
const API_BASE_URL = 'https://translatoragent-production.up.railway.app';

console.log('开始API集成测试...');
console.log('API Base URL:', API_BASE_URL);

// 测试任务创建
async function testTaskCreation() {
  try {
    console.log('\n=== 测试任务创建 ===');
    const response = await fetch(`${API_BASE_URL}/api/v1/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title: 'API测试任务',
        description: '用于测试API集成的任务',
        type: 'translation',
        priority: 'normal'
      })
    });
    
    console.log('响应状态:', response.status);
    const data = await response.json();
    console.log('响应数据:', data);
    
    if (response.ok && data.data && data.data.id) {
      console.log('✅ 任务创建成功');
      return data.data.id;
    } else {
      console.log('❌ 任务创建失败');
      return null;
    }
  } catch (error) {
    console.error('❌ 任务创建错误:', error);
    return null;
  }
}

// 测试任务处理
async function testTaskProcessing(taskId) {
  if (!taskId) {
    console.log('❌ 跳过任务处理测试，没有任务ID');
    return;
  }
  
  try {
    console.log('\n=== 测试任务处理 ===');
    console.log('任务ID:', taskId);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({})
    });
    
    console.log('响应状态:', response.status);
    const data = await response.json();
    console.log('响应数据:', data);
    
    if (response.ok) {
      console.log('✅ 任务处理请求成功');
    } else {
      console.log('❌ 任务处理失败');
    }
  } catch (error) {
    console.error('❌ 任务处理错误:', error);
  }
}

// 测试CORS
async function testCORS() {
  try {
    console.log('\n=== 测试CORS ===');
    
    const response = await fetch(`${API_BASE_URL}/api/v1/tasks`, {
      method: 'OPTIONS',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
      }
    });
    
    console.log('CORS 预检请求状态:', response.status);
    const corsHeaders = {
      'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
      'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
      'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
      'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
    };
    console.log('CORS 响应头:', corsHeaders);
    
    if (response.ok && corsHeaders['Access-Control-Allow-Origin']) {
      console.log('✅ CORS配置正确');
    } else {
      console.log('❌ CORS配置有问题');
    }
  } catch (error) {
    console.error('❌ CORS测试错误:', error);
  }
}

// 运行所有测试
async function runTests() {
  await testCORS();
  const taskId = await testTaskCreation();
  await testTaskProcessing(taskId);
  console.log('\n=== 测试完成 ===');
}

runTests();