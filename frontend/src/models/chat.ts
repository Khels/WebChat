export interface Message {
  id: number,
  type: string,
  content: string
}

export interface Chat {
  id: number
  messages: Message[]
}
