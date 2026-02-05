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

// CORS 中间件必须放在最前面，确保预检请求正确处理
const corsOptions = {
  origin: function(origin, callback) {
    // 允许没有origin的请求（如移动端应用、Postman等）
    if (!origin) return callback(null, true);
    
    // 允许的源列表 - 包括所有Vercel子域名
    const allowedOrigins = [
      'http://localhost:3000',
      'http://127.0.0.1:3000',
      'https://translator-agent-*.vercel.app'
    ];
    
    // 检查是否匹配
    const isAllowed = allowedOrigins.some(allowed => {
      if (allowed.includes('*')) {
        // 通配符匹配
        const pattern = '^' + allowed.replace(/\*/g, '.*') + '$';
        return new RegExp(pattern).test(origin);
      }
      return origin === allowed;
    });
    
    console.log(`[CORS] ${origin} -> ${isAllowed ? '✅ 允许' : '❌ 拒绝'}`);
    callback(null, isAllowed);
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
  exposedHeaders: ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'],
  maxAge: 86400 // 预检请求缓存时间（24小时）
};

app.use(cors(corsOptions));

// 处理OPTIONS预检请求
app.options('*', cors(corsOptions));

app.use(helmet()); // 安全头
app.use(compression()); // 压缩
// 处理 CORS 来源配置
const getCorsOrigins = () => {
  const envOrigins = process.env.CORS_ORIGIN;
  // 正则表达式匹配所有translator-agent Vercel子域名
  const vercelDomainPattern = /^https:\/\/translator-agent-.*\.vercel\.app$/;
  
  // 总是包含Vercel域名，确保前端可以访问
  const defaultOrigins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    vercelDomainPattern
  ];
  
  if (envOrigins) {
    let originsArray = [];
    if (typeof envOrigins === 'string') {
      originsArray = envOrigins.split(',').map(origin => origin.trim());
    } else if (Array.isArray(envOrigins)) {
      originsArray = envOrigins;
    }
    
    // 合并环境变量中的origins和默认origins
    return [...originsArray, ...defaultOrigins];
  }
  
  return defaultOrigins;
};

// 简化的CORS中间件 - 允许所有Vercel子域名和本地开发
const corsOptions = {
  origin: function(origin, callback) {
    // 允许没有origin的请求（如移动端应用、Postman等）
    if (!origin) return callback(null, true);
    
    // 允许的源列表
    const allowedOrigins = [
      'http://localhost:3000',
      'http://127.0.0.1:3000',
      'https://translator-agent-*.vercel.app'
    ];
    
    // 检查是否匹配
    const isAllowed = allowedOrigins.some(allowed => {
      if (allowed.includes('*')) {
        // 通配符匹配
        const pattern = '^' + allowed.replace(/\*/g, '.*') + '$';
        return new RegExp(pattern).test(origin);
      }
      return origin === allowed;
    });
    
    console.log(`[CORS] ${origin} -> ${isAllowed ? '✅ 允许' : '❌ 拒绝'}`);
    callback(null, isAllowed);
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
  exposedHeaders: ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset']
};

app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));

// 获取任务统计（移到速率限制器之前）
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

// 速率限制（针对不同端点使用不同限制）
const generalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1分钟窗口
  max: 300, // 每个IP最多300个请求/分钟
  message: { error: '请求过于频繁，请稍后再试' }
});

// 任务状态轮询使用更宽松的限制
const pollingLimiter = rateLimit({
  windowMs: 60 * 1000, // 1分钟窗口
  max: 120, // 每个IP最多120次轮询/分钟（每0.5秒一次）
  message: { error: '请求过于频繁，请稍后再试' }
});

// 应用速率限制（对轮询端点使用更宽松的限制）
app.use('/api/v1/tasks/:taskId', pollingLimiter); // 具体任务相关端点
app.use('/api/v1/tasks', pollingLimiter); // 任务列表端点（不包含stats）
app.use('/api/upload', generalLimiter); // 上传端点
app.use('/api/translation', generalLimiter); // 翻译端点
app.use('/api/video', generalLimiter); // 视频端点
app.use('/api/subtitle', generalLimiter); // 字幕端点

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
  limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024 * 1024 }, // 默认10GB，可通过环境变量配置
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
      
      // 将上传的文件移动到已处理数组
      if (task.files.uploaded.length > 0) {
        task.files.processed = [...task.files.uploaded];
        task.files.uploaded = [];
        
        // 添加处理结果到记忆层
        task.memoryLayer.processingResults.push({
          timestamp: new Date().toISOString(),
          result: '处理成功',
          details: `成功处理 ${task.files.processed.length} 个文件`,
          processedFiles: task.files.processed
        });
      }
      
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

// ==================== 实时处理（调用Python服务） ====================

// Python处理服务配置
const PYTHON_PROCESSING_SERVICE = process.env.PYTHON_PROCESSING_SERVICE || 'http://localhost:8001';

