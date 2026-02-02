/**
 * Translator Agent 后端 API 服务
 * 提供任务管理、进度更新、文件管理、记忆层操作等核心功能
 */

const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs').promises;

// 配置环境变量
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// 中间件配置
app.set('trust proxy', 1); // 信任反向代理（Railway等）
app.use(helmet()); // 安全头
app.use(compression()); // 压缩
// 处理 CORS 来源配置
const getCorsOrigins = () => {
  const envOrigins = process.env.CORS_ORIGIN;
  const defaultOrigins = ['http://localhost:3000', 'http://127.0.0.1:3000', 'https://translator-agent-rosy.vercel.app', 'https://translator-agent-*.vercel.app'];
  
  if (envOrigins) {
    // 如果环境变量是逗号分隔的字符串，转换为数组
    let originsArray = [];
    if (typeof envOrigins === 'string') {
      originsArray = envOrigins.split(',').map(origin => origin.trim());
    } else if (Array.isArray(envOrigins)) {
      originsArray = envOrigins;
    }
    
    // 确保包含 Vercel 前端域名（如果不在列表中，自动添加）
    const vercelDomains = ['https://translator-agent-rosy.vercel.app', 'https://translator-agent-*.vercel.app'];
    const hasVercelDomain = vercelDomains.some(vercel => originsArray.includes(vercel) || 
      originsArray.some(origin => origin.includes('vercel.app')));
    
    if (!hasVercelDomain) {
      console.log('[CORS] Auto-adding Vercel domains to allowed origins');
      originsArray.push(...vercelDomains);
    }
    
    return originsArray;
  }
  
  // 默认允许本地开发和 Vercel 前端
  return defaultOrigins;
};

app.use(cors({
  origin: getCorsOrigins(),
  credentials: true
}));
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

// 速率限制
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 100, // 每个IP最多100个请求
  message: { error: '请求过于频繁，请稍后再试' }
});
app.use('/api/', limiter);

// 文件上传配置
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    try {
      await fs.access(uploadDir).catch(() => fs.mkdir(uploadDir, { recursive: true }));
      cb(null, uploadDir);
    } catch (error) {
      cb(error);
    }
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});
const upload = multer({ 
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    // 允许的文件类型
    const allowedTypes = /jpeg|jpg|png|gif|mp4|avi|mov|mp3|wav|txt|json|pdf|doc|docx/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (extname && mimetype) {
      cb(null, true);
    } else {
      cb(new Error('不支持的文件类型'));
    }
  }
});

// 内存数据库（用于演示，生产环境应使用 Redis 或 MongoDB）
const db = {
  tasks: new Map(),
  files: new Map(),
  memoryLayers: new Map(),
  stats: {
    totalTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    processingTasks: 0
  }
};

