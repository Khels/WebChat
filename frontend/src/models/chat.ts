export interface Message {
  id: number;
  author_id: number;
  sender_id: number;
  chat_id: number;
  type: number;
  content: string
  is_read: boolean;
  is_edited: boolean;
  created_at: Date;
}

export interface Chat {
  id: number;
  messages: Message[];
}
