"use client";

import React, { ReactNode } from "react";

// 1. Shared Typography Elements conforming to Design tokens
export const Typography = {
  H1: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <h1 className={`text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white ${className}`}>
      {children}
    </h1>
  ),
  H2: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <h2 className={`text-2xl font-bold tracking-tight text-slate-900 dark:text-white ${className}`}>
      {children}
    </h2>
  ),
  H3: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <h3 className={`text-lg font-semibold text-slate-900 dark:text-white ${className}`}>
      {children}
    </h3>
  ),
  Paragraph: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <p className={`text-sm text-slate-500 dark:text-slate-400 leading-relaxed ${className}`}>
      {children}
    </p>
  ),
  Code: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <code className={`px-1.5 py-0.5 font-mono text-xs bg-slate-100 dark:bg-slate-800 rounded text-pink-600 dark:text-pink-400 ${className}`}>
      {children}
    </code>
  ),
};

// 2. Shared responsive Card Container
export function Card({
  title,
  subtitle,
  children,
  action,
  className = "",
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={`p-6 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && <Typography.H3>{title}</Typography.H3>}
            {subtitle && <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}

// 3. Shared standardized Table Layout
export function Table({
  headers,
  rows,
  emptyMessage = "No items available.",
}: {
  headers: string[];
  rows: ReactNode[][];
  emptyMessage?: string;
}) {
  return (
    <div className="w-full overflow-x-auto border border-slate-200 dark:border-slate-800 rounded-lg">
      <table className="w-full text-left border-collapse">
        <thead className="bg-slate-50 dark:bg-slate-800/50">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 border-b border-slate-200 dark:border-slate-800">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={headers.length} className="px-6 py-10 text-center text-sm text-slate-400">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors">
                {row.map((cell, j) => (
                  <td key={j} className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">
                    {cell}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

// 4. Shared accessible Modal Dialog trigger wrapper
export function Dialog({
  isOpen,
  onClose,
  title,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-lg p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-lg">
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 dark:border-slate-800 pb-3">
          <Typography.H3>{title}</Typography.H3>
          <button onClick={onClose} className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-slate-400 hover:text-slate-600 transition-colors">
            ✕
          </button>
        </div>
        <div className="mb-6">{children}</div>
      </div>
    </div>
  );
}

// 5. Shared dynamic Input field element
export function FormField({
  label,
  id,
  type = "text",
  placeholder,
  value,
  onChange,
  required = false,
}: {
  label: string;
  id: string;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (val: string) => void;
  required?: boolean;
}) {
  return (
    <div className="mb-4">
      <label htmlFor={id} className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1.5">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        id={id}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all"
        required={required}
      />
    </div>
  );
}
export default Card;
