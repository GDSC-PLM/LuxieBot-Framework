FROM oven/bun:1 AS base

WORKDIR /app

COPY package.json bun.lock ./
COPY shared/sdk/package.json ./shared/sdk/
COPY services/bot/package.json ./services/bot/

RUN bun install --frozen-lockfile

COPY shared/sdk ./shared/sdk
COPY services/bot ./services/bot

RUN cd shared/sdk && bun run build
RUN cd services/bot && bun run build

WORKDIR /app/services/bot

CMD ["bun", "run", "start"]
