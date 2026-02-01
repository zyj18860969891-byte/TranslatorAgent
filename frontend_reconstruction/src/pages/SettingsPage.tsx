import React, { useState } from 'react';
import { Settings, Save, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Label } from '../components/ui/Label';

export const SettingsPage: React.FC = () => {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState('mimo-v2-flash');
  const [temperature, setTemperature] = useState('0.7');

  const handleSave = () => {
    alert('设置已保存！');
  };

  const handleReset = () => {
    setApiKey('');
    setModel('mimo-v2-flash');
    setTemperature('0.7');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            系统设置
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            配置翻译引擎、语言偏好等
          </p>
        </div>

        {/* Settings Form */}
        <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <div className="space-y-6">
            <div>
              <Label htmlFor="apiKey">API密钥</Label>
              <Input
                id="apiKey"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="输入您的API密钥"
                className="mt-2"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                用于访问翻译服务的API密钥
              </p>
            </div>

            <div>
              <Label htmlFor="model">翻译模型</Label>
              <select
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="mt-2 w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
              >
                <option value="mimo-v2-flash">MIMO V2 Flash</option>
                <option value="mimo-v2-pro">MIMO V2 Pro</option>
                <option value="custom">自定义模型</option>
              </select>
            </div>

            <div>
              <Label htmlFor="temperature">生成温度</Label>
              <Input
                id="temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
                className="mt-2"
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                控制生成文本的随机性 (0.0-2.0)
              </p>
            </div>

            <div className="flex gap-4 pt-4">
              <Button onClick={handleSave} className="flex items-center gap-2">
                <Save className="w-4 h-4" />
                保存设置
              </Button>
              <Button variant="outline" onClick={handleReset} className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                重置
              </Button>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <Settings className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                关于设置
              </h3>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                这些设置将影响所有翻译和处理任务。API密钥存储在本地，不会上传到服务器。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};