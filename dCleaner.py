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
#   Version     :   0.2.1
#
#   Date        :   31 aout 2021
#

import parameters
from paddingFolder import paddingFolder
from colorizer import colorizer, textAttribute, textColor

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
        if None == options:
            raise ValueError("Pas de paramètres")

        self.options_ = options

        # Création de l'objet pour la gestion du dossier
        self.paddingFolder_ = paddingFolder(self.options_)
        done, message = self.paddingFolder_.init()

        if False == done:
            # Erreur d'initialisation du dossier
            raise ValueError(message)

    # Affichage des paramètres internes de l'objet
    def __repr__(self):
        
        res = self.paddingFolder_.partitionUsage()
    
        # Quelques informations ...
        #

        out = "\nParamètres : " 
        out += "\n\t- Taille de la partition : " + self.paddingFolder_.displaySize(res[0])
        out += "\n\t- Taux de remplissage max : " + str(self.options_.fillRate_) + "%"
        out += "\n\t- Taux de renouvellement de la partition : " + str(self.options_.renewRate_) + "%"        
        out += "\n\t- Attente entre 2 fichiers : " + str(self.paddingFolder_.elapseFiles()) + "s"
        out += "\n\t- Attente entre 2 traitements : " + str(self.paddingFolder_.elapseTasks()) + "s"

        out += "\n\nDossier : " 
        out += "\n\t- Nom : " + self.paddingFolder_.name()
        out += "\n\t- Contenu : " + self.paddingFolder_.displaySize(self.paddingFolder_.size())
        out += "\n\t- Remplissage de la partition : " + self.paddingFolder_.displaySize(res[1]) +  " = " + str(round(100*res[1]/res[0],2)) + "%"

        return out

    # Remplissage iniitial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    def fillPartition(self):

        res = self.paddingFolder_.partitionUsage()
        maxFill = res[0] * parameters.DEF_PARTITION_FILL_RATE / 100

        if res[1] < maxFill:
            # On fait en sorte de coller immédiatement au taux de remplissage
            fillSize = maxFill - res[1]
            #print("Remplissage initial de", self.paddingFolder_.displaySize(fillSize))
            self.paddingFolder_.newFiles(fillSize)
            return True
        
        # La partition est déja "pleine"
        return False
        
    # Nettoyage initial de la partition
    #   Retourne un booléen indiquant si l'action a été effectuée
    def freePartition(self):
        
        # Mode "initial" : on fait en sorte de coller immédiatement au taux de remplissage
        res = self.paddingFolder_.partitionUsage()
        maxFill = res[0] * parameters.DEF_PARTITION_FILL_RATE / 100
    
        if res[1] > maxFill:
            print(self.options_.color_.colored("La partition est déja trop remplie", textColor.JAUNE))

            # en retirant les fichiers déja générés
            paddingSize = self.paddingFolder_.size()
            if (res[1] - paddingSize) > maxFill:
                print(self.options_.color_.colored("Vidage du dossier de remplissage"))
                self.paddingFolder_.empty()
            else:
                # Retrait du "minimum"
                removeSize = res[1] - maxFill

                print("Suppression des fichiers de remplissage à hauteur de", self.paddingFolder_.displaySize(removeSize))
                self.paddingFolder_.deleteFiles(size=removeSize)
            
            return True

        # Rien n'a été fait
        return False

    # Rafraichissement - remplissage et nettoyage ponctuel
    def cleanPartition(self):
        
        # Taille en octets du volume à renouveller
        res = self.paddingFolder_.partitionUsage()
        
        # Valeur max. théorique
        renewSize = res[0] * (100 - self.options_.fillRate_) / 100 * self.options_.renewRate_ / 100 
        
        # on recadre avec l'espace effectivement dispo
        renewSize = self.options_.minMax(0, renewSize, res[2] * self.options_.renewRate_ / 100)        
        
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
        cleaner = dCleaner(params)

        print(cleaner)

        print("\nTraitements initiaux :")
        if False == cleaner.fillPartition():
            # Il faut plutôt libérer de la place
            cleaner.freePartition()

        # Maintenant traitement de "fond"
        print("\nTâches de fond :")
        cleaner.cleanPartition()

    except ValueError as e:
        print(self.options_.color_.colored("Erreur de paramètre(s) : " + str(e), params.colors_.textColor.ROUGE))

# EOF