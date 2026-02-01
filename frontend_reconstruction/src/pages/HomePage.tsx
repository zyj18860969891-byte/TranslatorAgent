import React from 'react';
import { 
  Play,
  CheckCircle2,
  Upload,
  Zap
} from 'lucide-react';
import { ProfessionalFeatureCards } from '../components/ProfessionalFeatureCards';

interface HomePageProps {
  onFeatureSelect?: (featureId: string) => void;
  onWorkflowStart?: (type: 'video-translation' | 'document-translation' | 'text-translation') => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onFeatureSelect, onWorkflowStart }) => {
  const selectedFeature = '';
  const steps = [
    { title: '选择专业模块', description: '从6个专业板块中选择您需要的功能', icon: Play },
    { title: '上传素材', description: '上传视频、字幕或文本文件', icon: Upload },
    { title: '获取专业结果', description: '查看AI处理结果并导出文件', icon: CheckCircle2 },
  ];

  const capabilities = [
    { title: '全流程自动化', description: '从输入到输出的完整闭环处理' },
    { title: 'AI智能决策', description: '自动选择最佳模型和处理策略' },
    { title: '专业级输出', description: '达到生产环境使用标准' },
    { title: '实时进度追踪', description: '可视化处理进度和状态' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="text-center">
            <div className="inline-flex items-center gap-2 bg-primary-600/20 text-primary-400 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              生产级 AI 视频处理系统
            </div>
            <h1 className="text-5xl font-bold text-white mb-6">
              TranslatorAgent
            </h1>
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              基于 NarratorAI 生产级 Skills 与 ModelScope 替代方案，提供从视频翻译、字幕处理到 AI 解说的完整专业解决方案
            </p>
            <div className="flex gap-4 justify-center">
              <button 
                className="px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-primary-600/30 flex items-center gap-2"
                onClick={() => onFeatureSelect?.('professional-video-translation')}
              >
                <Play className="w-5 h-5" />
                立即体验
              </button>
              <button className="px-8 py-4 border border-gray-600 text-gray-300 rounded-xl font-medium hover:bg-gray-800 hover:text-white transition-all duration-300 hover:scale-105">
                了解更多
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Professional Features Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            6 大专业处理模块
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            基于原型设计深度重构，每个模块都配置了准确的后端 Skill 指令与模型路由
          </p>
        </div>
        <ProfessionalFeatureCards 
          selectedFeature={selectedFeature}
          onFeatureSelect={onFeatureSelect}
          onWorkflowStart={onWorkflowStart}
        />
      </div>

      {/* Capabilities Section */}
      <div className="bg-white dark:bg-gray-950 border-y border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-12 text-center">
            核心能力
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {capabilities.map((cap, index) => (
              <div key={index} className="text-center p-6 bg-gray-50 dark:bg-gray-900 rounded-xl">
                <div className="w-12 h-12 bg-primary-600/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-primary-600 font-bold text-lg">{index + 1}</span>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {cap.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {cap.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Start Section */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-12 text-center">
          快速开始
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-primary-600 text-white rounded-xl flex items-center justify-center font-bold text-lg flex-shrink-0">
                  {index + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-lg mb-2">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {step.description}
                  </p>
                </div>
              </div>
              {index < 2 && (
                <div className="hidden md:block absolute top-6 left-1/2 w-full h-0.5 bg-gray-200 dark:bg-gray-800 -z-10" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="max-w-7xl mx-auto px-6 py-16 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            准备好开始专业级视频处理了吗？
          </h2>
          <p className="text-primary-100 mb-8 text-lg max-w-2xl mx-auto">
            选择上方任意一个专业模块，开始您的 AI 视频处理之旅
          </p>
          <button 
            className="px-8 py-4 bg-white text-primary-600 rounded-xl font-semibold hover:bg-gray-100 transition-all duration-300 hover:scale-105"
            onClick={() => onFeatureSelect?.('professional-video-translation')}
          >
            立即开始
          </button>
        </div>
      </div>
    </div>
  );
};