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

    # Nombre de fichier(s) contenu(s)
    def files(self):
        # Pour être certain de lancer le nettoyage
        return 1
    
    # Taille du dossier (et de tout ce qu'il contient)
    #
    #   element : Nom du dossier à analyser ou None pour le dossier courant
    #
    #   Retourne le tuple (taille en octets, nombre de fichiers, nombre de dossiers inclus)
    def sizes(self, element = "", recurse = False):
        return 0, self.files(), self.size()

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