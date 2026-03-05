# ─────────────────────────────────────────────────────────────
# Stage 1: deps – install production + dev deps for the build
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ─────────────────────────────────────────────────────────────
# Stage 2: builder – compile the Next.js app
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

# Copy deps installed above
COPY --from=deps /app/node_modules ./node_modules
# Copy all source files
COPY . .

# NEXT_PUBLIC_* vars are inlined at build time, so pass them here.
# Override with --build-arg on the CLI, or via compose `build.args`.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_ENABLE_CHATBOT=true
ARG NEXT_PUBLIC_AUTH_DOMAIN=auth.tracedata.ai

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_ENABLE_CHATBOT=$NEXT_PUBLIC_ENABLE_CHATBOT
ENV NEXT_PUBLIC_AUTH_DOMAIN=$NEXT_PUBLIC_AUTH_DOMAIN

RUN npm run build

# ─────────────────────────────────────────────────────────────
# Stage 3: runner – lean production image
# ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
# Allow the port to be overridden at runtime
ENV PORT=3000

# Copy only what next start needs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

# next start via the standalone server.js
CMD ["node", "server.js"]
