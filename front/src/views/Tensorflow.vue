<template>
    <div>
        <build-card v-for="build in buildsStore.tf" :build="build"></build-card>
        <div class="flex mt-4">
            <div>
                <label class="label">Python</label>
                <version-select v-model="buildBody.python" :versions="pyVersions"></version-select>
            </div>
            <div class="flex-auto ml-4">
                <label class="label">Tensorflow</label>
                <version-select v-model="buildBody.package" :versions="tfVersions"></version-select>
            </div>
            <div>
                <button class="btn btn-success" @click="build">Build</button>
            </div>
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

const buildBody = ref({python: '', package: '', type: 'tensorflow'});
const buildsStore = useBuildsStore();
const versionsStore = useVersionsStore();

const pyVersions = computed(() => {
    const versions = versionsStore.tensorflow.map(el => el.python);
    return sortVersions(Array.from(new Set(versions)));
});

const tfVersions = computed(() => {
    const versions = versionsStore.tensorflow.map(el => el.package);
    return sortVersions(Array.from(new Set(versions)));
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