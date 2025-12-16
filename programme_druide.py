#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Évaluateur RPN pour « Un drôle de calcul druide ».
Utilisation : python rpn_druide.py input.txt [--verbose]
"""

import sys
from typing import List, Tuple, Union
import logging
import operator

# --- Exceptions spécifiques ---
class RPNError(Exception):
    """Erreur de base."""

class InsufficientOperandsError(RPNError):
    """Manque d'opérandes."""

class DivisionByZeroError(RPNError):
    """Division par zéro."""

class InvalidTokenError(RPNError):
    """Jeton invalide."""

# --- Configuration du Logger ---
logger = logging.getLogger("rpn_druide")
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- Opérations ---
OPS = {
    '+': operator.add, '-': operator.sub,
    '*': operator.mul, '/': operator.truediv
}

# --- Fonctions utilitaires ---
def is_number(token: str) -> bool:
    """Vérifie si le jeton est un nombre."""
    try:
        float(token)
        return True
    except ValueError:
        return False

# --- Évaluateur RPN ---
def evaluate_rpn(tokens: List[str]) -> float:
    """Évalue une liste de jetons RPN."""
    stack: List[float] = []
    for idx, token in enumerate(tokens):
        if not token:
            continue
        if is_number(token):
            num = float(token)
            stack.append(num)
            logger.debug("push %f", num)
        elif token in OPS:
            if len(stack) < 2:
                msg = f"Opérateur '{token}' seul à la pos {idx}"
                raise InsufficientOperandsError(msg)
            val_b = stack.pop()
            val_a = stack.pop()
            if token == '/' and val_b == 0:
                raise DivisionByZeroError("Zéro division")
            res = OPS[token](val_a, val_b)
            stack.append(res)
        else:
            raise InvalidTokenError(f"Token '{token}' inconnu")
    if not stack:
        raise RPNError("Pile vide")
    if len(stack) > 1:
        raise RPNError(f"Pile mal formée: {len(stack)} restants")
    return stack[0]

# --- Traitement ---
def process_file(path: str, verbose: bool = False) -> List:
    """Traite le fichier ligne par ligne."""
    results = []
    if verbose:
        logger.setLevel(logging.DEBUG)
    try:
        with open(path, 'r', encoding='utf-8', newline='') as file_ptr:
            for i, raw_line in enumerate(file_ptr, start=1):
                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue
                try:
                    res = evaluate_rpn(line.split())
                    results.append((i, res))
                    logger.info("Ligne %d: %f", i, res)
                except RPNError as err:
                    logger.error("Ligne %d: %s", i, err)
                    results.append((i, str(err)))
    except (FileNotFoundError, PermissionError) as err:
        logger.error("Erreur fichier: %s", err)
        raise
    return results

# --- Point d'entrée ---
def main(args: List[str]) -> int:
    """Fonction principale."""
    if len(args) < 2:
        print("Usage: python rpn_druide.py <file> [--verbose]")
        return 1
    f_path = args[1]
    is_verbose = '--verbose' in args
    try:
        process_file(f_path, is_verbose)
    except (OSError, UnicodeDecodeError):
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))