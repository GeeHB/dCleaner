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
import os, random, shutil, time, platform, sys
from basicFolder import FSObject, basicFolder, basicFile
from sharedTools.colorizer import textColor
from parameters import WINDOWS_TRASH

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

        ret = super().init(self.options.folder_)

        # Ouverture / création du dossier de travail
        if 0 == len(self.options.folder_):
            return False, "Erreur de paramètres"

        # Le dossier existe t'il ?
        if not basicFolder.existsFolder(self.options.folder_):
            if self.options.verbose_:
                print(f"Le dossier '{self.options.folder_}' n'existe pas")

            # On essaye de le créer
            if self.create(self.options.folder_):
                if self.options.verbose_:
                    print("Dossier crée avec succès")
            else:
                return False, f"Impossible de créer le dossier '{self.options.folder_}'"
        
        # Ok - pas  de message
        self.valid_ = True
        return True , ""
    
    # Attente
    #
    #   duration : duréee d'attente en s
    def wait(self, duration):
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

    # Remplissage avec un taille totale à atteindre ...
    #
    #   expectedFillSize : Taille du remplissage en octets
    #   iterate : Dans une bouicle d'itérations ?   
    #
    #   Retourne un booléen indiquant si l'opération a pu être effectuée
    def newFiles(self, expectedFillSize, iterate = False):
        if True == self.valid_ and expectedFillSize > 0:
            if self.options.verbose_ :
                offset = "\t- " if iterate else ""
                print(f"{offset}Demande de remplissage de {FSObject.size2String(expectedFillSize)}")

            # Rien n'a été fait !!!
            still = int(expectedFillSize)
            totalSize = 0
            files = 0
            cont = True

            if self.options.verbose_:
                try:
                    from alive_progress import alive_bar as progressBar
                except ImportError as e:
                    print("Le module 'alive_bar' n'a pu être importé")
                    self.options.verbose_ = False
            
            if not self.options.verbose_:
                from fakeProgressBar import fakeProgressBar as progressBar
                
            # Barre de progression
            barPos = 0  # Ou je suis ...
            barMax = self.__convertSize2Progressbar(expectedFillSize * self.options.iterate_)
            with progressBar(barMax, title = "Ajouts: ", monitor ="{count} ko - {percent:.0%}", elapsed = "en {elapsed}",stats = False, monitor_end = "\033[2K", elapsed_end = None) as bar:
                # Boucle de remplissage
                while totalSize < expectedFillSize and cont:
                    # Création d'un fichier sans nom
                    bFile = basicFile(path = self.name, fName = None, iterate = self.options.iterate_)
                    for fragment in bFile.create(maxFileSize = still) :   
                        totalSize+=fragment
                        barInc = self.__convertSize2Progressbar(fragment) 
                        if barInc > 0:
                            barPos += barInc
                            bar(barInc)

                        still-=fragment
                        
                    # Un fichier de plus
                    files+=1

                    # On attend ...
                    self.wait(self.options.waitFiles_)
                    
            # Terminé
            if self.options.verbose_:
                # Retrait de la barre de progression
                print('\033[F', end='')

            offset = "\t " if iterate else ""
            print(f"{offset}Remplissage de {FSObject.size2String(totalSize / self.options.iterate_)} - {files} " + "fichiers crées" if files > 1 else f"{files} fichier crée")
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
    def deleteFiles(self, count = 0, size = 0, iterate = False): 
        tSize = 0
        tFiles = 0
        
        if True == self.valid_:
            # Il y a quelques choses à faire ....
            if not 0 == count or not 0 == size:
                
                if self.options.verbose_:
                    offset = "\t- " if iterate else ""    
                    if not 0 == size :
                        print(f"{offset}Demande de suppression à hauteur de {FSObject.size2String(size)}")
                    else:
                        print(f"{offset}Demande de suppression de {count} fichiers")

                
                # Liste des fichiers du dossier
                files = [ f for f in os.listdir(self.options.folder_) if os.path.isfile(os.path.join(self.options.folder_,f)) ]

                # On mélange la liste
                random.shuffle(files)

                if self.options.verbose_:
                    try:
                        from alive_progress import alive_bar as progressBar
                    except ImportError as e:
                        print("Le module 'alive_bar' n'a pu être importé")
                        self.options.verbose_ = False
            
                if not self.options.verbose_:
                    from fakeProgressBar import fakeProgressBar as progressBar

                # Barre de progression
                barPos = 0  # Là ou je suis ...
                
                if not 0 == size :
                    # Suppression sur le critère de taille => on compte les ko
                    barMax = self.__convertSize2Progressbar(size * self.options.iterate_)
                    barMonitor = "{count} ko - {percent:.0%}"
                else:
                    # On compte les fichiers
                    barMax = count
                    barMonitor = "{count} / {total} - {percent:.0%}"
                
                with progressBar(barMax, title = "Suppr: ", monitor = barMonitor, elapsed = "en {elapsed}", stats = False, monitor_end = "\033[2K", elapsed_end = None) as bar:
                    # Suppression des fichiers
                    try:
                        # Les fichiers du dossier
                        for file in files:
                            bFile = basicFile(path = self.options.folder_, fName = file, iterate = self.options.iterate_ )
                            
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
                                            bar(barInc)

                            # Un fichier de moins
                            tFiles+=1

                            if 0 == size:
                                # Suppression sur critère de nombre (de fichier)
                                bar(1)
                                barPos += 1
                                
                            # Quota atteint
                            if (count > 0 and tFiles >= count) or (size > 0 and tSize >= size):
                                break

                            # On attend ...
                            self.wait(self.options.waitFiles_)
                    except KeyboardInterrupt as kbe:
                        print("Interruption de la suppression")
                        exit(1)
                        
                        # Inutile ...
                        return False

                    # Retrait de la barre de progression
                    if self.options.verbose_:
                        print('\033[F', end='')

        # Terminé
        if self.options.verbose_:
            # Retrait de la barre de progression
            print('\033[F', end='')
        
        # Fin des traitements
        offset = "\t " if iterate else ""
        print(f"{offset}Suppression de {FSObject.size2String(tSize / self.options.iterate_)} avec {tFiles}","fichiers" if tFiles > 1 else "fichier")
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
        if self.options.verbose_:
            try:
                from alive_progress import alive_bar as progressBar
            except ImportError as e:
                print("Le module 'alive_bar' n'a pu être importé")
                self.options.verbose_ = False
            
        if not self.options.verbose_:
            from fakeProgressBar import fakeProgressBar as progressBar
        
        # Vidage du dossier (sans récursivité)
        with progressBar(barMax, title = "Suppr: ", monitor = "{count} / {total} - {percent:.0%}", elapsed = "en {elapsed}", stats = False, monitor_end = "\033[2K", elapsed_end = None) as bar:
            for isFile, fName in super().browse(self.options.folder_):    
                if isFile:
                    # Suppression du fichier
                    bFile = basicFile(iterate = self.options.iterate_)
                    bFile.name = fName
                    for _ in bFile.delete(False):
                        pass
                    
                    if not bFile.success():
                        print(self.options.color_.colored(f"Erreur lors de la suppression de {fName}", textColor.ROUGE), file=sys.stderr)
                    else:
                        count += 1
                    
                    # Dans tous les cas on fait avancer la barre
                    bar()

        # Retrait de la barre de progression
        if self.options.verbose_:
            print('\033[F', end='')
        
        # Dossier vidé
        return count, ""       
    
    # Vidage d'un ou de plusieurs dossiers
    #   
    #   folders : liste des dossier à vider
    #
    #   Retourne le tuple {#fichiers, #dossiers, message, erreur ?}
    #
    def cleanFolders(self, folders):
        
        if folders is None or len(folders) == 0:
            return 0, 0, "Le paramètre 'folders' n'est pas renseigné" , True
        
        # Ajout (ou pas) des barres de progression
        if self.options.verbose_:
            try:
                from alive_progress import alive_bar as progressBar
            except ImportError as e:
                print("Le module 'alive_bar' n'a pu être importé")
                self.options.verbose_ = False

        if not self.options.verbose_:
            from fakeProgressBar import fakeProgressBar as progressBar

        if self.options.verbose_:
            print("Estimation de la taille totale de dossier à supprimer ou vider")
    
        barMax = expectedFiles = 0
        vFolders = []
        bFolder = basicFolder(self.options)
        bFolder.init()
        with progressBar(title = "Taille", monitor = "", elapsed= "", stats = False, monitor_end = "\033[2K", elapsed_end = None) as bar:
            for folder in folders:
                try:
                    bFolder.name = folder
                    if bFolder.valid:
                        vFolders.append(folder) # Le dossier est valide je le garde
                        ret = bFolder.sizes(recurse = self.options.recurse_)
                        barMax += ret[0]
                        expectedFiles += ret[1]
                    else:
                        # La poubelle de Windows ?
                        if folder == WINDOWS_TRASH:
                            vFolders.append(folder)
                except OSError:
                    pass
        
        # Retrait de la barre de progression
        if self.options.verbose_:
            print('\033[F', end='')

        # Rien à faire ?
        if 0 == len(vFolders) or 0 == expectedFiles:
            return 0, 0, "Rien à supprimer", False
        
        print(f"A supprimer: {FSObject.size2String(barMax)} dans {FSObject.count2String('fichier', expectedFiles)}.")

        # Nettoyage des dossiers
        freed = barInc = barPos = deletedFolders = deletedFiles = 0
        barMax = self.__convertSize2Progressbar(barMax * self.options.iterate_)
        with progressBar(barMax, title = "Suppr.", monitor = "{count} ko - {percent:.0%}", elapsed = "en {elapsed}", stats = False, monitor_end = "\033[2K", elapsed_end = None) as bar:
            for folder in vFolders:        
                bFolder.name = folder
                if bFolder.valid:
                    for isFile, fullName in bFolder.browse(recurse = self.options.recurse_, remove = self.options.cleanDepth_) :
                        if isFile:
                            # Suppression du fichier
                            bFile = basicFile(iterate = self.options.iterate_)
                            bFile.name = fullName
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
                                print(self.options.color_.colored(f"Erreur lors de la suppression de '{fullName}'", textColor.ROUGE), file=sys.stderr)
                            else:
                                deletedFiles += 1
                        else:
                            # Un dossier ...
                            if self.rmdir(fullName):
                                deletedFolders += 1
                            else:
                                print(self.options.color_.colored(f"Erreur lors de la suppression de '{fullName}'", textColor.ROUGE), file=sys.stderr)
                else:
                    # Dossier windows ?
                    if folder == WINDOWS_TRASH:
                        # On essaye de le vider ...
                        self.__emptyWindowsTrash()

                            
            # Retrait de la barre
            if self.options.verbose_:
                print('\033[F', end='')

        print(f"Suppression de {FSObject.count2String('fichier', deletedFiles)} et de {FSObject.count2String('dossier', deletedFolders)}")
        if freed > 0 :
            print(f"{FSObject.size2String(int(freed/self.options.iterate_))} libérés")

        return deletedFiles, deletedFolders, "", False

    # Conversion d'une taille (en octets) avant son affichage dans la barre de progression
    def __convertSize2Progressbar(self, number = 0):
        return int(number / 1024)     # conversion en ko 
    
    # Vidage de le corbeille de Windows
    #
    # retourne le booléen fait ?
    def __emptyWindowsTrash(self):
        myPlatform = platform.system()
        if  myPlatform == "Windows":
            try :
                import winshell
            except ModuleNotFoundError:
                print(self.options.color_.colored("Erreur - Le module winshell est absent", textColor.ROUGE), file=sys.stderr)
                return False
            
            # On peut essayer de la vider
            try:
                winshell.recycle_bin().empty(False, False, False)
            except:
                print(self.options.color_.colored("Erreur - impossible de vider la corbeille Windows", textColor.ROUGE), file=sys.stderr)
                return False
            
            return True
        
        # Pas sous Windows ...
        return False

# EOF