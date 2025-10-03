import react from '@vitejs/plugin-react-swc';
import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import svgr from 'vite-plugin-svgr';
import tsconfigPaths from 'vite-tsconfig-paths';

const envDir = path.resolve(__dirname, 'environment');
const loadEnvVariables = (mode: string): void => {
  Object.assign(process.env, loadEnv(mode, envDir, ''));
  console.debug(
    'process.env contains: \n' + JSON.stringify(process.env, undefined, 2),
  );
};

export default defineConfig(({ mode }) => {
  loadEnvVariables(mode);

  return {
    plugins: [
      svgr(),
      react({
        tsDecorators: true,
      }),
      tsconfigPaths(),
    ],
    build: {
      modulePreload: true,
      target: 'esnext',
      minify: false,
      cssCodeSplit: false,
    },
    envPrefix: ['VITE_', 'APP', 'SERVICE'],
    server: {
      port: 3001,
    },
    preview: {
      port: 4173,
      strictPort: true,
    },
    css: {
      postcss: './postcss.config.js',
    },
  };
});
