import * as React from 'react';
import { X } from 'lucide-react';

interface DialogProps {
  open: boolean;
  onOpenChange?: (open: boolean) => void;
  title?: string;
  description?: string;
  children?: React.ReactNode;
}

const Dialog: React.FC<DialogProps> = ({ open, onOpenChange, title, description, children }) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="fixed inset-0 bg-black/50" 
        onClick={() => onOpenChange?.(false)}
      />
      <div className="relative z-50 w-full max-w-lg rounded-lg bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 shadow-lg">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
          <div>
            {title && <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h2>}
            {description && <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>}
          </div>
          <button
            onClick={() => onOpenChange?.(false)}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md"
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>
        <div className="p-4">
          {children}
        </div>
      </div>
    </div>
  );
};

export { Dialog };