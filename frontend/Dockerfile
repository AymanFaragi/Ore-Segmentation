# syntax=docker/dockerfile:1

# Note: this build does NOT require `output: "standalone"` in
# next.config.mjs — the runner stage copies full node_modules instead.
# That's simpler and safer against surprise breakage, at the cost of a
# larger final image. If you later add `output: "standalone"` to
# next.config.mjs, the runner stage can shrink to copying just
# .next/standalone + .next/static + public, which is meaningfully smaller.

# =========================================================================
# Stage 1: deps
# Installs node_modules from the lockfile only — cached independently of
# app source changes.
# =========================================================================
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci


# =========================================================================
# Stage 2: builder
# Builds the production Next.js output.
# =========================================================================
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build


# =========================================================================
# Stage 3: runner
# Only the built app + production node_modules, running as non-root.
# =========================================================================
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD node -e "fetch('http://localhost:3000/').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["npm", "start"]
