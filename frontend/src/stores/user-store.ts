import axios from 'axios';
import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import { useNotifications } from 'src/composables/notifications';
import { TokenResponse, User } from 'src/models/auth';
import { PATH } from 'src/router/constants';
import router from 'src/router/index';
import { setAuthorizationHeader } from 'src/services/auth';
import { computed, ref } from 'vue';


export const useUserStore = defineStore('user', () => {
  const notify = useNotifications();

  const user = ref<User | null>(null);

  const displayName = computed(() => {
    if (!user.value) return '';

    let name = '';
    if (user.value?.firstName) {
      name = user.value?.firstName;
      if (user.value?.lastName) {
        name = name + ' ' + user.value?.lastName;
      }
    }

    return name ? name : user.value?.username
  })

  async function getCurrentUser() {
    try {
      const { data } = await api.get<User>('users/me');

      user.value = data;
    } catch (error) {
      notify.error();
    }
  }

  async function signUp(username: string, password: string, passwordConfirm: string) {
    try {
      await api.post(
        'register',
        {
          username,
          password,
          passwordConfirm
        }
      );

      // get access and refresh tokens
      await signIn(username, password);
    } catch (error) {
      let message;

      if (axios.isAxiosError(error)) {
        switch (error.response?.status) {
          case 409:
            message = 'Это имя уже занято';
            break;
          case 400:
            message = 'Пароли не совпадают';
          default:
            break;
        }
      }

      notify.error(message);
    }
  }

  async function signIn(username: string, password: string) {
    const userData = new FormData();
    userData.append('username', username);
    userData.append('password', password);

    try {
      const { data } = await api.post<TokenResponse>(
        'token',
        userData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setAuthorizationHeader(data.accessToken);

      // save tokens to localStorage
      localStorage.setItem('accessToken', data.accessToken);
      localStorage.setItem('refreshToken', data.refreshToken);

      // get current user based on access token set above
      await getCurrentUser();

      // redirect to main page
      router.push({ name: PATH.CHAT });
    } catch (error) {
      let message;

      if (axios.isAxiosError(error)) {
        switch (error.response?.status) {
          case 404:
            message = 'Неверное имя пользователя';
            break;
          case 400:
            message = 'Неверный пароль';
          default:
            break;
        }
      }

      notify.error(message);
    }
  }

  async function signOut() {
    try {
      await api.post('token/revoke');

      user.value = null;
      delete api.defaults.headers.Authorization;

      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');

      // redirect to sign in page
      router.push({ name: PATH.SIGN_IN });
    } catch (error) {
      notify.error();
    }
  }

  async function searchUsers(q: string) {
    try {
      const { data } = await api.get(`users/search/?q=${q}`);

      return data
    } catch (error) {
      notify.error();
    }
  }

  return {
    user,
    displayName,
    searchUsers,
    getCurrentUser,
    signUp,
    signIn,
    signOut,
  }
});
