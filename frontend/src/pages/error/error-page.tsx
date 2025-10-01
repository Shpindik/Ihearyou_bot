import ErrorMessage from '@/pages/error/ui/error.tsx';
import { useParams } from 'react-router-dom';
const STATUS_PARAM_KEY = 'status';

export const ErrorPage = () => {
  const params = useParams<{ [STATUS_PARAM_KEY]: string }>();
  const status = Number(params[STATUS_PARAM_KEY]);

  const handleButtonClick = (): void => {
    if (status === 404) {
      window.history.back();
    } else {
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen white flex items-center justify-center">
      <div className="max-w-md w-full rounded-lg shadow-ui p-8 bg-white/60 mx-4">
        <ErrorMessage error={status} onButtonClick={handleButtonClick} />
      </div>
    </div>
  );
};

export default ErrorPage;

ErrorPage.url = `/error/:${STATUS_PARAM_KEY}`;
ErrorPage.displayName = 'ErrorPage' as const;
