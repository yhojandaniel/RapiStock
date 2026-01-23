#!/bin/bash

# Nombre del proyecto
PROJECT_NAME="RapiStock"

echo "Construyendo arquitectura profesional para: $PROJECT_NAME..."

# 1. Crear Raíz y entrar
# mkdir -p $PROJECT_NAME
# cd $PROJECT_NAME

# 2. Archivos de Configuración Raíz
touch .gitignore
touch .env
touch README.md
touch docker-compose.yml
touch alembic.ini

# 3. Directorios de CI/CD
mkdir -p .github/workflows

# 4. Estructura Backend
mkdir -p backend/app/core
mkdir -p backend/app/modules
mkdir -p backend/app/shared
mkdir -p backend/tests
mkdir -p backend/migrations

# 5. Archivos base del Backend
touch backend/Dockerfile
touch backend/requirements.txt
touch backend/prestart.sh
touch backend/app/main.py
touch backend/app/__init__.py

# 6. Archivos de Core
touch backend/app/core/__init__.py
touch backend/app/core/config.py
touch backend/app/core/db.py
touch backend/app/core/security.py

# 7. Archivos Shared
touch backend/app/shared/__init__.py
touch backend/app/shared/utils.py
touch backend/app/shared/dependencies.py

# 8. Generador de Módulos
# Nota: 'inventory' manejará 'products', y agregamos 'sellers' y 'refunds'
MODULES=("auth" "inventory" "orders" "refunds" "sellers")

for module in "${MODULES[@]}"; do
    echo "Creando módulo de dominio: $module"
    mkdir -p backend/app/modules/$module
    
    # Los 4 Archivos Sagrados
    touch backend/app/modules/$module/__init__.py
    touch backend/app/modules/$module/models.py   # Aquí irán tus tablas SQLModel
    touch backend/app/modules/$module/schemas.py  # Aquí irán los Pydantic
    touch backend/app/modules/$module/service.py  # Aquí irá la lógica (ej: validar stock)
    touch backend/app/modules/$module/router.py   # Aquí irán los endpoints
done

# 9. Estructura de Tests (Espejo)
touch backend/tests/__init__.py
touch backend/tests/conftest.py # Configuración de Pytest
for module in "${MODULES[@]}"; do
    mkdir -p backend/tests/test_$module
    touch backend/tests/test_$module/__init__.py
    touch backend/tests/test_$module/test_${module}_api.py
done

echo "Estructura V2 creada exitosamente en ./$PROJECT_NAME"