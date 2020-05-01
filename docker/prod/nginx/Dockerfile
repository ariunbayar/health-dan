# pull official base image
FROM nginx:1.17-alpine

# Clear built in conf: container
RUN rm /etc/nginx/conf.d/default.conf

# Copy conf template: host -> container
COPY nginx.conf /etc/nginx/conf.d/nginx.conf
