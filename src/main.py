from fastapi import FastAPI
from src.auth.routes import auth_router
from src.bot.routes import bots_router
from src.bot.instagram_integration.routes import bots_instagram
from src.core.middleware import register_middleware
from src.utils.error_handler import register_all_errors

version = "v1"

description = """
A REST API for NE
"""

version_prefix = f"/api/{version}"

app = FastAPI(
    title="Neuro-employees",
    description=description,
    version=version,
    license_info={"name": "MIT License","url":"https://opensource.org/licenses/MIT"},
    contact={
        "name": "isaog",
        "url": "https://github.com/watashiwaisadesu/nuero-employees",
        "email": "islambek040508@gmail.com",
    },
    docs_url=f"{version_prefix}/docs",
)

register_middleware(app)
register_all_errors(app)


app.include_router(auth_router, prefix=f"{version_prefix}/auth", tags=["Auth"])
app.include_router(bots_router, prefix=f"{version_prefix}/bots", tags=["Bots"])
app.include_router(bots_instagram, prefix=f"{version_prefix}/bots_instagram", tags=["Bots_instagram"])



