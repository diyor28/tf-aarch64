<template>
    <div>
        <build-card v-for="build in buildsStore.tf" :build="build"
                    :logs="logsStore.getLogs(build.id)"></build-card>
        <div class="flex mt-4">
            <div>
                <label class="label">Python</label>
                <version-select v-model="buildBody.python" :versions="['3.7', '3.8']"></version-select>
            </div>
            <div class="flex-auto ml-4">
                <label class="label">Tensorflow</label>
                <version-select v-model="buildBody.package" :versions="['2.7', '2.8', '2.9']"></version-select>
            </div>
            <div>
                <button class="btn btn-success" @click="build">Build</button>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import {ref} from "vue";

import BuildCard from '@/components/BuildCard.vue'
import {useLogsStore} from "@/stores/logs";
import VersionSelect from "@/components/VersionSelect.vue";
import {useBuildsStore} from "@/stores/builds";

const buildBody = ref({python: '', package: '', type: 'tensorflow'});
const logsStore = useLogsStore();
const buildsStore = useBuildsStore();
await buildsStore.fetch();

async function build() {
    try {
        await buildsStore.create(buildBody.value);
    } catch (e) {
        if (e.status === 400) {
            alert(e.body.detail);
        }
    }
}
</script>

<style scoped>
</style>