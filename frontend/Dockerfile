# --- Build Stage ---
# Use official Node.js image as build environment
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json files
COPY package.json package-lock.json ./

# Install project dependencies
RUN npm install

# Copy all source code
COPY . .

# Build production version static files
RUN npm run build

# --- Run Stage ---
# Use official Nginx image as web server
FROM nginx:1.27-alpine

# Copy static files generated in build stage to Nginx web root directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration file to container
COPY Nginx.conf /etc/nginx/conf.d/default.conf

# Expose Nginx default port 80
EXPOSE 80

# Nginx starts by default, we keep the default command
CMD ["nginx", "-g", "daemon off;"]
