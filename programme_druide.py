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

# --- Fonctions utilitaires ---
def is_number(token: str) -> bool :
    """Vérifie si un jeton de chaîne peut être analysé comme un nombre flottant."""
    try :
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
            
        elif token in ('+', '-', '*', '/') :
            if len(stack) < 2 :
                raise InsufficientOperandsError(f"Opérateur '{token}' sans opérandes suffisants (position {idx})")
            
            b = stack.pop()
            a = stack.pop()
            logger.debug(f"pop b={b}, a={a} for op '{token}'")
            
            if token == '+' :
                result = a + b
            elif token == '-' :
                result = a - b
            elif token == '*' :
                result = a * b
            else :
                if b == 0 :
                    raise DivisionByZeroError("Division par zéro")
                result = a / b

            stack.append(result)
            logger.debug(f"push result = {result} -> stack={stack}")
            
        else :
            raise InvalidTokenError(f"Token invalide : '{token}' (position {idx})")
            
    if len(stack) == 0 :
        raise RPNError("Expression vide ou résultat absent")
    
    if len(stack) > 1 :
        raise RPNError(f"Expression mal formée : {len(stack)} valeurs restantes sur la pile : {stack}")
        
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
        with open(path, 'r', encoding='utf-8') as f :
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
    process_file(path, verbose=verbose)
    return 0

if __name__ == "__main__" :
    sys.exit(main(sys.argv))