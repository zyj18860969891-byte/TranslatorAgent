// 测试API客户端processTask方法
import { APIClient } from './src/utils/apiClient';

const apiClient = new APIClient('https://translatoragent-production.up.railway.app');

// 测试processTask方法
async function testProcessTask() {
  const taskId = 'd564a950-06cb-4810-a686-0f34579dd3e0';
  
  console.log(`Testing processTask for task ${taskId}`);
  console.log('Sending POST request to /tasks/${taskId}/process');
  
  try {
    const response = await apiClient.processTask(taskId);
    console.log('Response:', response);
  } catch (error) {
    console.error('Error:', error);
  }
}

testProcessTask();