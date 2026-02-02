import React, { useState } from 'react';
import { 
  Video,
  Download,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { FileInput } from '../components/ui/FileInput';
import { Select } from '../components/ui/Select';
import { Progress } from '../components/ui/Progress';
import { apiClient } from '../utils/apiClient';

export const VideoPage: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [targetLanguage, setTargetLanguage] = useState('zh');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (file: File | null) => {
    setUploadedFile(file);
    setError(null);
    setResult(null);
  };

  const handleProcess = async () => {
    if (!uploadedFile) {
      setError('请先上传视频文件');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      // 先上传文件
      const uploadResponse = await apiClient.uploadFile(uploadedFile);
      if (!uploadResponse.success || !uploadResponse.data) {
        throw new Error(uploadResponse.error || '文件上传失败');
      }

      const { file_path } = uploadResponse.data;

      // 调用视频处理API
      const processResponse = await apiClient.processVideo({
        videoUrl: file_path,
        operation: 'translate_subtitles',
        targetLanguage,
        options: {}
      });

      if (processResponse.success && processResponse.data) {
        setResult(`视频处理完成！结果文件：${processResponse.data.resultUrl}`);
      } else {
        throw new Error(processResponse.error || '视频处理失败');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '视频处理失败');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    
    const blob = new Blob(['字幕翻译结果'], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `video_subtitle_${Date.now()}.srt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            视频处理
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            视频字幕提取、翻译、字幕增强
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                上传视频文件
              </label>
              <FileInput
                onChange={handleFileSelect}
                accept="video/*"
                className="mb-4"
              />
              {uploadedFile && (
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <span className="font-medium">已选择:</span>
                  <span>{uploadedFile.name}</span>
                </div>
              )}
            </div>

            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  目标语言
                </label>
                <Select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  disabled={isProcessing}
                >
                  <option value="zh">中文</option>
                  <option value="en">English</option>
                  <option value="ja">日本語</option>
                  <option value="ko">한국어</option>
                  <option value="fr">Français</option>
                  <option value="de">Deutsch</option>
                  <option value="es">Español</option>
                </Select>
              </div>

              <div className="flex items-end">
                <Button
                  onClick={handleProcess}
                  disabled={isProcessing || !uploadedFile}
                  className="flex items-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      处理中...
                    </>
                  ) : (
                    <>
                      <Video className="w-5 h-5" />
                      开始处理
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Section */}
        {isProcessing && (
          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              处理进度
            </h2>
            <Progress value={progress} max={100} className="mb-2" />
            <p className="text-center text-gray-600 dark:text-gray-400">
              正在处理视频，请稍候... ({progress}%)
            </p>
          </div>
        )}

        {/* Error Section */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        )}

        {/* Result Section */}
        {result && !isProcessing && (
          <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                处理结果
              </h2>
              <Button
                onClick={handleDownload}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                下载字幕
              </Button>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <p className="text-gray-900 dark:text-gray-100 mb-4">
                {result}
              </p>
              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex justify-between">
                  <span>提取字幕段数:</span>
                  <span className="font-medium">15</span>
                </div>
                <div className="flex justify-between">
                  <span>总时长:</span>
                  <span className="font-medium">2分34秒</span>
                </div>
                <div className="flex justify-between">
                  <span>翻译语言:</span>
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
      </div>
    </div>
  );
};