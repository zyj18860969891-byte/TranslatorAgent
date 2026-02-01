import React, { useState } from 'react';
import { 
  Upload, 
  Settings, 
  Play, 
  CheckCircle2,
  Loader2,
  ArrowLeft,
  Download
} from 'lucide-react';
import { FileInput } from './ui/FileInput';
import { Button } from './ui/Button';
import { Progress } from './ui/Progress';
import { Badge } from './ui/Badge';

interface WorkflowStepsProps {
  type: 'video-translation' | 'document-translation' | 'text-translation';
  onComplete: (result: string) => void;
}

export const WorkflowSteps: React.FC<WorkflowStepsProps> = ({ type, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [targetLanguage, setTargetLanguage] = useState('zh');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<string | null>(null);

  const steps = [
    { id: 1, title: '上传文件', icon: Upload },
    { id: 2, title: '配置参数', icon: Settings },
    { id: 3, title: '处理中', icon: Play },
    { id: 4, title: '完成', icon: CheckCircle2 },
  ];

  const handleFileSelect = (file: File | null) => {
    setUploadedFile(file);
  };

  const handleNext = () => {
    if (currentStep === 2 && !uploadedFile) {
      alert('请先上传文件');
      return;
    }
    
    if (currentStep === 3) {
      // 开始处理
      setIsProcessing(true);
      simulateProcessing();
    } else if (currentStep === 4) {
      onComplete(result || '处理完成');
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const simulateProcessing = () => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setProgress(progress);
      
      if (progress >= 100) {
        clearInterval(interval);
        setIsProcessing(false);
        setResult('处理完成！文件已准备好下载。');
        setCurrentStep(4);
      }
    }, 300);
  };

  const handleDownload = () => {
    // 模拟下载
    const blob = new Blob(['处理结果内容'], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translation_result_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
          >
            <ArrowLeft className="w-4 h-4" />
            返回
          </button>
          <Badge variant="default">
            {type === 'video-translation' ? '视频翻译' : 
             type === 'document-translation' ? '文档翻译' : '文本翻译'}
          </Badge>
        </div>

        {/* Progress Steps */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      currentStep > step.id
                        ? 'bg-green-600 text-white'
                        : currentStep === step.id
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                    }`}
                  >
                    {currentStep > step.id ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <step.icon className="w-5 h-5" />
                    )}
                  </div>
                  <span className="text-xs mt-2 text-center text-gray-600 dark:text-gray-400">
                    {step.title}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className="flex-1 h-0.5 bg-gray-200 dark:bg-gray-800 mx-2" />
                )}
              </div>
            ))}
          </div>
          <Progress value={currentStep} max={4} />
        </div>

        {/* Step Content */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          {currentStep === 1 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                上传文件
              </h2>
              <FileInput
                onChange={handleFileSelect}
                accept={type === 'video-translation' ? 'video/*' : '.txt,.doc,.docx,.pdf'}
                className="mb-4"
              />
              {uploadedFile && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <span className="font-medium">已选择:</span>
                  <span>{uploadedFile.name}</span>
                </div>
              )}
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                配置参数
              </h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  目标语言
                </label>
                <select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="zh">中文</option>
                  <option value="en">English</option>
                  <option value="ja">日本語</option>
                  <option value="ko">한국어</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                  <option value="es">Español</option>
                </select>
              </div>
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                  配置预览
                </h3>
                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex justify-between">
                    <span>文件类型:</span>
                    <span className="font-medium">
                      {type === 'video-translation' ? '视频文件' : '文档文件'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>目标语言:</span>
                    <span className="font-medium">
                      {targetLanguage === 'zh' ? '中文' : 
                       targetLanguage === 'en' ? 'English' :
                       targetLanguage === 'ja' ? '日本語' :
                       targetLanguage === 'ko' ? '한국어' :
                       targetLanguage === 'fr' ? 'Français' :
                       targetLanguage === 'de' ? 'Deutsch' : 'Español'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                处理中...
              </h2>
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
              </div>
              <Progress value={progress} max={100} />
              <p className="text-center text-gray-600 dark:text-gray-400">
                正在处理文件，请稍候... ({progress}%)
              </p>
            </div>
          )}

          {currentStep === 4 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                处理完成
              </h2>
              <div className="flex items-center justify-center py-8">
                <CheckCircle2 className="w-16 h-16 text-green-600" />
              </div>
              <p className="text-center text-gray-600 dark:text-gray-400">
                {result}
              </p>
              <div className="flex justify-center">
                <Button
                  onClick={handleDownload}
                  className="flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  下载结果
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 1 || isProcessing}
          >
            上一步
          </Button>
          <Button
            onClick={handleNext}
            disabled={isProcessing}
            className="flex items-center gap-2"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                处理中...
              </>
            ) : currentStep === 4 ? (
              '完成'
            ) : (
              '下一步'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};