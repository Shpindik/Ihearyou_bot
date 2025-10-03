import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import eslintPluginUnicorn from 'eslint-plugin-unicorn';
import fsdPlugin from '@conarti/eslint-plugin-feature-sliced';

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    settings: {},
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      unicorn: eslintPluginUnicorn,
      '@conarti/feature-sliced': fsdPlugin,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-hooks/exhaustive-deps': 'warn',
      'react-refresh/only-export-components': 'off',
      'unicorn/filename-case': [
        'error',
        {
          cases: {
            // файлы создаем только в kebab-case
            kebabCase: true,
          },
        },
      ],
      '@conarti/feature-sliced/layers-slices': ['error', {}],
      '@conarti/feature-sliced/public-api': 'error',
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
);