// 任务状态枚举
const TaskStatus = {
  CREATED: 'created',
  QUEUED: 'queued',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

// API 响应格式
const createResponse = (data = null, message = '成功', success = true) => ({
  success,
  message,
  data,
  timestamp: new Date().toISOString()
});

// API 错误处理
const createError = (message, code = 500, details = null) => ({
  error: message,
  code,
  details,
  timestamp: new Date().toISOString()
});

// ==================== 路由定义 ====================

// 健康检查
app.get('/api/health', (req, res) => {
  res.json(createResponse({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    dbSize: {
      tasks: db.tasks.size,
      files: db.files.size,
      memoryLayers: db.memoryLayers.size
    }
  }));
});

// 版本化健康检查（供前端使用）
app.get('/api/v1/health', (req, res) => {
  res.json(createResponse({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    dbSize: {
      tasks: db.tasks.size,
      files: db.files.size,
      memoryLayers: db.memoryLayers.size
    }
  }));
});

// ==================== 任务管理 ====================

// 创建任务
app.post('/api/v1/tasks', async (req, res) => {
  try {
    const { module, taskName, files, instructions, options = {} } = req.body;
    
    // 验证参数
    if (!module || !taskName) {
      return res.status(400).json(createError('缺少必要参数: module 和 taskName', 400));
    }

    const taskId = uuidv4();
    const task = {
      taskId,
      module,
      taskName,
      status: TaskStatus.CREATED,
      progress: 0,
      message: '任务已创建',
      files: {
        uploaded: files?.map(f => f.name) || [],
        processed: [],
        failed: []
      },
      memoryLayer: {
        conversationHistory: [],
        processingResults: [],
        intermediateData: []
      },
      instructions,
      options,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      completedAt: null,
      error: null
    };

    // 存储任务
    db.tasks.set(taskId, task);
    db.stats.totalTasks++;
    db.stats.processingTasks++;

    // 模拟异步处理
    setTimeout(() => {
      const currentTask = db.tasks.get(taskId);
      if (currentTask && currentTask.status === TaskStatus.CREATED) {
        currentTask.status = TaskStatus.QUEUED;
        currentTask.message = '任务已加入队列';
        currentTask.updatedAt = new Date().toISOString();
        db.tasks.set(taskId, currentTask);
      }
    }, 1000);

    res.status(201).json(createResponse(task, '任务创建成功'));
  } catch (error) {
    console.error('创建任务错误:', error);
    res.status(500).json(createError('创建任务失败: ' + error.message));
  }
});

// 获取任务状态
app.get('/api/v1/tasks/:taskId', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = db.tasks.get(taskId);

    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    res.json(createResponse(task, '任务状态获取成功'));
  } catch (error) {
    console.error('获取任务状态错误:', error);
    res.status(500).json(createError('获取任务状态失败: ' + error.message));
  }
});

// 更新任务状态
app.post('/api/v1/tasks/:taskId/status', async (req, res) => {
  try {
    const { taskId } = req.params;
    const { status, message } = req.body;

    const task = db.tasks.get(taskId);
    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 更新状态
    task.status = status;
    task.message = message || task.message;
    task.updatedAt = new Date().toISOString();

    // 更新统计
    if (status === TaskStatus.COMPLETED) {
      task.completedAt = new Date().toISOString();
      db.stats.completedTasks++;
      db.stats.processingTasks--;
    } else if (status === TaskStatus.FAILED) {
      db.stats.failedTasks++;
      db.stats.processingTasks--;
    }

    db.tasks.set(taskId, task);

    res.json(createResponse(task, '任务状态更新成功'));
  } catch (error) {
    console.error('更新任务状态错误:', error);
    res.status(500).json(createError('更新任务状态失败: ' + error.message));
  }
});

// 更新任务进度
app.post('/api/v1/tasks/:taskId/progress', async (req, res) => {
  try {
    const { taskId } = req.params;
    const { progress, message } = req.body;

    const task = db.tasks.get(taskId);
    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 更新进度
    task.progress = Math.max(0, Math.min(100, progress));
    if (message) task.message = message;
    task.updatedAt = new Date().toISOString();

    db.tasks.set(taskId, task);

    res.json(createResponse(task, '进度更新成功'));
  } catch (error) {
    console.error('更新进度错误:', error);
    res.status(500).json(createError('更新进度失败: ' + error.message));
  }
});

// 添加文件到任务
app.post('/api/v1/tasks/:taskId/files', async (req, res) => {
  try {
    const { taskId } = req.params;
    const { filePath, status } = req.body;

    const task = db.tasks.get(taskId);
    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 根据状态添加到相应数组
    if (status === 'uploaded') {
      task.files.uploaded.push(filePath);
    } else if (status === 'processed') {
      task.files.processed.push(filePath);
    } else if (status === 'failed') {
      task.files.failed.push(filePath);
    }

    task.updatedAt = new Date().toISOString();
    db.tasks.set(taskId, task);

    res.json(createResponse(task, '文件添加成功'));
  } catch (error) {
    console.error('添加文件错误:', error);
    res.status(500).json(createError('添加文件失败: ' + error.message));
  }
});

