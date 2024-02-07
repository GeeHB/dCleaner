# coding=UTF-8
#
#   Fichier     :   fakeProgressBar.py
#
#   Auteur      :   JHB
#
#   Description :   Interface // à alive_progress
#

from contextlib import contextmanager

"""
#
# Ma barre ...
#
class fakeProgressBar:
    
    # Constructeur // alive_progress 
    def __init__(self, maxValue, title = "", monitor = "", monitor_end = "", elapsed = "", elapsed_end = "", stats = False):
        pass
    
    # Surcharges pour pouvoir utiliser "with"
    def __enter__(self):
        pass
    def __exit__(self, exc_type,exc_value, exc_traceback):
        pass
"""

# Version 2 en utilisant un decorateur sur la fonction (qui ne fait rien)
@contextmanager
def fakeProgressBar(maxValue = 0, title = "", monitor = "", monitor_end = "", elapsed = "", elapsed_end = "", stats = False):
    # __enter__
    yield fakeProgressBar
    # __exit__

# EOF