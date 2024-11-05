<template>
  <WaitLoadWrapper>
    <form @submit.prevent="handleSubmit" class="form">
      <label for="platform">Select Dataset:</label>
      <select id="data_folder" v-model="data_folder">
        <option value="facebook">Facebook</option>
        <option value="twitter">Twitter</option>
      </select>
      <label for="number">Enter a Number (maximum 10,000):</label>
      <input
        type="number"
        id="number"
        v-model.number="node_count"
        :max="10000"
        min="0"
        required
      />
      <button type="submit">Submit</button>
    </form>
    <div>
      <video controls width="600">
        <source src="/public/reencoded_video.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
    </div>
    <div v-if="loading">Loading</div>
  </WaitLoadWrapper>
</template>

<script lang="ts" setup>
import { apiFetch } from "~/services/api";

const loading = ref(false);
const data_folder = ref<string>("facebook");
const node_count = ref<number>(100);

const handleSubmit = async () => {
  loading.value = true;
  try {
    await apiFetch("/api/videoize", {
      method: "POST",
      body: {
        data_folder: data_folder,
        node_count: node_count,
      },
    });
  } catch (error) {
    console.error("API request error:", error);
  } finally {
    loading.value = false;
  }
};
</script>