// 添加到记忆层
app.post('/api/v1/tasks/:taskId/memory', async (req, res) => {
  try {
    const { taskId } = req.params;
    const { type, data } = req.body;

    const task = db.tasks.get(taskId);
    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 根据类型添加到相应数组
    if (type === 'conversation') {
      task.memoryLayer.conversationHistory.push(data);
    } else if (type === 'result') {
      task.memoryLayer.processingResults.push(data);
    } else if (type === 'intermediate') {
      task.memoryLayer.intermediateData.push(data);
    }

    task.updatedAt = new Date().toISOString();
    db.tasks.set(taskId, task);

    res.json(createResponse(task, '添加到记忆层成功'));
  } catch (error) {
    console.error('添加到记忆层错误:', error);
    res.status(500).json(createError('添加到记忆层失败: ' + error.message));
  }
});

// 获取模块任务列表
app.get('/api/v1/tasks', async (req, res) => {
  try {
    const { module, status } = req.query;
    
    let tasks = Array.from(db.tasks.values());
    
    // 按模块过滤
    if (module) {
      tasks = tasks.filter(t => t.module === module);
    }
    
    // 按状态过滤
    if (status) {
      tasks = tasks.filter(t => t.status === status);
    }

    // 按创建时间排序（最新的在前）
    tasks.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

    res.json(createResponse(tasks, '任务列表获取成功'));
  } catch (error) {
    console.error('获取任务列表错误:', error);
    res.status(500).json(createError('获取任务列表失败: ' + error.message));
  }
});

// 清理旧任务
app.post('/api/v1/tasks/cleanup', async (req, res) => {
  try {
    const { maxAge = 7 * 24 * 60 * 60 * 1000 } = req.body; // 默认7天
    const now = Date.now();
    let cleanedCount = 0;

    for (const [taskId, task] of db.tasks.entries()) {
      const taskAge = now - new Date(task.createdAt).getTime();
      if (taskAge > maxAge) {
        db.tasks.delete(taskId);
        cleanedCount++;
      }
    }

    res.json(createResponse({ cleanedCount }, `清理了 ${cleanedCount} 个旧任务`));
  } catch (error) {
    console.error('清理任务错误:', error);
    res.status(500).json(createError('清理任务失败: ' + error.message));
  }
});

// 获取任务统计
app.get('/api/v1/tasks/stats', async (req, res) => {
  try {
    const { module } = req.query;
    
    let stats = { ...db.stats };
    
    // 按模块统计
    if (module) {
      const moduleTasks = Array.from(db.tasks.values()).filter(t => t.module === module);
      stats = {
        totalTasks: moduleTasks.length,
        completedTasks: moduleTasks.filter(t => t.status === TaskStatus.COMPLETED).length,
        failedTasks: moduleTasks.filter(t => t.status === TaskStatus.FAILED).length,
        processingTasks: moduleTasks.filter(t => t.status === TaskStatus.PROCESSING || t.status === TaskStatus.QUEUED).length
      };
    }

    res.json(createResponse(stats, '任务统计获取成功'));
  } catch (error) {
    console.error('获取任务统计错误:', error);
    res.status(500).json(createError('获取任务统计失败: ' + error.message));
  }
});

// ==================== 文件上传 ====================

// 上传文件
app.post('/api/v1/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json(createError('没有上传文件', 400));
    }

    const fileData = {
      fileId: uuidv4(),
      originalName: req.file.originalname,
      filename: req.file.filename,
      path: req.file.path,
      size: req.file.size,
      mimetype: req.file.mimetype,
      uploadedAt: new Date().toISOString()
    };

    db.files.set(fileData.fileId, fileData);

    res.status(201).json(createResponse(fileData, '文件上传成功'));
  } catch (error) {
    console.error('文件上传错误:', error);
    res.status(500).json(createError('文件上传失败: ' + error.message));
  }
});

// 批量上传文件
app.post('/api/v1/upload/batch', upload.array('files', 10), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json(createError('没有上传文件', 400));
    }

    const uploadedFiles = req.files.map(file => ({
      fileId: uuidv4(),
      originalName: file.originalname,
      filename: file.filename,
      path: file.path,
      size: file.size,
      mimetype: file.mimetype,
      uploadedAt: new Date().toISOString()
    }));

    uploadedFiles.forEach(file => db.files.set(file.fileId, file));

    res.status(201).json(createResponse(uploadedFiles, `成功上传 ${uploadedFiles.length} 个文件`));
  } catch (error) {
    console.error('批量上传错误:', error);
    res.status(500).json(createError('批量上传失败: ' + error.message));
  }
});

