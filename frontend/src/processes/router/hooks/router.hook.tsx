import {
  createBrowserRouter,
  Navigate,
  Outlet,
  RouteObject,
} from 'react-router-dom';
import { useMemo } from 'react';
import AuthGuard from '@/shared/guards/auth-guard';
import LoginPage from "@/pages/login/login-page.tsx";
import ErrorPage from "@/pages/error/error-page.tsx";

export const useRouter = () => {
  const routes: RouteObject[] = useMemo(() => {
    return [
      {
        path: '/',
        element: (
          <AuthGuard>
            <Outlet />
          </AuthGuard>
        ),
        children: [
          {
            path: '/login',
            Component: LoginPage,
          },
          {
            path: '*',
            element: <Navigate to={'/login'} replace />,
          },
          {
            index: true,
            element: <Navigate to={'/login'} replace />,
          },
        ],
      },
      {
        path: ErrorPage.url,
        Component: ErrorPage,
      },
    ];
  }, []);

  const router = useMemo(() => createBrowserRouter(routes), [routes]);

  return { router };
};
