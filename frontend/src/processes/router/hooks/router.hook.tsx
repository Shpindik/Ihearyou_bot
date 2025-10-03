import { ErrorPage, LoginPage, MainPage } from '@/pages/index.ts';
import AuthGuard from '@/shared/guards/auth-guard.tsx';
import { useMemo } from 'react';
import {
  createBrowserRouter,
  Navigate,
  Outlet,
  RouteObject,
} from 'react-router-dom';

export const useRouter = () => {
  const routes: RouteObject[] = useMemo(() => {
    return [
      {
        path: '/login',
        Component: LoginPage,
      },
      {
        path: '/',
        element: (
          <AuthGuard>
            <Outlet />
          </AuthGuard>
        ),
        children: [
          {
            path: '/admin',
            Component: MainPage,
          },
          {
            path: '*',
            element: <Navigate to={'/error/404'} replace />,
          },
          {
            index: true,
            element: <Navigate to={'/admin'} replace />,
          },
        ],
      },
      {
        path: ErrorPage.url,
        Component: ErrorPage,
      },
      {
        path: '*',
        element: <Navigate to={'/error'} replace />,
      },
    ];
  }, []);

  const router = useMemo(() => createBrowserRouter(routes), [routes]);

  return { router };
};