// ==================== 实时模拟处理 ====================

// 模拟任务处理（用于演示）
app.post('/api/v1/tasks/:taskId/process', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = db.tasks.get(taskId);

    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 更新为处理中状态
    task.status = TaskStatus.PROCESSING;
    task.message = '正在处理任务...';
    task.updatedAt = new Date().toISOString();
    db.tasks.set(taskId, task);

    // 模拟处理过程
    const simulateProcessing = async () => {
      for (let i = 1; i <= 10; i++) {
        await new Promise(resolve => setTimeout(resolve, 500)); // 每500ms更新一次进度
        
        const currentTask = db.tasks.get(taskId);
        if (!currentTask || currentTask.status === TaskStatus.FAILED) {
          return;
        }

        currentTask.progress = i * 10;
        currentTask.message = `处理中... ${i * 10}%`;
        currentTask.updatedAt = new Date().toISOString();
        db.tasks.set(taskId, currentTask);
      }

      // 处理完成
      const finalTask = db.tasks.get(taskId);
      if (finalTask) {
        finalTask.status = TaskStatus.COMPLETED;
        finalTask.progress = 100;
        finalTask.message = '任务处理完成';
        finalTask.completedAt = new Date().toISOString();
        finalTask.updatedAt = new Date().toISOString();
        
        // 添加处理结果到记忆层
        finalTask.memoryLayer.processingResults.push({
          timestamp: new Date().toISOString(),
          result: '处理成功',
          details: '所有文件已成功处理'
        });

        db.tasks.set(taskId, finalTask);
        db.stats.completedTasks++;
        db.stats.processingTasks--;
      }
    };

    // 异步执行处理
    simulateProcessing().catch(error => {
      console.error('处理任务错误:', error);
      const failedTask = db.tasks.get(taskId);
      if (failedTask) {
        failedTask.status = TaskStatus.FAILED;
        failedTask.message = '处理失败: ' + error.message;
        failedTask.error = error.message;
        failedTask.updatedAt = new Date().toISOString();
        db.tasks.set(taskId, failedTask);
        db.stats.failedTasks++;
        db.stats.processingTasks--;
      }
    });

    res.json(createResponse(task, '任务开始处理'));
  } catch (error) {
    console.error('启动处理错误:', error);
    res.status(500).json(createError('启动处理失败: ' + error.message));
  }
});

// ==================== 系统信息 ====================

// 获取系统信息
app.get('/api/v1/system/info', async (req, res) => {
  try {
    const info = {
      version: '1.0.0',
      name: 'Translator Agent Backend API',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      nodeVersion: process.version,
      platform: process.platform,
      arch: process.arch,
      timestamp: new Date().toISOString()
    };

    res.json(createResponse(info, '系统信息获取成功'));
  } catch (error) {
    console.error('获取系统信息错误:', error);
    res.status(500).json(createError('获取系统信息失败: ' + error.message));
  }
});

// ==================== 根路径重定向 ====================

// 根路径重定向到API健康检查
app.get('/', (req, res) => {
  res.redirect('/api/health');
});

// ==================== 错误处理中间件 ====================

// 404 处理
app.use((req, res) => {
  res.status(404).json(createError('API 端点不存在', 404));
});

// 全局错误处理
app.use((error, req, res, next) => {
  console.error('全局错误:', error);
  
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json(createError('文件大小超过限制 (10MB)', 400));
    }
    if (error.code === 'LIMIT_FILE_COUNT') {
      return res.status(400).json(createError('文件数量超过限制', 400));
    }
  }

  res.status(500).json(createError('服务器内部错误: ' + error.message));
});

// ==================== 启动服务器 ====================

// 导出 app 用于测试和启动
module.exports = app;