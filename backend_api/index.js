// Railway Node.js项目入口文件
// 这个文件帮助Railway正确识别项目为Node.js项目

// 导入主服务器
const app = require('./server.js');

// 启动服务器
const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('🚀 Translator Agent 后端 API 服务启动成功');
  console.log('='.repeat(60));
  console.log(`📍 服务地址: http://localhost:${PORT}`);
  console.log(`📊 API 文档: http://localhost:${PORT}/api/health`);
  console.log(`⏱️  启动时间: ${new Date().toLocaleString('zh-CN')}`);
  console.log('='.repeat(60));
  console.log('可用端点:');
  console.log('  GET  /api/health - 健康检查');
  console.log('  POST /api/v1/tasks - 创建任务');
  console.log('  GET  /api/v1/tasks/:taskId - 获取任务状态');
  console.log('  POST /api/v1/tasks/:taskId/status - 更新任务状态');
  console.log('  POST /api/v1/tasks/:taskId/progress - 更新进度');
  console.log('  POST /api/v1/tasks/:taskId/files - 添加文件');
  console.log('  POST /api/v1/tasks/:taskId/memory - 添加到记忆层');
  console.log('  GET  /api/v1/tasks - 获取任务列表');
  console.log('  POST /api/v1/tasks/cleanup - 清理旧任务');
  console.log('  GET  /api/v1/tasks/stats - 获取任务统计');
  console.log('  POST /api/v1/upload - 上传文件');
  console.log('  POST /api/v1/upload/batch - 批量上传文件');
  console.log('  POST /api/v1/tasks/:taskId/process - 模拟任务处理');
  console.log('  GET  /api/v1/system/info - 系统信息');
  console.log('='.repeat(60));
});

// 导出app供测试使用
module.exports = app;