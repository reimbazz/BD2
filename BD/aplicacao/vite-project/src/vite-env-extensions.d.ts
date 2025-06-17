/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_HMR_FORCE_FULL_RELOAD: string
  readonly VITE_HMR_TIMEOUT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
