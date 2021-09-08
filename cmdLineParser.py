# coding=UTF-8
#
#   File     :   cmdLineParser.py
#
#   Author      :   JHB
#
#   Description :   Définition des objets :
#                     - cmdLineParser : Gestion de la ligne de commandes
#
#   Remarque    :  
#
#   Version     :   1.4.1
#
#   Date        :   8 septembre 2021
#

import sys

#
#   cmdLineParser  - Gestion de la ligne de commandes
#
class cmdLineParser:
    # Données membres
    #
    optionChar_ = ""        # Caractère précédent les options
    assignChar_ = " "       # Caractère d'assignation / affectation

    options_    = 0         # Nombre d'options(restantes) dans la ligne de commandes

    NO_INDEX    = -1
    
    # Construction
    def __init__(self, optionChar = "-"):
        self.optionChar_ = optionChar
        
        # Analyse des paramètres de la ligne de commande
        self._parse()

    # Nombre total d'éléments
    def size(self):
        # On retire le nom du "programme"
        return (len(sys.argv) - 1)

    # Nombre d'options / paramètres
    def options(self):
        return self.options_

    # Accès
    #

    # Accès à un paramètre (ou valeur) par son index
    def at(self, index):
        if index > self.size() or index < 0:
            raise IndexError()

        # Valeur à l'index
        return sys.argv[index]

    # Accès à une valeur
    #   retourne le tuple {l'option / ou la valeur selon son index, option ? }
    def parameterOrValue(self, index):
        if index >= self.size() or index < 0:
            raise IndexError()

        # Valeur à l'index
        value = sys.argv[index + 1]

        # Une option ?
        if not value[0] == self.optionChar_:
            # non, une valeur ...
            # est ce une chaine de caractères quotée ?
            lenV = len(value)
            if value[0] == '/"' and value[lenV - 1] == '/"':
                value = value[1:lenV - 1]

        return (value, value[0] == self.optionChar_)

    
    # Recherche d'une option par son nom
    #   retourne son index ou NO_INDEX (-1) si l'option n'existe pas
    def findOption(self, name, remove):
        # Pas de nom => pas d'index valable
        if not 0 == len(name):
            index = 0
            searchedName = self.optionChar_ + name
            for parameter in sys.argv:
                if parameter == searchedName:
                    # Trouvé
                    if True == remove:
                        self.options_-=1
                    return (index - 1)
                
                # paramètre suivant
                index+=1

        # Pas trouvé
        return self.NO_INDEX

    # Recherche et retrait si existante d'une option
    # l'option peut avoir plusieurs noms
    #   retourne son index ou NO_INDEX (-1) si l'option n'existe pas
    def old_findAndRemoveOption(self, name, altName = None):
        # On recherche le premier nom
        index = self.findOption(name, True)
        if index == self.NO_INDEX:
            # On recherche la valeur alternative (si elle est fournie)
            return self.NO_INDEX if None == altName else self.findOption(altName, True)
        return index

    # Nombre variable de paramètres ayant la même signification ...
    def findAndRemoveOption(self, *args):          
        for name in args:
            # Les paramètres par ordre ....
            index = self.findOption(name, True)
            
            # Trouvé ?
            if self.NO_INDEX != index:
                return index
        
        # Non trouvé
        return self.NO_INDEX

    # Recherche d'une option et de sa valeur à partir d'un ou plusieurs noms
    #   
    #   Retourne la valeur ou None si non trouvée
    #
    def getOptionValue(self, *args):
        
        index = self.findAndRemoveOption(*args)
        if self.NO_INDEX == index:
            # non trouvé
            return None

        # Recherche de la valeur (qui doit suivre) ...
        try :
            rets = self.parameterOrValue(index + 1)
            if rets[1] == False : 
                return rets[0]
        except IndexError:
            # Pas de valeur ...
            return None

    # Recherche d'une option et de sa valeur numérique à partir d'un ou plusieurs noms
    #   Lorsque les bornes min et max sont fournies, la métode s'assurera que la valeur sera dans l'intervalle
    #
    #   Retourne la valeur ou None si non trouvée ou non numérique
    #
    def getOptionValueNum(self, name, min = None, max = None):

        value = self.getOptionValue(name)
        if None == value:
            # Non trouvé ...
            return None

        # La valeur est-elle numérique ?
        try:
            if True == value.isnumeric():
                num = int(value)    # Peut malgré tout poser des pb ...
                
                # Valeur bornée (et bornes valides) ?
                return self._minMax(num, min, max) if (min!=None and max!=None and min < max) else num
        except ValueError:
            # Problème de format et/ou de conversion
            pass

        # Une erreur ou dans un mauvais format
        return None

    #
    # Méthodes privées
    # 

    # Première analyse de la ligne de commande
    def _parse(self):
        self.options_ = 0

        for parameter in sys.argv:
            if parameter[0] == self.optionChar_:
                # Une option de +
                self.options_+=1
                
    # Taille
    def __len__(self) :
        size = self.size()
        return (size if size >= 0 else 0) # len ne doit pas retourner de valeur négative ! 
        
    # Accès
    def __getitem__(self, index):
        return self.at(index)

    # On s'assure qu'une valeur se trouve dans un intervalle donné
    #   retourne la valeur ou sa version corrigée
    def _minMax(self, source, min, max):
        if source < min :
            source = min
        else:
            if source > max:
                source = max
        return source
# EOF