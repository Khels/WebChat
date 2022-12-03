<template>
  <q-page class="window-height window-width row justify-center items-center">
    <q-card square class="shadow-24 auth-card">
      <q-card-section class="bg-deep-purple-7">
        <h4 class="text-h5 text-white q-my-md">
          Регистрация
        </h4>
      </q-card-section>
      <q-card-section>
        <q-form
          ref="signUpForm"
          @submit.prevent="submit"
          class="q-gutter-md"
        >
          <q-input
            v-model="username"
            label="Имя пользователя *"
            lazy-rules
            :rules="[required]"
          >
            <template v-slot:prepend>
              <q-icon name="person" />
            </template>
          </q-input>

          <q-input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            label="Придумайте пароль *"
            lazy-rules
            :rules="[required]"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="showPassword ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="showPassword = !showPassword"
              />
            </template>
          </q-input>
          <q-input
            v-model="passwordConfirm"
            :type="showPasswordConfirm ? 'text' : 'password'"
            label="Повторите пароль *"
            lazy-rules
            :rules="[
              required,
              val => val && val === password || 'Пароли должны совпадать'
            ]"
          >
            <template v-slot:prepend>
              <q-icon name="lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="showPasswordConfirm ? 'visibility_off' : 'visibility'"
                class="cursor-pointer"
                @click="(showPasswordConfirm = !showPasswordConfirm)"
              />
            </template>
          </q-input>
        </q-form>
      </q-card-section>
      <q-card-actions class="q-px-lg">
        <q-btn
          unelevated 
          size="lg"
          color="secondary"
          @click="submit"          
          class="full-width text-white"
          label="Войти"
        />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import type { QForm, QInput } from 'quasar';
import { useUserStore } from 'src/stores/user-store';
import { required } from 'src/utils/validators';
import { ref } from 'vue';

const userStore = useUserStore();

const username = ref<string>('');
const password = ref<string>('');
const passwordConfirm = ref<string>('');

const showPassword = ref<boolean>(false);
const showPasswordConfirm = ref<boolean>(false);

const signUpForm = ref<QForm>();

async function submit() {
  signUpForm.value?.getValidationComponents().forEach(
    async (field: QInput) => {
      await field.validate()
    }
  )

  if (await signUpForm.value?.validate()) {
    await userStore.signUp(username.value, password.value, passwordConfirm.value);
  }
}
</script>
