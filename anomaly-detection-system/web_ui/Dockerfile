# Use an official Nginx image as a parent image
FROM nginx:alpine

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy the static HTML files
COPY index.html /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Command to run Nginx (default for nginx:alpine)
CMD ["nginx", "-g", "daemon off;"]
