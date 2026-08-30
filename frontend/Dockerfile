FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

ARG VITE_API_BASE_URL=""

COPY . .

RUN if [ -n "$VITE_API_BASE_URL" ]; then \
      printf 'VITE_API_BASE_URL=%s\n' "$VITE_API_BASE_URL" > .env.production; \
    fi \
    && npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
