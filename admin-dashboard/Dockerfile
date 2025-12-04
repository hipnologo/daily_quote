# Build stage for Admin Dashboard
FROM node:18-alpine AS build

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package*.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application (outputs to /app/dist with /admin base path)
RUN pnpm run build

# Production stage
FROM nginx:alpine

# Create directories for both sites
RUN mkdir -p /usr/share/nginx/html/public /usr/share/nginx/html/admin

# Copy admin dashboard build to /admin
COPY --from=build /app/dist /usr/share/nginx/html/admin

# Copy public website files (index.html and assets from project root)
# These will be copied via docker-compose context or build args
COPY --from=build /app/../index.html /usr/share/nginx/html/public/ 2>/dev/null || true
COPY --from=build /app/../public /usr/share/nginx/html/public/public/ 2>/dev/null || true
COPY --from=build /app/../images /usr/share/nginx/html/public/images/ 2>/dev/null || true

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
