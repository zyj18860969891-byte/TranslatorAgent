// Toast hook implementation

interface ToastProps {
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
}

export const toast = (props: ToastProps) => {
  // 简单的toast实现
  const { title, description, variant = 'default' } = props;
  
  // 创建toast元素
  const toastEl = document.createElement('div');
  toastEl.className = `fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
    variant === 'destructive' 
      ? 'bg-red-600 text-white' 
      : 'bg-gray-900 text-white'
  }`;
  
  toastEl.innerHTML = `
    ${title ? `<div class="font-semibold mb-1">${title}</div>` : ''}
    ${description ? `<div class="text-sm opacity-90">${description}</div>` : ''}
  `;
  
  document.body.appendChild(toastEl);
  
  // 3秒后自动移除
  setTimeout(() => {
    toastEl.style.opacity = '0';
    toastEl.style.transition = 'opacity 0.3s';
    setTimeout(() => {
      if (toastEl.parentNode) {
        toastEl.parentNode.removeChild(toastEl);
      }
    }, 300);
  }, 3000);
};