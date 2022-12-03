import { api, client } from 'src/boot/axios';
import { TokenResponse } from 'src/models/auth';

export async function refreshAccessToken() {
  // this instance of axios doesn't have any interceptors so there won't be infinite retry
  const { data } = await client.post<TokenResponse>(
    process.env.AXIOS_BASE_URL + '/token/refresh',
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
