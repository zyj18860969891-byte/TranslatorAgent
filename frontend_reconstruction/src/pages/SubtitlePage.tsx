import React, { useState } from 'react';
import { 
  File as FileIcon,
  Download,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Edit,
  Clock
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { FileInput } from '../components/ui/FileInput';
import { Select } from '../components/ui/Select';
import { Textarea } from '../components/ui/Textarea';

export const SubtitlePage: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [targetLanguage, setTargetLanguage] = useState('zh');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [subtitleText, setSubtitleText] = useState('');

  const handleFileSelect = (file: File | null) => {
    setUploadedFile(file);
    setError(null);
    setResult(null);
  };

  const handleProcess = async () => {
    if (!uploadedFile) {
      setError('请先上传字幕文件');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);

    // 模拟字幕处理
    setTimeout(() => {
      const mockResult = `1
00:00:01,000 --> 00:00:04,000
[翻译] 这是一个示例字幕

2
00:00:05,000 --> 00:00:08,000
[翻译] 字幕翻译完成

3
00:00:09,000 --> 00:00:12,000
[翻译] 感谢使用`;
      
      setSubtitleText(mockResult);
      setResult('字幕翻译完成！');
      setIsProcessing(false);
    }, 2000);
  };

  const handleDownload = () => {
    if (!subtitleText) return;
    
    const blob = new Blob([subtitleText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `subtitle_translated_${Date.now()}.srt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            字幕编辑
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            字幕预览、时间轴编辑、SRT导出
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                上传字幕文件 (.srt)
              </label>
              <FileInput
                onChange={handleFileSelect}
                accept=".srt,.txt"
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
                      <FileIcon className="w-5 h-5" />
                      翻译字幕
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>

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
                翻译结果
              </h2>
              <Button
                onClick={handleDownload}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                下载SRT
              </Button>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <Textarea
                value={subtitleText}
                onChange={(e) => setSubtitleText(e.target.value)}
                className="h-64 font-mono text-sm"
                placeholder="字幕内容..."
              />
              <div className="mt-4 grid grid-cols-3 gap-4 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>总时长: 12秒</span>
                </div>
                <div className="flex items-center gap-2">
                  <FileIcon className="w-4 h-4" />
                  <span>字幕段数: 3</span>
                </div>
                <div className="flex items-center gap-2">
                  <Edit className="w-4 h-4" />
                  <span>可编辑: 是</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};