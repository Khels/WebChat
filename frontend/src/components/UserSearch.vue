<template>
  <div class="q-pa-md">
    <div class="q-gutter-md row items-start">
      <div style="min-width: 250px; max-width: 300px">
        <q-select
          filled
          hide-dropdown-icon
          use-input
          input-debounce="0"
          v-model="model"
          multiple
          :options="options"
          use-chips
          @filter="filterFn"
          stack-label
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-select>
        <q-btn
          v-show="model.length > 0"
          color="primary"
          size="md"
          @click="createChat"
        >Создать чат</q-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from 'src/stores/user-store';
import { useChatStore } from 'src/stores/chat-store';

const userStore = useUserStore();
const chatStore = useChatStore();

const model = ref([])
const options = ref([])

async function filterFn(val, update) {
  update(async () => {
    const users = await userStore.searchUsers(val)
    options.value = users.map(a => ({ 'label': a.username, 'value': a.id }))
  })
}

async function createChat() {
  if (model.value.length > 1) {
    const groupChatName = model.value.slice(0, 2).map(a => a.label).join(', ')

    chatStore.createChat('group', groupChatName, model.value.map(a => ({id: a.value})))
  }
  else if (model.value.length === 1) {
    chatStore.createChat('dialogue', '', model.value.map(a => ({id: a.value})))
  }
}
</script>
