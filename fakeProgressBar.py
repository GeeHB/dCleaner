# coding=UTF-8
#
#   Fichier     :   fakeProgressBar.py
#
#   Author      :   JHB
#
#   Description :   Interface // à alive_progress
#

#
# Ma barre ...
#
class fakeProgressBar:
    
    # Constructeur // alive_progress (qui utilise  une decorator)
    def __init__(self, maxValue, title = "", monitor = "", monitor_end = "", elapsed = "", elapsed_end = "", stats = False):
        pass
    
    # Surcharges pour pouvoir utiliser "with"
    def __enter__(self):
        pass
    def __exit__(self, exc_type,exc_value, exc_traceback):
        pass

# EOF