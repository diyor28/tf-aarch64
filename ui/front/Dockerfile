FROM node:16-alpine as build-stage
WORKDIR /app
COPY package*.json ./

RUN npm i
RUN npm install -g @vue/cli

COPY . .

RUN npm run build

FROM nginx:1.23.2-alpine as production-stage
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
