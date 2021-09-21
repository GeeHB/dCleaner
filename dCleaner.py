#!/bin/python3

# coding=UTF-8
#
#   File     :   dCleaner.py
#
#   Auteur      :   JHB
#
#   Description :   Point d'entrée du programme
#
#   Remarque    : 
#
#   Dépendances :  + Nécessite python-psutil (apt-get install / dnf install)
#
#   Version     :   0.2.4
#
#   Date        :   20 septembre 2021
#

import parameters
from os import path
from cmdLineParser import cmdLineParser
from paddingFolder import paddingFolder
from colorizer import textAttribute, textColor

# Classe dCleaner
#   Actions sur le dossier de remplissage
#
class dCleaner:
    # Données membre
    #
    options_ = None

    # Construction
    def __init__(self, options):
        # Initialisation des données membres
        if None == options or None == options.folder_:
            raise ValueError("Pas de paramètres")

        self.options_ = options

        # Le dossier est-il correct ?
        if self.options_.folder_ == "\\" or not path.isdir(self.options_.folder_):
            message = "Le dossier '" + self.options_.folder_ + "' n'est pas correct"
            raise ValueError(message)

        # Création de l'objet pour la gestion du dossier
        self.paddingFolder_ = paddingFolder(self.options_)
        done, message = self.paddingFolder_.init()

        if False == done:
            # Erreur d'initialisation du dossier
            raise ValueError(message)

    # Affichage des paramètres internes de l'objet
    def __repr__(self):
        
        # Quelques informations ...
        #
        if self.options_.verbose_:
            res = self.paddingFolder_.partitionUsage()
    
            out = "Paramètres : " 
            out += "\n\t- Mode : " + self.options_.color_.colored("nettoyage" if self.options_.clear_ else ("ajustement" if self.options_.adjust_ else "remplissage / nettoyage"), formatAttr=[textAttribute.GRAS])
            out += "\n\t- Taille de la partition : " + self.paddingFolder_.displaySize(res[0])
            out += "\n\t- Taux de remplissage max : " + self.options_.color_.colored(str(self.options_.fillRate_) + "%", formatAttr=[textAttribute.GRAS])
            out += "\n\t- Taux de renouvellement de la partition : " + self.options_.color_.colored(str(self.options_.renewRate_) + "%", formatAttr=[textAttribute.GRAS])
            out += "\n\t- Itération(s) de nettoyage : " + self.options_.color_.colored(str(self.options_.iterate_), formatAttr=[textAttribute.GRAS])
            out += "\n\t- Attente entre 2 fichiers : " + str(self.paddingFolder_.elapseFiles()) + "s"
            out += "\n\t- Attente entre 2 traitements : " + str(self.paddingFolder_.elapseTasks()) + "s"

            out += "\n\nDossier : " 
            out += "\n\t- Nom : " + self.options_.color_.colored(self.paddingFolder_.name(), formatAttr=[textAttribute.GRAS])
            out += "\n\t- Contenu : " + self.paddingFolder_.displaySize(self.paddingFolder_.size())
            out += "\n\t- Remplissage de la partition : " + self.paddingFolder_.displaySize(res[1]) +  " = " + str(round(100*res[1]/res[0],2)) + "%"
        else :
            out = "Dossier : " + self.options_.color_.colored(self.paddingFolder_.name(), formatAttr=[textAttribute.GRAS])
            out += "\nMode : " + ("nettoyage" if self.options_.clear_ else ("ajustement" if self.options_.adjust_ else "remplissage / nettoyage"))
            out += "\nTaux de remplissage max : " + self.options_.color_.colored(str(self.options_.fillRate_) + "%", formatAttr=[textAttribute.GRAS])
            out += "\nTaux de renouvellement de la partition : " + self.options_.color_.colored(str(self.options_.renewRate_) + "%", formatAttr=[textAttribute.GRAS])                    
            out += "\nItération(s) de nettoyage : " + self.options_.color_.colored(str(self.options_.iterate_), formatAttr=[textAttribute.GRAS])
            
        return out

    # Nettoyage (vidage) du dossier de remplissage / 'padding'
    #   Retourne Le tuple (# supprimé, message d'erreur / "")
    #
    def clearFolder(self):
        #return self.paddingFolder_.deleteFiles(count = self.paddingFolder_.files())
        return self.paddingFolder_.empty()
    
    # Remplissage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    #
    def fillPartition(self):

        res = self.paddingFolder_.partitionUsage()
        maxFill = res[0] * self.options_.fillRate_ / 100

        if res[1] < maxFill:
            # On fait en sorte de coller immédiatement au taux de remplissage
            fillSize = maxFill - res[1]
            self.paddingFolder_.newFiles(fillSize)
            return True
        
        # La partition est déja "pleine"
        return False
        
    # Nettoyage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    #
    def freePartition(self):
        
        # Mode "initial" : on fait en sorte de coller immédiatement au taux de remplissage
        totalSize, currentFillSize, _ = self.paddingFolder_.partitionUsage()
        maxFillSize = totalSize * self.options_.fillRate_ / 100
    
        if currentFillSize > maxFillSize:
            if self.options_.verbose_:
                print(self.options_.color_.colored("La partition est déja trop remplie", textColor.JAUNE))

            # ... en retirant les fichiers déja générés
            paddingFillSize = self.paddingFolder_.size()
            
            # Taille de ce que je dois supprimer
            gap = currentFillSize - maxFillSize
            
            if gap > paddingFillSize:
                # Tout le dossier de 'padding' n'y suffira pas ...
                print(self.options_.color_.colored("Le vidage du dossier de remplissage ne sera pas suffisant pour atteindre le tauxc de remplissage demandé", textColor.JAUNE))
                res = self.paddingFolder_.empty()
                
                if len(res[1]) > 0:
                    print(self.options_.color_.colored("Erreur lors du vidage du dossier de remplissage : " + res[1], textColor.ROUGE))
                    return False
            else:
                # Retrait du "minimum"
                self.paddingFolder_.deleteFiles(size=gap)
            
            return True

        # Rien n'a été fait
        return False

    # Rafraichissement - remplissage et nettoyage ponctuel
    def cleanPartition(self, wait = False):
        
        if wait:
            self.paddingFolder_.wait(self.paddingFolder_.elapseTasks())
        
        # Taille en octets du volume à renouveller
        res = self.paddingFolder_.partitionUsage()
        
        # Valeur max. théorique
        renewSize = res[0] * (100 - self.options_.fillRate_) / 100 * self.options_.renewRate_ / 100 
        
        # on recadre avec l'espace effectivement dispo
        renewSize = cmdLineParser.minMax(None, 0, renewSize, res[2] * self.options_.renewRate_ / 100)        
        
        # On remplit 
        self.paddingFolder_.newFiles(renewSize)
        
        # On supprime
        self.paddingFolder_.deleteFiles(size = renewSize)    

