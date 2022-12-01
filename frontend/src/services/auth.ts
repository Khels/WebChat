import { api } from 'src/boot/axios';

export async function refreshAccessToken() {
  await api.get('');
}
