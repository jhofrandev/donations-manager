#!/bin/sh
# wait-for-postgres.sh
# Espera a que PostgreSQL esté listo antes de continuar

set -e

host="$1"
shift

# Validar variables de entorno
if [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ] || [ -z "$DATABASE_NAME" ]; then
  echo "Faltan variables de entorno:"
  echo "  DATABASE_USER=$DATABASE_USER"
  echo "  DATABASE_PASSWORD=${DATABASE_PASSWORD:+***}"
  echo "  DATABASE_NAME=$DATABASE_NAME"
  exit 1
fi

echo "Esperando a Postgres en host: $host, base: $DATABASE_NAME, usuario: $DATABASE_USER"

until PGPASSWORD="$DATABASE_PASSWORD" psql -h "$host" -U "$DATABASE_USER" -d "$DATABASE_NAME" -c '\q' 2>/dev/null; do
  >&2 echo "Postgres no está disponible aún - esperando..."
  sleep 1
done

>&2 echo "Postgres está listo - continuando..."
exec "$@"
