<script setup>
import { computed } from 'vue';

const props = defineProps({
  ownMessage: {
    type: Boolean
  },
  text: {
    type: String,
    default: '',
  },
  backgroundColor: {
    type: String,
    default: '#ffa13d'
  }
})

const styleObject = computed(() => {
  return {
    float: props.ownMessage ? 'right' : 'left',
    backgroundColor: props.ownMessage ? '#70548b' : '#ffa13d'
  }
})
</script>

<template>
  <div class="message p-3 my-1" :style="styleObject">
    {{ text }}
  </div>
</template>

<style scoped>
  .message {
    color: white;
    border-radius: 1rem;
    width: 40vw;
    white-space: break-spaces;
  }
</style>
