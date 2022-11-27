<script setup>
import { useVuelidate } from '@vuelidate/core';
import { required } from '@vuelidate/validators';
import { reactive } from 'vue';

const state = reactive({
  username: "",
  password: ""
})

const rules = {
  username: {
    required
  },
  password: {
    required
  }
}

const v$ = useVuelidate(rules, state)

async function login() {
  
}

async function submitForm() {
  await v$.value.$validate()

  if (!v$.value.$error) {
    console.log("login");
    await login()
  }
}
</script>

<template>
  <div class="container-fluid vh-100">
    <div class="row h-100">
      <div class="col form-container">
        <form class="form-login" novalidate>
          <img class="mb-3 chat-icon" src="/img/chat-icon.png" alt="" width="72" height="72" draggable="false">
          <h1 class="h3 mb-3 fw-normal">Вход</h1>
          <div class="input-group">
            <span class="input-group-text" id="atPrepend">@</span>
            <div class="form-floating">
              <input type="text" class="form-control" id="usernameInput" aria-describedby="atPrepend" placeholder="Имя пользователя"
                v-model="state.username"
              >
              <label for="usernameInput">Имя пользователя</label>
            </div>
            <div class="input-errors" v-for="error of v$.username.$errors" :key="error.$uid">
              <div class="error-msg">{{ error.$message }}</div>
            </div>
          </div>
          <div class="input-group">
            <div class="form-floating">
              <input type="password" class="form-control" id="passwordInput" placeholder="Пароль"
                v-model="state.password"
              >
              <label for="passwordInput">Пароль</label>
            </div>
            <div class="invalid-feedback">
              Please choose a username.
            </div>
          </div>
          <button class="w-100 btn btn-lg btn-primary mt-3" type="button" @click="submitForm">Войти</button>
          <p class="mt-5 mb-3 text-muted">© 2022</p>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .form-container {
    display: flex;
    text-align: center !important;
    align-items: center;
    padding-top: 40px;
    padding-bottom: 40px;
    background-color: #f5f5f5;
  }

  .form-login {
    width: 100%;
    max-width: 330px;
    padding: 15px;
    margin: auto;
  }

  .form-login {
    font-weight: 400;
  }

  .form-login {
    z-index: 2;
  }

  .form-login input[type="text"] {
    margin-bottom: -1px;
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }

  .form-login input[type="password"] {
    margin-bottom: 10px;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  .input-errors {
    text-align: start !important;
    width: 100%;
    margin-top: .25rem;
    font-size: .875em;
    color: #dc3545;
  }

  .chat-icon {
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
  }

  #atPrepend {
    border-bottom-left-radius: 0 !important;
  }
</style>
