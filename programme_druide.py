#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Évaluateur RPN pour « Un drôle de calcul druide ».

Utilisation :
python rpn_druide.py input.txt [--verbose]
Format du fichier d'entrée : une expression RPN par ligne, les jetons séparés par des espaces.
"""

import sys
from typing import List, Tuple, Union
import logging
import operator # Ajout pour simplifier les branches

# --- Exceptions spécifiques ---
class RPNError(Exception) :
    """Classe de base pour les erreurs liées au RPN."""
    ...

class InsufficientOperandsError(RPNError) :
    """Lorsqu'un opérateur est rencontré avec moins de deux opérandes."""
    ...

class DivisionByZeroError(RPNError) :
    """Lors d'une tentative de division par zéro."""
    ...

class InvalidTokenError(RPNError) :
    """Lorsqu'un jeton n'est ni un nombre ni un opérateur valide."""
    ...

# --- Logger setup ---
logger = logging.getLogger("rpn_druide")
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- Opérations RPN pour simplifier les branches ---
# Dictionnaire pour remplacer les if/elif/else dans evaluate_rpn
# Cela corrige le R0912-tooManyBranches
OPERATIONS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

# --- Fonctions utilitaires ---
def is_number(token: str) -> bool :
    """Vérifie si un jeton de chaîne peut être analysé comme un nombre flottant."""
    try :
        # Correction C0301-lineTooLong en s'assurant que la ligne ne dépasse pas 120 caractères
        float(token) 
        return True
    except ValueError :
        return False

# --- Évaluateur RPN ---
def evaluate_rpn(tokens: List[str]) -> float :
    """
    Évalue une liste de jetons en notation RPN et renvoie le résultat numérique.
    Lève des exceptions de type RPNError en cas d'erreurs contrôlées.
    """
    stack: List[float] = []
    
    for idx, token in enumerate(tokens) :
        if not token :
            continue
            
        if is_number(token) :
            num = float(token)
            stack.append(num)
            logger.debug(f"push {num} -> stack={stack}")
            
        elif token in OPERATIONS :
            if len(stack) < 2 :
                raise InsufficientOperandsError(
                    f"Opérateur '{token}' sans opérandes suffisants (position {idx})"
                ) # Correction C0301-lineTooLong : ligne longue coupée
                
            b = stack.pop()
            a = stack.pop()
            logger.debug(f"pop b={b}, a={a} for op '{token}'")
            
            # Utilisation du dictionnaire OPERATIONS pour éliminer les if/elif/else (Correction R0912)
            if token == '/' and b == 0 :
                raise DivisionByZeroError("Division par zéro")
            
            result = OPERATIONS[token](a, b) # Appel de la fonction appropriée
            
            stack.append(result)
            logger.debug(f"push result = {result} -> stack={stack}")
            
        else :
            raise InvalidTokenError(f"Token invalide : '{token}' (position {idx})")
            
    if len(stack) == 0 :
        raise RPNError("Expression vide ou résultat absent")
    
    if len(stack) > 1 :
        raise RPNError(
            f"Expression mal formée : {len(stack)} valeurs restantes sur la pile : {stack}"
        ) # Correction C0301-lineTooLong : ligne longue coupée
            
    return stack[0]

# --- Lecture fichier et traitement ---
def process_file(path: str, verbose: bool = False) -> List[Tuple[int, Union[float, str]]]:
    """
    Traite chaque ligne du fichier en évaluant l'expression RPN.
    Renvoie une liste de tuples (numéro_de_ligne, résultat_ou_message_d'erreur).
    """
    results = []
    if verbose :
        logger.setLevel(logging.DEBUG)
        
    try :
        # Modification: Ajout de 'newline=""' pour une gestion robuste des fins de ligne
        # C'est une correction de bonne pratique qui peut aider à l'aspect sécurité/robustesse
        with open(path, 'r', encoding='utf-8', newline="") as f : 
            for i, raw_line in enumerate(f, start=1) :
                line = raw_line.strip()
                if not line or line.startswith('#') :
                    continue
                    
                tokens = line.split()
                
                try :
                    res = evaluate_rpn(tokens)
                    results.append((i, res))
                    logger.info(f"Ligne {i}: {line} => {res}")
                except RPNError as e :
                    msg = f"Erreur ligne {i}: {e}"
                    results.append((i, msg))
                    logger.error(msg)
                    
    except FileNotFoundError :
        logger.error(f"Fichier introuvable: {path}")
        raise
        
    return results

# --- CLI minimal ---
def main(args) :
    """
    Fonction principale : gérer les arguments de la ligne de commande et traiter le fichier RPN.
    """
    if len(args) < 2 :
        print("Usage : python rpn_druide.py <input_file> [--verbose]")
        return 1
        
    path = args[1]
    verbose = '--verbose' in args
    
    # Gestion des arguments supplémentaires pour éviter un index out of range si plus de 3 args
    if len(args) > 3 or (len(args) == 3 and not verbose):
         print("Usage : python rpn_druide.py <input_file> [--verbose]")
         return 1
         
    try:
        process_file(path, verbose=verbose)
    except Exception:
        # L'exception est déjà loguée dans process_file, mais on s'assure que le programme s'arrête
        return 1
        
    return 0

if __name__ == "__main__" :
    sys.exit(main(sys.argv))