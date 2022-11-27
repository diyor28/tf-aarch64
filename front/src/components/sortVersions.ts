export function sortVersions(versions: any[]) {
	return versions.sort((a, b) => a.replace(/\d+/g, (n: any) => + n + 100000).localeCompare(b.replace(/\d+/g, (n: any) => + n + 100000)));
}