# Provenance

Scholarly creator: Anonymous. Publisher: Evidence Press. Publication authorisation is not human mathematical
verification.

## Input

The work started from a research package supplied by the publisher on 7 October 2026,
`PMMS_Impasse_Research_Bundle_20261007.zip` (20,924,160 bytes, SHA-256
`39fa59d70301c9f9b8475e0ff4fd65724d82ade595fecc6e8ffc6815ec1cdd1b`). It contained an AI-assisted note proving
existence for at most seven goods, a memorandum recording an impasse at eight goods, and their scripts. The model
that produced that package is not established here. The package is not redistributed; its results that this paper
uses (six and seven goods) are re-proved here from scratch.

## Production, 7–10 October 2026

Anthropic's Claude models, working in Claude Code, redeveloped the encoding (sign variables, restriction-lemma
injection, the normal form and its least-agent sub-cases), wrote the generator, the clause verifier and the Python
LRAT checker, ran CaDiCaL 3.0.1 (about 110 CPU-hours for the eight-good certificates), trimmed and checked the
certificates, wrote the paper and prepared this package.

OpenAI's `gpt-5.6-sol` model reviewed the drafts adversarially three times (`review/sol_review.md`,
`sol_review2.md`, `sol_review3.md`); responses are in `review/sol_review_response.md`. An external review of the
PDF (10 October 2026; authorship not recorded; not redistributed) is answered in
`review/external_review_response.md`.

## Certificates

Each certificate was produced by CaDiCaL as an LRAT proof and trimmed to the steps the refutation needs, with
lrat-trim (Armin Biere, commit recorded in `tools/LRAT_TRIM_VERSION.txt`), which checks every step it keeps. The
exception is `eight_goods/case223_sub2`: its untrimmed proof (73 GB of text) exceeded the memory available to
lrat-trim, which was killed three times, and it was trimmed by `tools/lowmem_trim.c`, a short external-memory
program written for this purpose (on a seven-good proof it keeps exactly the steps lrat-trim keeps). Trimming is not
trusted: every trimmed proof was then accepted by both checkers. The
untrimmed proofs (about 111 GB) are not distributed; the trimmed certificates are the evidence. Solver logs are kept
in each certificate directory.
