export interface Message {
  id: number;
  authorId: number;
  senderId: number;
  chatId: number;
  type: number;
  content: string
  isRead: boolean;
  isEdited: boolean;
  createdAt: string;
}

export interface PreviewMessage {
  content: string;
  createdAt: string;
  isRead: boolean;
}

export interface User {
  id: number;
  username: string;
  firstName: string;
  lastName: string;
  lastOnline?: Date;
  isActive: boolean;
  isAdmin: boolean;
}

export interface Participant {
  participant: User;
  isAdmin: boolean;
}

export enum ChatType {
  SAVED_MESSAGES = 'saved_messages',
  DIALOGUE = 'dialogue',
  GROUP = 'group',
}

export interface ChatResponse {
  id: number;
  name?: string;
  type: ChatType;
  imageUrl?: string;
  participants: Participant[];
  messages: Message[];
}

export interface Chat extends ChatResponse {
  previewMessage?: PreviewMessage;
}
