/* lowmem_trim: trim an ASCII LRAT proof to the steps the empty clause depends on, using external memory.
 *
 * Used for one certificate whose untrimmed proof (73 GB of ASCII LRAT) exceeded the memory available to
 * lrat-trim.  The trimmer is an untrusted producer: its output is accepted only after lrat-check and the
 * standard-library Python checker both verify it against the formula.
 *
 *   lowmem_trim scan HINTS < proof.lrat          writes, for every added clause, its hints then (nhints, id)
 *                                                as int32 to HINTS; prints "empty <id> maxid <id>" on stdout
 *   lowmem_trim mark HINTS EMPTY MAXID NEEDED    walks HINTS backwards from the empty clause and writes a
 *                                                byte per clause id (1 = needed) to NEEDED
 *   lowmem_trim emit NORIG NEEDED < proof.lrat   copies the needed addition lines unchanged (original ids
 *                                                kept), keeps deletions of original or needed clauses only,
 *                                                and stops after the empty clause
 * Only RUP steps are accepted (negative hints, i.e. RAT steps, abort).
 */
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define BUF (64u << 20)

static void die(const char *m) { fprintf(stderr, "lowmem_trim: %s\n", m); exit(2); }

/* line reader over stdin */
static char *buf; static size_t blen, bpos; static int eof;
static char *next_line(size_t *len) {
  for (;;) {
    char *s = buf + bpos, *nl = memchr(s, '\n', blen - bpos);
    if (nl) { *len = (size_t)(nl - s); bpos = (size_t)(nl - buf) + 1; return s; }
    if (eof) { if (bpos < blen) { *len = blen - bpos; bpos = blen; return s; } return NULL; }
    size_t rest = blen - bpos;
    memmove(buf, buf + bpos, rest); blen = rest; bpos = 0;
    if (blen == BUF) die("line longer than buffer");
    size_t n = fread(buf + blen, 1, BUF - blen, stdin);
    if (n == 0) eof = 1;
    blen += n;
  }
}

/* parse next integer from *p (bounded by e); returns 0 at end of line */
static int next_int(const char **p, const char *e, long long *out, int *is_d) {
  const char *s = *p;
  while (s < e && (*s == ' ' || *s == '\t' || *s == '\r')) s++;
  if (s >= e) { *p = s; return 0; }
  if (*s == 'd') { *is_d = 1; *p = s + 1; return 2; }
  int neg = 0; if (*s == '-') { neg = 1; s++; }
  if (s >= e || *s < '0' || *s > '9') die("parse error");
  long long v = 0;
  while (s < e && *s >= '0' && *s <= '9') v = v * 10 + (*s++ - '0');
  *out = neg ? -v : v; *p = s; return 1;
}

static void wr(FILE *f, int32_t v) { if (fwrite(&v, 4, 1, f) != 1) die("write failed"); }

static int scan(const char *hp) {
  FILE *h = fopen(hp, "wb"); if (!h) die("cannot open hints file");
  setvbuf(h, NULL, _IOFBF, 16u << 20);
  size_t len; char *l; long long empty = -1, maxid = 0, adds = 0, hints_total = 0;
  while ((l = next_line(&len))) {
    const char *p = l, *e = l + len; long long v, id; int isd = 0;
    if (len == 0 || l[0] == 'c') continue;
    if (next_int(&p, e, &id, &isd) != 1) die("missing id");
    int r = next_int(&p, e, &v, &isd);
    if (r == 2) continue;                       /* deletion line */
    if (r != 1) die("truncated addition");
    long long nlits = 0;
    while (v != 0) { nlits++; if (next_int(&p, e, &v, &isd) != 1) die("truncated literals"); }
    int32_t nh = 0;
    for (;;) {
      if (next_int(&p, e, &v, &isd) != 1) die("truncated hints");
      if (v == 0) break;
      if (v < 0) die("RAT step (negative hint) not supported");
      if (v > INT32_MAX) die("id overflow");
      wr(h, (int32_t)v); nh++;
    }
    if (id > INT32_MAX) die("id overflow");
    wr(h, nh); wr(h, (int32_t)id);
    adds++; hints_total += nh; if (id > maxid) maxid = id;
    if (nlits == 0) { empty = id; break; }
  }
  if (fclose(h)) die("close failed");
  if (empty < 0) die("no empty clause in proof");
  printf("empty %lld maxid %lld additions %lld hints %lld\n", empty, maxid, adds, hints_total);
  return 0;
}

