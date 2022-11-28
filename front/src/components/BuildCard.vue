<template>
    <div class="card mt-4">
        <div class="flex align-center justify-center">
            <div class="flex-auto">
                <div style="display: inline-flex">
                    <python-icon class="icon-md"></python-icon>
                    <div class="ml-2">
                        {{ props.build.python }}
                    </div>
                </div>
                <div class="ml-4" style="display: inline-flex">
                    <tensorflow-icon class="icon-md"></tensorflow-icon>
                    <div class="ml-2">
                        {{ props.build.package }}
                    </div>
                </div>
                <div class="ml-4" style="display: inline-flex">
                    <x-icon v-if="['failed', 'cancelled'].includes(props.build.status)" class="icon-md"
                            style="color: rgb(255,29,29)"></x-icon>
                    <check-icon v-else-if="props.build.status === 'completed'" class="icon-md"
                                style="color: rgb(44,255,29)"></check-icon>
                    <refresh-icon v-else class="spin-animation icon-md"></refresh-icon>
                </div>
            </div>
            <div>
                <div class="flex space-x-4">
                    <button class="btn flex align-center items-center space-x-2" @click="rebuild">
                        Rebuild
                        <refresh-icon class="icon-sm"></refresh-icon>
                    </button>
                    <button class="btn flex align-center items-center space-x-2" @click="cancel">
                        Cancel
                        <stop-icon class="icon-sm"></stop-icon>
                    </button>
                    <button class="btn flex align-center items-center space-x-2" @click="remove">
                        Delete
                        <trash-icon class="icon-sm"></trash-icon>
                    </button>
                </div>
            </div>
        </div>
        <div v-if="logs.length" class="build-log mt-4">
            <div v-for="log in logs" class="log-line">
                <span class="line-number">{{ log.line_number }}</span>
                <span class="ml-4" v-html="log.line"></span>
            </div>
        </div>
        <div class="flex mt-4 mb-2">
            <div class="flex-auto"></div>
            <a :href="`/logs/${props.build.id}.txt`">Full log file</a>
        </div>
    </div>
</template>

<script lang="ts" setup>
import Convert from 'ansi-to-html';
import {computed} from "vue";
import {useBuildsStore} from "@/stores/builds";

// noinspection
import XIcon from "@/components/Icons/X.vue";
import StopIcon from "@/components/Icons/Stop.vue";
import CheckIcon from "@/components/Icons/Check.vue";
import PythonIcon from "@/components/Icons/Python.vue";
import TrashIcon from "@/components/Icons/Trash.vue";
import RefreshIcon from "@/components/Icons/Refresh.vue";
import TensorflowIcon from "@/components/Icons/Tensorflow.vue";

interface LogLine {
    line_number: number
    line: string
}

const props = defineProps<{ build: any }>();
const converter = new Convert();
const logs = computed((): LogLine[] => {
    return props.build.logs.map((log: LogLine): LogLine => {
        return {line_number: log.line_number, line: converter.toHtml(log.line)};
    });
});
const buildsStore = useBuildsStore();

async function cancel() {
    try {
        await buildsStore.cancel(props.build.id);
    } catch (e: any){
        if (e.status === 400) {
            alert(e.body.detail);
        }
    }
}

async function rebuild() {
    try {
        await buildsStore.put(props.build.id, props.build);
    } catch (e: any){
        if (e.status === 400) {
            alert(e.body.detail);
        }
    }
}

async function remove() {
    try {
        await buildsStore.remove(props.build.id);
    } catch (e: any){
        if (e.status !== 200) {
            alert(e.body.detail);
        }
    }
}

</script>

<style scoped>

.build-log {
    border: solid 1px #efefef;
    border-radius: 8px;
    padding: 4px;
    background: #efefef;
    max-height: 400px;
    overflow-y: auto;
}

.log-line {
    display: flex;
    padding: 8px;
    font-size: 14px;
    font-family: 'Space Mono', monospace;
}

.log-line:hover {
    background: rgba(0, 0, 0, 0.1);
}

.line-number {
    color: rgba(0, 0, 0, 0.7);
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.spin-animation {
    animation: spin 5s linear infinite;
}

.icon-md {
    height: 20px;
    width: 20px;
}

.icon-sm {
    height: 16px;
    width: 16px;
}
</style>