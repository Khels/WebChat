import { RouteRecordRaw } from 'vue-router';
import { PATH } from './constants';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: { name: PATH.CHAT }
  },
  {
    path: '/auth',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      {
        path: 'sign-up',
        name: PATH.SIGN_UP,
        component: () => import('pages/SignUpPage.vue')
      },
      {
        path: 'sign-in',
        name: PATH.SIGN_IN,
        component: () => import('pages/SignInPage.vue')
      }
    ]
  },
  {
    path: '/chats',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: PATH.CHAT,
        component: () => import('pages/ChatPage.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
