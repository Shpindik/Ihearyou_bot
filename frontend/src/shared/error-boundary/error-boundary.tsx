import { Component, ErrorInfo, PropsWithChildren } from 'react';

export type ErrorBoundaryProps = PropsWithChildren;
export type ErrorBoundaryState = object;

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: PropsWithChildren) {
    super(props);
  }

  static getDerivedStateFromError() {
    return null;
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary:');
    console.error('Error:', error);
    if (errorInfo.componentStack) {
      console.error('ErrorInfo:', errorInfo?.componentStack);
    }
  }

  render() {
    return <>{this.props?.children}</>;
  }
}

export default ErrorBoundary;
