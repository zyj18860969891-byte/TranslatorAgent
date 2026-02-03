// API 集成测试脚本
// 用于验证前端和后端的API集成是否正常工作

// 使用内置的fetch API

// 配置
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

console.log(`🚀 开始API集成测试...`);
console.log(`📡 API基础URL: ${API_BASE_URL}`);
console.log(`📋 API版本: ${API_VERSION}`);
console.log('');

// 测试函数
async function testApiCall(endpoint, method = 'GET', data = null) {
  const url = `${API_BASE_URL}/api/${API_VERSION}${endpoint}`;
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    console.log(`🔄 ${method} ${endpoint}`);
    const response = await fetch(url, options);
    const result = await response.json();
    
    console.log(`   状态码: ${response.status}`);
    if (result.success) {
      console.log(`   ✅ 成功: ${result.message || '请求成功'}`);
    } else {
      console.log(`   ❌ 失败: ${result.error || '未知错误'}`);
    }
    console.log('');
    
    return {
      success: response.ok && result.success,
      status: response.status,
      data: result
    };
  } catch (error) {
    console.log(`   ❌ 错误: ${error.message}`);
    console.log('');
    return {
      success: false,
      error: error.message
    };
  }
}

// 测试健康检查
async function testHealthCheck() {
  console.log('🏥 测试健康检查...');
  return await testApiCall('/health');
}

// 测试任务创建
async function testTaskCreation() {
  console.log('📝 测试任务创建...');
  const taskData = {
    module: 'translation',
    taskName: 'API集成测试任务',
    instructions: '这是一个API集成测试任务',
    options: {
      test: true
    }
  };
  return await testApiCall('/tasks', 'POST', taskData);
}

// 测试任务处理
async function testTaskProcessing(taskId) {
  console.log(`⚙️ 测试任务处理 (任务ID: ${taskId})...`);
  return await testApiCall(`/tasks/${taskId}/process`, 'POST', {});
}

// 测试任务状态
async function testTaskStatus(taskId) {
  console.log(`📊 测试任务状态 (任务ID: ${taskId})...`);
  return await testApiCall(`/tasks/${taskId}`);
}

// 测试任务列表
async function testTaskList() {
  console.log('📋 测试任务列表...');
  return await testApiCall('/tasks');
}

// 主测试函数
async function runTests() {
  console.log('=====================================');
  console.log('🧪 Translator Agent API 集成测试');
  console.log('=====================================');
  console.log('');

  // 测试1: 健康检查
  const healthResult = await testHealthCheck();
  if (!healthResult.success) {
    console.log('❌ 健康检查失败，停止测试');
    return;
  }

  // 测试2: 创建任务
  const taskResult = await testTaskCreation();
  if (!taskResult.success || !taskResult.data.data) {
    console.log('❌ 任务创建失败，停止测试');
    return;
  }

  const taskId = taskResult.data.data.taskId;
  console.log(`✅ 任务创建成功，任务ID: ${taskId}`);

  // 测试3: 任务状态
  await testTaskStatus(taskId);

  // 测试4: 任务处理
  const processResult = await testTaskProcessing(taskId);
  if (processResult.success) {
    console.log('✅ 任务处理请求成功');
    
    // 等待一段时间让任务处理完成
    console.log('⏳ 等待任务处理完成...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 测试5: 任务状态（处理中）
    await testTaskStatus(taskId);
    
    // 再等待一段时间
    console.log('⏳ 等待任务处理完成...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // 测试6: 任务状态（完成）
    await testTaskStatus(taskId);
  } else {
    console.log('❌ 任务处理失败');
  }

  // 测试7: 任务列表
  await testTaskList();

  console.log('=====================================');
  console.log('🎉 API集成测试完成');
  console.log('=====================================');
}

// 运行测试
runTests().catch(error => {
  console.error('❌ 测试运行失败:', error);
  process.exit(1);
});