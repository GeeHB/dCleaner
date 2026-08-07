#!/bin/python
#
# coding=UTF-8
#
#   Fichier     :   jlogger.py
#
#   Description :   Définition des objets :
#                     - LogLevel : Niveau des logs
#                     - jLogger : Gestion des affichages et des logs
#
#

import datetime
import os
import sys
from zoneinfo import ZoneInfo

# Format de la date (pour les logs)
JLOG_VERSION = "1.0.1"

# Date et heure pour les logs
JLOG_DATE_REGION = "Europe/Paris"
JLOG_DATE_FORMAT = "%d/%m/%Y-%H:%M:%S"
JLOG_DATE_FORMAT_PID = f"{JLOG_DATE_FORMAT} [{os.getpid()}] "

class LogLevel:
    LOG_NONE = 0
    LOG_QUIET = 1
    LOG_NORMAL = 10
    LOG_FULL = 100
    LOG_ERROR = 255     # Toujours affiché

class jLogger:
    # Construction
    def __init__(self):
        self.level_ = LogLevel.LOG_FULL
        self.logInfos_ = False
        self.pid_ = False

    # Niveau de logs
    @property
    def level(self):
        return self.level_
    @level.setter
    def level(self, value : int):
        if value >= LogLevel.LOG_NONE and value <= LogLevel.LOG_FULL :
            self.level_ = value

    # Ajout de la date et de l'heure
    @property
    def log(self):
        return self.logInfos_
    @log.setter
    def log(self, value : bool):
        self.logInfos_ = value

    # Ajout du pid ?
    @property
    def pid(self):
        return self.pid_
    @pid.setter
    def pid(self, value : bool):
        self.pid_ = value

    # Ajout d'une ligne de texte
    def print(self, level = LogLevel.LOG_NORMAL, text = "", bloc = ""):
        # plusieurs lignes ?
        if len(bloc) > 0:
            lignes = bloc.splitlines()
            for ligne in lignes :
                self.print(level, text = ligne)
        else:
            # Juste ce qu'il faut afficher
            if len(text) and (level == LogLevel.LOG_ERROR or self.level >= level) :
                prefix = ""
                if self.log:
                    # En mode log. on ajoute la date et l'heure et éventuellement le pid
                    today = datetime.datetime.now(tz=ZoneInfo(JLOG_DATE_REGION))
                    prefix = today.strftime(JLOG_DATE_FORMAT_PID if self.pid else JLOG_DATE_FORMAT)
                    line = prefix + " " + text
                else:
                    line = text

                if level == LogLevel.LOG_ERROR :
                    sys.stderr.write(line)
                else:
                    print(line)

    # Ajout d'une ligne d'erreur ou d'avertissement
    def error(self, msg : str, level = LogLevel.LOG_NORMAL):
        self.print(text = msg, level = LogLevel.LOG_ERROR)

# EOF
