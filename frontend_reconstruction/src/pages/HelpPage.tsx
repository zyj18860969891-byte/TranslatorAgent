import React from 'react';
import { 
  HelpCircle, 
  Book, 
  Zap,
  Shield,
  Globe,
  Mail,
  ExternalLink
} from 'lucide-react';

export const HelpPage: React.FC = () => {
  const faqs = [
    {
      question: '如何使用文本翻译功能？',
      answer: '选择文本翻译功能，输入要翻译的文本，选择目标语言，点击翻译按钮即可。',
    },
    {
      question: '支持哪些语言？',
      answer: '目前支持中文、英文、日文、韩文、法文、德文、西班牙文等多种语言。',
    },
    {
      question: '视频处理需要多长时间？',
      answer: '处理时间取决于视频长度和复杂度，通常1分钟的视频需要2-3分钟处理。',
    },
    {
      question: '如何保护我的隐私？',
      answer: '所有处理都在本地进行，不会上传到云端，确保您的数据安全。',
    },
  ];

  const features = [
    {
      icon: Book,
      title: '详细文档',
      description: '查看完整的使用指南和API文档',
      link: '#',
    },
    {
      icon: Zap,
      title: '快速开始',
      description: '5分钟快速上手教程',
      link: '#',
    },
    {
      icon: Shield,
      title: '隐私政策',
      description: '了解我们如何保护您的数据',
      link: '#',
    },
    {
      icon: Globe,
      title: '社区支持',
      description: '加入用户社区获取帮助',
      link: '#',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            帮助中心
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            查看使用指南、常见问题和获取支持
          </p>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            
            return (
              <a
                key={index}
                href={feature.link}
                className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-5 hover:shadow-md transition-shadow"
              >
                <div className="w-10 h-10 bg-primary-50 text-primary-600 rounded-lg flex items-center justify-center mb-3">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {feature.description}
                </p>
                <span className="text-sm text-primary-600 dark:text-primary-400 flex items-center gap-1">
                  查看详情 <ExternalLink className="w-3 h-3" />
                </span>
              </a>
            );
          })}
        </div>

        {/* FAQs */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-primary-600" />
            常见问题
          </h2>
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="border-b border-gray-200 dark:border-gray-800 pb-4 last:border-0 last:pb-0">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {faq.question}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Contact */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2">
            <Mail className="w-5 h-5 text-primary-600" />
            联系我们
          </h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                问题反馈
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                如果您在使用过程中遇到问题，请通过以下方式联系我们：
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                  电子邮件
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  support@translator-agent.com
                </p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                  社区论坛
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  translator-agent.community
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};