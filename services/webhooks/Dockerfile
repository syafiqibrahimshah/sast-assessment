FROM node:18-alpine
WORKDIR /srv
COPY package*.json .
RUN npm install --omit=dev
COPY . .
EXPOSE 8081
CMD ["npm", "start"]
