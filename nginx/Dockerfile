FROM nginx:alpine

# Install curl for health check support
# Benefits: Enables HTTP health checks, container monitoring
RUN apk add --no-cache curl

COPY  ./default.conf /etc/nginx/conf.d/default.conf
