#!/usr/bin/env node

/**
 * 前端API客户端测试脚本
 * 测试前端API客户端是否能正确连接到后端服务
 */

import { apiClient, checkApiHealth } from './src/utils/apiClient.js';

console.log('🚀 开始前端API客户端测试...');
console.log('📡 API基础URL:', apiClient.baseURL);
console.log('📋 API版本:', 'v1');

console.log('\n=====================================');
console.log('🧪 前端API客户端集成测试');
console.log('=====================================');

async function runTests() {
  try {
    // 测试1: 健康检查
    console.log('\n🏥 测试健康检查...');
    try {
      const healthResponse = await apiClient.healthCheck();
      console.log('🔄 GET /health');
      console.log('   状态:', healthResponse.success ? '✅ 成功' : '❌ 失败');
      if (healthResponse.success) {
        console.log('   ✅ 成功:', healthResponse.data?.status || '正常');
      } else {
        console.log('   ❌ 错误:', healthResponse.error);
      }
    } catch (error) {
      console.log('❌ 健康检查失败:', error.message);
    }

    // 测试2: 创建任务
    console.log('\n📝 测试任务创建...');
    try {
      const taskRequest = {
        module: 'translation',
        taskName: '前端API测试任务',
        instructions: '测试前端API客户端与后端的连接',
        options: { test: true }
      };
      
      const createResponse = await apiClient.createTask(taskRequest);
      console.log('🔄 POST /tasks');
      console.log('   状态:', createResponse.success ? '✅ 成功' : '❌ 失败');
      if (createResponse.success) {
        console.log('   ✅ 成功: 任务创建成功');
        const taskId = createResponse.data?.taskId || createResponse.data?.id;
        console.log('   ✅ 任务ID:', taskId);
        
        // 测试3: 获取任务状态
        console.log('\n📊 测试任务状态...');
        try {
          const statusResponse = await apiClient.getTaskStatus(taskId);
          console.log('🔄 GET /tasks/' + taskId);
          console.log('   状态:', statusResponse.success ? '✅ 成功' : '❌ 失败');
          if (statusResponse.success) {
            console.log('   ✅ 成功: 任务状态获取成功');
            console.log('   📋 任务状态:', statusResponse.data?.status);
            console.log('   📋 任务进度:', statusResponse.data?.progress);
          } else {
            console.log('   ❌ 错误:', statusResponse.error);
          }
        } catch (error) {
          console.log('❌ 任务状态获取失败:', error.message);
        }
        
        // 测试4: 处理任务
        console.log('\n⚙️ 测试任务处理...');
        try {
          const processResponse = await apiClient.processTask(taskId);
          console.log('🔄 POST /tasks/' + taskId + '/process');
          console.log('   状态:', processResponse.success ? '✅ 成功' : '❌ 失败');
          if (processResponse.success) {
            console.log('   ✅ 成功: 任务开始处理');
          } else {
            console.log('   ❌ 错误:', processResponse.error);
          }
        } catch (error) {
          console.log('❌ 任务处理失败:', error.message);
        }
        
        // 测试5: 获取任务列表
        console.log('\n📋 测试任务列表...');
        try {
          const listResponse = await apiClient.getModuleTasks('translation');
          console.log('🔄 GET /tasks');
          console.log('   状态:', listResponse.success ? '✅ 成功' : '❌ 失败');
          if (listResponse.success) {
            console.log('   ✅ 成功: 任务列表获取成功');
            console.log('   📋 任务数量:', listResponse.data?.length || 0);
          } else {
            console.log('   ❌ 错误:', listResponse.error);
          }
        } catch (error) {
          console.log('❌ 任务列表获取失败:', error.message);
        }
        
      } else {
        console.log('   ❌ 错误:', createResponse.error);
      }
    } catch (error) {
      console.log('❌ 任务创建失败:', error.message);
    }

    console.log('\n=====================================');
    console.log('🎉 前端API客户端测试完成');
    console.log('=====================================');
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error);
  }
}

// 运行测试
runTests();