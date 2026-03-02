# ============================================================
# Stage 1: Build Stage
# ============================================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install all dependencies (yarn is built into node:18-alpine)
RUN yarn install --frozen-lockfile

# Copy the rest of the source code
COPY . .

# ============================================================
# Stage 2: Production Stage
# ============================================================
FROM node:18-alpine AS production

LABEL maintainer="devops-student"
LABEL app="icecream"
LABEL version="1.0.0"

# Create a non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install production dependencies only
RUN yarn install --production --frozen-lockfile

# Copy app from builder
COPY --from=builder /app .

# Set ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the app
CMD ["node", "index.js"]
