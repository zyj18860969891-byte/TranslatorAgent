import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 翻译API
export const translateText = async (text: string, targetLang: string) => {
  const response = await apiClient.post('/translation/translate', {
    text,
    target_language: targetLang,
  })
  return response.data
}

// 视频处理API
export const processVideo = async (videoFile: File, targetLang: string) => {
  const formData = new FormData()
  formData.append('video', videoFile)
  formData.append('target_language', targetLang)
  
  const response = await apiClient.post('/video/process', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// 健康检查
export const healthCheck = async () => {
  const response = await apiClient.get('/health')
  return response.data
}