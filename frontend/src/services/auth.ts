import axios from 'axios';
import { api } from 'src/boot/axios';
import { TokenResponse } from 'src/models/auth';

import applyCaseMiddleware from 'axios-case-converter';

export async function refreshAccessToken() {
  // this instance of axios doesn't have any interceptors so there won't be infinite retry
  const client = applyCaseMiddleware(axios.create({ baseURL: process.env.AXIOS_BASE_URL }));
  const { data } = await client.post<TokenResponse>(
    'token/refresh',
    {},
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('refreshToken')}`
      }
    }
  );

  // save tokens to a local storage
  localStorage.setItem('accessToken', data.accessToken);
  localStorage.setItem('refreshToken', data.refreshToken);

  return data.accessToken;
}

export function setAuthorizationHeader(
  token: string | null = null,
  tokenType = 'accessToken'
) {
  token = token ? token : localStorage.getItem(tokenType);
  if (token) {
    api.defaults.headers.Authorization = `Bearer ${token}`;
  }
}
