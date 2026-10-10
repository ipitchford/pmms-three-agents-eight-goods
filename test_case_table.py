"""Consistency check: the verifier's inline case table equals the generator's (needs numpy via cases.py)."""
import re, ast
from cases import CASES
src = open("verify_case.py").read()
start = src.index("    CASES = {")
end = src.index("    all_cases = CASES[args.goods]")
block = src[start:end].replace("    CASES = ", "", 1)
assert ast.literal_eval(block.strip()) == CASES, "case tables differ"
print("CASE_TABLES_IDENTICAL")
