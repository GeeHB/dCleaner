#!/bin/python3

# coding=UTF-8
#
#   File     :   test.py
#
#   Auteur      :   JHB
#
#   Description :   Tests du programme
#
import sys
sys.path.insert(0, '/home/jhb/Nextcloud/dev/python/dCleaner')
from basicFolder import basicFolder, basicFile

if '__main__' == __name__:

    # basicFile
    bFile = basicFile("/home/jhb/Téléchargements/temp", "other.mkv")

    if bFile.exists():
        # Suppression
        total = 0
        expected = bFile.size()
        index = 0
        for index, portion in enumerate(bFile.delete()):
            if index % 10 == 0: 
                print(f"Effacement de {portion} octets")
            total += portion

        if bFile.noError():
            print(f"Suppression de {total} octets / {expected} octets")
        else:
            print(f"Erreur : {bFile.error}")
    else:
        print(f"Le fichier {bFile.name} n'existe pas")

# EOF
