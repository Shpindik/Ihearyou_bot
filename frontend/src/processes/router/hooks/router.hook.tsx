import {
  ErrorPage,
  DashBoardPage,
  FilesPage,
  LoginPage,
  EditPage,
  AccessPage,
  RemindersPage,
} from '@/pages/index.ts';
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
            path: '/login',
            Component: LoginPage,
          },
          {
            path: '/dashboard',
            Component: DashBoardPage,
          },
          {
            path: '/files',
            Component: FilesPage,
          },
          {
            path: '/edit',
            Component: EditPage,
          },
          {
            path: '/access',
            Component: AccessPage,
          },
          {
            path: '/reminders',
            Component: RemindersPage,
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
