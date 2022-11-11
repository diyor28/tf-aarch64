<template>
    <div>
        <ul class="nav flex">
            <li class="tab">
                <router-link exact-active-class="active" to="/">Tensorflow</router-link>
            </li>
            <li class="tab">
                <router-link exact-active-class="active" to="/tfx">Tfx</router-link>
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

.nav {
    background: rgb(36, 41, 47);
}

.tab {
    padding: 1rem;
}

.tab a {
    color: rgb(190, 191, 193);
    font-family: "system-ui", serif;
}

.tab a:hover, .tab a.active {
    color: rgb(255, 255, 255);
}
</style>