<template>
    <div>
        <ul class="flex">
            <li class="tab">
                <router-link to="/">Tensorflow</router-link>
            </li>
            <li class="tab">
                <router-link to="/tfx">Tfx</router-link>
            </li>
            <li class="tab">
                <router-link to="/tfx-bsl">Tfx-bsl</router-link>
            </li>
        </ul>
        <router-view></router-view>
    </div>
</template>

<script lang="ts" setup>
import {reactive} from "vue";
import {useLogsStore} from "@/stores/logs";

useLogsStore().listenLogs();

const logs = reactive({});
</script>

<style>
.card {
    border: solid #c4c4c4 1px;
    border-radius: 8px;
    padding: 10px;
}

.tab {
    padding: 1rem;
}

</style>