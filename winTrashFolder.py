# coding=UTF-8
#
#   Fichier     :   winTrashFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet winTrashFolder pour la modélisation de la poubelle Windows
#
#   Remarque    : 
#
from basicFolder import basicFolder
from parameters import WINDOWS_TRASH

#
# Objet du système de fichier (dossier ou fichier) à supprimer / vider
#
class winTrashFolder(basicFolder):
    
    # Taille en octets (ou None en cas d'erreur)
    def size(self):
        # Pas de connaissance de la taille
        return 0
    
    def files(self):
        return 0
    
    # Constructeur
    #
    def __init__(self, opts, pMaxSize = 0):
        super().__init__(opts, pMaxSize)

    # Initalisation
    #
    #   name : Nom du dossier (ou None si dossier 'vierge')
    #
    #  Retourne le tuple (Ok? , message d'erreur)
    def init(self, name = None):
        if WINDOWS_TRASH !=  name:
            return False, f"{name} n'est pas un dossier de poubelle Windows"

        # Ok
        self.name_ = name
        self.valid = True
        return True, ""

# EOF