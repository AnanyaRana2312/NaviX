version: "3.9"

services:
  backend:
    build: .
    container_name: navix-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - ./backend:/app/backend
    restart: always

  db:
    image: postgis/postgis:15-3.3
    container_name: navix-db
    environment:
      POSTGRES_DB: navix
      POSTGRES_USER: navix_user
      POSTGRES_PASSWORD: navix_pass
    ports:
      - "5432:5432"
    volumes:
      - navix_db_data:/var/lib/postgresql/data
    restart: always

volumes:
  navix_db_data:
