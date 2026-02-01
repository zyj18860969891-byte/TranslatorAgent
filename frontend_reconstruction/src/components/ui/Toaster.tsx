import * as React from 'react'

interface ToastProps {
  title?: string
  description?: string
  variant?: 'default' | 'destructive'
}

const Toaster: React.FC = () => {
  return null // 简化实现，实际项目中可以使用react-hot-toast等库
}

export { Toaster }
export type { ToastProps }