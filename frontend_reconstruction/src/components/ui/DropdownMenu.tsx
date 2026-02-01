import * as React from 'react';
import { ChevronDown } from 'lucide-react';

interface DropdownMenuProps {
  trigger: React.ReactNode;
  children?: React.ReactNode;
}

interface DropdownMenuItemProps {
  children?: React.ReactNode;
  onClick?: () => void;
}

const DropdownMenu: React.FC<DropdownMenuProps> = ({ trigger, children }) => {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="relative">
      <div onClick={() => setOpen(!open)} className="cursor-pointer">
        {trigger}
      </div>
      {open && (
        <>
          <div 
            className="fixed inset-0" 
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-48 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-950 z-50">
            {children}
          </div>
        </>
      )}
    </div>
  );
};

const DropdownMenuTrigger: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <button className="flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
      {children}
      <ChevronDown className="h-4 w-4" />
    </button>
  );
};

const DropdownMenuContent: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div className="absolute right-0 mt-2 w-48 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-950">
      {children}
    </div>
  );
};

const DropdownMenuItem: React.FC<DropdownMenuItemProps> = ({ children, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800 cursor-pointer"
    >
      {children}
    </div>
  );
};

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem };