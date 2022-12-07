import axios from 'axios';
import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import { useNotifications } from 'src/composables/notifications';
import { TokenResponse, User } from 'src/models/auth';
import { PATH } from 'src/router/constants';
import { setAuthorizationHeader } from 'src/services/auth';

const notify = useNotifications();

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
  }),
  getters: {
    displayName(): string {
      if (!this.user) return '';

      let name = '';
      if (this.user?.firstName) {
        name = this.user?.firstName;
        if (this.user?.lastName) {
          name = name + ' ' + this.user?.lastName;
        }
      }

      return name ? name : this.user?.username
    }
  },
  actions: {
    async getCurrentUser() {
      try {
        const { data } = await api.get<User>('users/me');

        this.user = data;
      } catch (error) {
        notify.error();
      }
    },
    async signUp(username: string, password: string, passwordConfirm: string) {
      try {
        await api.post(
          'register',
          {
            username: username,
            password: password,
            passwordConfirm: passwordConfirm
          }
        );

        // get access and refresh tokens
        await this.signIn(username, password);
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
    },
    async signIn(username: string, password: string) {
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
        await this.getCurrentUser();

        // redirect to main page
        this.router.push({ name: PATH.CHAT });
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
    },
    async signOut() {
      try {
        await api.post('token/revoke');

        this.user = null;
        delete api.defaults.headers.Authorization;

        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');

        // redirect to sign in page
        this.router.push({ name: PATH.SIGN_IN });
      } catch (error) {
        notify.error();
      }
    },
  },
});
