import React from 'react';
import { 
  FileText, 
  Video, 
  CheckCircle2,
  Clock,
  Download
} from 'lucide-react';
import { Badge } from './ui/Badge';
import { Chart } from './ui/Chart';
import { DataTable } from './ui/DataTable';

interface DashboardProps {
  results?: any[];
}

export const Dashboard: React.FC<DashboardProps> = () => {
  const stats = [
    {
      label: '总任务数',
      value: '12',
      icon: FileText,
      color: 'blue',
    },
    {
      label: '已完成',
      value: '10',
      icon: CheckCircle2,
      color: 'green',
    },
    {
      label: '处理中',
      value: '2',
      icon: Clock,
      color: 'orange',
    },
    {
      label: '成功率',
      value: '95%',
      icon: CheckCircle2,
      color: 'purple',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
    green: 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400',
    orange: 'bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
  };

  const chartData = [
    { label: '周一', value: 12 },
    { label: '周二', value: 19 },
    { label: '周三', value: 15 },
    { label: '周四', value: 25 },
    { label: '周五', value: 22 },
    { label: '周六', value: 18 },
    { label: '周日', value: 14 },
  ];

  const tableData = [
    { id: '001', type: '文本翻译', status: '已完成', language: '中→英', time: '2分钟前' },
    { id: '002', type: '视频处理', status: '处理中', language: '中→日', time: '5分钟前' },
    { id: '003', type: '字幕翻译', status: '已完成', language: '英→中', time: '10分钟前' },
    { id: '004', type: '文本翻译', status: '已完成', language: '中→韩', time: '15分钟前' },
    { id: '005', type: '视频处理', status: '失败', language: '中→法', time: '20分钟前' },
  ];

  const columns = [
    { key: 'id', header: '任务ID' },
    { key: 'type', header: '类型' },
    { key: 'status', header: '状态', render: (value: string) => (
      <Badge variant={value === '已完成' ? 'default' : value === '处理中' ? 'secondary' : 'destructive'}>
        {value}
      </Badge>
    )},
    { key: 'language', header: '语言' },
    { key: 'time', header: '时间' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            仪表板
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            查看您的翻译和处理任务统计信息
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            const colorClass = colorClasses[stat.color as keyof typeof colorClasses];
            
            return (
              <div
                key={index}
                className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6"
              >
                <div className={`w-12 h-12 rounded-lg ${colorClass} flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              任务趋势
            </h2>
            <Chart
              type="bar"
              data={chartData}
              options={{
                width: 400,
                height: 200,
                colors: ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'],
                title: '本周任务量',
              }}
            />
          </div>
          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              任务分布
            </h2>
            <Chart
              type="pie"
              data={[
                { label: '文本翻译', value: 40 },
                { label: '视频处理', value: 30 },
                { label: '字幕编辑', value: 20 },
                { label: '其他', value: 10 },
              ]}
              options={{
                width: 400,
                height: 200,
                colors: ['#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6'],
              }}
            />
          </div>
        </div>

        {/* Recent Tasks */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              最近任务
            </h2>
            <button className="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
              查看全部
            </button>
          </div>
          <DataTable data={tableData} columns={columns} />
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            快速操作
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
              <FileText className="w-5 h-5 text-primary-600" />
              <span className="font-medium text-gray-900 dark:text-gray-100">新建翻译</span>
            </button>
            <button className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
              <Video className="w-5 h-5 text-green-600" />
              <span className="font-medium text-gray-900 dark:text-gray-100">处理视频</span>
            </button>
            <button className="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors">
              <Download className="w-5 h-5 text-orange-600" />
              <span className="font-medium text-gray-900 dark:text-gray-100">导出结果</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};