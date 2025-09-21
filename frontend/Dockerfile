# Multi-stage build for optimized production image
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first (cache layer - only rebuilds when package.json changes)
COPY package*.json ./

# Install dependencies (cached unless package.json changes)
RUN npm ci --only=production --silent

# Copy source code (runs when code changes, but deps are cached)
COPY . .

# Build the app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]