<script setup>
import histItem from '../components/histItem.vue'
</script>

<template>
  <div v-if="this.loading" class="spinner-border" role="status"></div>
  <div v-if="this.history.length > 0">
    <table class="table">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Дата</th>
          <th scope="col">Запрос</th>
          <th scope="col">Статус</th>
          <th scope="col">Действия</th>
        </tr>
      </thead>
      <tbody>
        <histItem v-for="(hi, index) in this.history" :item="hi" :index="index"></histItem>
      </tbody>
    </table>
    <footer class="fixed-bottom d-flex justify-content-center">
      <vue-awesome-paginate :total-items="this.itemsCount" :items-per-page="10" :max-pages-shown="5"
        v-model="this.curPage" :on-click="this.loadPage" />
    </footer>
  </div>
  <div v-if="this.history.length == 0 && !this.loading" class="d-flex justify-content-center">
    <h1>Вы пока не сделали ни одного запроса</h1>
  </div>
</template>

<script>
import axios from 'axios';
import emitter from '../emitter.js';
export default {
  data() {
    return {
      loading: true,
      curPage: null,
      pagesCount: null,
      itemsCount: null,
      history: [],
    }
  },
  methods: {
    async loadPage(pageNum) {
      this.curPage = pageNum
      const historyItemsRes = await axios.get(`/history/${pageNum - 1}`);
      this.history = historyItemsRes.data;
    }
  },
  async mounted() {
    const pagesCountRes = await axios.get(`/history/pages`);
    this.pagesCount = pagesCountRes.data.pagesCount;
    this.itemsCount = pagesCountRes.data.itemsCount;

    await this.loadPage(1);

    this.loading = false;

    emitter.on('deleteHistItem', async () => {
      await this.loadPage(this.curPage);
    })
  }
}
</script>