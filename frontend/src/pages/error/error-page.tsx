import { useParams } from 'react-router-dom';

const STATUS_PARAM_KEY = 'status';

const ErrorPage = () => {
  const params = useParams<{ [STATUS_PARAM_KEY]: string }>();
  const status = params[STATUS_PARAM_KEY];

  const errorMessage = () => {
    switch (status) {
      case '404':
        return 'Page Not Found';

      case '500':
        return 'Server Error';

      default:
        return null;
    }
  };

  return (
    <div>Страница ошибок, через свич-кейс по статусам: {errorMessage()}</div>
  );
};

export default ErrorPage;

ErrorPage.url = `/error/:${STATUS_PARAM_KEY}`;
ErrorPage.displayName = 'ErrorPage' as const;
