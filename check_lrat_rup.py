#!/usr/bin/env python3
"""Check a positive-hint LRAT refutation by plain Boolean unit propagation.

This deliberately small checker accepts the RUP-only fragment used by the
six-, seven- and eight-good certificates. It rejects negative (RAT) hints and requires a
checked empty clause. Hints already satisfied under the current assignment are skipped
(version 2, 7 October 2026); every other hint must be unit or conflicting. No SAT solver, floating-point arithmetic, or optional dependency
is used. The separate encoding audit binds the CNF to the PMMS theorem.
"""
import argparse
import gzip
import hashlib
import json
import time
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_cnf(path):
    header = None
    pending = []
    clauses = {}
    for line in path.read_text().splitlines():
        tokens = line.split()
        if not tokens or tokens[0] == 'c':
            continue
        if tokens[0] == 'p':
            require(header is None and len(tokens) == 4 and tokens[1] == 'cnf',
                    'Invalid or duplicate DIMACS header')
            header = tuple(map(int, tokens[2:]))
            continue
        require(header is not None, 'Missing DIMACS header')
        for token in tokens:
            literal = int(token)
            if literal:
                require(abs(literal) <= header[0], 'Variable exceeds header')
                pending.append(literal)
            else:
                clauses[len(clauses) + 1] = tuple(set(pending))
                pending = []
    require(header is not None and not pending, 'Incomplete DIMACS input')
    require(len(clauses) == header[1], 'DIMACS clause count mismatch')
    return header[0], clauses


def check(cnf_path, proof_path):
    started = time.monotonic()
    nvars, clauses = read_cnf(cnf_path)
    original = len(clauses)
    greatest_id = original
    additions = deletions = hint_count = skipped_satisfied = 0
    empty_id = next((k for k, c in clauses.items() if not c), None)
    proof_reader = gzip.open if proof_path.suffix == '.gz' else open
    for line_number, line in enumerate(proof_reader(proof_path, 'rt'), 1):
        tokens = line.split()
        if not tokens or tokens[0] == 'c':
            continue
        label = int(tokens[0])
        require(len(tokens) >= 3 and tokens[-1] == '0',
                f'Incomplete LRAT line {line_number}')
        if tokens[1] == 'd':
            for token in tokens[2:-1]:
                require(int(token) > 0, 'Invalid deletion identifier')
                clauses.pop(int(token), None)
            deletions += 1
            continue
        data = list(map(int, tokens[1:]))
        split = data.index(0)
        clause, hints = tuple(set(data[:split])), data[split + 1:-1]
        require(label > greatest_id, 'Non-increasing addition identifier')
        require(all(0 < abs(lit) <= nvars for lit in clause),
                'Invalid proof variable')
        require(all(h > 0 for h in hints), 'Only positive RUP hints supported')
        require(all(h in clauses for h in hints), 'Hint names an absent clause')
        values = {}
        contradiction = False
        for lit in clause:
            var, value = abs(lit), lit < 0
            if var in values and values[var] != value:
                contradiction = True  # Negating a tautology is inconsistent.
            values[var] = value
        for hint in hints:
            hint_count += 1
            if contradiction:
                continue
            unassigned = []
            satisfied = False
            for lit in clauses[hint]:
                value = values.get(abs(lit))
                if value is None:
                    unassigned.append(lit)
                elif value == (lit > 0):
                    satisfied = True
                    break
            if satisfied:
                # A hint clause already satisfied under the current assignment yields neither a
                # unit nor a conflict; skipping it keeps the derivation a valid RUP check.
                # (CaDiCaL 3.0 emits such hints occasionally; drat-trim's lrat-check also tolerates them.)
                skipped_satisfied += 1
                continue
            require(len(unassigned) <= 1, 'RUP hint is not unit or conflicting')
            if not unassigned:
                contradiction = True
            else:
                lit = unassigned[0]
                values[abs(lit)] = lit > 0
        require(contradiction, f'No RUP contradiction at line {line_number}')
        clauses[label] = clause
        greatest_id = label
        additions += 1
        if not clause:
            empty_id = label
    require(empty_id is not None, 'No checked empty clause')
    return {
        'status': 'VERIFIED', 'method': 'positive-hint LRAT unit propagation',
        'variables': nvars, 'input_clauses': original,
        'checked_additions': additions, 'deletion_lines': deletions,
        'hint_references': hint_count, 'satisfied_hints_skipped': skipped_satisfied,
        'empty_clause_id': empty_id,
        'seconds': time.monotonic() - started,
        'cnf_sha256': hashlib.sha256(cnf_path.read_bytes()).hexdigest(),
        'proof_sha256': hashlib.sha256(proof_path.read_bytes()).hexdigest(),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cnf', type=Path)
    parser.add_argument('proof', type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.cnf, args.proof), indent=2))
