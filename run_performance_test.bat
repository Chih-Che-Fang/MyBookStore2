REM Get docker entry point script
xcopy /y .\docker_scripts\run_client.sh .\run.sh

REM kill all docker process
@ECHO OFF
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker stop %%i
FOR /f "tokens=*" %%i IN ('docker ps -aq') DO docker rm %%i

REM Build docker image
docker build -t bookstore .

REM Run the docker image and map port to local host
start cmd /k docker run --name mybookstore32144321 bookstore

pause