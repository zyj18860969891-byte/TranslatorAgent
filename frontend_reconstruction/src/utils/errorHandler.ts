import { toast } from '../components/ui/useToast';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
  }
}

export const handleError = (error: any) => {
  if (error instanceof APIError) {
    // API错误处理
    console.error(`API Error ${error.status}: ${error.message}`);
    
    let userMessage = '发生API错误';
    
    switch (error.status) {
      case 400:
        userMessage = '请求参数错误，请检查输入';
        break;
      case 401:
        userMessage = '认证失败，请重新登录';
        break;
      case 403:
        userMessage = '没有权限访问该资源';
        break;
      case 404:
        userMessage = '请求的资源不存在';
        break;
      case 500:
        userMessage = '服务器内部错误，请稍后重试';
        break;
      case 503:
        userMessage = '服务暂时不可用，请稍后重试';
        break;
      default:
        userMessage = `API错误: ${error.message}`;
    }
    
    // 显示错误提示
    toast({
      title: '错误',
      description: userMessage,
      variant: 'destructive',
    });
    
    return { error: userMessage, status: error.status };
  } else if (error instanceof Error) {
    // 一般错误处理
    console.error(`Error: ${error.message}`);
    
    const userMessage = '发生未知错误';
    
    toast({
      title: '错误',
      description: userMessage,
      variant: 'destructive',
    });
    
    return { error: userMessage };
  } else {
    // 未知错误
    console.error('Unknown error:', error);
    
    const userMessage = '发生未知错误';
    
    toast({
      title: '错误',
      description: userMessage,
      variant: 'destructive',
    });
    
    return { error: userMessage };
  }
};

// 简化的错误边界组件
export const ErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return children;
};