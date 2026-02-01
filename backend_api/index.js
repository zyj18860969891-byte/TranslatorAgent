// Railway Node.js项目入口文件
// 这个文件帮助Railway正确识别项目为Node.js项目

// 导入主服务器
const app = require('./server.js');

// 启动服务器
const PORT = process.env.PORT || 8000;

app.listen(PORT, () => {
  console.log(`TranslatorAgent Backend API running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});

// 导出app供测试使用
module.exports = app;