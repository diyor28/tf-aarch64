import {defineStore} from "pinia";

export interface Build {
    id: number
    python: string
    package: string
    type: string
    filename: string
}

export const useBuildsStore = defineStore("builds", {
    state: (): { builds: Build[] } => {
        return {builds: []};
    },
    actions: {
		async fetch() {
			const response = await fetch(process.env.VUE_APP_API_URL + '/builds', {
				method: 'get',
				headers: {'Content-Type': 'application/json'}
			});
			this.builds = await response.json();
		},

		async create(data: any) {
			const response = await fetch(process.env.VUE_APP_API_URL + '/builds', {
				method: 'post',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(data)
			});
			const respBody = await response.json();
			if (response.status >= 200 && response.status < 300) {
				this.builds.push(respBody);
				return respBody;
			}
			return Promise.reject({status: response.status, statusText: response.statusText, body: respBody});
		},

		async put(filename: string, data: any) {
			const response = await fetch(process.env.VUE_APP_API_URL + '/builds/' + filename, {
				method: 'put',
				headers: {'Content-Type': 'application/json'},
				body: JSON.stringify(data)
			});
			const build = await response.json();
			if (response.status >= 200 && response.status < 300) {
				const idx = this.builds.findIndex(el => el.id === build.id);
				if (idx === - 1) {
					this.builds.push(build);
				} else {
					this.builds[idx] = build;
				}
				return build;
			}
			return Promise.reject({status: response.status, statusText: response.statusText, body: build});
		},

		async cancel(filename: string) {
			const response = await fetch(process.env.VUE_APP_API_URL + `/builds/${filename}/cancel`, {
				method: 'post',
				headers: {'Content-Type': 'application/json'},
			});
			const respBody = await response.json();
			if (response.status >= 200 && response.status < 300) {
				return respBody;
			}
			return Promise.reject({status: response.status, statusText: response.statusText, body: respBody});

		}
	},
	getters: {
		tf: (state) => {
			return state.builds.filter(el => el.type === 'tensorflow');
		},
		tfx: (state) => {
			return state.builds.filter(el => el.type === 'tfx');
		},
		tfxbsl: (state) => {
			return state.builds.filter(el => el.type === 'tfx-bsl');
		},
    },
});