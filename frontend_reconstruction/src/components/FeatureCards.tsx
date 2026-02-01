import React from 'react';
import { 
  FileText, 
  Video, 
  File as FileIcon,
  Zap,
  Upload,
  Settings
} from 'lucide-react';

interface FeatureCardsProps {
  selectedFeature: string;
  onFeatureSelect: (featureId: string) => void;
  onWorkflowStart: (type: 'video-translation' | 'document-translation' | 'text-translation') => void;
}

export const FeatureCards: React.FC<FeatureCardsProps> = ({
  selectedFeature,
  onFeatureSelect,
  onWorkflowStart,
}) => {
  const features = [
    {
      id: 'text-translation',
      icon: FileText,
      title: '文本翻译',
      description: '支持多语言文本翻译，实时预览结果',
      color: 'blue',
      workflowType: 'text-translation' as const,
    },
    {
      id: 'video-translate',
      icon: Video,
      title: '视频翻译',
      description: '视频字幕提取、翻译、字幕增强',
      color: 'green',
      workflowType: 'video-translation' as const,
    },
    {
      id: 'document-translate',
      icon: Upload,
      title: '文档翻译',
      description: '上传文档进行批量翻译',
      color: 'purple',
      workflowType: 'document-translation' as const,
    },
    {
      id: 'subtitle-edit',
      icon: FileIcon,
      title: '字幕编辑',
      description: '字幕预览、时间轴编辑、SRT导出',
      color: 'orange',
      workflowType: 'text-translation' as const,
    },
    {
      id: 'quick-process',
      icon: Zap,
      title: '快速处理',
      description: '批处理优化，高效处理大量内容',
      color: 'red',
      workflowType: 'text-translation' as const,
    },
    {
      id: 'settings',
      icon: Settings,
      title: '系统设置',
      description: '配置翻译引擎、语言偏好等',
      color: 'indigo',
      workflowType: 'text-translation' as const,
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
    green: 'bg-green-50 text-green-600 dark:bg-green-900/20 dark:text-green-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
    orange: 'bg-orange-50 text-orange-600 dark:bg-orange-900/20 dark:text-orange-400',
    red: 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400',
    indigo: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400',
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {features.map((feature) => {
        const Icon = feature.icon;
        const colorClass = colorClasses[feature.color as keyof typeof colorClasses];
        const isSelected = selectedFeature === feature.id;

        return (
          <div
            key={feature.id}
            onClick={() => {
              onFeatureSelect(feature.id);
              if (feature.id !== 'settings') {
                onWorkflowStart(feature.workflowType);
              }
            }}
            className={`cursor-pointer rounded-xl border p-4 transition-all hover:shadow-md ${
              isSelected
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                : 'border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950 hover:border-gray-300 dark:hover:border-gray-700'
            }`}
          >
            <div className={`w-10 h-10 rounded-lg ${colorClass} flex items-center justify-center mb-3`}>
              <Icon className="w-5 h-5" />
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
              {feature.title}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {feature.description}
            </p>
          </div>
        );
      })}
    </div>
  );
};