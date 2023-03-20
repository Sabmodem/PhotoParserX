<template>
  <div class="row">
    <div class="col-md-2">
      <img class="img-thumbnail" :src="this.thumb_src" v-if="this.thumb_src"/>
      <img class="img-thumbnail" :src="this.src" v-else-if="this.src"/>
    </div>
    <div class="col-md-10">
      <div class="row">
        <div class="row" v-if="this.src">
          <div class="col-md-2"><strong>src:</strong></div>
          <a class="col-md-10 text-truncate" :href="this.src">{{ this.src }}</a>
        </div>
        <div class="row" v-if="this.thumb_src">
          <div class="col-md-2"><strong>thumb src:</strong></div>
          <a class="col-md-8 text-truncate" :href="this.thumb_src">{{ this.thumb_src }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {}
  },
  props: ['src', 'thumb_src'],
  mounted() {
  }
}
</script>