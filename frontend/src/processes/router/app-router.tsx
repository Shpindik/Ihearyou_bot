import { RouterProvider } from 'react-router-dom';
import { useRouter } from './hooks';

const AppRoutes = () => {
  const { router } = useRouter();

  return <RouterProvider router={router}></RouterProvider>;
};

export default AppRoutes;