// 调用Python处理服务
async function callPythonProcessingService(endpoint, data) {
  try {
    const response = await fetch(`${PYTHON_PROCESSING_SERVICE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Python服务响应错误: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('调用Python处理服务失败:', error);
    throw error;
  }
}

// 任务处理（调用Python服务）
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

    // 准备传递给Python服务的数据
    const processingData = {
      taskId: taskId,
      type: task.type || 'video-translate',
      module: task.module || 'video-translate',
      title: task.title,
      description: task.description,
      files: task.files.uploaded,
      options: task.options || {}
    };

    // 调用Python处理服务
    callPythonProcessingService('/api/v1/process/tasks/' + taskId, processingData)
      .then(async (result) => {
        // 处理成功，更新任务状态
        const updatedTask = db.tasks.get(taskId);
        if (updatedTask) {
          updatedTask.status = TaskStatus.COMPLETED;
          updatedTask.progress = 100;
          updatedTask.message = '任务处理完成';
          updatedTask.completedAt = new Date().toISOString();
          updatedTask.updatedAt = new Date().toISOString();
          
          // 将上传的文件移动到已处理数组
          if (updatedTask.files.uploaded.length > 0) {
            updatedTask.files.processed = [...updatedTask.files.uploaded];
            updatedTask.files.uploaded = [];
          }
          
          // 添加处理结果到记忆层
          if (result.data && result.data.result) {
            updatedTask.memoryLayer.processingResults.push({
              timestamp: new Date().toISOString(),
              result: '处理成功',
              details: `成功处理 ${updatedTask.files.processed.length} 个文件`,
              processedFiles: updatedTask.files.processed,
              modelResult: result.data.result
            });
          }
          
          db.tasks.set(taskId, updatedTask);
          db.stats.completedTasks++;
          db.stats.processingTasks--;
          
          console.log(`任务处理完成: ${taskId}`);
        }
      })
      .catch(async (error) => {
        // 处理失败，更新任务状态
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

// ==================== 翻译处理 ====================

// 文本翻译（调用Python服务）
app.post('/api/v1/translation/translate', async (req, res) => {
  try {
    const { text, targetLanguage, sourceLanguage = 'auto' } = req.body;
    
    if (!text || !targetLanguage) {
      return res.status(400).json(createError('缺少必要参数: text 和 targetLanguage', 400));
    }
    
    // 调用Python处理服务进行翻译
    const translateData = {
      text,
      targetLanguage,
      sourceLanguage
    };
    
    const result = await callPythonProcessingService('/api/v1/process/translate', translateData);
    
    res.json(createResponse({
      originalText: text,
      translatedText: result.data?.translatedText || result.data?.result || `[${targetLanguage}] ${text}`,
      sourceLanguage: sourceLanguage,
      targetLanguage: targetLanguage,
      timestamp: new Date().toISOString(),
      modelUsed: 'qwen3'
    }, '翻译完成'));
  } catch (error) {
    console.error('翻译错误:', error);
    res.status(500).json(createError('翻译失败: ' + error.message));
  }
});

// ==================== 视频处理 ====================

// 视频处理（调用Python服务）
app.post('/api/v1/video/process', async (req, res) => {
  try {
    const { videoUrl, operation, targetLanguage, options = {} } = req.body;
    
    if (!videoUrl || !operation) {
      return res.status(400).json(createError('缺少必要参数: videoUrl 和 operation', 400));
    }
    
    // 调用Python处理服务进行视频处理
    const videoData = {
      video_url: videoUrl,
      operation,
      targetLanguage,
      options
    };
    
    const result = await callPythonProcessingService('/api/v1/process/video', videoData);
    
    res.json(createResponse({
      jobId: result.data?.jobId || uuidv4(),
      status: 'completed',
      progress: 100,
      resultUrl: result.data?.resultUrl || videoUrl.replace(/\.[^/.]+$/, '_processed.mp4'),
      estimatedTime: 0,
      operation,
      targetLanguage,
      timestamp: new Date().toISOString(),
      modelUsed: 'qwen3-omni-flash'
    }, '视频处理完成'));
  } catch (error) {
    console.error('视频处理错误:', error);
    res.status(500).json(createError('视频处理失败: ' + error.message));
  }
});

// ==================== 字幕处理 ====================

// 字幕处理（调用Python服务）
app.post('/api/v1/subtitle/process', async (req, res) => {
  try {
    const { subtitleUrl, operation, targetLanguage, options = {} } = req.body;
    
    if (!subtitleUrl || !operation) {
      return res.status(400).json(createError('缺少必要参数: subtitleUrl 和 operation', 400));
    }
    
    // 调用Python处理服务进行字幕处理
    const subtitleData = {
      subtitle_url: subtitleUrl,
      operation,
      targetLanguage,
      options
    };
    
    const result = await callPythonProcessingService('/api/v1/process/subtitle', subtitleData);
    
    res.json(createResponse({
      jobId: result.data?.jobId || uuidv4(),
      status: 'completed',
      progress: 100,
      resultUrl: result.data?.resultUrl || subtitleUrl.replace(/\.[^/.]+$/, '_processed.srt'),
      operation,
      targetLanguage,
      timestamp: new Date().toISOString(),
      modelUsed: 'qwen3-vl-rerank'
    }, '字幕处理完成'));
  } catch (error) {
    console.error('字幕处理错误:', error);
    res.status(500).json(createError('字幕处理失败: ' + error.message));
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

// ==================== 任务管理扩展 ====================

// 取消任务
app.post('/api/v1/tasks/:taskId/cancel', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = db.tasks.get(taskId);

    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    if (task.status === 'completed' || task.status === 'failed') {
      return res.status(400).json(createError('任务已完成或失败，无法取消', 400));
    }

    task.status = TaskStatus.FAILED;
    task.message = '任务已取消';
    task.error = '用户取消任务';
    task.updatedAt = new Date().toISOString();
    db.tasks.set(taskId, task);
    db.stats.failedTasks++;
    db.stats.processingTasks--;

    res.json(createResponse(task, '任务已取消'));
  } catch (error) {
    console.error('取消任务错误:', error);
    res.status(500).json(createError('取消任务失败: ' + error.message));
  }
});

// 删除任务
app.delete('/api/v1/tasks/:taskId', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = db.tasks.get(taskId);

    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 删除任务及相关数据
    db.tasks.delete(taskId);
    
    // 清理相关的文件记录
    for (const [fileId, file] of db.files.entries()) {
      if (file.taskId === taskId) {
        db.files.delete(fileId);
      }
    }

    res.json(createResponse(null, '任务删除成功'));
  } catch (error) {
    console.error('删除任务错误:', error);
    res.status(500).json(createError('删除任务失败: ' + error.message));
  }
});

// 获取所有任务（包含所有模块）
app.get('/api/v1/tasks/all', async (req, res) => {
  try {
    const allTasks = Array.from(db.tasks.values());
    res.json(createResponse(allTasks, '所有任务获取成功'));
  } catch (error) {
    console.error('获取所有任务错误:', error);
    res.status(500).json(createError('获取所有任务失败: ' + error.message));
  }
});

// 获取任务文件列表
app.get('/api/v1/tasks/:taskId/files', async (req, res) => {
  try {
    const { taskId } = req.params;
    const task = db.tasks.get(taskId);

    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 收集任务的所有文件信息
    const taskFiles = [];
    for (const fileId of task.files.uploaded) {
      const file = db.files.get(fileId);
      if (file) {
        taskFiles.push({
          fileId: file.fileId,
          name: file.originalName,
          type: file.mimetype,
          size: file.size,
          url: `/api/v1/tasks/${taskId}/files/${encodeURIComponent(file.originalName)}`,
          uploadedAt: file.uploadedAt
        });
      }
    }

    res.json(createResponse(taskFiles, '任务文件列表获取成功'));
  } catch (error) {
    console.error('获取任务文件错误:', error);
    res.status(500).json(createError('获取任务文件失败: ' + error.message));
  }
});

// 下载任务文件
app.get('/api/v1/tasks/:taskId/files/:fileName', async (req, res) => {
  try {
    const { taskId, fileName } = req.params;
    const task = db.tasks.get(taskId);

    if (!task) {
      return res.status(404).json(createError('任务不存在', 404));
    }

    // 查找文件记录
    let targetFile = null;
    for (const fileId of task.files.uploaded) {
      const file = db.files.get(fileId);
      if (file && file.originalName === fileName) {
        targetFile = file;
        break;
      }
    }

    if (!targetFile) {
      return res.status(404).json(createError('文件不存在', 404));
    }

    // 发送文件
    res.download(targetFile.path, targetFile.originalName);
  } catch (error) {
    console.error('下载文件错误:', error);
    res.status(500).json(createError('下载文件失败: ' + error.message));
  }
});

// 获取可用模型信息
app.get('/api/v1/models', async (req, res) => {
  try {
    const models = [
      {
        id: 'whisper-large-v3',
        name: 'Whisper Large v3',
        provider: 'modelscope',
        capabilities: ['speech-to-text', 'transcription'],
        description: '高性能语音识别模型'
      },
      {
        id: 'qwen-audio',
        name: 'Qwen Audio',
        provider: 'modelscope',
        capabilities: ['audio-understanding', 'transcription'],
        description: '阿里通义千问音频模型'
      },
      {
        id: 'funasr-realtime',
        name: 'FunASR Real-time',
        provider: 'modelscope',
        capabilities: ['real-time-transcription'],
        description: '实时语音识别'
      }
    ];

    res.json(createResponse(models, '模型列表获取成功'));
  } catch (error) {
    console.error('获取模型错误:', error);
    res.status(500).json(createError('获取模型失败: ' + error.message));
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
      const maxSize = parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024 * 1024;
      const maxSizeGB = (maxSize / (1024 * 1024 * 1024)).toFixed(1);
      return res.status(400).json(createError(`文件大小超过限制 (${maxSizeGB}GB)`, 400));
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