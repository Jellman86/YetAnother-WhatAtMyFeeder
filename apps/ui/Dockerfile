# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

# Increase memory limit for build to avoid OOM on smaller instances
ENV NODE_OPTIONS="--max-old-space-size=2048"

COPY package.json ./
# We skip copying package-lock.json to force a fresh install compatible with the container's architecture
# This fixes potential cross-platform lockfile issues (e.g. missing optional dependencies for ARM)
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]