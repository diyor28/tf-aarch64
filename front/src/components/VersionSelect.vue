<template>
    <select :value="props.modelValue" class="select" @change="emit('update:modelValue', $event.target.value)">
        <option v-for="version in props.versions" :value="version">
            {{ version }}.x
        </option>
    </select>
</template>

<script lang="ts" setup>
const props = defineProps<{ modelValue: string, versions: string[] }>();
const emit = defineEmits(['update:modelValue']);
</script>

<style scoped>

</style>