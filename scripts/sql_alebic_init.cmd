@echo off
PUSHD ..

alembic init migrations

alembic revision --autogenerate -m "Init"

POPD