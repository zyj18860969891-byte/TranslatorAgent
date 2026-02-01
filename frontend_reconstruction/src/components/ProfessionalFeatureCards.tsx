import React from 'react';
import { 
  Video,
  Type,
  Eraser,
  Film,
  MessageSquare,
  PlayCircle,
  CheckCircle2,
  FileText
} from 'lucide-react';

interface ProfessionalFeatureCardsProps {
  selectedFeature?: string;
  onFeatureSelect?: (featureId: string) => void;
  onWorkflowStart?: (type: 'video-translation' | 'document-translation' | 'text-translation') => void;
}

export const ProfessionalFeatureCards: React.FC<ProfessionalFeatureCardsProps> = ({
  selectedFeature,
  onFeatureSelect,
  onWorkflowStart
}) => {
  const professionalFeatures = [
    {
      id: 'professional-video-translation',
      icon: Video,
      title: '专业视频翻译',
      description: '基于 video-translation-SKILL 的全流程编排。协同调用 OCR 提取、情绪识别（emotion2vec）、模型翻译（mimo-v2-flash）以及最终的视频压制',
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600',
      features: [
        '自动处理从视频输入到多语言视频输出的完整闭环',
        'OCR 提取 + 情绪识别 + 模型翻译 + 视频压制',
        '支持多种视频格式和分辨率'
      ]
    },
    {
      id: 'subtitle-translation',
      icon: FileText,
      title: '字幕翻译',
      description: '基于 srt-translation-skill。专注于纯 SRT 文件的处理，通过 BDI 心理建模与术语知识图谱确保译文的本土化与上下文连贯性',
      color: 'green',
      gradient: 'from-green-500 to-green-600',
      features: [
        'BDI 心理建模确保译文本土化',
        '术语知识图谱保持上下文连贯性',
        '专业级 SRT 文件处理'
      ]
    },
    {
      id: 'subtitle-extraction',
      icon: Type,
      title: '字幕提取',
      description: '推荐模型：Llama-3.2-11B-Vision-Instruct (ModelScope 替代方案)。在 DocVQA 上有 90.1% 的准确率',
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600',
      features: [
        'Llama-3.2-11B-Vision-Instruct 模型',
        'DocVQA 准确率 90.1%',
        'OpenCV 预处理检测字幕变化帧'
      ]
    },
    {
      id: 'subtitle-erasure',
      icon: Eraser,
      title: '字幕视频无痕擦除',
      description: '推荐模型：xingzi/diffuEraser。具备 SOTA 级的时间一致性和内容完整性',
      color: 'orange',
      gradient: 'from-orange-500 to-orange-600',
      features: [
        'SOTA 级时间一致性',
        '内容完整性保证',
        'Vision 模型提供字幕位置 Mask'
      ]
    },
    {
      id: 'video-subtitle-pressing',
      icon: Film,
      title: '视频字幕压制',
      description: '核心方案：FFmpeg (ModelScope 无直接对应模型，推荐成熟方案)。支持自定义字体、颜色、位置及对齐方式',
      color: 'red',
      gradient: 'from-red-500 to-red-600',
      features: [
        'FFmpeg 成熟方案',
        '自定义字体、颜色、位置',
        'Agent 封装为独立微服务'
      ]
    },
    {
      id: 'ai-video-narrative',
      icon: MessageSquare,
      title: 'AI 视频解说',
      description: '对应原型中的“短剧解说”。利用 mimo-v2-flash 进行内容理解与文案创作，配合解说风格进行自动化脚本生成',
      color: 'indigo',
      gradient: 'from-indigo-500 to-indigo-600',
      features: [
        'mimo-v2-flash 内容理解',
        '自动化脚本生成',
        '多种解说风格支持'
      ]
    },
  ];



  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {professionalFeatures.map((feature, index) => {
        const Icon = feature.icon;
        
        return (
          <div
            key={index}
            className={`relative bg-white dark:bg-gray-950 rounded-xl border-2 transition-all duration-300 ${
              selectedFeature === feature.id
                ? 'border-primary-600 shadow-lg shadow-primary-600/20'
                : 'border-gray-200 dark:border-gray-800 hover:border-primary-600 hover:shadow-lg hover:shadow-primary-600/10'
            } overflow-hidden cursor-pointer`}
            onClick={() => onFeatureSelect?.(feature.id)}
          >
            {/* Gradient Header */}
            <div className={`bg-gradient-to-r ${feature.gradient} p-4`}>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">{feature.title}</h3>
                  <div className="flex items-center gap-2 text-xs text-white/80">
                    <span className="bg-white/20 px-2 py-0.5 rounded">模块 {index + 1}</span>
                    <span>专业版</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                {feature.description}
              </p>
              
              {/* Features List */}
              <ul className="space-y-2 mb-4">
                {feature.features.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-gray-700 dark:text-gray-300">
                    <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>

              {/* Action Button */}
              <button
                className="w-full py-2 px-4 bg-gray-100 dark:bg-gray-800 hover:bg-primary-600 hover:text-white dark:hover:bg-primary-600 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                onClick={(e) => {
                  e.stopPropagation();
                  if (feature.id === 'professional-video-translation') {
                    onWorkflowStart?.('video-translation');
                  } else if (feature.id === 'subtitle-translation' || feature.id === 'subtitle-extraction') {
                    onWorkflowStart?.('text-translation');
                  } else {
                    onFeatureSelect?.(feature.id);
                  }
                }}
              >
                <PlayCircle className="w-4 h-4" />
                开始使用
              </button>
            </div>

            {/* Hover Effect Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary-600/5 to-transparent opacity-0 hover:opacity-100 transition-opacity pointer-events-none" />
          </div>
        );
      })}
    </div>
  );
};