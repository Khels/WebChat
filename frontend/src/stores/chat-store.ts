import { defineStore } from 'pinia';
import { useNotifications } from 'src/composables/notifications';
import { Chat, Message } from 'src/models/chat';

const notify = useNotifications();

export const useChatStore = defineStore('chat', {
  state: () => ({
    currentChat: null as Chat | null,
    chats: [
      {
        id: 1,
        messages: [] as Message[]
      }
    ] as Chat[],
    messages: []
  }),
  getters: {

  },
  actions: {
    addMessage(message: Message) {
      if (this.currentChat) {
        this.currentChat.messages.push(message);
      }
    }
  }
});
