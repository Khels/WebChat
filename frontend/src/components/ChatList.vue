<template>
  <q-toolbar class="bg-grey-3">
    <q-space />

    <q-btn round flat icon="message" />
    <q-btn round flat icon="more_vert">
      <q-menu auto-close :offset="[110, 8]">
        <q-list style="min-width: 150px">
          <q-item clickable>
            <q-item-section>Новая группа</q-item-section>
          </q-item>
          <q-item clickable @click="userStore.signOut">
            <q-item-section>Выйти</q-item-section>
          </q-item>
        </q-list>
      </q-menu>
    </q-btn>

    <q-btn
      round
      flat
      icon="close"
      class="WAL__drawer-close"
      @click="emit('toggle')"
    />
  </q-toolbar>

  <q-toolbar class="bg-grey-2">
    <q-input rounded outlined dense class="WAL__field full-width" bg-color="white" v-model="search" placeholder="Найти">
      <template v-slot:prepend>
        <q-icon name="search" />
      </template>
    </q-input>
  </q-toolbar>

  <q-scroll-area style="height: calc(100% - 100px)">
    <q-list>
      <q-item
        v-for="chat in chatStore.chats"
        :key="chat.id"
        clickable
        v-ripple
        @click="chatStore.setCurrentChat(chat.id)"
      >
        <q-item-section avatar>
          <q-avatar>
            <img src="/person.svg">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label lines="1">
            {{ chat.name ? chat.name : chatStore.getDisplayName(chatStore.getDialogParticipant(chat, userStore.getCurrentUser())) }}
          </q-item-label>
          <q-item-label class="conversation__summary" caption>
            <q-icon name="check" v-if="chat.previewMessage?.isRead" />
            <!-- <q-icon name="not_interested" v-if="conversation.deleted" /> -->
            {{ chat.previewMessage?.content }}
          </q-item-label>
        </q-item-section>

        <q-item-section side>
          <q-item-label caption>
            {{ chat.previewMessage?.createdAt.slice(11, 16) }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-scroll-area>
</template>

<script setup lang="ts">
import { useChatStore } from 'src/stores/chat-store';
import { useUserStore } from 'src/stores/user-store';
import { ref } from 'vue';

const emit = defineEmits(['toggle']);

const userStore = useUserStore();
const chatStore = useChatStore();

console.log('chats', chatStore.chats);


const search = ref('');
</script>
