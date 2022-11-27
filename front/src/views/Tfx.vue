<template>
    <build-card v-for="build in buildsStore.tfx" :build="build"></build-card>
    <div class="flex mt-4">
        <div>
            <label class="label">Python</label>
            <version-select v-model="buildBody.python" :versions="pyVersions"></version-select>
        </div>
        <div class="flex-auto ml-4">
            <label class="label">Tfx</label>
            <version-select v-model="buildBody.package" :versions="tfxVersions"></version-select>
        </div>
        <div>
            <button class="btn btn-success" @click="build()">Build</button>
        </div>
    </div>
</template>

<script lang="ts" setup>
import {computed, ref} from "vue";

import BuildCard from '@/components/BuildCard.vue'
import VersionSelect from "@/components/VersionSelect.vue";
import {useBuildsStore} from "@/stores/builds";
import {useVersionsStore} from "@/stores/versions";
import {sortVersions} from "@/components/sortVersions";

const buildBody = ref({python: '', package: '', type: 'tfx'});
const buildsStore = useBuildsStore();
const versionsStore = useVersionsStore();

const pyVersions = ['3.7', '3.8', '3.9', '3.10', '3.11'];

const tfxVersions = computed(() => {
    return sortVersions(Array.from(new Set(versionsStore.tfx)));
});

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