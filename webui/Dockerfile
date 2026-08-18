FROM node:24-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:24-alpine
WORKDIR /app
COPY --from=builder /app/node_modules node_modules
COPY package.json webui.js ./
COPY files files
USER 1000
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s CMD ["wget", "-q", "-O-", "http://localhost:80/index.html"]
CMD ["node", "webui.js"]
