/* eslint-disable */

declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: string;
    VUE_ROUTER_BASE: string | undefined;
    AXIOS_BASE_URL: string;
  }
}
