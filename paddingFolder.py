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
#   Dépendances :  Nécessite alive_progress (pip install alive-progress)
#
import os, random, shutil, time
from basicFolder import basicFolder, basicFile
from sharedTools.colorizer import textColor

# Classe paddingFolder - un dossier de remplissage
#
class paddingFolder(basicFolder):

    files_ = 0  # Nombre de fichiers générés

    # Constructeur
    def __init__(self, options, pMaxSize = 0):
        # Initialisation des données membres
        super().__init__(options, pMaxSize)

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
                print(f"Le dossier '{self.params_.folder_}' n'existe pas")

            # On essaye de le créer
            try:
                os.makedirs(self.params_.folder_)

                if self.params_.verbose_:
                    print("Dossier crée avec succès")
            except:   
                return False, f"Impossible de créer le dossier '{self.params_.folder_}'"
        
        # Ok - pas  de message
        self.valid_ = True
        return True , ""
    
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
                print(f"Demande de remplissage de {self.size2String(expectedFillSize)}")

            # Rien n'a été fait !!!
            still = expectedFillSize
            totalSize = 0
            files = 0
            cont = True

            if self.params_.verbose_:
                try:
                    from alive_progress import alive_bar as progressBar
                except ImportError as e:
                    print("Le module 'alive_bar' n'a pu être importé")
                    self.params_.verbose_ = False
            
            if not self.params_.verbose_:
                from fakeProgressBar import fakeProgressBar as progressBar
                
            # Barre de progression
            barPos = 0  # On je suis ...
            barMax = self.__convertSize2Progressbar(expectedFillSize)
            with progressBar(barMax, title = "Ajouts: ", monitor ="{count} Mo - {percent:.0%}", monitor_end = "Terminé", elapsed = "en {elapsed}", elapsed_end = "en {elapsed}", stats = False) as bar:
            
                # Boucle de remplissage
                while totalSize < expectedFillSize and cont:
                    res = self.newFile(maxFileSize = still)

                    if 0 == res[1]:
                        # Fin des traitement  ou erreur ...
                        cont = False
                    else:
                        
                        totalSize+=res[1] # Ajout de la taille du fichier
                        
                        #if self.params_.verbose_:
                        barInc = self.__convertSize2Progressbar(res[1]) 
                        if barInc > 0:
                            # Si on appelle bar(0) => incrémente qd même de 1 (bug ?)
                            barPos += barInc
                            bar(barInc)

                        still-=res[1]
                        files+=1

                        # On attend ...
                        time.sleep(self.params_.waitFiles_)
                
                if barPos != barMax:
                    # Tout n'a peut-être pas été fait
                    # ou soucis d'arrondis ...
                    bar(barMax - barPos)
                    
            # Terminé
            print(f"Remplissage de {self.size2String(totalSize)} - {files} " + "fichiers crées" if files > 1 else "{files} fichier crée")
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
                        print(f"Demande de suppression à hauteur de {self.size2String(size)}")
                    else:
                        print(f"Demande de suppression de {count} fichiers")

                
                # Liste des fichiers du dossier
                files = [ f for f in os.listdir(self.params_.folder_) if os.path.isfile(os.path.join(self.params_.folder_,f)) ]

                # On mélange la liste
                random.shuffle(files)

                if self.params_.verbose_:
                    try:
                        from alive_progress import alive_bar as progressBar
                    except ImportError as e:
                        print("Le module 'alive_bar' n'a pu être importé")
                        self.params_.verbose_ = False
            
                if not self.params_.verbose_:
                    from fakeProgressBar import fakeProgressBar as progressBar

                # Barre de progression
                barPos = 0  # On je suis ...
                
                if not 0 == size :
                    # Suppression sur le critère de taille => on compte les Mo
                    barMax = self.__convertSize2Progressbar(size * self.params_.iterate_)
                    barMonitor = "{count} Mo - {percent:.0%}"
                else:
                    # On compte les fichiers
                    barMax = count
                    barMonitor = "{count} / {total} - {percent:.0%}"
                
                with progressBar(barMax, title = "Suppr: ", monitor = barMonitor, monitor_end = "Terminé", elapsed = "en {elapsed}", elapsed_end = "en {elapsed}", stats = False) as bar:
                
                    # Suppression des fichiers
                    try:
                        # Les fichiers du dossier
                        for file in files:
                            bFile = basicFile(self.params_.folder_, file) 
                            res = self.deleteFile(fullName)

                            # Suppression effectuée ?
                            if res[1] > 0:
                                tFiles+=1       # Un fichier de + (de supprimé ...)
                                tSize+=res[1]   # La taille en octets

                                #if self.params_.verbose_ :
                                if 0 == size:
                                    #print("  -v" + res[0] + " - " + str(tFiles) + " / " + str(count) + " restant(s)")
                                    bar(1)
                                    barPos += 1
                                else:
                                    #print("  - " + res[0] + " - " + self.size2String(res[1]) + " / " + self.size2String(size - tSize) + " restants")
                                    barInc = self.__convertSize2Progressbar(res[1]) 
                                    if barInc > 0:
                                        # Si on appelle bar(0) => incrémente qd même de 1 (bug ?)
                                        barPos += barInc

                                        # Ici on peut dépasser ...
                                        if barPos > barMax:
                                            barInc = barMax - barPos + barInc
                                            barPos = barMax
                                        bar(barInc)

                                # Quota atteint
                                if (count > 0 and tFiles >= count) or (size > 0 and tSize >= size):
                                    break

                            # On attend ...
                            time.sleep(self.params_.waitFiles_)

                    except :
                        # Une erreur => on arrête de suite ...
                        return False

                    #if self.params_.verbose_ and barPos != barMax:
                    if barPos != barMax:
                        # Tout n'a peut-être pas été fait
                        # ou soucis d'arrondis ...
                        bar(barMax - barPos)

        # Fin des traitements
        print(f"Suppression de {self.size2String(tSize)} - {tFiles}","fichiers supprimés" if tFiles > 1 else "fichier supprimé")
        return True

    # Vidage du dossier courant
    #   
    #   Retourne Le tuple (# fichiers supprimés, message d'erreur / "")
    #
    def clean(self):
        if False == self.valid_:
            return 0, "Objet non initialisé"
     
        # Nombre de fichiers dans le dossier
        _, barMax = self.sizes()
        
        if 0 == barMax:
            # Rien à faire ....
            return 0, ""

        count = 0   # Ce que j'ai effectivement supprimé ...
        if self.params_.verbose_:
            try:
                from alive_progress import alive_bar as progressBar
            except ImportError as e:
                print("Le module 'alive_bar' n'a pu être importé")
                self.params_.verbose_ = False
            
        if not self.params_.verbose_:
            from fakeProgressBar import fakeProgressBar as progressBar
        
        # Vidage du dossier
        with progressBar(barMax, title = "Suppr: ", monitor = "{count} / {total} - {percent:.0%}", monitor_end = "Terminé", elapsed = "en {elapsed}", elapsed_end = "en {elapsed}", stats = False) as bar:        
            for ret in super().empty(self.params_.folder_):
                if ret[2]:
                    if ret[0]:
                        count += 1
                        bar()                    
                else:
                    print(self.params_.color_.colored(f"Erreur lors de la suppression de {ret[1]}", textColor.ROUGE))

        # Ajustement de la barre de progression
        if barMax > count:
            bar(barMax - count)
        
        # Dossier vidé
        return count, ""       
    
    # Vidage d'un ou de plusieurs dossiers
    #   
    #   Retourne le tuple {#fichiers, #dossiers, message}
    #
    def cleanFolders(self, folders, cleanDepth):
        # Ajout (ou pas) des barres de progression
        if self.params_.verbose_:
            try:
                from alive_progress import alive_bar as progressBar
            except ImportError as e:
                print("Le module 'alive_bar' n'a pu être importé")
                self.params_.verbose_ = False

        if not self.params_.verbose_:
            from fakeProgressBar import fakeProgressBar as progressBar
        
        # Estimation de la taille totale
        expectedFiles = 0
        vFolders = []
        bFolder = basicFolder(self.params_)
        bFolder.init()
        with progressBar(title = "Taille", monitor = "", elapsed= "", spinner = None, stats = False) as bar:
            for folder in folders:
                try:
                    if bFolder.setName(folder):
                        vFolders.append(folder) # Le dossier est valide je le garde
                        ret = bFolder.sizes()
                        expectedFiles += ret[1] # on conserve le nombre de fichiers
                except:
                    pass
        print(f"Analyse des dossiers terminée : {expectedFiles} fichier(s) à supprimer.")

        # Rien à faire ?
        if 0 == len(vFolders):
            return 0, 0, "Rien à supprimer"
        
        # Nettoyage des dossiers
        deletedFolders = deletedFiles = 0
        with progressBar(expectedFiles, title = "Suppr.", monitor = "{count} / {total} - {percent:.0%}", monitor_end = "Terminé", elapsed = "en {elapsed}", elapsed_end = "en {elapsed}", stats = False) as bar:
            for folder in vFolders:        
                if bFolder.setName(folder):
                    for isFile, shortName, done in bFolder.empty(recurse = True, remove = cleanDepth) :
                        if done:
                            if isFile:
                                deletedFiles += 1
                                bar()
                            else:
                                deletedFolders += 1
                        else:
                            print(self.params_.color_.colored(f"Erreur lors de la suppression de {shortName}", textColor.ROUGE))
        # Ajustement de la barre de progression
        if expectedFiles > deletedFiles:
            # Des erreurs ?
            bar(expectedFiles - deletedFiles)
        print(f"Suppression de {deletedFiles} fichier(s) et de  {deletedFolders} dossier(s)")
        return deletedFiles, deletedFolders, ""

    # Conversion d'une taille (en octets) avant son affichage dans la barre de progression
    def __convertSize2Progressbar(self, number = 0):
        return int(number / 1024 / 1024)     # conversion en Mo 

# EOF