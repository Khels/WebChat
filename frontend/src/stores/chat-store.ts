import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import { useNotifications } from 'src/composables/notifications';
import { Chat, ChatResponse, Message, PreviewMessage } from 'src/models/chat';
import { ChatType } from 'src/services/constants';
import router from 'src/router/index';
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { User } from 'src/models/auth';

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

  function getDisplayName(user: User | undefined) {
    if (!user) return '';

    let name = '';
    if (user.firstName) {
      name = user.firstName;
      if (user.lastName) {
        name = name + ' ' + user.lastName;
      }
    }

    return name ? name : user.username
  }

  function getDialogParticipant(chat: Chat, user: User) {
    if (chat.type === ChatType.DIALOGUE) {
      for (const participant of chat.participants) {
        if (participant.participant.id !== user.id) {
          return participant.participant
        }
      }
    }
  }

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

  async function deleteCurrentChat() {
    try {
      await api.delete(`chats/${currentChat.value.id}`);

      const index = chats.value.indexOf(currentChat.value, 0);
      if (index > -1) {
        chats.value.splice(index, 1);
      }
      currentChat.value = null
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

  function getChatParticipant(chat: Chat, userId: number) {
    for (const participant of chat.participants) {
      if (participant.participant.id === userId) {
        return participant.participant
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
    getDialogParticipant,
    getDisplayName,
    getChats,
    deleteCurrentChat,
    getMessages,
    setCurrentChat,
    getChatParticipant,
    addMessage
  }
});
