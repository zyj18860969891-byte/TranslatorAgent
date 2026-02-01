import * as React from 'react';
import { Upload } from 'lucide-react';

interface FileInputProps {
  onChange?: (file: File | null) => void;
  accept?: string;
  multiple?: boolean;
  className?: string;
}

const FileInput: React.FC<FileInputProps> = ({ onChange, accept, multiple, className }) => {
  const [fileName, setFileName] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFileName(file ? file.name : null);
    onChange?.(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={className}>
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileChange}
        className="hidden"
      />
      <div
        onClick={handleClick}
        className="flex items-center justify-center gap-2 w-full h-32 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-900 dark:hover:bg-gray-800 cursor-pointer transition-colors"
      >
        <Upload className="h-6 w-6 text-gray-400" />
        <div className="text-center">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {fileName || '点击或拖拽文件到此处'}
          </p>
          {accept && (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              支持格式: {accept}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export { FileInput };
