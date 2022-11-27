import {defineStore} from "pinia";

export interface Version {
	package: string
	python: string
}

export interface State {
	tfVersions: Version[]
	tfxVersions: Version[]
}

export const useVersionsStore = defineStore("versions", {
	state: (): State => {
		return {tfVersions: [], tfxVersions: []};
	},
	actions: {
		async fetch() {
			const response = await fetch(process.env.VUE_APP_API_URL + '/versions', {
				method: 'get',
				headers: {'Content-Type': 'application/json'}
			});
			const data = await response.json();
			this.tfVersions = data.tensorflow;
			this.tfxVersions = data.tfx;
		}
	},
	getters: {
		tensorflow: (state) => state.tfVersions,
		tfx: (state) => state.tfxVersions
	},
});