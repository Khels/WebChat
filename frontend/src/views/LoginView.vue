<script setup>
import { nextTick, onBeforeUnmount, onMounted } from 'vue';

onMounted(async () => {
  await nextTick()
  document.documentElement.classList.add('override-html')
  document.body.classList.add('override-body')
})

onBeforeUnmount(async () => {
  await nextTick()
  document.documentElement.classList.remove('override-html')
  document.body.classList.remove('override-body')
})
</script>

<template>
  <main class="form-login text-center">
    <form>
      <img class="mb-3 chat-icon" src="/img/chat-icon.png" alt="" width="72" height="72" draggable="false">
      <h1 class="h3 mb-3 fw-normal">Вход</h1>

      <div class="form-floating">
        <input type="text" class="form-control" id="floatingInput" placeholder="name@example.com">
        <label for="floatingInput">Псевдоним</label>
      </div>
      <div class="form-floating">
        <input type="password" class="form-control" id="floatingPassword" placeholder="Password">
        <label for="floatingPassword">Пароль</label>
      </div>

      <div class="checkbox mb-3">
        <label>
          <input type="checkbox" value="remember-me"> Запомнить меня
        </label>
      </div>
      <button class="w-100 btn btn-lg btn-primary" type="submit">Войти</button>
      <p class="mt-5 mb-3 text-muted">© 2022</p>
    </form>
  </main>
</template>

<style>
  .override-html,
  .override-body {
    height: 100%;
  }

  .override-body {
    display: flex;
    text-align: center !important;
    align-items: center;
    padding-top: 40px;
    padding-bottom: 40px;
    background-color: #f5f5f5;
  }
</style>

<style scoped>
  .form-login {
    width: 100%;
    max-width: 330px;
    padding: 15px;
    margin: auto;
  }

  .form-login .checkbox {
    font-weight: 400;
  }

  .form-login .form-floating:focus-within {
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

  .chat-icon {
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
  }

  .bd-placeholder-img {
    font-size: 1.125rem;
    text-anchor: middle;
    -webkit-user-select: none;
    -moz-user-select: none;
    user-select: none;
  }

  @media (min-width: 768px) {
    .bd-placeholder-img-lg {
      font-size: 3.5rem;
    }
  }
</style>