static int mark(const char *hp, long long empty, long long maxid, const char *np) {
  /* read the hints file backwards in large sequential blocks (a reversed mmap walk defeats read-ahead) */
  int fd = open(hp, O_RDONLY); if (fd < 0) die("cannot open hints file");
  struct stat st; if (fstat(fd, &st)) die("stat failed");
  long long n = (long long)st.st_size / 4;               /* ints in file */
#ifndef MARK_CH
#define MARK_CH (64ll << 20)
#endif
  const long long CH = MARK_CH;                           /* ints per block (256 MB) */
  int32_t *w = NULL; long long lo = n, cur = n;           /* buffer holds file ints [lo, cur) */
  uint8_t *need = calloc((size_t)maxid + 1, 1); if (!need) die("out of memory");
  need[empty] = 1;
  long long kept = 0;
  #define AT(k) w[(k) - lo]
  while (cur > 0) {
    if (cur - lo < 2 || cur - lo < (long long)AT(cur - 2) + 2) {   /* need more data before lo */
      if (lo == 0) die("corrupt hints file");
      long long nlo = lo > CH ? lo - CH : 0;
      int32_t *nw = malloc((size_t)(cur - nlo) * 4); if (!nw) die("out of memory");
      if (pread(fd, nw, (size_t)(lo - nlo) * 4, nlo * 4) != (ssize_t)((lo - nlo) * 4)) die("read failed");
      if (cur > lo) memcpy(nw + (lo - nlo), w, (size_t)(cur - lo) * 4);
      free(w); w = nw; lo = nlo;
      continue;
    }
    int32_t id = AT(cur - 1), nh = AT(cur - 2);
    if (nh < 0) die("corrupt record");
    long long start = cur - 2 - nh;
    if (id <= 0 || id > maxid) die("id out of range");
    if (need[id]) {
      kept++;
      for (long long k = start; k < cur - 2; k++) { int32_t h = AT(k); if (h <= 0 || h > maxid) die("hint out of range"); need[h] = 1; }
    }
    cur = start;
  }
  #undef AT
  FILE *o = fopen(np, "wb"); if (!o) die("cannot open needed file");
  if (fwrite(need, 1, (size_t)maxid + 1, o) != (size_t)maxid + 1 || fclose(o)) die("write failed");
  printf("kept_additions %lld\n", kept);
  return 0;
}

static int emit(long long norig, const char *np) {
  FILE *f = fopen(np, "rb"); if (!f) die("cannot open needed file");
  fseek(f, 0, SEEK_END); long long maxid = ftell(f) - 1; fseek(f, 0, SEEK_SET);
  uint8_t *need = malloc((size_t)maxid + 1); if (!need) die("out of memory");
  if (fread(need, 1, (size_t)maxid + 1, f) != (size_t)maxid + 1) die("read failed");
  fclose(f);
  size_t cap = 1 << 20; char *out = malloc(cap); if (!out) die("out of memory");
  setvbuf(stdout, NULL, _IOFBF, 16u << 20);
  size_t len; char *l; long long written = 0;
  while ((l = next_line(&len))) {
    const char *p = l, *e = l + len; long long v, id; int isd = 0;
    if (len == 0 || l[0] == 'c') continue;
    if (next_int(&p, e, &id, &isd) != 1) die("missing id");
    int r = next_int(&p, e, &v, &isd);
    if (r == 2) {                               /* deletion: keep ids that exist in the trimmed proof */
      size_t k = (size_t)snprintf(out, cap, "%lld d", id); int any = 0;
      while (next_int(&p, e, &v, &isd) == 1 && v != 0) {
        if (v <= norig || (v <= maxid && need[v])) {
          if (k + 32 > cap) { cap *= 2; out = realloc(out, cap); if (!out) die("out of memory"); }
          k += (size_t)snprintf(out + k, cap - k, " %lld", v); any = 1;
        }
      }
      if (any) { fwrite(out, 1, k, stdout); fputs(" 0\n", stdout); }
      continue;
    }
    if (id > maxid || !need[id]) continue;
    fwrite(l, 1, len, stdout); fputc('\n', stdout); written++;
    /* stop after the empty clause: its literal part is just "0" */
    const char *q = l; long long w; int d2 = 0; next_int(&q, e, &w, &d2); next_int(&q, e, &w, &d2);
    if (w == 0) break;
  }
  if (fflush(stdout)) die("write failed");
  fprintf(stderr, "emitted_additions %lld\n", written);
  return 0;
}

int main(int argc, char **argv) {
  buf = malloc(BUF); if (!buf) die("out of memory");
  if (argc == 3 && !strcmp(argv[1], "scan")) return scan(argv[2]);
  if (argc == 6 && !strcmp(argv[1], "mark")) return mark(argv[2], atoll(argv[3]), atoll(argv[4]), argv[5]);
  if (argc == 4 && !strcmp(argv[1], "emit")) return emit(atoll(argv[2]), argv[3]);
  fprintf(stderr, "usage: lowmem_trim scan HINTS | mark HINTS EMPTY MAXID NEEDED | emit NORIG NEEDED\n");
  return 2;
}
