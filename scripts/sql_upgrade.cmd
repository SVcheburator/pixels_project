@echo off

PUSHD ..

rem alembic revision --autogenerate -m "Updates"
alembic upgrade head 

POPD