import * as React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-primary-600 text-white',
      secondary: 'bg-gray-200 text-gray-900 dark:bg-gray-800 dark:text-gray-100',
      destructive: 'bg-red-600 text-white',
      outline: 'border border-gray-300 text-gray-700 dark:border-gray-700 dark:text-gray-300',
    };
    
    return (
      <div
        ref={ref}
        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variants[variant]} ${className}`}
        {...props}
      />
    );
  }
);
Badge.displayName = 'Badge';

export { Badge };