<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div>
    <header>
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="#">PhotoParserX</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav mr-auto">
            <li class="nav-item active">
              <RouterLink class="nav-link" to="/"><i class="bi bi-search"></i> Поиск</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/history"><i class="bi bi-list-task"></i> История</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink class="nav-link" to="/about"><i class="bi bi-info-circle"></i> О программе</RouterLink>
            </li>
          </ul>
        </div>
      </nav>
    </header>
    <main class="container" style="height: 75vh">
      <RouterView />
      <notifications position="bottom right" />
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import emitter from './emitter.js';
import Swal from 'sweetalert2';
export default {
  data() {
    return {}
  },
  methods: {
  },
  async created() {
      const socket = new WebSocket('ws://127.0.0.1:8765');
      socket.onerror = () => {
        Swal.fire({ title: 'Ошибка', text: 'Ошибка подключения к серверу уведомлений. Попробуйте обновить страницу или перезапустить софт, если проблема не уйдет', type: 'error', confirmButtonText: 'Ок' });
      };
      socket.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        const query_data = await axios.get(`/history/${data.id}`);
        emitter.emit('updateStatus', { id: data.id });
        this.$notify(`Изменен статус запроса "${query_data.data.query_string}". <a href="/#/history">Перейти к истории запросов</a>`);
      };
  },
  mounted() {
  }
}
</script>
