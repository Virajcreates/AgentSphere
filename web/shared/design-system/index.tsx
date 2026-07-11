"use client";

import React, { ReactNode } from "react";

// ==============================================================================
// 1. DESIGN TOKENS & TYPOGRAPHY
// ==============================================================================
export const Typography = {
  H1: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <h1 className={`text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl ${className}`}>
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
    <code className={`px-1.5 py-0.5 font-mono text-xs bg-slate-100 dark:bg-slate-800/80 rounded border border-slate-200 dark:border-slate-700 text-pink-600 dark:text-pink-400 ${className}`}>
      {children}
    </code>
  ),
  Lead: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <p className={`text-base text-slate-400 dark:text-slate-500 leading-relaxed ${className}`}>
      {children}
    </p>
  ),
  Label: ({ children, className = "" }: { children: ReactNode; className?: string }) => (
    <span className={`text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider ${className}`}>
      {children}
    </span>
  ),
};

// ==============================================================================
// 2. DESIGN SYSTEM WIDGETS & BUTTONS
// ==============================================================================
export type ButtonVariant = "primary" | "secondary" | "destructive" | "outline" | "ghost";

export function Button({
  children,
  onClick,
  variant = "primary",
  type = "button",
  disabled = false,
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: ButtonVariant;
  type?: "button" | "submit" | "reset";
  disabled?: bool;
  className?: string;
}) {
  const baseStyle = "px-4 py-2 text-sm font-semibold rounded-lg transition-all duration-150 flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 disabled:active:scale-100";
  
  const variants: Record<ButtonVariant, string> = {
    primary: "bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-500/10 border border-blue-700",
    secondary: "bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200/50 dark:border-slate-700/50",
    destructive: "bg-red-600 hover:bg-red-500 text-white shadow-md shadow-red-500/10 border border-red-700",
    outline: "bg-transparent border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900 text-slate-700 dark:text-slate-300",
    ghost: "bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800/50 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}

// ==============================================================================
// 3. ELEVATED CARD PRIMITIVE
// ==============================================================================
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
    <div className={`p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-xl shadow-sm hover:shadow-md hover:border-slate-300 dark:hover:border-slate-700/50 transition-all duration-200 flex flex-col justify-between ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between mb-5">
          <div>
            {title && <Typography.H3>{title}</Typography.H3>}
            {subtitle && <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{subtitle}</p>}
          </div>
          {action && <div className="flex items-center gap-2">{action}</div>}
        </div>
      )}
      <div className="flex-1">{children}</div>
    </div>
  );
}

// ==============================================================================
// 4. POLISHED RESPONSIVE TABLE
// ==============================================================================
export function Table({
  headers,
  rows,
  emptyState,
}: {
  headers: string[];
  rows: ReactNode[][];
  emptyState?: ReactNode;
}) {
  return (
    <div className="w-full overflow-x-auto border border-slate-200 dark:border-slate-800/80 rounded-xl bg-white dark:bg-slate-900/20 shadow-sm">
      <table className="w-full text-left border-collapse">
        <thead className="bg-slate-50/50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-800">
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={headers.length} className="px-6 py-12 text-center text-sm text-slate-400">
                {emptyState || <EmptyState title="No items found" description="There are no records matching this table view." />}
              </td>
            </tr>
          ) : (
            rows.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50/30 dark:hover:bg-slate-800/10 transition-colors">
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

// ==============================================================================
// 5. ACCESSIBLE DIALOG MODAL
// ==============================================================================
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-lg p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl overflow-hidden animate-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between mb-5 border-b border-slate-100 dark:border-slate-800 pb-3">
          <Typography.H3>{title}</Typography.H3>
          <button onClick={onClose} className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            ✕
          </button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}

// ==============================================================================
// 6. DESIGN SYSTEM INPUT FORMS
// ==============================================================================
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
      <label htmlFor={id} className="block text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        id={id}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700/60 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-all duration-150"
        required={required}
      />
    </div>
  );
}

// ==============================================================================
// 7. POLISHED EMPTY STATES
// ==============================================================================
export function EmptyState({
  icon = "📂",
  title,
  description,
  action,
}: {
  icon?: string;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="p-8 text-center max-w-sm mx-auto flex flex-col items-center justify-center">
      <span className="text-4xl mb-4 select-none">{icon}</span>
      <Typography.H3 className="mb-2">{title}</Typography.H3>
      <Typography.Paragraph className="mb-6">{description}</Typography.Paragraph>
      {action}
    </div>
  );
}

// ==============================================================================
// 8. HIGH-PERFORMANCE SVG SPARKLINES (ZERO-DEPENDENCY CHARTS)
// ==============================================================================
export function Sparkline({
  data,
  color = "#3b82f6", // standard blue-500
  width = 120,
  height = 40,
}: {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}) {
  if (data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min === 0 ? 1 : max - min;

  const points = data
    .map((val, idx) => {
      const x = (idx / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={points} />
    </svg>
  );
}

export function MiniBarChart({
  data,
  color = "#3b82f6",
  width = 140,
  height = 50,
}: {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}) {
  if (data.length === 0) return null;

  const max = Math.max(...data);
  const range = max === 0 ? 1 : max;
  const barWidth = width / data.length - 3;

  return (
    <svg width={width} height={height} className="flex items-end overflow-visible">
      {data.map((val, idx) => {
        const barHeight = (val / range) * height;
        const x = idx * (barWidth + 3);
        const y = height - barHeight;
        return (
          <rect
            key={idx}
            x={x}
            y={y}
            width={barWidth}
            height={barHeight}
            fill={color}
            rx="2"
            className="transition-all duration-300 hover:opacity-80"
          />
        );
      })}
    </svg>
  );
}
