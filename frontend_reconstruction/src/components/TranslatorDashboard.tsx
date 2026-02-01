import React, { useState } from 'react'
import { Card, CardContent } from './ui/Card'
import { Button } from './ui/Button'
import { Textarea } from './ui/Textarea'
import { apiClient } from '@/utils/apiClient'
import { Copy, Download, Bot, User } from 'lucide-react'

interface TranslationResult {
  original: string
  translated: string
  sourceLang: string
  targetLang: string
  confidence: number
}

export const TranslatorDashboard: React.FC = () => {
  const [inputText, setInputText] = useState('')
  const [targetLang, setTargetLang] = useState('en')
  const [result, setResult] = useState<TranslationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleTranslate = async () => {
    if (!inputText.trim()) {
      setError('请输入要翻译的文本')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.post('/api/v1/translation/translate', {
        text: inputText,
        target_language: targetLang,
      })
      setResult({
        original: inputText,
        translated: response.data.translated_text,
        sourceLang: response.data.source_lang,
        targetLang: response.data.target_lang,
        confidence: response.data.confidence,
      })
    } catch (err) {
      setError('翻译失败，请稍后重试')
      console.error('Translation error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const handleDownload = () => {
    if (!result) return
    const content = `原文：\n${result.original}\n\n译文：\n${result.translated}`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'translation_result.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* 输入区域 */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                源文本
              </label>
              <Textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="输入要翻译的文本..."
                className="min-h-[150px] resize-y"
                disabled={loading}
              />
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  目标语言
                </label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                  disabled={loading}
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

              <div className="flex-shrink-0 mt-6">
                <Button
                  onClick={handleTranslate}
                  disabled={loading || !inputText.trim()}
                  className="w-32"
                >
                  {loading ? '翻译中...' : '开始翻译'}
                </Button>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300 text-sm">
                {error}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 结果区域 */}
      {result && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              {/* 用户消息 */}
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 ml-14">
                  <span className="text-sm font-medium text-gray-500">用户</span>
                  <span className="text-xs text-gray-400">{new Date().toLocaleTimeString()}</span>
                </div>
                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 flex-shrink-0 flex items-center justify-center shadow-sm">
                    <User className="h-5 w-5 text-gray-700 dark:text-gray-300" />
                  </div>
                  <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg rounded-tl-none p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{result.original}</p>
                  </div>
                </div>
              </div>

              {/* 系统响应 */}
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-2 ml-14">
                  <span className="text-sm font-medium text-primary">TranslatorAI</span>
                  <span className="text-xs text-gray-400">{new Date().toLocaleTimeString()}</span>
                </div>
                <div className="flex gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex-shrink-0 flex items-center justify-center shadow-sm">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 bg-primary/5 dark:bg-gray-800 border border-primary/10 dark:border-primary/20 rounded-lg rounded-tl-none p-4 shadow-sm">
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{result.translated}</p>
                    <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex justify-end gap-2">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-7 px-2 text-xs rounded-md"
                        onClick={() => handleCopy(result.translated)}
                      >
                        <Copy className="h-3.5 w-3.5 mr-1" /> 复制
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-7 px-2 text-xs rounded-md"
                        onClick={handleDownload}
                      >
                        <Download className="h-3.5 w-3.5 mr-1" /> 保存
                      </Button>
                    </div>
                  </div>
                </div>
              </div>

              {/* 翻译信息 */}
              <div className="grid grid-cols-3 gap-2 text-sm mt-4">
                <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-gray-500 dark:text-gray-400">源语言</span>
                  <div className="font-medium">{result.sourceLang}</div>
                </div>
                <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-gray-500 dark:text-gray-400">目标语言</span>
                  <div className="font-medium">{result.targetLang}</div>
                </div>
                <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <span className="text-gray-500 dark:text-gray-400">置信度</span>
                  <div className="font-medium">{(result.confidence * 100).toFixed(1)}%</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}