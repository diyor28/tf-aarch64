<template>

</template>

<script lang="ts" setup>
const wheels = await fetch('/api/wheels', {method: 'get', headers: {'Content-Type': 'application/json'}}).then(res => {
    res.json();
});


</script>

<style scoped>

</style>