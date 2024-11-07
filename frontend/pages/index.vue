<template>
  <WaitLoadWrapper>
    <div>
      <a class="text-2xl m-2 block"
        >Iterative Decomposition of Communities in Undirected Graphs</a
      >
    </div>
    <div class="flex m-2 block items-start">
      <form
        @submit.prevent="handleSubmit"
        class="form space-y-4 bg-gray-100 p-6 rounded-md shadow-md max-w-lg"
      >
        <label for="platform" class="block text-gray-700 font-semibold"
          >Select Dataset:</label
        >
        <select
          id="data_folder"
          v-model="data_folder"
          class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="facebook">Facebook</option>
          <option value="twitter">Twitter</option>
        </select>

        <label for="number" class="block text-gray-700 font-semibold"
          >Enter a Number:</label
        >
        <input
          type="number"
          id="number"
          v-model.number="node_count"
          :max="100000"
          min="0"
          required
          class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        />

        <label for="show_uncircled" class="block text-gray-700 font-semibold"
          >Show uncircled nodes:</label
        >
        <select
          id="show_uncircled"
          v-model="show_uncircled"
          class="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="false">false</option>
          <option value="true">true</option>
        </select>

        <button
          type="submit"
          class="w-full bg-blue-600 text-white font-semibold py-2 rounded-md hover:bg-blue-700 transition duration-200"
        >
          <a v-if="loading">Loading...</a>
          <a v-else>Submit</a>
        </button>
      </form>

      <div v-if="videoReady" class="flex justify-center items-start">
        <video controls width="600" class="rounded-lg shadow-md">
          <source src="/public/reencoded_video.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    </div>
  </WaitLoadWrapper>
</template>

<script lang="ts" setup>
import { apiFetch } from "~/services/api";
import { ref } from "vue";

const loading = ref(false);
const videoReady = ref(true);
const data_folder = ref<string>("facebook");
const node_count = ref<number>(100);
const show_uncircled = ref<boolean>(false);

const handleSubmit = async () => {
  loading.value = true;
  videoReady.value = false;

  try {
    await apiFetch("/api/videoize/", {
      method: "POST",
      body: JSON.stringify({
        data_folder: data_folder.value,
        node_count: node_count.value,
        show_uncircled: show_uncircled.value,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    videoReady.value = true;
  } catch (error) {
    console.error("API request error:", error);
  } finally {
    loading.value = false;
  }
};
</script>
