#!/bin/python
#
# coding=UTF-8
#
#   Fichier     :   fakeProgressBar.py
#
#   Auteur      :   JHB
#
#   Description :   Interface // à alive_progress
#

from contextlib import contextmanager

# Constantes
#
MSG_NO_ALIVE_PROGRESS = "Le module 'alive_progress.alive_bar' n'est pas installé. Essayez : pip install alive-progress"

#
# Ma barre ...
#

# Version 2 en utilisant un decorateur sur la fonction (qui ne fait rien)
@contextmanager
def fakeProgressBar(_maxValue:int = 0, _title:str = "", _monitor:str = "", _monitor_end:str = "", _elapsed:str = "", _elapsed_end:str = "", _stats:bool = False):
    # __enter__
    yield fakeProgressBar
    # __exit__

# EOF
