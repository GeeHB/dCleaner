#!/bin/python
#
# coding=UTF-8
#
#   Fichier     :   jlogger.py
#
#   Description :   Définition des objets :
#                     - LogLevel : Niveau des logs
#                     - jLogger : Gestion des erreurs et des logs
#
#

import datetime
import os
import sys
from zoneinfo import ZoneInfo

JLOG_VERSION = "1.1.1"

# Date et heure pour les logs
JLOG_DATE_REGION = "Europe/Paris"
JLOG_DATE_FORMAT = "%d/%m/%Y-%H:%M:%S"
JLOG_DATE_FORMAT_PID = f"{JLOG_DATE_FORMAT} [{os.getpid()}]"

# Prefixes des lignes
LOG_PREFIX_DEBUG = "DBG"
LOG_PREFIX_ERROR = "ERR"

# Niveaux reconnus
class LogLevel:
    LOG_NONE:int = 0
    LOG_QUIET:int = 1
    LOG_NORMAL:int = 10
    LOG_FULL:int = 20
    LOG_DEBUG:int = 200
    LOG_ERROR:int = 255     # Toujours affiché
    LOG_MIN:int = LOG_NONE
    LOG_MAX:int = LOG_ERROR

class jLogger:
    # Construction
    def __init__(self):
        self.level_:int = LogLevel.LOG_FULL
        self.logInfos_:bool = False
        self.pid_:bool = False

    # Niveau de logs
    @property
    def level(self):
        return self.level_
    @level.setter
    def level(self, value : int):
        if value >= LogLevel.LOG_MIN and value <= LogLevel.LOG_MAX :
            self.level_ = value

    # Ajout de la date et de l'heure
    @property
    def log(self)->bool:
        return self.logInfos_
    @log.setter
    def log(self, value : bool):
        self.logInfos_ = value

    # Ajout du pid ?
    @property
    def pid(self)->int:
        return self.pid_
    @pid.setter
    def pid(self, value : bool):
        self.pid_ = value

    # Ajout d'une ligne de texte
    def print(self, level:int = LogLevel.LOG_NORMAL, text:str = "", bloc:str = "", linePrefix:str = ""):
        # plusieurs lignes ?
        if len(bloc) > 0:
            lignes = bloc.splitlines()
            for ligne in lignes :
                self.print(level, text = ligne)
        else:
            # Juste ce qu'il faut afficher
            if len(text) and (level == LogLevel.LOG_ERROR or self.level >= level) :
                prefix = f" [{linePrefix}]" if len(linePrefix) >0 else ""
                if self.log:
                    # En mode log. on ajoute la date et l'heure et éventuellement le pid
                    today = datetime.datetime.now(tz=ZoneInfo(JLOG_DATE_REGION))
                    prefix = today.strftime(JLOG_DATE_FORMAT_PID if self.pid else JLOG_DATE_FORMAT) + prefix
                    line = prefix + " " + text
                else:
                    line = text

                if level == LogLevel.LOG_ERROR :
                    _ = sys.stderr.write(line)
                else:
                    print(line)

    # Ajout d'une ligne d'erreur ou d'avertissement
    def error(self, msg : str):
        self.print(text = msg, level = LogLevel.LOG_ERROR)

    # Ajout d'une ligne de logs enmode debug
    def debug(self, msg : str):
        self.print(text = msg, level = LogLevel.LOG_DEBUG, linePrefix = LOG_PREFIX_DEBUG)

# EOF
