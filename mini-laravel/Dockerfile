FROM php:8.4-cli
RUN apt-get update && apt-get install -y unzip git libsqlite3-dev \
    && docker-php-ext-install pdo pdo_sqlite
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /var/www/html
COPY . .
RUN composer install --no-interaction --prefer-dist \
    && cp -n .env.example .env \
    && touch database/database.sqlite \
    && php artisan key:generate
EXPOSE 8080
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8080"]
