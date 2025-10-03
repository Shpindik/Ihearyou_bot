import ApiErrorBoundary from '@/shared/error-boundary/api-error-boundary.tsx';
import ErrorBoundary from '@/shared/error-boundary/error-boundary.tsx';
import AppRoutes from '../processes/router/app-router.tsx';
import './fonts.less';
import './normalize.less';
import './styles/globals.css';

function App() {
  return (
    <ErrorBoundary>
      <ApiErrorBoundary>
        <AppRoutes />
      </ApiErrorBoundary>
    </ErrorBoundary>
  );
}

export default App;
