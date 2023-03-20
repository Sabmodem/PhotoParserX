<template>
  <div class="d-flex flex-column h-100">
    <div class="d-flex flex-column justify-content-center align-items-center h-100">
      <h1>PhotoParserX</h1>
      <div class="input-group">
        <input type="text" class="form-control" placeholder="Искать по запросу..." v-model="this.settings.query">
        <div class="input-group-btn">
          <button class="btn btn-outline-secondary" @click="search()"><i class="bi bi-search"></i></button>
          <button class="btn btn-outline-secondary" @click="clearQueryInput()"><i class="bi bi-x-lg"></i></button>
        </div>
      </div>
      <div class="d-flex flex-row m-3">
        <input class="form-control m-3" type="number" v-model="this.settings.pagesCount">
        <select class="form-control m-3" v-model="this.settings.language">
          <option v-for="lang in Object.keys(this.langs)" :value="this.langs[lang]">{{ lang }}</option>
        </select>
        <select class="form-control m-3" v-model="this.settings.time">
          <option v-for="time in Object.keys(this.times)" :value="this.times[time]">{{ time }}</option>
        </select>
        <select class="form-control m-3" v-model="this.settings.timeout">
          <option v-for="timeout in this.timeouts" :value="timeout.timeout">{{ timeout.text }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import langs from '../assets/langs.json';
import times from '../assets/times.json';

export default {
  data() {
    const timeouts = [];
    for(let i = 60; i <= 60*100; i += 60) {
      const text = `${i / 60} мин`;
      timeouts.push({ text, timeout: i });
    };
    return {
      imgs: [],
      langs,
      times,
      timeouts,
      settings: {
        query: null,
        pagesCount: 10,
        time: null,
        language: null,
        timeout: 60
      },
    }
  },
  methods: {
    async search() {    
      if (!this.settings.query) {
        return;
      };
      const imgs = await axios.post('/search', this.settings);
      this.imgs = imgs.data;
      this.$notify(`Начат поиск по запросу "${this.settings.query}". <a href="/#/history">Перейти к истории запросов</a>`);
      this.clearQueryInput();
    },
    clearQueryInput() {
      this.settings.query = null;
    }
  },
  async mounted() {
    this.settings.time = this.times[Object.keys(this.times)[0]];
    this.settings.language = this.langs[Object.keys(this.langs)[0]];
  }
}
</script>