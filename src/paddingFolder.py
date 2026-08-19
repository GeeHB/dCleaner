#!/bin/python
#
# coding=UTF-8
#
#   Fichier     :   paddingFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet paddingFolder
#                   Cet objet modélise le dossier de "remplissage" dans lequel seront
#                   ajoutés et supprimés les fichiers
#
#   Remarque    :
#
#   Dépendances :  Utilise alive_progress (pip install alive-progress)
#
import os
import platform
import random
import shutil
import sys
import time
from typing import override

import fakeProgressBar
from basicFile import basicFile
from basicFolder import basicFolder
from FSObject import FSObject
from parameters import options as opts
from sharedTools import jlogger as logs
from winTrashFolder import winTrashFolder


# Classe paddingFolder - un dossier de remplissage
#
class paddingFolder(basicFolder):
    # Constructeur
    def __init__(self, options:opts, pMaxSize:int = 0):
        # Initialisation de l'objet
        self.files_:int = 0  # Nombre de fichiers générés
        super().__init__(options, pMaxSize)

        # Création de la barre (reèlle ou pas ...)
        if self.params_.showProgress:
            try:
                from alive_progress import alive_bar as pBar
                self.progressBar_ = pBar  # pzyright: ignore[reportUnannotatedClassAttribute]
            except ImportError:
                self.options.logger_.error(fakeProgressBar.MSG_NO_ALIVE_PROGRESS)
                self.options.quiet = True

        if not self.options.showProgress:
            from fakeProgressBar import fakeProgressBar as fakeBar
            self.progressBar_ = fakeBar

    # Initalisation
    #  Retourne le tuple (booléen , message d'erreur)
    @override
    def init(self, name : str | None= None) -> tuple[bool, str]:
        _ = super().init(self.options.folder_)

        # Ouverture / création du dossier de travail
        if 0 == len(self.options.folder_):
            return False, "Erreur de paramètres"

        # Le dossier existe t'il ?
        if not FSObject.existsFolder(self.options.folder_):
            self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"Le dossier '{self.options.folder_}' n'existe pas")

            # On essaye de le créer
            if self.create(self.options.folder_):
                self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"Dossier '{self.options.folder_} crée avec succès")
            else:
                return False, f"Impossible de créer le dossier '{self.options.folder_}'"

        # Ok - pas  de message
        self.valid_ : bool = True
        return True , ""

    # Attente
    #
    #   duration : duréee d'attente en s
    def wait(self, duration : float):
        if duration > 0 : time.sleep(duration)

    # Usage du disque (de la partition sur laquelle le dossier courant est situé)
    #   Retourne le tuple (total, used, free)
    def partitionUsage(self):
        #return shutil.disk_usage(self.options.folder_) if self.valid_ else 0,0,0
        if True == self.valid_:
            total, used, free = shutil.disk_usage(self.options.folder_)
            return total, used, free
        else:
            return 0,0,0

    # Remplissage du dossier avec une taille totale à atteindre ...
    #
    #   expectedFillSize : Taille du remplissage en octets
    #   iterate : Dans une boucle d'itérations ?
    #
    #   Retourne un booléen indiquant si l'opération a pu être effectuée
    def newFiles(self, expectedFillSize:int, iterate:bool = False):
        if self.options.test:
            return True

        if True == self.valid_ and expectedFillSize > 0:
            offset = "\t- " if iterate else ""
            self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"{offset}Demande de remplissage de {FSObject.size2String(expectedFillSize)}")

            # Rien n'a été fait !!!
            still = int(expectedFillSize)
            totalSize = 0
            files = 0

            if self.options.showProgress:
                try:
                    barPos = 0  # Ou je suis ...
                    barMax = self.__convertSize2Progressbar(expectedFillSize)
                    with self.progressBar_(barMax, _title = "Ajouts: ", _monitor ="{count} ko - {percent:.0%}", _elapsed = "en {elapsed}",_stats = False, _monitor_end = "\033[2K") as bar:  # pyright: ignore[reportUnknownVariableType]
                         # Boucle de remplissage
                         while totalSize < expectedFillSize:
                             # Création d'un fichier sans nom
                             bFile = basicFile(parameters = self.options, path = self.name, fName = None)
                             for fragment in bFile.create(maxFileSize = still) :
                                 totalSize+=fragment
                                 barInc = self.__convertSize2Progressbar(fragment)
                                 if barInc > 0:
                                     barPos += barInc
                                     bar(barInc)  # pyright: ignore[reportUnusedCallResult]

                                 still-=fragment

                             # Un fichier de plus
                             files+=1

                             # On attend ...
                             if self.options.waitFiles_ > 0:
                                 self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"\tAttente entre 2 fcihiers : {int(self.options.waitFiles_)} sec.")
                                 self.wait(self.options.waitFiles_)

                    # Retrait de la barre de progression
                    self.__tprint('\033[F', '')
                except ImportError:
                    self.options.logger_.error(fakeProgressBar.MSG_NO_ALIVE_PROGRESS)
                    self.options.quiet = True
            else:
                # sans barre de progression ...
                while totalSize < expectedFillSize:
                    # Création d'un fichier sans nom
                    bFile = basicFile(parameters = self.options, path = self.name, fName = None)
                    #bFile.create(maxFileSize = still)
                    for fragment in bFile.create(maxFileSize = still) :
                        totalSize+=fragment
                        still-=fragment

                    # Un fichier de plus
                    files+=1

                    # On attend ...
                    if self.options.waitFiles_ > 0:
                        self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"\tAttente avant le prochain traitement : {int(self.options.waitFiles_)} sec.")
                        self.wait(self.options.waitFiles_)

            offset = "\t " if iterate else ""

            self.options.logger_.print(level = logs.LogLevel.LOG_NORMAL, text = f"{offset}Remplissage de {FSObject.size2String(totalSize)} - {files} " + "fichiers crées" if files > 1 else f"{files} fichier crée")
            return True

        # Erreur
        return False

    # Suppression d'un ou plusieurs fichiers sur un critère de nombre ou de taille à libérer
    #
    #   count   : Suppression de {count} fichiers
    #       ou
    #   size    : Supression de {size octets}
    #
    #   iterate : Dans une boucle d'itérations ?
    #
    #   retourne True lorsque l'opération s'est déroulée correctement
    def deleteFiles(self, count:int = 0, size:int = 0, iterate:bool = False) -> bool:
        # if True == self.valid_ and (not 0 == count or not 0 == size):
        if not self.valid_ or (0 == count and 0 == size):
            return False

        tSize = 0
        tFiles = 0

        offset = "\t- " if iterate else ""
        if 0 != size :
            self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"{offset}Demande de suppression à hauteur de {FSObject.size2String(size)}")
        else:
            self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"{offset}Demande de suppression de {FSObject.count2String('fichier', count)}")

        # Liste des fichiers du dossier
        files = [ f for f in os.listdir(self.options.folder_) if os.path.isfile(os.path.join(self.options.folder_,f)) ]

        # On mélange la liste
        random.shuffle(files)

        # Barre de progression
        barPos = 0  # Là ou je suis ...

        if 0 != size :
            # Suppression sur le critère de taille => on compte les ko
            barMax = self.__convertSize2Progressbar(size)
            barMonitor = "{count} ko - {percent:.0%}"
        else:
            # On compte les fichiers
            barMax = count
            barMonitor = "{count} / {total} - {percent:.0%}"

        with self.progressBar_(barMax, _title = "Suppr: ", _monitor = barMonitor, _elapsed = "en {elapsed}", _stats = False, _monitor_end = "\033[2K", _elapsed_end = None) as bar: # pyright: ignore[reportArgumentType, reportUnknownVariableType]
            # Suppression des fichiers
            try:
                # Les fichiers du dossier
                for file in files:
                    bFile = basicFile(parameters = self.options, path = self.options.folder_, fName = file)

                    # Suppression d'un fichier
                    for frag in bFile.delete(True):
                        if size:
                            # Suppression sur critère de taille
                            tSize += frag
                            barInc = self.__convertSize2Progressbar(frag)
                            if barInc > 0:
                                # Ici on peut dépasser ...
                                if (barPos + barInc) > barMax:
                                    barInc = barMax - barPos

                                barPos += barInc

                                # !!!
                                if barInc:
                                    bar(barInc)  # pyright: ignore[reportUnusedCallResult]

                    # Un fichier de moins
                    tFiles+=1

                    if 0 == size:
                        # Suppression sur critère de nombre (de fichier)
                        bar(1)  # pyright: ignore[reportUnusedCallResult]
                        barPos += 1

                    # Quota atteint
                    if (count > 0 and tFiles >= count) or (size > 0 and tSize >= size):
                        break

                    # On attend ...
                    if self.options.waitFiles_ > 0:
                        self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"\tAttente avant le prochain traitement : {int(self.options.waitFiles_)} sec.")
                        self.wait(self.options.waitFiles_)
            except KeyboardInterrupt:
                self.options.logger_.error("Interruption de la suppression")
                sys.exit(1)

            # Retrait de la barre de progression
            if self.options.showProgress:
                self.__tprint('\033[F', '')

        # Terminé
        if self.options.showProgress:
            self.__tprint('\033[F', '')

        # Fin des traitements
        offset = "\t " if iterate else ""
        self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = f"{offset}Suppression de {FSObject.size2String(tSize)} avec {FSObject.count2String('fichier', tFiles)}")

        return True

    # Vidage du dossier courant
    #
    #   Retourne Le tuple (# fichiers supprimés, message d'erreur / "")
    #
    def clean(self):
        if False == self.valid_:
            return 0, "Objet non initialisé"

        # Nombre de fichiers dans le dossier
        _, barMax,_ = self.sizes()

        if 0 == barMax:
            # Rien à faire ....
            return 0, ""

        count = 0   # Ce que j'ai effectivement supprimé ...

        """
        if self.options.showProgress:
            try:
                from alive_progress import alive_bar as pBar
                progressBar = pBar
            except ImportError:
                self.options.logger_.error(fakeProgressBar.MSG_NO_ALIVE_PROGRESS)
                self.options.quiet = True
        else:
            from fakeProgressBar import fakeProgressBar as fakeBar
            progressBar = fakeBar
        """

        # Vidage du dossier (sans récursivité)
        #with progressBar(barMax, _title = "Suppr: ", _monitor = "{count} / {total} - {percent:.0%}", _elapsed = "en {elapsed}", _stats = False, _monitor_end = "\033[2K", _elapsed_end = None) as bar: # pyright: ignore[reportPossiblyUnboundVariable,reportArgumentType, reportUnknownVariableType]
        with self.progressBar_(barMax, _title = "Suppr: ", _monitor = "{count} / {total} - {percent:.0%}", _elapsed = "en {elapsed}", _stats = False, _monitor_end = "\033[2K", _elapsed_end = None) as bar: # pyright: ignore[reportPossiblyUnboundVariable,reportArgumentType, reportUnknownVariableType]
            for isFile, fName in super().browse(self.options.folder_):
                if isFile:
                    # Suppression du fichier
                    bFile = basicFile(parameters = self.options)
                    bFile.setName(fName)
                    for _ in bFile.delete(False):
                        pass

                    if not bFile.success():
                        self.options.logger_.error(f"paddingFolder::clean - Erreur lors de la suppression de '{fName}'\n")
                    else:
                        count += 1

                    # Dans tous les cas on fait avancer la barre
                    bar()

        # Retrait de la barre de progression
        if self.options.showProgress:
            self.__tprint('\033[F', '')

        # Dossier vidé
        return count, ""

    # Vidage d'un ou de plusieurs dossiers (ou fichiers)
    #
    #   fList : liste des dossiers ou fichiers à supprimer
    #
    #   Retourne le tuple {#fichiers, #dossiers, message, erreur ?}
    #
    def cleanFolders(self, fList:list[FSObject] | None)->tuple[int,int,str,bool]:
        if fList is None or 0 == len(fList):
            return 0, 0, "Le paramètre 'fList' n'est pas renseigné" , True

        self.options.logger_.print(level = logs.LogLevel.LOG_FULL, text = "Estimation de la taille totale de dossier à supprimer ou à vider")

        barMax:int = 0
        expectedFiles:int = 0
        expectedFolders:int = 0
        with self.progressBar_(_title = "Taille", _monitor = "", _elapsed= "", _stats = False, _monitor_end = "\033[2K", _elapsed_end = None) as bar: # pyright: ignore[reportArgumentType, reportUnknownVariableType]
            for obj in fList:
                try:
                    ret = obj.sizes(_recurse = self.options.recurse)
                    barMax += ret[0]
                    expectedFiles += ret[1]
                    expectedFolders += ret[2]
                except OSError:
                    pass

        # Retrait de la barre de progression
        if self.options.showProgress :
            self.__tprint('\033[F', '')

        # Rien à faire ?
        if 0 == expectedFolders and 0 == expectedFiles:
            return 0, 0, "Rien à supprimer", False

        self.options.logger_.print(level = logs.LogLevel.LOG_NORMAL, text = f"A supprimer: {FSObject.size2String(barMax)} dans {FSObject.count2String('fichier', expectedFiles)} et {FSObject.count2String('dossier', expectedFolders)}")

        # Nettoyage des dossiers
        freed = barPos = deletedFolders = deletedFiles = 0
        barMax = self.__convertSize2Progressbar(barMax * self.options.iterate_)
        with self.progressBar_(barMax, _title = "Suppr.", _monitor = "{count} ko - {percent:.0%}", _elapsed = "en {elapsed}", _stats = False, _monitor_end = "\033[2K", _elapsed_end = None) as bar: # pyright: ignore[reportArgumentType, reportUnknownVariableType]
            for obj in fList:
                # Un dossier
                if type(obj) is basicFolder:
                    for isFile, fullName in obj.browse("", recurse = self.options.recurse, remove = self.options.cleanDepth_) :
                        if isFile:
                            barPos, deletedFiles, freed = self.__deleteFileInFolder(fullName, bar, barPos, barMax, deletedFiles, freed)
                        else:
                            # Un dossier ...
                            if self.rmdir(fullName):
                                deletedFolders += 1
                            else:
                                self.options.logger_.error(f"paddingFolder::cleanFolders - Erreur lors de la suppression du dossier '{fullName}'\n")
                else:
                    # Dossier windows ?
                    if type(obj) is winTrashFolder:
                        # On essaye de le vider ...
                        _ = self.__emptyWindowsTrash()
                        deletedFolders += 1
                    else:
                        # Un simple fichier ?
                        if type(obj) is basicFile:
                            barPos, deletedFiles, freed = self.__deleteFile(obj, bar, barPos, barMax, deletedFiles, freed)

            # Retrait de la barre
            if self.options.showProgress:
                self.__tprint('\033[F', '')

        self.options.logger_.print(level = logs.LogLevel.LOG_NORMAL, text = f"Suppression de {FSObject.count2String('fichier', deletedFiles)} et de {FSObject.count2String('dossier', deletedFolders)}")
        self.options.logger_.print(level = logs.LogLevel.LOG_NORMAL, text = f"{FSObject.size2String(int(freed/self.options.iterate_))} libérés")

        return deletedFiles, deletedFolders, "", False

    # Conversion d'une taille (en octets) avant son affichage dans la barre de progression
    def __convertSize2Progressbar(self, number:int = 0):
        return int(number / 1024)     # conversion en ko

    # Vidage de le corbeille de Windows
    #
    # retourne le booléen fait ?
    def __emptyWindowsTrash(self):
        if self.options.test:
            return True

        myPlatform = platform.system()
        if  myPlatform == "Windows":
            try :
                import winshell  # pyright: ignore[reportMissingImports]

                # On peut essayer de la vider
                winshell.recycle_bin().empty(False, False, False)
                return True

            except ModuleNotFoundError:
                self.options.logger_.error("Erreur - Le module 'winshell' est absent\n")
                return False

        # Pas sous Windows ...
        return False

    # Affichage dans la console
    #
    def __tprint(self, text:str, endL:str | None = None):
        if not self.options.quiet:
            print(text, end = endL)

    # Suppression directe d'un fichier
    #
    def __deleteFile(self, FSO, bar, barPos, barMax, deletedFiles, freed):
        for fragment in FSO.delete():
            freed+=fragment
            barInc = self.__convertSize2Progressbar(fragment)
            if barInc > 0:
                if (barPos + barInc) > barMax:
                    barInc = barMax - barPos

                barPos += barInc

                # !!!
                if barInc:
                    bar(barInc)
        # Terminé
        if not FSO.success():
            self.options.logger_.error(f"paddingFolder::cleanFolders - Erreur lors de la suppression du fichier '{FSO.name}'\n")
        else:
            deletedFiles += 1

        return barPos, deletedFiles, freed


    # Suppression d'un fichier dans un dossier à supprimer ...
    #
    def __deleteFileInFolder(self, fullName:str, bar, barPos:int, barMax:int, deletedFiles:int, freed:int):
        bFile = basicFile(parameters = self.options)
        bFile.setName(fullName)
        for fragment in bFile.delete():
            freed+=fragment
            barInc = self.__convertSize2Progressbar(fragment)
            if barInc > 0:
                if (barPos + barInc) > barMax:
                    barInc = barMax - barPos

                barPos += barInc

                # !!!
                if barInc:
                    bar(barInc)

        if not bFile.success():
            self.options.logger_.error(f"paddingFolder::cleanFolders - Erreur lors de la suppression itérative de '{fullName}'\n")
        else:
            deletedFiles += 1

        return barPos, deletedFiles, freed

# EOF
