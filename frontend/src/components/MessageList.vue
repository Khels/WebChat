<template>
  <q-page class="row justify-center q-pa-md" :class="classObject">
    <template v-if="chatStore.currentChat">
      <div style="width: 100%; max-width: 400px">
        <q-chat-message
          v-for="message in chatStore.currentChat?.messages"
          :key="message.content"
          :name="chatStore.currentChat?.type === ChatType.GROUP ? userStore.displayName : undefined"
          :avatar="chatStore.currentChat?.type === ChatType.GROUP ? 'https://cdn.quasar.dev/img/avatar3.jpg' : undefined"
          :text="[message.content, message.senderId, userStore.user?.id]"
          stamp="20:51"
          :sent="(message.senderId == userStore.user?.id)"
          text-color="white"
          :bg-color="message.senderId == userStore.user?.id ? 'amber-7' : 'blue-grey-7'"
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
