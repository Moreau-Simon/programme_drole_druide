#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RPN evaluator for "Un drôle de calcul druide".
Usage:
    python rpn_druide.py input.txt
Input file format: one RPN expression per line, tokens separated by spaces.
"""

from __future__ import annotations
import sys
from typing import List, Tuple, Union, Callable, Dict
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

# --- Opérations ---
# Définition des fonctions d'opération binaires
def op_add(a: float, b: float) -> float:
    return a + b

def op_subtract(a: float, b: float) -> float:
    return a - b

def op_multiply(a: float, b: float) -> float:
    return a * b

def op_divide(a: float, b: float) -> float:
    if b == 0:
        raise DivisionByZeroError("Division par zéro")
    return a / b

# Dictionnaire de mappage (Réduit la complexité cyclomatique dans l'évaluateur)
OPERATORS: Dict[str, Callable[[float, float], float]] = {
    '+': op_add,
    '-': op_subtract,
    '*': op_multiply,
    '/': op_divide,
}

# --- Évaluateur RPN (Refactorisé) ---
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
            # Simplification : utilise float() partout pour la robustesse et la simplicité
            num = float(token)
            stack.append(num)
            logger.debug(f"push {num} -> stack={stack}")
            
        elif token in OPERATORS:
            if len(stack) < 2:
                raise InsufficientOperandsError(f"Opérateur '{token}' sans opérandes suffisants (position {idx})")
            
            # Les opérandes sont dans le bon ordre RPN (b puis a)
            b = stack.pop()
            a = stack.pop()
            logger.debug(f"pop b={b}, a={a} for op '{token}'")
            
            # Utilisation du dictionnaire de fonctions
            operator_func = OPERATORS[token]
            result = operator_func(a, b)
            
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

# --- Lecture fichier et traitement (Fonction légèrement simplifiée) ---
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

# --- Tests unitaires simples ---
def _run_tests():
    tests = [
        ("3 5 +", 8),
        ("4 7 + 3 *", 33),
        ("3 4 7 + *", 33),
        ("10 4 + 2 -", 12),
        ("2 10 4 + -", -12),
        ("4 0 /", DivisionByZeroError),
        ("3 +", InsufficientOperandsError),
        ("", RPNError),
        ("2 3 4 +", RPNError), # Test expression mal formée
        ("3.5 2 *", 7.0),
    ]
    
    failures = 0
    print("\n--- Début des tests unitaires ---")
    for expr, expected in tests:
        try:
            tokens = expr.split()
            res = evaluate_rpn(tokens)
            
            # Vérification si une exception était attendue mais un résultat a été obtenu
            if isinstance(expected, type) and issubclass(expected, Exception):
                print(f"TEST FAIL: '{expr}' attendait exception {expected.__name__}, obtenu résultat {res}")
                failures += 1
            # Vérification du résultat numérique
            elif abs(res - expected) > 1e-9:
                print(f"TEST FAIL: '{expr}' attendait {expected}, obtenu {res}")
                failures += 1
            else:
                print(f"TEST OK: '{expr}' => {res}")
                
        except Exception as e:
            # Vérification si l'exception attendue a été levée
            if isinstance(expected, type) and isinstance(e, expected):
                print(f"TEST OK: '{expr}' a levé {e.__class__.__name__}")
            else:
                print(f"TEST FAIL: '{expr}' a levé {e.__class__.__name__}: {e} (au lieu de {expected.__name__ if isinstance(expected, type) else 'un résultat'})")
                failures += 1
                
    if failures:
        print(f"\n{failures} tests échoués.")
    else:
        print("\nTous les tests sont OK.")

# --- CLI minimal ---
def main(argv):
    if len(argv) < 2:
        print("Usage: python rpn_druide.py <input_file> [--verbose] [--test]")
        return 1
        
    if '--test' in argv:
        _run_tests()
        return 0
        
    path = argv[1]
    verbose = '--verbose' in argv
    process_file(path, verbose=verbose)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))