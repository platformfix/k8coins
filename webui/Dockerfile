# Build stage: resolve node_modules from the lockfile, production only.
FROM node:24-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Final stage: copy only the resolved modules and app code, no npm cache,
# no dev dependencies.
FROM node:24-alpine
WORKDIR /app
COPY --from=builder /app/node_modules node_modules
COPY package.json webui.js ./
COPY files files
# node:*-alpine already ships a node user at UID 1000, so this image needs
# no addgroup/adduser line, unlike the Python and Ruby services.
USER 1000
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s CMD ["wget", "-q", "-O-", "http://localhost:80/index.html"]
CMD ["node", "webui.js"]
