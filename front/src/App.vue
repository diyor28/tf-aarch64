<template>
    <html>
    <body>
    <suspense>
        <router-view></router-view>
    </suspense>
    </body>
    </html>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono&display=swap');

body {
    font-family: "system-ui", serif;
}

ul {
    padding-left: 0;
}

li {
    list-style-type: none;
}

a {
    text-decoration: none;
}

button {
    background: none;
    color: inherit;
    border: none;
    padding: 0;
    font: inherit;
    cursor: pointer;
    outline: inherit;
}

.select {
    padding: 0.5rem;
    border-radius: 8px;
    border-color: rgb(209, 213, 219);
    background-color: rgb(249, 250, 251);
}

.btn {
    background: rgba(0, 0, 0, 0);
    border: solid 1px rgb(229, 231, 235);
    padding: 10px 16px;
    border-radius: 8px;
    text-shadow: none;
    box-sizing: border-box;
    -webkit-border-image: none;
}

.btn-success {
    background: rgb(47,164,78);
    color: rgb(255,255,255);
}

.label {
    display: block;
    font-size: .875rem;
    line-height: 1.25rem;
}

.flex {
    display: flex;
}

.flex-auto {
    flex: 1 1 auto;
}

.flex-initial {
    flex: 1 0 auto;
}

.align-center {
    align-items: center;
}

.justify-center {
    justify-content: center;
}

.space-x-2 {
    column-gap: 0.5rem;
}

.space-x-4 {
    column-gap: 1rem;
}

.ml-2 {
    margin-left: 0.5rem;
}

.mr-2 {
    margin-right: 0.5rem;
}

.p-2 {
    padding: 0.5rem;
}

.pl-2 {
    padding-left: 0.5rem;
}

.pr-2 {
    padding-right: 0.5rem;
}

.ml-4 {
    margin-left: 1rem;
}

.mr-4 {
    margin-right: 1rem;
}

.mt-2 {
    margin-top: 0.5rem;
}

.mt-4 {
    margin-top: 1rem;
}

.my-auto {
    margin-top: auto;
    margin-bottom: auto;
}
</style>
