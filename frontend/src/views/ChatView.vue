<script setup>
import { ref } from 'vue';
import MessageItem from '../components/MessageItem.vue';
import ResizableTextarea from '../components/ResizableTextarea.vue';

const message = ref("")
const messages = ref([])

const clientId = Date.now()
console.log(clientId);

let ws = new WebSocket("ws://127.0.0.1:8000/api/v1/chat/")

ws.onmessage = function(event) {
  let data = JSON.parse(event.data)
  console.log(data)
  messages.value.push({text: data.message, own: data.client === clientId})
}

function sendMessage() {
  if (message.value) {
    // messages.value.push(message.value)
    ws.send(JSON.stringify({ client: clientId, message: message.value }))
    message.value = ""
  }
}
</script>

<template>
  <div class="container-fluid vh-100">
    <div class="row" v-for="msg in messages" :key="msg">
      <div class="col">
        <MessageItem :text="msg.text" :own-message="msg.own"/>
      </div>
    </div>
    <div class="row fixed-bottom p-4">
      <div class="col">
        <ResizableTextarea
          placeholder="Напишите сообщение..."
          v-model="message"
          @keydown.ctrl.enter.exact="sendMessage"
        ></ResizableTextarea>
      </div>
      <div class="col-sm-auto">
        <button @click="sendMessage">Отправить</button>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
