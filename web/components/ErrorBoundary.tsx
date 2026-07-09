"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { Card, Typography } from "../shared/design-system";

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an exception:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Standard design system compliant fallback card
      return (
        <div className="p-6">
          <Card title="Something went wrong" subtitle="Operational Panel Error Captured">
            <Typography.Paragraph className="mb-4">
              A runtime React exception occurred in this panel. Please refresh the page or contact systems administration.
            </Typography.Paragraph>
            {this.state.error && (
              <pre className="p-4 overflow-auto font-mono text-xs text-red-600 bg-red-50 dark:bg-red-950/20 rounded-lg">
                {this.state.error.stack || this.state.error.message}
              </pre>
            )}
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
