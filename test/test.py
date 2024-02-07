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
from basicFile import basicFile
from parameters import options

# creation
def create(bFile, rename, size):
    
    if rename :
        if not bFile.exists():
            print("Erreur le fichier n'existe pas. Il ne peut être renommé")
            return
        
        # Dossier destination
        folder = bFile.folder()
        if folder is None:
            print("Erreur - Pas de dossier pour le fichier")

        # Nouveau nom
        name = basicFile.genName(folder, False)
        if name is None:
            print("Erreur - Impossible de générer un nouveau nom")
        
        bFile.rename(name)

    total = 0
    index = 0
    
    for index, portion in enumerate(bFile.create(size)):
        if index % 10 == 0: 
            # Affichage un fois sur 10 !
            print(f"Ecriture de {portion} octets")
        total += portion

    if bFile.success():
        print(f"Creation de {bFile.name} avec {total} octets / {size} octets")
    else:
        print(f"Erreur : {bFile.error}")
    
# Remplissage et/ou suppression
def fillorDelete(bFile):
    
    if bFile.exists():
        # Suppression
        total = 0
        expected = bFile.size()
        index = 0
        #for index, portion in enumerate(bFile.delete()):
        for index, portion in enumerate(bFile.fill(True)):
            if index % 10 == 0: 
                # Affichage un fois sur 10 !
                print(f"Ecriture de {portion} octets")
            total += portion

        if bFile.success():
            print(f"Rempliisage de {total} octets / {expected} octets")
        else:
            print(f"Erreur : {bFile.error}")
    else:
        print(f"Le fichier {bFile.name} n'existe pas")

if '__main__' == __name__:

    # basicFile
    params = options
    bFile = basicFile(params, path = "/home/jhb/Téléchargements/temp", fname = "other.mkv")

    # fillorDelete(bFile)
    create(bFile, False, 456789)
    #create(bFile, True, 2340539)
    
# EOF
