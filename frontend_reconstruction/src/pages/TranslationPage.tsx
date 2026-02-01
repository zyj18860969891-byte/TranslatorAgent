import React, { useState } from 'react';
import { 
  Download,
  CheckCircle2,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Textarea } from '../components/ui/Textarea';
import { Select } from '../components/ui/Select';
// import { Badge } from '../components/ui/Badge';

export const TranslationPage: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('zh');
  const [result, setResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTranslate = async () => {
    if (!inputText.trim()) {
      setError('请输入要翻译的文本');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    // 模拟API调用
    setTimeout(() => {
      const mockResult = `[翻译] ${inputText}`;
      setResult(mockResult);
      setIsLoading(false);
    }, 1500);
  };

  const handleDownload = () => {
    if (!result) return;
    
    const blob = new Blob([result], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'translation_result.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            文本翻译
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            支持多语言文本翻译，实时预览结果
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                源文本
              </label>
              <Textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="请输入要翻译的文本..."
                className="h-32"
                disabled={isLoading}
              />
            </div>

            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  目标语言
                </label>
                <Select
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                  disabled={isLoading}
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
                  onClick={handleTranslate}
                  disabled={isLoading || !inputText.trim()}
                  className="flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      翻译中...
                    </>
                  ) : (
                    <>
                      翻译
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
        {result && (
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
                下载
              </Button>
            </div>
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 min-h-[100px]">
              <p className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                {result}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};