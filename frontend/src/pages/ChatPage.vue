<template>
  <div class="WAL position-relative bg-grey-4" :style="style">
    <q-layout view="lHh Lpr lFf" class="WAL__layout shadow-3" container>
      <q-drawer
        v-model="chatMenuOpen"
        show-if-above
        bordered
        :breakpoint="690"
      >
        <ChatList @toggle="toggleChatMenu"/>
      </q-drawer>

      <q-header elevated v-show="chatStore.currentChat">
        <q-toolbar class="bg-grey-3 text-black">
          <q-btn
            round
            flat
            icon="keyboard_arrow_left"
            class="WAL__drawer-open q-mr-sm"
            @click="toggleChatMenu"
          />

          <q-btn round flat>
            <q-avatar>
              <img src="/person.svg">
            </q-avatar>
          </q-btn>

          <span class="q-subtitle-1 q-pl-md">
            {{ chatStore.currentChat?.name ? chatStore.currentChat?.name : chatStore.currentChat ? chatStore.getDisplayName(chatStore.getDialogParticipant(chatStore.currentChat, userStore.user)) : undefined }}
          </span>

          <q-space/>

          <q-btn round flat icon="more_vert">
            <q-menu auto-close :offset="[110, 0]">
              <q-list style="min-width: 150px">
                <q-item clickable>
                  <q-item-section @click="chatStore.deleteCurrentChat()">Удалить чат</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </q-toolbar>
      </q-header>

      <q-page-container class="bg-grey-2">
        <MessageList />
      </q-page-container>

      <q-footer v-show="chatStore.currentChat">
        <q-toolbar class="bg-grey-3 text-black row">
          <q-btn round flat icon="insert_emoticon" class="q-mr-sm" />
          <q-input
            outlined
            dense
            class="WAL__field col-grow q-mr-sm"
            bg-color="white"
            v-model="message"
            autogrow
            placeholder="Напишите сообщение..."
            @keydown.ctrl.enter.exact="sendMessage()"
          />
          <q-btn round flat icon="send" v-show="message" @click="sendMessage()" />
        </q-toolbar>
      </q-footer>
    </q-layout>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import ChatList from 'src/components/ChatList.vue';
import MessageList from 'src/components/MessageList.vue';
import { Message } from 'src/models/chat';
import { MessageType, WSMessageType } from 'src/services/constants';
import { useChatStore } from 'src/stores/chat-store';
import { useUserStore } from 'src/stores/user-store';
import { camelCaseKeys } from 'src/utils/case-converters';
import { computed, onBeforeMount, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

interface WSMessageBase {
  type: number;
}

interface WSAuthMessageSend extends WSMessageBase {
  body: {
    token: string | null;
  };
}

interface WSMessageSend extends WSMessageBase {
  body: {
    chat_id: number;
    type: number;
    content: string;
  };
}

interface WSErrorMessageReceive {
  type?: never;
  body?: never;
  error: object;
}

interface WSMessage extends WSMessageBase {
  body: Message;
  error?: never;
}

type WSMessageReceive = WSMessage | WSErrorMessageReceive;

const $q = useQuasar();
const route = useRoute();
const router = useRouter();
const chatStore = useChatStore();
const userStore = useUserStore();

onBeforeMount(async () => {
  await chatStore.getChats();

  if (route.query.id) {
    chatStore.setCurrentChat(route.query.id);
    if (chatStore.currentChat && chatStore.currentChat.messages.length <= 1) {
      chatStore.currentChat.messages = [];
      await chatStore.getMessages(chatStore.currentChat?.id);
    }
  }
})

onMounted(() => {
  window.addEventListener('keydown', handleEscPress);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscPress);
});

function handleEscPress(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    chatStore.currentChat = null;
    router.push({ query: {} });
  }
}

const chatMenuOpen = ref(false);
const message = ref('');
const currentConversationIndex = ref(0);

const style = computed(() => ({
  height: $q.screen.height + 'px'
}));

const ws = new WebSocket(process.env.WEBSOCKET_BASE_URL + '/chat');

ws.onopen = (e) => {
  const token = localStorage.getItem('accessToken')
  send({
    type: WSMessageType.AUTHENTICATION,
    body: { token }
  });
}

ws.onmessage = (e) => {
  const data: WSMessageReceive = camelCaseKeys(JSON.parse(JSON.parse(e.data)));
  console.log('onmessage data: ', data);

  if (data.error) {
    console.log('error: ', data.error);
  } else {
    chatStore.currentChat?.messages.push(data.body);
    for (let chat of chatStore.chats) {
      if (chat.id === data.body.chatId) {
        if (chat.previewMessage) {
          chat.previewMessage.content = data.body.content;
          chat.previewMessage.isRead = data.body.isRead;
          chat.previewMessage.createdAt = data.body.createdAt;
        }
      }
    }
  }
}

ws.onclose = (e) => {
  console.log('ws closed: ', e);
  if (e.code === 4000) {
    // authentication failed
  }
}

// function sendNotification() {

// }

function sendMessage() {
  if (message.value && chatStore.currentChat) {
    send({
      type: WSMessageType.MESSAGE,
      body: {
        chat_id: chatStore.currentChat.id,
        type: MessageType.TEXT,
        content: message.value
      }
    })
    message.value = '';
  }
}

function send(msg: WSAuthMessageSend | WSMessageSend) {
  ws.send(JSON.stringify(msg))
}

function toggleChatMenu () { 
  chatMenuOpen.value = !chatMenuOpen.value;
}
</script>

<style lang="sass">
.WAL
  width: 100%
  height: 100%
  padding-top: 20px
  padding-bottom: 20px
  &:before
    content: ''
    height: 127px
    position: fixed
    top: 0
    width: 100%
    background-color: $teal-6
  &__layout
    margin: 0 auto
    z-index: 4000
    height: 100%
    width: 90%
    max-width: 950px
    border-radius: 5px
  &__field.q-field--outlined .q-field__control:before
    border: none
  .q-drawer--standard
    .WAL__drawer-close
      display: none
@media (max-width: 850px)
  .WAL
    padding: 0
    &__layout
      width: 100%
      border-radius: 0
@media (min-width: 691px)
  .WAL
    &__drawer-open
      display: none
.conversation__summary
  margin-top: 4px
.conversation__more
  margin-top: 0!important
  font-size: 1.4rem
</style>
