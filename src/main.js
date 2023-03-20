import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Notifications from '@kyvg/vue3-notification';
import { PromiseDialog } from 'vue3-promise-dialog';
import VueAwesomePaginate from "vue-awesome-paginate";

import "vue-awesome-paginate/dist/style.css";
import './assets/bootstrap/js/bootstrap'
import './assets/main.css'

const app = createApp(App)

app.use(router)
app.use(Notifications);
app.use(PromiseDialog);
app.use(VueAwesomePaginate);

app.mount('#app')
