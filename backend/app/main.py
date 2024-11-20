from app.controllers.user_controller import router as user_controller
from app.controllers.migration import router as migration_controller
from app.controllers.auth_controller import router as auth_controller
from app.controllers.category_controller import router as category_controller
from app.controllers.storage_controller import router as storage_controller

from fastapi.middleware.cors import CORSMiddleware


from fastapi import FastAPI

app = FastAPI(
    title="API DE GESTION D'UNE BIBLIOTHÈQUE UNIVERSITAIRE",
    version="1.0.0",
    description="Une API pour la gestion d'une bibliothèque universitaire, incluant les fonctionnalités de gestion des utilisateurs, des livres, des catégories, des emprunts et des retours.",
    contact={
        "name": "Support Technique",
        "email": "support@bibliotheque-universitaire.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre à toutes les origines (mieux vaut restreindre cela en production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller, prefix="/api/v1/auth", tags=["auth"])
app.include_router(migration_controller, prefix="/api/v1/migrations", tags=["migrations"])
app.include_router(user_controller,prefix="/api/v1/users",tags=["users"])
app.include_router(category_controller, prefix="/api/v1/categories", tags=["categories"])
app.include_router(storage_controller, prefix="/api/v1/storage", tags=["storage"])

