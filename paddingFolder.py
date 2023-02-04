# coding=UTF-8
#
#   File     :   paddingFolder.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet paddingFolder
#                   Cet objet modélise le dossier de "remplissage" dans lequel seront 
#                   ajoutés et supprimés les fichiers
#
#   Remarque    : 
#
#   Version     :   0.5.2
#
#   Date        :   27 jan. 2023
#
import basicFolder
import os, random, shutil, time
import parameters
from sharedTools.colorizer import textColor

# Classe paddingFolder - un dossier de remplissage
#
class paddingFolder(basicFolder.basicFolder):

    # Données membres
    elapseFiles_ = 0                    # Attente entre le traitement de 2 fichiers
    elapseTasks_ = 0                    # Attente entre deux traitements


    files_ = 0  # Nombre de fichiers générés

    # Constructeur
    def __init__(self, options, pMaxSize = 0, elapseFiles = parameters.MIN_ELPASE_FILES, elapseTasks = parameters.MIN_ELAPSE_TASKS):
        # Initialisation des données membres
        super().__init__(options, pMaxSize)
        self.elapseFiles_ = elapseFiles
        self.elapseTasks_ = elapseTasks

    # Initalisation
    #  Retourne le tuple (booléen , message d'erreur)
    def init(self):

        ret = super().init(self.params_.folder_)

        # Ouverture / création du dossier de travail
        if 0 == len(self.params_.folder_):
            return False, "Erreur de paramètres"

        # Le dossier existe t'il ?
        if False == os.path.isdir(self.params_.folder_):
            if self.params_.verbose_:
                print("Le dossier '" +  self.params_.folder_ + "' n'existe pas")

            # On essaye de le créer
            try:
                os.makedirs(self.params_.folder_)

                if self.params_.verbose_:
                    print("Dossier crée avec succès")
            except:   
                return False, "Impossible de créer le dossier '" + self.params_.folder_ + "'"
        
        # Ok - pas  de message
        self.valid_ = True
        return True , ""
    
    # Temps d'attente
    def elapseFiles(self):
        return self.elapseFiles_

    def elapseTasks(self):
        return self.elapseTasks_

    def wait(self, duration):
        time.sleep(duration)
    
    # Usage du disque (de la partition sur laquelle le dossier courant est situé)
    #   Retourne le tuple (total, used, free)
    def partitionUsage(self):
        if True == self.valid_:
            total, used, free = shutil.disk_usage(self.params_.folder_)
            return total, used, free
        else:
            return 0,0,0

    # Contenu du dossier
    #   retourne le contenu du dossier
    def content(self):
        return 0

    # Remplissage avec un taille totale à atteindre ...
    #   Retourne un booléen indiquant si l'opération a pu être effectuée
    def newFiles(self, expectedFillSize):
        if True == self.valid_ and expectedFillSize > 0:
            if self.params_.verbose_ :
                print("Demande de remplissage de", self.size2String(expectedFillSize))

            # Rien n'a été fait !!!
            still = expectedFillSize
            totalSize = 0
            files = 0
            cont = True
            
            while totalSize < expectedFillSize and cont:
                res = self.newFile(maxFileSize = still)

                if 0 == res[1]:
                    # Erreur ...
                    cont = False
                else:
                    if self.params_.verbose_:
                        print("  + " + res[0] + " - " + self.size2String(res[1]) + " / " + self.size2String(still) + " restants")
                    
                    totalSize+=res[1] # Ajout de la taille du fichier
                    still-=res[1]
                    files+=1

                    # On attend ...
                    time.sleep(self.elapseFiles_)

            # Terminé
            print("Remplissage de", self.size2String(totalSize), " -", str(files),"fichiers crées")
            return True
        
        # Erreur
        return False

    # Suppression d'un fichier (le nom doit être complet)
    #   retourne le tuple (nom du fichier, nombre d'octets libérés) ou ("" , 0) en cas d'erreur
    def deleteFile(self, name):
        if True == self.valid_:
            # Pas de nom ?
            if 0 == len(name):
                # On supprime le premier qui vient ...
                name = ""
                for file in os.listdir(self.params_.folder_):
                    fName = os.path.join(self.params_.folder_, file)
                    
                    # Un fichier ?
                    if self._fileExists(fName):
                        name = fName
                        break

            return super().deleteFile(name, False)

        # Rien n'a été fait
        return "", 0

    # Suppression d'un ou plusieurs fichiers sur un critère de nombre ou de taille à libérer
    #   retourne True lorsque l'opération s'est déroulée correctement
    def deleteFiles(self, count = 0, size = 0):
        
        tSize = 0
        tFiles = 0
        
        if True == self.valid_:
            # Il y a quelques choses à faire ....
            if not 0 == count or not 0 == size:
                
                if self.params_.verbose_:
                    if not 0 == size :
                        print("Demande de suppression à hauteur de", self.size2String(size))
                    else:
                        print("Demande de suppression de " + str(count) + " fichiers")

                
                # Liste des fichiers du dossier
                files = [ f for f in os.listdir(self.params_.folder_) if os.path.isfile(os.path.join(self.params_.folder_,f)) ]

                # On mélange la liste
                random.shuffle(files)
                
                # Suppression des fichiers
                try:
                    # Les fichiers "fils"
                    for file in files:
                        fullName = os.path.join(self.params_.folder_, file) 
                        res = self.deleteFile(fullName)

                        # Suppression effectuée ?
                        if res[1] > 0:
                            tFiles+=1       # Un fichier de + (de supprimé ...)
                            tSize+=res[1]   # La taille en octets

                            if self.params_.verbose_:
                                if 0 == size:
                                    print("  -v" + res[0] + " - " + str(tFiles) + " / " + str(count) + " restant(s)")
                                else:
                                    print("  - " + res[0] + " - " + self.size2String(res[1]) + " / " + self.size2String(size - tSize) + " restants")

                            # Quota atteint
                            if (count > 0 and tFiles >= count) or (size > 0 and tSize >= size):
                                break

                        # On attend ...
                        time.sleep(self.elapseFiles_)

                except :
                    # Une erreur => on arrête de suite ...
                    return False

        # Fin des traitements
        print("Suppression de", self.size2String(tSize), " -", str(tFiles),"fichiers supprimés")
        return True

    # Vidage du dossier
    #   
    #   Retourne Le tuple (# supprimé, message d'erreur / "")
    #
    def empty(self):
        if False == self.valid_:
            return 0, "Objet non initialisé"

        count = 0

        # Vidage du dossier
        try:
            # Analyse récursive du dossier
            for (curPath, dirs, files) in os.walk(self.params_.folder_):
                if curPath == self.params_.folder_:
                    dirs[:]=[] # On arrête de parser
            
                # Les fichiers "fils"
                for file in files:
                    fullName = os.path.join(curPath, file) 
                    count+=1

                    self.deleteFile(fullName)
        except:
            return 0, "Erreur lors du vidage de "+self.params_.folder_
        
        # Dossier vidé
        return count, ""        

# EOF