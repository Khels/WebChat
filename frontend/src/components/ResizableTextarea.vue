<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  rows: {
    type: Number,
    default: 1,
  },
  cols: {
    type: Number,
    default: 0,
  },
  minHeight: {
    type: Number,
    default: null,
  },
  maxHeight: {
    type: Number,
    default: null,
  },
  modelValue: {
    type: String,
    default: '',
  },
  autoResize: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const textarea = ref(null)

const height = ref('auto !important')
const isScrollEnabled = ref(false)

const styleObject = computed(() => {
  return {
    resize: props.autoResize ? 'none !important' : '',
    height: height.value,
    overflow: `${isScrollEnabled.value ? 'scroll' : 'hidden'} !important`,
  }
})

watch(
  () => props.modelValue,
  async () => {
    await resize()
  }
)

onMounted(async () => {
  await resize()
})

async function resize() {
  height.value = 0

  await nextTick()

  if (props.minHeight) {
    height.value = `${textarea.value.scrollHeight < props.minHeight ? props.minHeight : textarea.value.scrollHeight}px`
  }
  if (props.maxHeight) {
    if (textarea.value.scrollHeight > props.maxHeight) {
      height.value = `${props.maxHeight}px`;
      isScrollEnabled.value = true;
    } else {
      isScrollEnabled.value = false;
    }
  } else {
    textarea.value.scrollHeight  // just leave it be
    height.value = `${textarea.value.scrollHeight}px`
  }
}
</script>

<template>
  <textarea
    class="text-area"
    :style="styleObject"
    :rows="rows"
    :cols="cols"
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
    ref="textarea"
  ></textarea>
</template>

<style scoped>
  .text-area {
    width: 100%;
    border: 1px solid #ced4da;
    border-radius: .25rem;
    padding: .375rem .75rem
  }
</style>
