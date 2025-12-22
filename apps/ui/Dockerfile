# Stage 1: Build
FROM node:20-slim as builder

WORKDIR /app

# Increase memory limit for build to avoid OOM on smaller instances
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Copy package files (including lock file for reproducible builds)
COPY package.json package-lock.json ./

# Clean install with ci for reproducible builds
RUN npm ci

# Copy source files
COPY . .

# Run build
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]