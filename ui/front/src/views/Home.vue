<template>
    {{ wheels }}
</template>

<script lang="ts" setup>
import * as process from "process";

const wheels = await fetch(process.env.VUE_APP_API_URL + '/api/wheels', {
    method: 'get',
    headers: {'Content-Type': 'application/json'}
}).then(res => {
    res.json();
});
</script>

<style scoped>

</style>