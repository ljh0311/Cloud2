REM Run Hadoop job with simplified arguments
REM Usage: run_hadoop.bat <dataset> <output>

IF "%~1"=="" (
    echo Usage: run_hadoop.bat ^<dataset^> ^<output^>
    echo Example: run_hadoop.bat drivingsg_data_20250318_143009.json output
    exit /b 1
)

IF "%~2"=="" (
    echo Usage: run_hadoop.bat ^<dataset^> ^<output^>
    echo Example: run_hadoop.bat drivingsg_data_20250318_143009.json output
    exit /b 1
)

set DATASET=%~1
set OUTPUT=%~2

echo Running Hadoop job with:
echo Dataset: %DATASET%
echo Output: %OUTPUT%

REM Find the project directory whether run from Eclipse or command line
IF EXIST ".\target\CloudProjectHadoop.jar" (
    set PROJECT_DIR=.
) ELSE IF EXIST "..\target\CloudProjectHadoop.jar" (
    set PROJECT_DIR=..
) ELSE (
    echo ERROR: Could not find CloudProjectHadoop.jar
    exit /b 1
)

REM Delete the output directory if it exists to prevent FileAlreadyExistsException
IF EXIST "%OUTPUT%" (
    echo Deleting existing output directory: %OUTPUT%
    rmdir /s /q "%OUTPUT%"
)

REM Run the Java command with simplified arguments and added security settings
java -Djava.security.manager=allow -Dlog4j.configuration=file:%PROJECT_DIR%/src/main/resources/log4j.properties -jar %PROJECT_DIR%/target/CloudProjectHadoop.jar %DATASET% %OUTPUT%

echo Job completed with exit code %ERRORLEVEL%

