<template>
  <q-page class="row items-start justify-center q-pa-md">
    
    <div style="width: 100%; max-width: 400px">
      <q-chat-message
        v-for="message in chatStore.messages"
        :key="message.content"
        :name="userStore.displayName"
        avatar="https://cdn.quasar.dev/img/avatar3.jpg"
        :text="[message.content]"
        stamp="20:51"
        :sent="(message.sender_id == userStore.user?.id)"
        :bg-color="'amber-7' ? message.sender_id == userStore.user?.id : 'primary'"
      ></q-chat-message>
    </div>
    <q-page-scroller reverse position="top" :scroll-offset="20" :offset="[0, 18]">
      <q-btn fab icon="keyboard_arrow_down" color="accent" />
    </q-page-scroller>
  </q-page>
</template>

<script setup lang="ts">
import { useChatStore } from 'src/stores/chat-store';
import { useUserStore } from 'src/stores/user-store';
import { watch } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const userStore = useUserStore();
const chatStore = useChatStore();

watch(
  () => route.query.id,
  () => {
    console.log('chat changed!');
  }
);
</script>