#
# Corps du programme
#
if '__main__' == __name__:
    
    # Ma ligne de commandes
    params = parameters.options()
    if False == params.parse():
        exit(1)

    try:    
        params.usage(False)

        cleaner = dCleaner(params)
        print(cleaner)

        if params.clear_:
            print("Nettoyage du dossier de 'padding'")
            res = cleaner.clearFolder()
            if len(res[1] > 0)  :
                print(params.color_.colored("Erreur lors de la suppression : " + res[1], textColor.ROUGE))
            else:
                if params.verbose_:
                    print(str(res[0]) + " fichier(s) supprimé(s)")
        else:
            
            print("Vérification du dossier de 'padding'")
            if False == cleaner.fillPartition():
                # Il faut plutôt libérer de la place
                cleaner.freePartition()

            # doit-on maintenant "salir" le disque ?
            if False == params.adjust_:
                
                for index in range(params.iterate_):
                    print("Iteration " + str(index + 1) + " / " + str(params.iterate_))
                    cleaner.cleanPartition(index > 0)

        print(params.color_.colored("Fin des traitements", datePrefix = (False == params.verbose_)))

    except ValueError as e:
        print(params.color_.colored("Erreur de paramètre(s) : " + str(e), textColor.ROUGE))
    except :
        print(params.color_.colored("Erreur inconnue", textColor.ROUGE))

# EOF