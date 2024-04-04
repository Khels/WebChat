<template>
  <q-page class="row justify-center q-pa-md" :class="classObject">
    <template v-if="chatStore.currentChat">
      <div class="message-container">
        <q-chat-message
          v-for="message in chatStore.currentChat?.messages"
          :key="message.content"
          :name="chatStore.currentChat?.type === ChatType.GROUP ? userStore.displayName : undefined"
          :avatar="chatStore.currentChat?.type === ChatType.GROUP ? 'https://cdn.quasar.dev/team/razvan_stoenescu.jpeg' : undefined"
          :text="[message.content]"
          :stamp="message.createdAt.slice(11, 16)"
          :sent="(message.senderId == userStore.user?.id)"
          text-color="white"
          :bg-color="message.senderId == userStore.user?.id ? 'teal-6' : 'blue-grey-7'"
        ></q-chat-message>
      </div>
      <q-page-scroller reverse position="bottom-right" :scroll-offset="20">
        <q-btn round icon="keyboard_arrow_down" color="teal-6" />
      </q-page-scroller>
    </template>
    <template v-else>
      Выберите чат
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { ChatType } from 'src/services/constants';
import { useChatStore } from 'src/stores/chat-store';
import { useUserStore } from 'src/stores/user-store';
import { computed } from 'vue';

const userStore = useUserStore();
const chatStore = useChatStore();

const classObject = computed(() => ({
  'items-end': chatStore.currentChat !== null,
  'items-center': chatStore.currentChat === null
}))
</script>

<style>
.message-container {
  width: 100%;
}
</style>
