import {defineStore} from "pinia";
import {EventBus} from "@/components/eventBus";

function connectWs(url: string) {
    const socket = new WebSocket(url);
    const bus = new EventBus();
    socket.onopen = (event) => {
        bus.emit('open', event);
    };
    socket.onclose = (event) => {
        bus.emit('close', event);
    };
    socket.onmessage = (message) => {
        const {event, data} = JSON.parse(message.data);
        bus.emit(event, data);
    };
    return bus;
}

export const useLogsStore = defineStore("logs", {
    state: (): { logs: Record<string, Record<number, string>> } => {
        return {logs: {}};
    },
    actions: {
        listenLogs(truncate: number = 100) {
            const socket = connectWs(process.env.VUE_APP_WS_URL);

            socket.on('log_updates', (data: { name: string, line_number: number, line: string }) => {
                this.logs[data.name] = this.logs[data.name] || {};
                this.logs[data.name][data.line_number] = data.line;
                const keys: any[] = Object.keys(this.logs[data.name]);
                if (keys.length >= truncate) {
                    for (let i = 0; i <= truncate; i++) {
                        if (keys.length - i <= truncate) {
                            const key = keys[i];
                            delete this.logs[data.name][key];
                        }
                    }
                }
            });
        }
    },
    getters: {
        getLogs: (state) => {
            return (filename: string) => state.logs[filename] || {};
        }
    },
});