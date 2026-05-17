# Build stage
FROM node:18-alpine as build
WORKDIR /app

COPY package*.json ./
RUN npm ci || npm install

COPY . .

# Set API URL as arg to be passed during build
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
