#!/bin/python
#
# coding=UTF-8
#
#   Fichier     :   basicFile.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet basicFile pour la gestion d'un fichier
#
#   Remarque    :
#
import datetime
import hashlib
import os
import random
import stat
from typing import override
from zoneinfo import ZoneInfo

from FSObject import FSObject
from parameters import (
    FILESIZE_MAX,
    FILESIZE_MIN,
    PATTERN_BASE_STRING,
    PATTERN_MAX_LEN,
    PATTERN_MIN_LEN,
)
from parameters import options as opt
from sharedTools.jlogger import JLOG_DATE_REGION


#
# Classe basicFile - un fichier (à créer, salir ou supprimer)
#
class basicFile(FSObject):

    # Constructeur
    def __init__(self, parameters : opt, path : str | None = None, fName : str | None = None, FQN : str | None = None):

        super().__init__(parameters)

        # Initialisation des données membres
        self.pattern_: str = ""
        self.error_: str  = ""
        self.name_: str = ""

        # Un nom complet (ie. le fichier existe !!!)
        if FQN is not None :
            self.name = FQN
        else:
            # Nom du fichier
            if path is not None and FSObject.existsFolder(path):
                # Le dossier est valide
                if fName is not None and len(fName)>0 :
                    # Le nom est "correct"
                    self.name = os.path.join(path, fName)
                else:
                    # Génération d'un nom nouveau
                    self.name_ = basicFile.genName(path, False)
            else:
                # pas de nom (pour l'instant)
                self.name_ = ""

    # Est-ce un fichier ?
    @override
    def isFile(self) -> bool:
        return True

    # Nom du fichier
    @property
    def name(self):
        return self.name_

    @name.setter
    def name(self, value:str):
        self.name_ = value

    # Nom court
    def shortName(self)->str:
        if len(self.name_) == 0:
            return ""
        _, sName = os.path.split(self.name_)
        return sName

    # Nom du dossier
    def folder(self) -> str | None:
        if 0 == len(self.name):
            return None

        f, _ = os.path.split(self.name)
        return f

    #
    # Gestion des erreurs
    #
    @property
    def error(self)->str:
        message =self.error_
        if len(message):
            # Effacement du message après consultation
            self.error_ = ""
        return message

    @error.setter
    def error(self, value:str):
        self.error_ = value

    # La dernière opération s'est correctement déroulée ?
    def success(self)->bool:
        return 0 == len(self.error_)

    #
    # Gestion du fichier
    #

    # Création d'un nouveau fichier
    #
    #   Generator qui énumère les blocks d'octets crées
    #
    #   fileSize : Taille en octets du fichier (ou 0 si taille aléatoire)
    #   maxFileSize : Taille max. n octets d'un fichier
    #
    def create(self, fileSize:int = 0, maxFileSize:int = 0):  # pyright: ignore[reportUnknownParameterType]
        if not self.options.test:
            if len(self.name_):
                # Si le fichier existe, je le supprime ...
                if self.exists():
                    _ = self.delete()
            else:
                # Pas de nom
                self.error = "Impossible de créer le fichier. Il n'a pas de nom"

            if self.success():
                # Creation à la "bonne taille"
                for _ in range(self.options.iterate_):
                    yield from self._create(fileSize, maxFileSize)

    # Remplissage d'un fichier existant
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    #   rename : Doit-on renomer le fichier (avec un nom aléatoire) ?
    #
    def fill(self, rename:bool = False):  # pyright: ignore[reportUnknownParameterType]
        if not self.options.test and self.exists():
            for _ in range(self.options.iterate_):
                yield from self._create()

            if False == self.success():
                return

            # Nouveau nom
            if rename and len(self.rename()) == 0:
                self.error = f"Impossible de renommer '{self.name_}'"

    # Renomage
    #
    #   Retourne le nouveau nom (ou "" en cas d'erreur)
    def rename(self)->str:
        #if (not force and self.exists()) or force:
        if not self.options.test and self.exists():
            folder, _ = os.path.split(self.name)

            # Nouveau nom "complet"
            name:str = basicFile.genName(folder)
            try:
                if len(self.name_):
                    os.rename(self.name_, name)
                self.name_ = name
            except OSError:
                # une erreur
                return ""

            return name

        # On retourne le nom de base
        return self.name_

    # Suppression
    #
    #   replace : Doit-on remplacer le contenu ?
    #
    #   Generator qui énumère les blocks d'octets supprimés
    #
    def delete(self, replace:bool = True):  # pyright: ignore[reportUnknownParameterType]
        # Le fichier doit exister
        if not self.options.test and self.exists():

            # L'accès en lecture et en ecriture doit être possible
            if False == os.access(self.name_, os.W_OK):
                # sys.stderr.write(f"basicFile::cleanFolders - Erreur '{self.name_}' n'a pas l'attribut d'ecriture\n")
                try:
                    os.chmod(self.name_, stat.S_IWUSR)
                except OSError:
                    self.error = f"Erreur - pas d'accès en ecriture pour '{self.name_}'"

            # Remplacement du contenu ?
            if replace:
                # Nouveau nom
                nName:str = self.rename()
                if len(nName) == 0:
                    self.error = f"Impossible de renommer '{self.name_}'"

                # Nouveau contenu (on itère l'effacement)
                for _ in range(self.options.iterate_):
                    yield from self._create()

                if False == self.success():
                    return
            # Dans tous les cas, effacement
            try:
                if len(self.name_)>0:
                    os.remove(self.name_)
            except OSError:
                self.error = f"Erreur lors de la tentative de suppression de '{self.name_}'"

    # Taille en octets (ou None en cas d'erreur)
    @override
    def size(self)->int:
        return 0 if len(self.name_) == 0 or not self.exists() else os.path.getsize(self.name_)

    # Nombre de fichier(s) contenus
    @override
    def files(self)->int:
        # Juste moi ...
        return 1

    # Le fichier existe t'il ?
    #
    def exists(self)->bool:
        return False if len(self.name) == 0 else FSObject.existsFile(self.name)

    # Génération d'un nom de fichier pour un fichier existant ou un nouveau fichier
    #
    #   parentFolder : dossier parent (qui contiendra le nouvel élément)
    #   folder : S'agit'il d'un dossier ?
    #
    #   Retourne le nouveau nom complet ou "" en cas d'anomalie
    @staticmethod
    def genName(parentFolder:str | None, folder:bool = False)->str:
        # Dossier parent
        if parentFolder is None:
            return ""

        # Tant qu'il existe (avec le même nom)
        generate = True
        fName = ""
        while True == generate:
            fName = os.path.join(parentFolder, basicFile._genName())

            # Si le fichier ou le dossier existe on génère un nouveau nom
            #generate = os.path.isdir(fName) if folder else self.exists(fName)
            generate = FSObject.existsFolder(fName) if folder else FSObject.existsFile(fName)

        # Retour du nom complet
        return fName

    #
    # Méthodes internes
    #

    # Génération d'un nouveau nom (fichier ou dossier)
    #   Retourne le nouveau nom
    @staticmethod
    def _genName()->str:
        now = datetime.datetime.now(tz=ZoneInfo(JLOG_DATE_REGION))
        hash = hashlib.blake2b(digest_size=20)
        hash.update(str.encode(now.strftime("%Y%m%d-%H%M%S-%f")))
        return hash.hexdigest()

    # Génération d'un motif aléatoire
    def _genPattern(self, maxPatternSize:int = PATTERN_MAX_LEN):
        self.pattern_ = ""
        iSize = int(maxPatternSize)
        maxSize = PATTERN_MAX_LEN if iSize > PATTERN_MAX_LEN else max(iSize, PATTERN_MIN_LEN)

        for _ in range(random.randint(PATTERN_MIN_LEN, maxSize)):
            self.pattern_+=PATTERN_BASE_STRING[random.randint(0, len(PATTERN_BASE_STRING) - 1)]

    # Création d'un fichier à la taille demandée
    #  Si le fichier existe son contenu sera remplacé
    #
    #   fileSize : Taille en octets du fichier (ou 0 si taille aléatoire)
    #   maxFileSize : Taille max. n octets d'un fichier
    #   isNew : Est-ce une création de fichier ?
    #
    def _create(self, fileSize:int = 0, maxFileSize:int = 0, isNew:bool = False):
        # Création ?
        size:int = fileSize
        if isNew:
            # Si la taille est nulle => on choisit aléatoirement
            if 0 == fileSize:
                # 1 => ko, 2 = Mo
                unit:int = 1 + random.randint(1, 1024) % 2
                size = pow(base=2, exp=unit * 10) * random.randint(FILESIZE_MIN, FILESIZE_MAX)

                # On remplit (mais on ne déborde pas !)
                if maxFileSize >0 and size > maxFileSize:
                    size = maxFileSize
        else:
            # On conserve la taille
            size = self.size()

        # Nouveau motif
        self._genPattern(size)
        pSize = len(self.pattern_)

        # Taille du buffer
        buffSize = min(pSize, size)

        # Ouverture / création du fichier
        currentSize = 0
        try:
            with open(self.name_, 'w') as file:
                # Remplissage du fichier
                while currentSize < size:
                    # Le dernier paquet (qui peut aussi être le premier) doit-il être tronqué ?
                    if (currentSize + buffSize) > size:
                        buffSize = size - currentSize
                        self.pattern_ = self.pattern_[:buffSize]

                    # Ecriture du buffer
                    _ = file.write(self.pattern_)
                    currentSize+=buffSize

                    # On retourne la taille du paquet écrit
                    yield buffSize
        except OSError:
            self.error = f"Erreur lors de l'ecriture dans '{self.name_}'"

# EOF
