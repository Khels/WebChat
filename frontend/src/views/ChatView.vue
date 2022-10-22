<script setup>
import { ref } from 'vue'
import MessageItem from '../components/MessageItem.vue'
import ResizableTextarea from '../components/ResizableTextarea.vue'

const message = ref("ksdg;lfamskld;fjbnlksfdjsadnbsdfnb;lsdf;aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
const messages = ref([])

function sendMessage() {
  if (message.value) {
    messages.value.push(message.value)
    message.value = ""
  }
}
</script>

<template>
  <div class="container-fluid vh-100">
    <div class="row" v-for="msg in messages" :key="msg">
      <div class="col">
        <MessageItem :text="msg" :own-message="true"/>
      </div>
    </div>
    <div class="row fixed-bottom p-4">
      <div class="col">
        <ResizableTextarea
          placeholder="Напишите сообщение..."
          v-model="message"
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
