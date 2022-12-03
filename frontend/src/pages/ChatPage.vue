<template>
  <q-page class="row items-start justify-evenly">
    <div class="q-pa-md row justify-center">
      <div style="width: 100%; max-width: 400px">
        <q-chat-message
          name="me"
          avatar="https://cdn.quasar.dev/img/avatar3.jpg"
          :text="['hey, how are you?']"
          stamp="7 minutes ago"
          sent
          bg-color="amber-7"
        />
        <q-chat-message
          name="Jane"
          avatar="https://cdn.quasar.dev/img/avatar5.jpg"
          :text="[
            'doing fine, how r you?',
            'I just feel like typing a really, really, REALLY long message to annoy you...'
          ]"
          size="6"
          stamp="4 minutes ago"
          text-color="white"
          bg-color="primary"
        />
        <q-chat-message
          name="Jane"
          avatar="https://cdn.quasar.dev/img/avatar5.jpg"
          :text="['Did it work?']"
          stamp="1 minutes ago"
          size="8"
          text-color="white"
          bg-color="primary"
        />
        <q-chat-message
          name="Jane"
          avatar="https://cdn.quasar.dev/img/avatar5.jpg"
          bg-color="primary"
        >
          <q-spinner-dots size="2rem" />
        </q-chat-message>
      </div>
    </div>
    <q-page-scroller reverse position="top" :scroll-offset="20" :offset="[0, 18]">
      <q-btn fab icon="keyboard_arrow_down" color="accent" />
    </q-page-scroller>
  </q-page>
</template>

<script setup lang="ts">
import { useUserStore } from 'src/stores/user-store';
import { ref } from 'vue';

interface TokenMessage {
  token: string | null
}

interface Message {
  id: string,
  text: string[],
  own: boolean
}

const userStore = useUserStore();

const message = ref('');
const messages = ref<Message[]>([]);

const ws = new WebSocket('ws://127.0.0.1:8000/api/v1/chat/');

ws.onopen = (event) => {
  sendMessage({ token: localStorage.getItem('accessToken') });
}

ws.onmessage = (event) => {
  let data = JSON.parse(event.data);
  console.log('onmessage', data);
  messages.value.push({text: data.message, own: data.client === clientId});
}

ws.onclose = (event) => {
  console.log('ws closed: ', event);
  if (event.code === 4000) {
    // authentication failed
  }
}

function sendMessage(msg: string | TokenMessage | null = null) {
  if (msg) {
    ws.send(JSON.stringify(msg))
  } else if (message.value) {
    // messages.value.push(message.value)
    ws.send(JSON.stringify({ client: clientId, message: message.value }));
    message.value = '';
  }
}
</script>
