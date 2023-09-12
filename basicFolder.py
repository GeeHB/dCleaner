# coding=UTF-8
#
#   Fichier     :   basicFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des objets basicFile et basicFolder
#
#                   basicFile : Gestion d'un fichier
#
#                   basicFolder modélise un dossier lequel seront 
#                   ajoutés et supprimés les fichiers
#
#   Remarque    : 
#
import os
from FSObject import FSObject
from basicFile import basicFile
from parameters import WINDOWS_TRASH, PATTERN_MIN_LEN, PATTERN_MAX_LEN

#
# Classe basicFolder - un dossier de remplissage ou à vider ...
#
class basicFolder(FSObject):

    # Nom du fichier
    @property
    def name(self):
        return self.name_ if self.name_ is not None else ""
    
    @name.setter
    def name(self, value):
        # Poubelle Windows => non géré ...
        if value != WINDOWS_TRASH:
            # Le dossier existe t'il ?
            if value is None or value == "" or False == os.path.isdir(value):
                self.name_ = ""
                self.valid = False
                return
        else:
            self.name_ = WINDOWS_TRASH
            self.valid = False
            return
            
        # Ok
        self.name_ = value
        self.valid = True

    # Les données internes sont-elles valides ?
    @property
    def valid(self):
        return self.valid_
    
    @valid.setter
    def valid(self, value):
        self.valid_ = value

    # Paramètres & options
    @property
    def options(self):
        return self.params_
    
    @options.setter
    def options(self, value):
        self.params_ = value

    # Constructeur
    #
    def __init__(self, opts, pMaxSize = 0):
        # Initialisation des données membres
        self.name = ""
        self.valid = False
        self.options = opts
        self.maxPatternSize_ = pMaxSize if (pMaxSize > PATTERN_MIN_LEN and pMaxSize < PATTERN_MAX_LEN) else PATTERN_MAX_LEN
        self.sizes_ = None

    # Initalisation
    #
    #   name : nom du dossier (ou None si dossier 'vierge')
    #
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self, name = None):

        if name is not None and False == basicFolder.existsFolder(name):
            return False, f"Le dossier '{name}' n'existe pas"
        
        # Ok - pas  de message
        self.name = name
        return True , ""
    
    # Création du dossier
    #
    #   name : nom du dossier à créer
    #
    #   retourne le booléen : crée ?
    def create(self, name):
        if name is None or len(name) == 0 :
            return False
        
        # On essaye de le créer
        try:
            os.makedirs(name)
            return True
        except OSError:   
            return False
    
    # Parcours récursif d'un dossier en vue de le vider
    #
    #       folder : Nom complet du dossier de départ ("" => dossier courant)
    #       recurse : Parcours recursif des sous-dossiers ?
    #       remove : Suppression du dossier (-1 : pas de suppression; 0 : Suppression du dossier et de tous les descendants; n : suppression à partir de la profondeur n)
    #   
    #   Generateur - "Retourne" {Fichier?, nom du fichier/dossier}
    #
    def browse(self, folder = None, recurse = False, remove = -1):
        folderName = self.name_ if folder is None else folder
        # Analyse récursive du dossier
        for entry in os.scandir(folderName):
            fullName = os.path.join(folderName, entry.name) 
            if entry.is_file():
                # Un fichier
                yield True, fullName
            elif entry.is_dir():
                # Un sous dossier => appel récursif
                if recurse:
                    yield from self.browse(fullName, True, remove - 1 if remove > 0 else remove)
        
        # Suppression du dossier courant?
        if 0 == remove:
            yield False, folderName
    
    # Taille du dossier (et de tout ce qu'il contient)
    #
    #   element : Nom du dossier à analyser ou None pour le dossier courant
    #
    #   Retourne le tuple (taille en octets, nombre de fichiers, nombre de dossiers inclus)
    def sizes(self, element = "", recurse = False):
        if False == self.valid :
            # Pas ouvert
            return 0,0

        totalSize = 0
        totalFiles = 0
        totalFolders = 0
        try:
            # Par défaut, moi !
            if 0 == len(element):
                element = self.name_ if len(self.name_) else self.options.folder_
            
            # On regarde tous les éléments du dossier
            for entry in os.scandir(element):
                if entry.is_file():
                    # Un fichier
                    totalSize += entry.stat().st_size
                    totalFiles += 1
                elif entry.is_dir():
                    # Un sous dossier
                    totalFolders += 1

                    # Appel récursif ?
                    if recurse:
                        total = self.sizes(entry.path, True)
                        totalSize += total[0]
                        totalFiles += total[1]
                        totalFolders += total[2]

        except NotADirectoryError:
            # ?
            return os.path.getsize(element), 1
        except PermissionError:
            # Je n'ai pas les droits ...
            return 0, 0
        return totalSize, totalFiles, totalFolders

    # Taille en octets
    #   retourne un entier
    def size(self):
        # Déja caclculé ?
        if None == self.sizes_:
            self.sizes_ = self.sizes()
        return self.sizes_[0]

    # Nombre de fichier(s) contenu(s)
    #   Retourne un entier
    def files(self):
        # Déja caclculé ?
        if None == self.sizes_:
            self.sizes_ = self.sizes()
        return self.sizes_[1]
    
    # Suppression du dossier
    #   
    #   folder : nom du dossier à supprimer
    #
    #   retourne un booléen : fait ?
    def rmdir(self, folder):
        if folder is None or len(folder) == 0:
            return False
        
        # Puis-je le supprimer ?
        if self.options.isRectrictedAccess(folder):
            # Non, le dossier est dans la liste ....
            return False
        
        # Récupération du dossier parent
        res = os.path.split(folder)
        if len(res[0]) == 0 or len(res[1]) == 0 :
            # Le chemin n'est pas possible => pas de dossier parent
            return False

        # Nouveau nom
        nFolder = basicFile.genName(res[0], True)
        if nFolder is not None:    
            # Renommage demandé mais pas obligatoire ...
            try:
                os.rename(folder, nFolder)
            except OSError:
                # Impossible de renommer
                nFolder = folder    # Peut-être que l'on pourra malgré tout supprimer le fichier
        else:
            nFolder = folder
            
        # Suppression
        try:
            os.rmdir(nFolder)
        except OSError:
            return False
        
        return True

    # Le dossier existe-il ?
    @staticmethod
    def existsFolder(folderName):
        # On vérifie ...
        return os.path.isdir(folderName)
    
    def exists(self, folderName = None):
        # On vérifie ...
        return self.existsFolder(folderName if (folderName is not None and len(folderName)) != 0 else self.name_)
    
# EOF