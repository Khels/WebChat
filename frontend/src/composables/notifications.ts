import { Notify } from 'quasar';


export function useNotifications() {
  function error(message = 'Что-то пошло не так...') {
    return Notify.create({
      color: 'red-5',
      textColor: 'white',
      icon: 'warning',
      message: message
    });
  }

  return {
    error,
  }
}