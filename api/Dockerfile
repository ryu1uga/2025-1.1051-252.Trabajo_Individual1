FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --production
COPY index.js ./
ENV REDIS_URL redis://redis:6379
EXPOSE 3000
CMD ["node","index.js"]