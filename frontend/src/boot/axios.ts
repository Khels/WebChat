import axios, { AxiosInstance } from 'axios';
import applyCaseMiddleware from 'axios-case-converter';
import { boot } from 'quasar/wrappers';
import { PATH } from 'src/router/constants';
import { refreshAccessToken, setAuthorizationHeader } from 'src/services/auth';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// snake_case -> camelCase and backwards
const api = applyCaseMiddleware(axios.create({ baseURL: process.env.AXIOS_BASE_URL }));

setAuthorizationHeader();

export default boot(({ app, router }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  api.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error) => {
      const originalConfig = error.config;

      if (error.response?.status === 401) {
        if (!originalConfig._retry) {
          originalConfig._retry = true;
          try {
            // if this request failes, the user will be redirected to a sign in page
            const accessToken = await refreshAccessToken();
            
            setAuthorizationHeader(accessToken);
            originalConfig.headers.Authorization = `Bearer ${accessToken}`;

            // repeat initial request with refreshed access token
            return api(originalConfig);
          } catch (error) {
            router.push({ name: PATH.SIGN_IN });
          }
          return Promise.reject(error);
        }
      }
      return Promise.reject(error);
    }
  );
});

export { api };
