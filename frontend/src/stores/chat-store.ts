import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import { useNotifications } from 'src/composables/notifications';
import { Chat, ChatResponse, Message, PreviewMessage } from 'src/models/chat';
import { ChatType } from 'src/services/constants';
import router from 'src/router/index';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';

export const useChatStore = defineStore('chat', () => {
  const route = useRoute();
  const notify = useNotifications();

  const currentChat = ref<Chat | null>(null);
  const chats = ref<Chat[]>([]);

  watch(
    () => route.query.id,
    () => {
      if (currentChat.value && currentChat.value.messages.length <= 1) {
        getMessages(currentChat.value.id);
      }
    }
  );

  async function getChats() {
    chats.value = [];

    try {
      const { data } = await api.get<ChatResponse[]>('chats');

      data.forEach(chat => {
        (chat as Chat | null).previewMessage = setUpPreviewMessage(chat);
        if (chat.type === ChatType.SAVED_MESSAGES) {
          chat.name = "Saved Messages"
          chat.imageUrl = "/bookmark.svg"
        }
        chats.value.push((chat as Chat));
      })
    } catch (error) {
      console.log('getChats', error);
      notify.error()
    }
  }

  async function getMessages(chatId: number, limit: number | null = null, offset: number | null = null) {
    try {
      const { data } = await api.get<Message[]>(`chats/${chatId}/messages`, {
        params: {
          limit,
          offset
        }
      });

      for (const chat of chats.value) {
        if (chat.id === chatId) {
          chat.messages.push(...data);
          console.log(chat.messages);
          
          break
        }
      }
    } catch (error) {
      
    }
  }

  function setCurrentChat(chatId: number) {
    for (const chat of chats.value) {
      if (chat.id == chatId) {
        currentChat.value = chat;
        router.push({ query: { id: chatId } });
        break
      }
    }
  }

  function setUpPreviewMessage(chat: ChatResponse): PreviewMessage | null {
    if (chat.messages.length > 0) {
      const lastMessage = chat.messages[chat.messages.length - 1];
      return {
        content: lastMessage.content,
        createdAt: formatCreationDate(lastMessage.createdAt),
        isRead: lastMessage.isRead,
      };
    }
    return null;
  }

  function formatCreationDate(createdAt: string): string {
    return createdAt;
  }

  function addMessage(message: Message, chatId: number) {
    for (const chat of chats.value) {
      if (chat.id === chatId) {
        chat.messages.push(message);
        break;
      }
    }
  }

  return {
    currentChat,
    chats,
    getChats,
    getMessages,
    setCurrentChat,
    addMessage
  }
});
