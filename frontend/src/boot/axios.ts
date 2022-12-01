import axios, { AxiosInstance } from 'axios';
import applyCaseMiddleware from 'axios-case-converter';
import { boot } from 'quasar/wrappers';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// snake_case -> camelCase and backwards
const api = applyCaseMiddleware(axios.create({ baseURL: process.env.AXIOS_BASE_URL }));



export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  // api.interceptors.response.use(response =>  response
  // , async (error) => {
    
  //   redirect('/');
  //   const originalRequest = error.config;
  
  //   if (error.response?.status === 401 && !originalRequest._retry) {
  //     originalRequest._retry = true;
  //     const accessToken = await refreshAccessToken();
  //     api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  //     return api(originalRequest);
  //   } else {
  //     // redirect({ name: PATH.SIGN_IN });
  //   }
  //   return Promise.reject(error);
  // });
});

export { api };
