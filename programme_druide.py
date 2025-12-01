#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPN evaluator for "Un drôle de calcul druide".
Usage:
    python rpn_druide.py input.txt [--verbose]
Input file format: one RPN expression per line, tokens separated by spaces.
"""

from __future__ import annotations
import sys
from typing import List, Tuple, Union
import logging

# --- Exceptions spécifiques ---
class RPNError(Exception):
    """Base class for RPN related errors."""
    pass

class InsufficientOperandsError(RPNError):
    pass

class DivisionByZeroError(RPNError):
    pass

class InvalidTokenError(RPNError):
    pass

# --- Logger setup ---
logger = logging.getLogger("rpn_druide")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- Fonctions utilitaires ---
def is_number(token: str) -> bool:
    """Return True if token can be parsed as float."""
    try:
        float(token)
        return True
    except ValueError:
        return False

# --- Évaluateur RPN ---
def evaluate_rpn(tokens: List[str]) -> float:
    """
    Evaluate a list of tokens in RPN and return the numeric result.
    Raises RPNError subclasses for controlled errors.
    """
    stack: List[float] = []
    
    for idx, token in enumerate(tokens):
        if not token:
            continue
            
        if is_number(token):
            # Utilise float() pour la simplicité
            num = float(token)
            stack.append(num)
            logger.debug(f"push {num} -> stack={stack}")
            
        elif token in ('+', '-', '*', '/'):
            if len(stack) < 2:
                raise InsufficientOperandsError(f"Opérateur '{token}' sans opérandes suffisants (position {idx})")
            
            # Les opérandes sont dans le bon ordre RPN (b puis a)
            b = stack.pop()
            a = stack.pop()
            logger.debug(f"pop b={b}, a={a} for op '{token}'")
            
            # Logique d'opération réintégrée pour éviter la fragmentation
            if token == '+':
                result = a + b
            elif token == '-':
                result = a - b
            elif token == '*':
                result = a * b
            elif token == '/':
                if b == 0:
                    raise DivisionByZeroError("Division par zéro")
                result = a / b

            stack.append(result)
            logger.debug(f"push result={result} -> stack={stack}")
            
        else:
            raise InvalidTokenError(f"Token invalide: '{token}' (position {idx})")
            
    if len(stack) == 0:
        raise RPNError("Expression vide ou résultat absent")
    
    if len(stack) > 1:
        # reste d'opérandes non consommés -> expression mal formée
        raise RPNError(f"Expression mal formée: {len(stack)} valeurs restantes sur la pile: {stack}")
        
    return stack[0]

# --- Lecture fichier et traitement ---
def process_file(path: str, verbose: bool = False) -> List[Tuple[int, Union[float, str]]]:
    """
    Process each line of the file.
    Returns list of tuples (line_number, result_or_error_message).
    """
    results = []
    if verbose:
        logger.setLevel(logging.DEBUG)
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, raw_line in enumerate(f, start=1):
                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue  # ignore empty / comment lines
                    
                tokens = line.split()
                
                try:
                    res = evaluate_rpn(tokens)
                    results.append((i, res))
                    logger.info(f"Ligne {i}: {line} => {res}")
                except RPNError as e:
                    msg = f"Erreur ligne {i}: {e}"
                    results.append((i, msg))
                    logger.error(msg)
                    
    except FileNotFoundError:
        logger.error(f"Fichier introuvable: {path}")
        raise
        
    return results

# --- CLI minimal (Ajusté) ---
def main(args): # Renommé argv en args
    if len(args) < 2:
        print("Usage: python rpn_druide.py <input_file> [--verbose]")
        return 1
        
    path = args[1]
    verbose = '--verbose' in args
    process_file(path, verbose=verbose)
    return 0

if __name__ == "__main__":
    # Changement final : utilisation de sys.exit() au lieu de raise SystemExit()
    sys.exit(main(sys.argv))