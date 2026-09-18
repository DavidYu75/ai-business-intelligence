import nextCoreWebVitals from 'eslint-config-next/core-web-vitals'
import tseslint from 'typescript-eslint'
import globals from 'globals'

// Flat config, replacing .eslintrc.json. ESLint 9 no longer reads eslintrc
// by default, and eslint-config-next 16 only ships flat config.
export default [
  {
    ignores: ['.next/**', 'coverage/**', 'node_modules/**', 'next-env.d.ts'],
  },

  // was: "extends": ["next/core-web-vitals"]
  ...nextCoreWebVitals,

  // was: "extends": ["plugin:@typescript-eslint/recommended"]
  // The unified `typescript-eslint` package now supplies the plugin and the
  // parser together, which is why the two separate @typescript-eslint/*
  // packages are gone from package.json.
  ...tseslint.configs.recommended,

  {
    files: ['**/*.{js,jsx,ts,tsx}'],
    // was: "env": { "browser": true, "es2021": true, "node": true }
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021,
      },
    },
    // carried over verbatim from .eslintrc.json
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      'react-hooks/exhaustive-deps': 'warn',
    },
  },
]
