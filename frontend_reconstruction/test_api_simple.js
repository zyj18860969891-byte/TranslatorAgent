#!/usr/bin/env node

/**
 * 简单API测试脚本
 * 直接使用fetch API测试后端连接
 */

const API_BASE_URL = 'http://localhost:8000';

console.log('🚀 开始简单API测试...');
console.log('📡 API基础URL:', API_BASE_URL);

console.log('\n=====================================');
console.log('🧪 简单API集成测试');
console.log('=====================================');

async function runTests() {
  try {
    // 测试1: 健康检查
    console.log('\n🏥 测试健康检查...');
    try {
      const healthResponse = await fetch(`${API_BASE_URL}/api/health`);
      console.log('🔄 GET /api/health');
      console.log('   状态码:', healthResponse.status);
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        console.log('   ✅ 成功:', healthData.data?.status || '正常');
      } else {
        const errorText = await healthResponse.text();
        console.log('   ❌ 错误:', healthResponse.status, errorText);
      }
    } catch (error) {
      console.log('❌ 健康检查失败:', error.message);
    }

    // 测试2: 创建任务
    console.log('\n📝 测试任务创建...');
    try {
      const taskRequest = {
        module: 'translation',
        taskName: '简单API测试任务',
        instructions: '测试API连接',
        options: { test: true }
      };
      
      const createResponse = await fetch(`${API_BASE_URL}/api/v1/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskRequest)
      });
      
      console.log('🔄 POST /api/v1/tasks');
      console.log('   状态码:', createResponse.status);
      if (createResponse.ok) {
        const createData = await createResponse.json();
        console.log('   ✅ 成功: 任务创建成功');
        const taskId = createData.data?.taskId;
        console.log('   ✅ 任务ID:', taskId);
        
        // 测试3: 获取任务状态
        console.log('\n📊 测试任务状态...');
        try {
          const statusResponse = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}`);
          console.log('🔄 GET /api/v1/tasks/' + taskId);
          console.log('   状态码:', statusResponse.status);
          if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            console.log('   ✅ 成功: 任务状态获取成功');
            console.log('   📋 任务状态:', statusData.data?.status);
            console.log('   📋 任务进度:', statusData.data?.progress);
          } else {
            const errorText = await statusResponse.text();
            console.log('   ❌ 错误:', statusResponse.status, errorText);
          }
        } catch (error) {
          console.log('❌ 任务状态获取失败:', error.message);
        }
        
        // 测试4: 处理任务
        console.log('\n⚙️ 测试任务处理...');
        try {
          const processResponse = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}/process`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          console.log('🔄 POST /api/v1/tasks/' + taskId + '/process');
          console.log('   状态码:', processResponse.status);
          if (processResponse.ok) {
            const processData = await processResponse.json();
            console.log('   ✅ 成功: 任务开始处理');
            console.log('   📋 消息:', processData.message);
          } else {
            const errorText = await processResponse.text();
            console.log('   ❌ 错误:', processResponse.status, errorText);
          }
        } catch (error) {
          console.log('❌ 任务处理失败:', error.message);
        }
        
        // 测试5: 获取任务列表
        console.log('\n📋 测试任务列表...');
        try {
          const listResponse = await fetch(`${API_BASE_URL}/api/v1/tasks`);
          console.log('🔄 GET /api/v1/tasks');
          console.log('   状态码:', listResponse.status);
          if (listResponse.ok) {
            const listData = await listResponse.json();
            console.log('   ✅ 成功: 任务列表获取成功');
            console.log('   📋 任务数量:', listData.data?.length || 0);
          } else {
            const errorText = await listResponse.text();
            console.log('   ❌ 错误:', listResponse.status, errorText);
          }
        } catch (error) {
          console.log('❌ 任务列表获取失败:', error.message);
        }
        
      } else {
        const errorText = await createResponse.text();
        console.log('   ❌ 错误:', createResponse.status, errorText);
      }
    } catch (error) {
      console.log('❌ 任务创建失败:', error.message);
    }

    console.log('\n=====================================');
    console.log('🎉 简单API测试完成');
    console.log('=====================================');
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error);
  }
}

// 运行测试
runTests();