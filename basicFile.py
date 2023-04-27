# coding=UTF-8
#
#   Fichier     :   basicFile.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet basicFile
#                   Gestion d'un fichier
#
#   Remarque    : 
#

import os, random, datetime, hashlib
from parameters import FILESIZE_MAX, FILESIZE_MIN, PATTERN_MIN_LEN, PATTERN_MAX_LEN, PATTERN_BASE_STRING

# Classe basicFile - un fichier (à créer, salir ou supprimer)
#
class basicFile:
    
    # Constructeur
    def __init__(self, fName = None, iterate = 1):
        self.name_ = fName
        self.iterate_ = iterate
        self.pattern_ = ""
        self.error_ = ""

    # Nom du fichier
    @property
    def name(self) -> str:
        return self.name_
    
    @name.setter
    def name(self, value):
        self.name_ = value

    # Nom court
    def shortName(self):
        if len(self.name_) == 0:
            return ""
        res = os.path.split(self.name_)
        return res[1]
    
    #
    # Gestion des erreurs
    #
    @property
    def error(self) -> str:
        message =self.error_
        if len(message):
            self.error_ = ""
        return message
    
    @error.setter
    def error(self, value):
        self.error_ = value

    # Une erreur ?
    def noError(self):
        return 0 == len(self.error_)

    #
    # Gestion des fichiers
    #

    # Création d'un nouveau fichier
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def create(self, fileSize = 0, maxFileSize = 0):
        if self.exists():
            try:
                if len(self.rename(True)) > 0:
                    yield from self._createFile(fileSize, maxFileSize, True)  
            except:
                self.error_ = f"Erreur lors de la création de {self.name_}"        

    # Remplissage d'un fichier existant
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def fill(self):
        if self.exists():
            try:
                if len(self.rename()) > 0:
                    for _ in range(self.iterate_):
                        yield from self._createFile()
            except:
                self.error_ = f"Erreur lors de la réecriture de {self.name_}"

    # Renomage
    #   Retourne le nouveau nom (ou l'ancien en cas d'erreur)
    def rename(self, force = False):
        if (not force and self.exists()) or force:
            # Nouveau nom "complet"
            name = self.newFileName()
            try:
                os.rename(self.name_, name)
                self.name_ = name
            except:
                # une erreur
                return self.name_

            return name

        # sinon on retourne le nom de base
        return self.name_

    # Suppression
    #   clear : Doit-on effacer le contenu ?
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def delete(self, clear = True):
        # Le fichier doit exister
        if self.exists():
            try:
                # Remplacement du contenu ?
                if clear:
                    # Nouveau nom
                    if len(self.rename()) > 0:
                        # Nouveau contenu (on itère l'effacement)
                        for _ in range(self.iterate_):
                            yield from self._createFile()                            

                # (puis) effacement
                if len(self.name_)>0:
                    os.remove(self.name_)
            except:
                self.error_ = f"Erreur lors de la tentative de suppression de {self.name_}"                

    # Taille en octets (ou None en cas d'erreur)
    def size(self):
        return None if len(self.name_) == 0 or not self.exists() else os.path.getsize(self.name_)

    # Le fichier existe t'il ?
    def exists(self, fileName = None):
        # Le nom est-il renseigné ?
        if len(self.name_) == 0 and len(fileName) == 0:
            return False

        # On va essayer d'ouvrir le fichier en lecture
        try:
            file = open(fileName if fileName is not None else self.name_, 'r')
            file.close()
            return True
        except:
            return False

    # Génération d'un nouveau nom (fichier ou dossier)
    #   Retourne le nouveau nom
    def genName(self):
        hash = hashlib.blake2b(digest_size=20)
        hash.update(str.encode(now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")))
        return hash.hexdigest()
            
    # Génération d'un nom de fichier pour un fichier existant ou un nouveau fichier
    #   Retourne le nouveau nom complet ou "" en cas d'anomalie
    def newFileName(self, parentFolder = None):
        # Dossier parent
        if parentFolder is None:
            # Utilisation du nom courant
            if len(self.name_) == 0:
                return ""
            folder, _ = os.path.split(self.name_)
        else:
            folder = parentFolder
        
        # Tant qu'il existe (avec le même nom)
        generate = True
        while True == generate:
            fName = os.path.join(folder, self.newName())
        
            # Si le fichier existe on génère un nouveau nom
            generate = self.exists(fName)
        return fName

    #
    # Méthodes internes
    #

    # Génération d'un motif aléatoire
    def _genPattern(self):
        self.pattern_ = ""
        for _ in range(random.randint(PATTERN_MIN_LEN, self.maxPatternSize_)):
            self.pattern_+=PATTERN_BASE_STRING[random.randint(0, len(PATTERN_BASE_STRING) - 1)]

    # Création d'un fichier à la taille demandée
    #  Si le fichier existe son contenu sera remplacé
    def _createFile(self, fileSize = 0, maxFileSize = 0, isNew = False):
        currentSize = 0
        
        # Création ?
        if isNew:
            # Si la taille est nulle => on choisit aléatoirement
            if 0 == fileSize:
                # 1 => ko, 2 = Mo
                unit = 1 + random.randint(1, 1024) % 2
                fileSize = 2 ** (unit * 10) * random.randint(FILESIZE_MIN, FILESIZE_MAX)

                # On remplit (mais on ne déborde pas !)
                if maxFileSize >0 and fileSize > maxFileSize:
                    fileSize = maxFileSize
        else:
            # Remplissage
            if False == self.exists():
                # Le fichier n'existe pas
                return

            # On conserve la taille
            fileSize = self.size()

        # Nouveau motif
        self._genPattern()
        pSize = len(self.pattern_)

        # Taille du buffer
        buffSize = pSize if pSize < fileSize else fileSize

        try:
            # Ouverture / création du fichier
            file = open(self.name_, 'w')
        except:
            return

        try:
            # Remplissage du fichier
            while currentSize < fileSize:
                # Ecriture du buffer
                file.write(pattern)
                currentSize+=buffSize

                # On renvoit la taille du paquet écrit
                yield buffSize

                # Le dernier paquet doit-il être tronqué ?
                if (currentSize + buffSize) > fileSize:
                    buffSize = fileSize - currentSize
                    pattern = pattern[:buffSize]
        except:
            pass
        finally:
            file.close()
# EOF