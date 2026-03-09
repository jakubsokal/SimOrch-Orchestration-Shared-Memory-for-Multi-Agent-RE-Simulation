import React from 'react';

interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  fullWidth?: boolean;
  error?: string;
}

export default function FormTextarea({ label, fullWidth, error, className = '', ...props }: FormTextareaProps) {
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          {label}
        </label>
      )}
      <textarea
        className={`
          px-3 py-2 text-sm rounded-lg border resize-none
          ${error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-200 focus:ring-blue-500 focus:border-blue-500'}
          bg-white placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-offset-0
          transition-colors
          ${fullWidth ? 'w-full' : ''}
          ${className}
        `}
        rows={3}
        {...props}
      />
      {error && (
        <p className="mt-1 text-xs text-red-500">{error}</p>
      )}
    </div>
  );
}