export interface Message {
    id?: number
    type: 'sender' | 'receiver',
    text: string
}