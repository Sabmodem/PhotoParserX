import { createRouter, createWebHashHistory } from 'vue-router'
import search from '../views/search.vue'
import history from '../views/history.vue'
import results from '../views/results.vue'
import about from '../views/about.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'search',
      component: search
    },
    {
      path: '/history',
      name: 'history',
      component: history
    },
    {
      path: '/results/:id',
      name: 'results',
      component: results
    },
    {
      path: '/about',
      name: 'about',
      component: about
    }
  ]
})

export default router
