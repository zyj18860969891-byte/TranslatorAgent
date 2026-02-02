import React, { useState, useEffect } from 'react'
import { Toaster } from './components/ui/Toaster'
import { FeatureCards } from './components/FeatureCards'
import { WorkflowSteps } from './components/WorkflowSteps'
import { RefactoredDashboard } from './components/RefactoredDashboard'
import { HomePage } from './pages/HomePage'
import { TranslationPage } from './pages/TranslationPage'
import { VideoPage } from './pages/VideoPage'
import { SubtitlePage } from './pages/SubtitlePage'
import { DashboardPage } from './pages/DashboardPage'
import { SettingsPage } from './pages/SettingsPage'
import { HelpPage } from './pages/HelpPage'
import { InteractiveDetailPage } from './pages/InteractiveDetailPage'
import ConversationalDetailPage from './pages/ConversationalDetailPage'
import { MicroserviceIntegrationPage } from './pages/MicroserviceIntegrationPage'
import { ApiIntegrationPage } from './pages/ApiIntegrationPage'
import { LogPage } from './pages/LogPage'
import { getPerformanceMonitor } from './utils/PerformanceMonitor'

const App: React.FC = () => {
  const [selectedFeature, setSelectedFeature] = useState('video-translate')
  const [showWorkflow, setShowWorkflow] = useState(false)
  const [showDashboard, setShowDashboard] = useState(false)
  const [showRefactoredDashboard, setShowRefactoredDashboard] = useState(false)
  const [showHomePage, setShowHomePage] = useState(true)
  const [showTranslation, setShowTranslation] = useState(false)
  const [showVideo, setShowVideo] = useState(false)
  const [showSubtitle, setShowSubtitle] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showHelp, setShowHelp] = useState(false)
  const [showInteractiveDetail, setShowInteractiveDetail] = useState(false)
  const [showConversationalDetail, setShowConversationalDetail] = useState(false);
  const [showMicroservice, setShowMicroservice] = useState(false);
  const [showApiIntegration, setShowApiIntegration] = useState(false);
  const [showLogPage, setShowLogPage] = useState(false);
  const [workflowType, setWorkflowType] = useState<'video-translation' | 'document-translation' | 'text-translation'>('video-translation')

  // 初始化性能监控器
  useEffect(() => {
    const monitor = getPerformanceMonitor();
    monitor.start();
    
    return () => {
      // 注意：不要在这里停止监控器，因为它可能在其他地方使用
    };
  }, []);

  const handleFeatureSelectOld = (featureId: string) => {
    setSelectedFeature(featureId)
    setShowWorkflow(false)
    setShowDashboard(false)
  }

  const handleWorkflowStart = (type: 'video-translation' | 'document-translation' | 'text-translation') => {
    setWorkflowType(type)
    setShowWorkflow(true)
    setShowDashboard(false)
  }

  const handleWorkflowComplete = (result: string) => {
    setShowWorkflow(false)
    setShowDashboard(true)
    console.log('Workflow completed:', result)
  }

  const handleShowHomePage = () => {
    setShowHomePage(true)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
  }

  const handleShowDashboard = () => {
    setShowDashboard(true)
    setShowHomePage(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
  }

  // Unused function - can be removed if not needed
  // const handleShowTranslator = () => {
  //   setShowDashboard(false)
  //   setShowHomePage(false)
  //   setShowRefactoredDashboard(false)
  //   setShowWorkflow(false)
  //   setShowTranslation(false)
  //   setShowVideo(false)
  //   setShowSubtitle(false)
  //   setShowSettings(false)
  //   setShowHelp(false)
  // }

  const handleShowTranslation = () => {
    setShowTranslation(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowHelp(false)
  }

  const handleShowVideo = () => {
    setShowVideo(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowHelp(false)
  }

  const handleShowSubtitle = () => {
    setShowSubtitle(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSettings(false)
    setShowHelp(false)
  }

  const handleShowSettings = () => {
    setShowSettings(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowHelp(false)
  }

  const handleShowHelp = () => {
    setShowHelp(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowMicroservice(false)
  }

  const handleShowMicroservice = () => {
    setShowMicroservice(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowHelp(false)
    setShowInteractiveDetail(false)
    setShowApiIntegration(false)
  }

  const handleShowApiIntegration = () => {
    setShowApiIntegration(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowHelp(false)
    setShowInteractiveDetail(false)
    setShowMicroservice(false)
    setShowLogPage(false)
  }

  const handleShowLogPage = () => {
    setShowLogPage(true)
    setShowHomePage(false)
    setShowDashboard(false)
    setShowRefactoredDashboard(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowHelp(false)
    setShowInteractiveDetail(false)
    setShowMicroservice(false)
    setShowApiIntegration(false)
  }

  const handleShowRefactoredDashboard = () => {
    setShowRefactoredDashboard(true)
    setShowDashboard(false)
    setShowHomePage(false)
    setShowWorkflow(false)
    setShowTranslation(false)
    setShowVideo(false)
    setShowSubtitle(false)
    setShowSettings(false)
    setShowHelp(false)
    setShowInteractiveDetail(false)
    setShowMicroservice(false)
  }

  const handleFeatureSelect = (featureId: string) => {
    // Map professional features to conversational detail page (ChatGPT模式)
    if (featureId === 'professional-video-translation') {
      setSelectedFeature('video-translate')
      setShowConversationalDetail(true)
      setShowHomePage(false)
      setShowDashboard(false)
      setShowRefactoredDashboard(false)
      setShowWorkflow(false)
      setShowTranslation(false)
      setShowVideo(false)
      setShowSubtitle(false)
      setShowSettings(false)
      setShowHelp(false)
      setShowMicroservice(false)
      setShowInteractiveDetail(false)
    } else if (featureId === 'subtitle-translation') {
      setSelectedFeature('subtitle-translate')
      setShowConversationalDetail(true)
      setShowHomePage(false)
      setShowDashboard(false)
      setShowRefactoredDashboard(false)
      setShowWorkflow(false)
      setShowTranslation(false)
      setShowVideo(false)
      setShowSubtitle(false)
      setShowSettings(false)
      setShowHelp(false)
      setShowMicroservice(false)
      setShowInteractiveDetail(false)
    } else if (featureId === 'subtitle-extraction') {
      setSelectedFeature('subtitle-extract')
      setShowConversationalDetail(true)
      setShowHomePage(false)
      setShowDashboard(false)
      setShowRefactoredDashboard(false)
      setShowWorkflow(false)
      setShowTranslation(false)
      setShowVideo(false)
      setShowSubtitle(false)
      setShowSettings(false)
      setShowHelp(false)
      setShowMicroservice(false)
      setShowInteractiveDetail(false)
    } else if (featureId === 'subtitle-erasure') {
      setSelectedFeature('subtitle-erase')
      setShowConversationalDetail(true)
      setShowHomePage(false)
      setShowDashboard(false)
      setShowRefactoredDashboard(false)
      setShowWorkflow(false)
      setShowTranslation(false)
      setShowVideo(false)
      setShowSubtitle(false)
      setShowSettings(false)
      setShowHelp(false)
      setShowMicroservice(false)
      setShowInteractiveDetail(false)
    } else if (featureId === 'video-subtitle-pressing') {
      setSelectedFeature('subtitle-burn')
      setShowConversationalDetail(true)
      setShowHomePage(false)
      setShowDashboard(false)
      setShowRefactoredDashboard(false)
      setShowWorkflow(false)
      setShowTranslation(false)
      setShowVideo(false)
      setShowSubtitle(false)
      setShowSettings(false)
      setShowHelp(false)
      setShowMicroservice(false)
      setShowInteractiveDetail(false)
    } else if (featureId === 'ai-video-narrative') {
      setSelectedFeature('ai-narration')
      setShowConversationalDetail(true)
      setShowHomePage(false)
      setShowDashboard(false)
      setShowRefactoredDashboard(false)
      setShowWorkflow(false)
      setShowTranslation(false)
      setShowVideo(false)
      setShowSubtitle(false)
      setShowSettings(false)
      setShowHelp(false)
      setShowMicroservice(false)
    }
  }

  const handleBackFromInteractive = () => {
    setShowInteractiveDetail(false)
    setShowHomePage(true)
  }

  const handleBackFromMicroservice = () => {
    setShowMicroservice(false)
    setShowHomePage(true)
  }

  const handleBackFromLogPage = () => {
    setShowLogPage(false)
    setShowHomePage(true)
  }

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* 主内容区域 */}
      <div className="flex-1 h-screen">
        {/* 顶部导航 */}
        <header className="bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">AI智能处理系统</h1>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => handleShowHomePage()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showHomePage 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                主页
              </button>
              <button
                onClick={() => handleShowTranslation()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showTranslation 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                翻译
              </button>
              <button
                onClick={() => handleShowVideo()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showVideo 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                视频
              </button>
              <button
                onClick={() => handleShowSubtitle()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showSubtitle 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                字幕
              </button>
              <button
                onClick={() => handleShowDashboard()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showDashboard 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                仪表板
              </button>
              <button
                onClick={() => handleShowRefactoredDashboard()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showRefactoredDashboard 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                重构仪表板
              </button>
              <button
                onClick={() => handleShowSettings()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showSettings 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                设置
              </button>
              <button
                onClick={() => handleShowHelp()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showHelp 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                帮助
              </button>
              <button
                onClick={() => handleShowMicroservice()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showMicroservice 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                微服务
              </button>
              <button
                onClick={() => handleShowApiIntegration()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showApiIntegration 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                API集成
              </button>
              <button
                onClick={() => handleShowLogPage()}
                className={`px-3 py-1.5 text-sm border rounded-md transition-colors ${
                  showLogPage 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'border-gray-300 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                日志
              </button>
              <span className="text-sm text-gray-500 dark:text-gray-400">AI智能处理系统</span>
            </div>
          </div>
        </header>
        
        {/* 内容区域 */}
        <main className="h-[calc(100vh-64px)] overflow-y-auto">
          {showHomePage ? (
            <HomePage onFeatureSelect={handleFeatureSelect} onWorkflowStart={handleWorkflowStart} />
          ) : showConversationalDetail ? (
            <ConversationalDetailPage />
          ) : showInteractiveDetail ? (
            <InteractiveDetailPage 
              featureType={'video-translate' as any}
              onBack={handleBackFromInteractive}
            />
          ) : showMicroservice ? (
            <MicroserviceIntegrationPage onBack={handleBackFromMicroservice} />          ) : showApiIntegration ? (
            <ApiIntegrationPage onBack={() => {
              setShowApiIntegration(false)
              setShowHomePage(true)
            }} />
          ) : showLogPage ? (
            <LogPage onBack={handleBackFromLogPage} />
          ) : showTranslation ? (
            <TranslationPage />
          ) : showVideo ? (
            <VideoPage />
          ) : showSubtitle ? (
            <SubtitlePage />
          ) : showDashboard ? (
            <DashboardPage />
          ) : showRefactoredDashboard ? (
            <div className="p-6">
              <RefactoredDashboard />
            </div>
          ) : showSettings ? (
            <SettingsPage />
          ) : showHelp ? (
            <HelpPage />
          ) : showWorkflow ? (
            <WorkflowSteps 
              type={workflowType} 
              onComplete={handleWorkflowComplete}
            />
          ) : (
            <div className="p-6 space-y-6">
              {/* 功能卡片区域 */}
              <FeatureCards 
                selectedFeature={selectedFeature}
                onFeatureSelect={handleFeatureSelectOld}
                onWorkflowStart={handleWorkflowStart}
              />
              
              {/* 翻译面板 */}
              <div className="bg-white dark:bg-gray-950 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  快速翻译
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  选择上方功能卡片开始使用，或使用顶部导航栏访问具体功能页面。
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
      
      <Toaster />
    </div>
  )
}

export default App