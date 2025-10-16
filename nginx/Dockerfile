FROM nginx:alpine

# Remove default configuration

RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration

COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx user and set permissions

RUN chown -R nginx:nginx /var/cache/nginx &&   
chown -R nginx:nginx /var/log/nginx &&   
touch /var/run/nginx.pid &&   
chown -R nginx:nginx /var/run/nginx.pid

# Use non-root user

USER nginx

# Expose ports

EXPOSE 80 443

# Health check

HEALTHCHECK –interval=30s –timeout=3s –start-period=5s –retries=3   
CMD wget –quiet –tries=1 –spider http://localhost/api/health || exit 1

CMD [“nginx”, “-g”, “daemon off;”]
