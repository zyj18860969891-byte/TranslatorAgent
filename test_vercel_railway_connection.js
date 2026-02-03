#!/usr/bin/env node

/**
 * Vercel前端到Railway后端连接测试
 * 模拟Vercel前端发起的跨域请求
 */

const VERCEL_FRONTEND_URL = 'https://translator-agent-sandy.vercel.app';
const RAILWAY_BACKEND_URL = 'http://localhost:8000';

console.log('🚀 开始Vercel到Railway连接测试...');
console.log('🌐 Vercel前端URL:', VERCEL_FRONTEND_URL);
console.log('🚂 Railway后端URL:', RAILWAY_BACKEND_URL);

console.log('\n=====================================');
console.log('🧪 Vercel前端到Railway后端连接测试');
console.log('=====================================');

async function runTests() {
  try {
    // 测试1: 健康检查（跨域）
    console.log('\n🏥 测试健康检查（跨域请求）...');
    try {
      const healthResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/health`, {
        method: 'GET',
        headers: {
          'Origin': VERCEL_FRONTEND_URL,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('🔄 GET /api/health');
      console.log('   状态码:', healthResponse.status);
      console.log('   CORS头 - Access-Control-Allow-Origin:', healthResponse.headers.get('access-control-allow-origin'));
      
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

    // 测试2: 创建任务（跨域）
    console.log('\n📝 测试任务创建（跨域请求）...');
    try {
      const taskRequest = {
        module: 'translation',
        taskName: 'Vercel跨域测试任务',
        instructions: '测试Vercel前端到Railway后端的跨域连接',
        options: { test: true, source: 'vercel' }
      };
      
      const createResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
        method: 'POST',
        headers: {
          'Origin': VERCEL_FRONTEND_URL,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(taskRequest)
      });
      
      console.log('🔄 POST /api/v1/tasks');
      console.log('   状态码:', createResponse.status);
      console.log('   CORS头 - Access-Control-Allow-Origin:', createResponse.headers.get('access-control-allow-origin'));
      console.log('   CORS头 - Access-Control-Allow-Credentials:', createResponse.headers.get('access-control-allow-credentials'));
      
      if (createResponse.ok) {
        const createData = await createResponse.json();
        console.log('   ✅ 成功: 任务创建成功');
        const taskId = createData.data?.taskId;
        console.log('   ✅ 任务ID:', taskId);
        
        // 测试3: 获取任务状态（跨域）
        console.log('\n📊 测试任务状态（跨域请求）...');
        try {
          const statusResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/${taskId}`, {
            method: 'GET',
            headers: {
              'Origin': VERCEL_FRONTEND_URL,
              'Content-Type': 'application/json'
            }
          });
          
          console.log('🔄 GET /api/v1/tasks/' + taskId);
          console.log('   状态码:', statusResponse.status);
          console.log('   CORS头 - Access-Control-Allow-Origin:', statusResponse.headers.get('access-control-allow-origin'));
          
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
        
        // 测试4: 处理任务（跨域）
        console.log('\n⚙️ 测试任务处理（跨域请求）...');
        try {
          const processResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks/${taskId}/process`, {
            method: 'POST',
            headers: {
              'Origin': VERCEL_FRONTEND_URL,
              'Content-Type': 'application/json'
            }
          });
          
          console.log('🔄 POST /api/v1/tasks/' + taskId + '/process');
          console.log('   状态码:', processResponse.status);
          console.log('   CORS头 - Access-Control-Allow-Origin:', processResponse.headers.get('access-control-allow-origin'));
          
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
        
        // 测试5: 获取任务列表（跨域）
        console.log('\n📋 测试任务列表（跨域请求）...');
        try {
          const listResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
            method: 'GET',
            headers: {
              'Origin': VERCEL_FRONTEND_URL,
              'Content-Type': 'application/json'
            }
          });
          
          console.log('🔄 GET /api/v1/tasks');
          console.log('   状态码:', listResponse.status);
          console.log('   CORS头 - Access-Control-Allow-Origin:', listResponse.headers.get('access-control-allow-origin'));
          
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

    // 测试6: 预检请求测试
    console.log('\n🔍 测试预检请求...');
    try {
      const optionsResponse = await fetch(`${RAILWAY_BACKEND_URL}/api/v1/tasks`, {
        method: 'OPTIONS',
        headers: {
          'Origin': VERCEL_FRONTEND_URL,
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type, Origin'
        }
      });
      
      console.log('🔄 OPTIONS /api/v1/tasks (预检请求)');
      console.log('   状态码:', optionsResponse.status);
      console.log('   CORS头 - Access-Control-Allow-Origin:', optionsResponse.headers.get('access-control-allow-origin'));
      console.log('   CORS头 - Access-Control-Allow-Methods:', optionsResponse.headers.get('access-control-allow-methods'));
      console.log('   CORS头 - Access-Control-Allow-Headers:', optionsResponse.headers.get('access-control-allow-headers'));
      
      if (optionsResponse.ok) {
        console.log('   ✅ 成功: 预检请求处理成功');
      } else {
        console.log('   ❌ 错误:', optionsResponse.status);
      }
    } catch (error) {
      console.log('❌ 预检请求测试失败:', error.message);
    }

    console.log('\n=====================================');
    console.log('🎉 Vercel到Railway连接测试完成');
    console.log('=====================================');
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error);
  }
}

// 运行测试
runTests();