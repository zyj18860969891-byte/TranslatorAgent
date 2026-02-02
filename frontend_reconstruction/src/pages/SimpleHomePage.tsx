import React from 'react';

interface HomePageProps {
  onFeatureSelect: (feature: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onFeatureSelect }) => {
  const features = [
    {
      id: 'video',
      title: '视频翻译',
      description: 'AI驱动的视频翻译，支持多语言字幕生成',
      icon: '🎬'
    },
    {
      id: 'subtitle',
      title: '字幕处理',
      description: '字幕提取、翻译和同步处理',
      icon: '📝'
    },
    {
      id: 'translation',
      title: '文本翻译',
      description: '高质量文本翻译服务',
      icon: '🔤'
    },
    {
      id: 'dashboard',
      title: '数据仪表板',
      description: '查看处理进度和结果统计',
      icon: '📊'
    }
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Translator Agent
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          基于AI的智能翻译系统
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature) => (
          <div
            key={feature.id}
            className="bg-white rounded-lg shadow-md p-6 cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => onFeatureSelect(feature.id)}
          >
            <div className="text-4xl mb-4">{feature.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {feature.title}
            </h3>
            <p className="text-gray-600 text-sm">
              {feature.description}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          系统状态
        </h2>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">后端API</span>
            <span className="text-green-600 font-medium">正常运行</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">数据库</span>
            <span className="text-green-600 font-medium">连接正常</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">AI模型</span>
            <span className="text-green-600 font-medium">已加载</span>
          </div>
        </div>
      </div>
    </div>
  );
};