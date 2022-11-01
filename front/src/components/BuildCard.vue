<template>
    <div class="card mt-4">
        <div class="flex align-center justify-center">
            <div class="flex-auto">
                <div style="display: inline-flex">
                    <python style="width: 20px; height: 20px"></python>
                    <div class="ml-2">
                        {{ props.build.python }}
                    </div>
                </div>
                <div class="ml-4" style="display: inline-flex">
                    <tensorflow style="width: 20px; height: 20px"></tensorflow>
                    <div class="ml-2">
                        {{ props.build.package }}
                    </div>
                </div>
            </div>
            <div>
                <button class="btn">
                    Rebuild
                    <refresh style="height: 16px; width: 16px"></refresh>
                </button>
            </div>
        </div>
        <div v-if="entries.length" class="build-log mt-4">
            <p v-for="[line_n, log] in entries">
                <span>{{ line_n }}</span><span class="ml-4">{{ log }}</span>
            </p>
        </div>
    </div>
</template>

<script lang="ts" setup>
import Python from "@/components/Icons/Python.vue";
import Refresh from "@/components/Icons/Refresh.vue";
import Tensorflow from "@/components/Icons/Tensorflow.vue";
import {computed} from "vue";

const props = defineProps<{ build: any, logs: Record<number, string> }>()
const entries = computed(() => {
    return Object.entries(props.logs || {})
});

</script>

<style scoped>

.build-log {
    border: solid 1px #efefef;
    border-radius: 8px;
    padding: 8px;
    background: #efefef;
}
</style>