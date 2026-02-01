// TranslatorAgent 主入口文件
// 这个文件帮助Railway正确识别项目为Node.js项目

// 导入后端服务器
const app = require('./backend_api/server.js');

// 启动服务器
const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  console.log(`TranslatorAgent Backend API running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`API Documentation: http://localhost:${PORT}/api/docs`);
});

// 导出app供测试使用
module.exports = app;