import React, { useState } from 'react';
import { 
  FileText, 
  Video, 
  File as FileIcon,
  Upload,
  Settings,
  Search,
  Filter,
  MoreVertical,
  Play,
  Pause,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/Tabs';
import { DropdownMenu, DropdownMenuItem } from './ui/DropdownMenu';

export const RefactoredDashboard: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  const stats = [
    { label: '总任务', value: '156', change: '+12%', trend: 'up' },
    { label: '成功率', value: '98.5%', change: '+2.3%', trend: 'up' },
    { label: '平均处理时间', value: '2.3min', change: '-15%', trend: 'down' },
    { label: '活跃任务', value: '8', change: '+2', trend: 'up' },
  ];

  const recentTasks = [
    { id: 'T001', type: '视频翻译', status: 'processing', progress: 65, time: '2分钟前' },
    { id: 'T002', type: '文本翻译', status: 'completed', progress: 100, time: '5分钟前' },
    { id: 'T003', type: '字幕编辑', status: 'completed', progress: 100, time: '10分钟前' },
    { id: 'T004', type: '文档翻译', status: 'failed', progress: 0, time: '15分钟前' },
    { id: 'T005', type: '视频处理', status: 'pending', progress: 0, time: '20分钟前' },
  ];

  // const typeColors = {
  //   '视频翻译': 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400',
  //   '文本翻译': 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
  //   '字幕编辑': 'bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
  //   '文档翻译': 'bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400',
  // };

  const statusConfig = {
    processing: { color: 'secondary', icon: Play, text: '处理中' },
    completed: { color: 'default', icon: CheckCircle2, text: '已完成' },
    failed: { color: 'destructive', icon: AlertCircle, text: '失败' },
    pending: { color: 'outline', icon: Pause, text: '待处理' },
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              重构仪表板
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              基于NarratorAI设计原则的现代化界面
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              上传文件
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              设置
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-5"
            >
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                {stat.label}
              </div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                {stat.value}
              </div>
              <div className={`text-sm ${stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {stat.change}
              </div>
            </div>
          ))}
        </div>

        {/* Search and Filter */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="搜索任务..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 text-sm"
              >
                <option value="all">全部类型</option>
                <option value="video">视频翻译</option>
                <option value="text">文本翻译</option>
                <option value="subtitle">字幕编辑</option>
              </select>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value="recent" onValueChange={() => {}}>
          <TabsList>
            <TabsTrigger value="recent">最近任务</TabsTrigger>
            <TabsTrigger value="processing">处理中</TabsTrigger>
            <TabsTrigger value="completed">已完成</TabsTrigger>
            <TabsTrigger value="failed">失败</TabsTrigger>
          </TabsList>

          <TabsContent value="recent">
            <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">任务ID</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">类型</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">状态</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">进度</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">时间</th>
                    <th className="px-4 py-3 text-left font-medium text-gray-700 dark:text-gray-300">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                  {recentTasks.map((task) => {
                    const status = statusConfig[task.status as keyof typeof statusConfig];
                    const TypeIcon = task.type.includes('视频') ? Video : task.type.includes('文本') ? FileText : FileIcon;
                    
                    return (
                      <tr key={task.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                        <td className="px-4 py-3 font-medium text-gray-900 dark:text-gray-100">{task.id}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <TypeIcon className="w-4 h-4 text-gray-500" />
                            <span className="text-gray-900 dark:text-gray-100">{task.type}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={status.color as any}>
                            {status.text}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-primary-600 transition-all duration-300"
                                style={{ width: `${task.progress}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-600 dark:text-gray-400">
                              {task.progress}%
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{task.time}</td>
                        <td className="px-4 py-3">
                          <DropdownMenu
                            trigger={
                              <button className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
                                <MoreVertical className="w-4 h-4 text-gray-500" />
                              </button>
                            }
                          >
                            <DropdownMenuItem>查看详情</DropdownMenuItem>
                            <DropdownMenuItem>重新处理</DropdownMenuItem>
                            <DropdownMenuItem>下载结果</DropdownMenuItem>
                            <DropdownMenuItem>删除任务</DropdownMenuItem>
                          </DropdownMenu>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </TabsContent>

          <TabsContent value="processing">
            <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
              <p className="text-gray-600 dark:text-gray-400">处理中的任务列表...</p>
            </div>
          </TabsContent>

          <TabsContent value="completed">
            <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
              <p className="text-gray-600 dark:text-gray-400">已完成的任务列表...</p>
            </div>
          </TabsContent>

          <TabsContent value="failed">
            <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
              <p className="text-gray-600 dark:text-gray-400">失败的任务列表...</p>
            </div>
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-5 hover:shadow-md transition-shadow cursor-pointer">
            <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-3">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">文本翻译</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">快速翻译文本内容</p>
            <Button variant="outline" size="sm" className="w-full">开始</Button>
          </div>

          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-5 hover:shadow-md transition-shadow cursor-pointer">
            <div className="w-10 h-10 bg-green-50 text-green-600 rounded-lg flex items-center justify-center mb-3">
              <Video className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">视频处理</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">提取和翻译视频字幕</p>
            <Button variant="outline" size="sm" className="w-full">开始</Button>
          </div>

          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-5 hover:shadow-md transition-shadow cursor-pointer">
            <div className="w-10 h-10 bg-purple-50 text-purple-600 rounded-lg flex items-center justify-center mb-3">
              <FileIcon className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">字幕编辑</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">编辑和导出字幕文件</p>
            <Button variant="outline" size="sm" className="w-full">开始</Button>
          </div>
        </div>
      </div>
    </div>
  );
};