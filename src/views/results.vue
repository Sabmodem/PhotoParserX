<script setup>
import result from '../components/result.vue'
</script>
<template>
  <div>
    <div v-if="this.loading" class="spinner-border" role="status"></div>
    <div v-if="!this.loading && this.results.length == 0" class="d-flex justify-content-center">
      <h1>Этот запрос не дал результатов</h1>
    </div>
    <div v-if="this.results.length > 0">
      <div v-for="result in this.results">
        <result :src="result.img_src" :thumb_src="result.thumb_src"></result>
      </div>
      <footer class="fixed-bottom d-flex justify-content-center">
        <vue-awesome-paginate :total-items="this.resultsCount" :items-per-page="50" :max-pages-shown="5" v-model="this.curPage" :on-click="this.loadPage" />
      </footer>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      loading: true,
      results: [],
      curPage: null,
      pagesCount: null,
      resultsCount: null
    }
  },
  methods: {
    async loadPage(pageNum) {
      this.curPage = pageNum
      const resultsRes = await axios.get(`/results/${this.$route.params.id}/${pageNum - 1}`);
      this.results = resultsRes.data;
    },
  },
  async mounted() {
    const pagesCountRes = await axios.get(`/results/${this.$route.params.id}/pages`);
    this.pagesCount = pagesCountRes.data.pagesCount;
    this.resultsCount = pagesCountRes.data.resultsCount;
   
    await this.loadPage(1);

    this.loading = false;
  }
}
</script>