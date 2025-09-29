FROM node:20-alpine AS build

WORKDIR /app

COPY ../package.json package-lock.json ./
RUN npm ci

COPY .. .
ARG VITE_API_URL=http://localhost:8001/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

COPY --from=build /app/dist ./dist

RUN npm install -g serve

CMD ["serve", "-s", "dist", "-l", "3001"]
