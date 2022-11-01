<template>
    <build-card v-for="build in buildsStore.tfx" :build="build" :logs="logsStore.getLogs(build.filename)"></build-card>
    <div class="flex mt-4">
        <div>
            <label class="label">Python</label>
            <version-select v-model="buildBody.python" :versions="['3.7', '3.8', '3.9', '3.10']"></version-select>
        </div>
        <div class="flex-auto ml-4">
            <label class="label">Tfx</label>
            <version-select v-model="buildBody.package" :versions="['1.4', '1.5', '1.6', '1.7']"></version-select>
        </div>
        <div>
            <button class="btn" @click="buildsStore.create(buildBody)">Build</button>
        </div>
    </div>
</template>

<script lang="ts" setup>
import {ref} from "vue";

import BuildCard from '@/components/BuildCard.vue'
import {useLogsStore} from "@/stores/logs";
import VersionSelect from "@/components/VersionSelect.vue";
import {useBuildsStore} from "@/stores/builds";

const buildBody = ref({python: '', package: '', type: 'tfx'});
const logsStore = useLogsStore();
const buildsStore = useBuildsStore();
await buildsStore.fetch();
</script>

<style scoped>

</style>