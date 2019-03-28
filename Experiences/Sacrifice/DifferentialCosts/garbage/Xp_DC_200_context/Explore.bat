@echo off
echo Lancement d une serie d experience a partir de %2
if "%2" EQU "" goto usage
:debut
if exist fini goto fin
date /T
time /T
echo ...
EvoGen.py %1 %2 Evolife.evo
start /BELOWNORMAL /WAIT /MIN ..\Evolife_Main.py
goto debut
goto fin
:usage
echo Usage: Explore [typical_conf_file.evo] [fich.evm]
pause
:fin
time /T
del /Q fini
