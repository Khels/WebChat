import { boot } from 'quasar/wrappers';
import { useUserStore } from 'src/stores/user-store';

export default boot(async ({ router }) => {
  const userStore = useUserStore();

  router.beforeEach(async (to, from) => {
    if (to.meta.requiresAuth && !userStore.user) {
      // this route requires auth, check if logged in,
      // otherwise axios interceptor will handle the authentication
      await userStore.getCurrentUser();
    }
  })
})
