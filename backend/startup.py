import importlib
import pkgutil
from fastapi import FastAPI, Request
from fastapi.routing import APIRouter
import controllers

def startup_app(app: FastAPI):
    for _, module_name, _ in pkgutil.iter_modules(controllers.__path__, "controllers."):
        module = importlib.import_module(module_name)
        if hasattr(module, "router") and isinstance(module.router, APIRouter):
            app.include_router(module.router)
            