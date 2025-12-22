# Stage 1: Build
FROM node:20-alpine as builder
WORKDIR /app

# Install build dependencies that might be needed
RUN apk add --no-cache python3 make g++

# Increase memory limit for build
ENV NODE_OPTIONS="--max-old-space-size=2048"

# Copy package files
# CRITICAL: We only copy package.json (NOT package-lock.json) to ensure we get fresh,
# architecture-correct binaries for the container's OS/CPU.
COPY package.json ./

# Clean install (use npm ci if you have package-lock.json)
RUN npm install --legacy-peer-deps

# Copy source files
COPY . .

# Add verbose logging to see what's failing
RUN npm run build --verbose

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]