/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly REACT_APP_API_BASE_URL?: string
  readonly REACT_APP_ENVIRONMENT?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}