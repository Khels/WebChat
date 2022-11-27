import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.min.js'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

// PROJECT: COMMONS
// import development from "@/config/development.json"
// import production from "@/config/production.json"

// if (process.env.NODE_ENV === "production") {
//   Vue.prototype.$config = Object.freeze(production);
// } else {
//   Vue.prototype.$config = Object.freeze(development);
// }

