// Entry point for the gta6-meme-x-01 bounty (Node 22, standard library only).
//
// The entry itself is a post on X, not something this program computes: the
// meme picture (meme.png) and the post text (POST_TEXT.md) live in this
// repository, the post goes out from a public X account, and POST.json names
// the post's address. Until the post is up, POST.json still holds the
// starter's placeholder address, which the gate refuses on purpose; the
// parent replaces it with the real post address right after posting. All this program has to do is hand POST.json to the
// grader by copying it from the repository into the output directory.
//
// The grader runs it twice and both runs must write the same bytes, so this
// is a plain byte-for-byte copy: no timestamps, no randomness, no network,
// and nothing read from outside the repository.
//
// Local run (the grader's container uses /bot and /output instead):
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const repoDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const source = join(repoDir, "POST.json");
const target = join(outDir, "POST.json");

if (!existsSync(source)) {
  console.error(`no POST.json found in ${repoDir}, cannot hand in the post`);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
try {
  const bytes = readFileSync(source);
  writeFileSync(target, bytes);
} catch (err) {
  console.error(`could not write ${target}: ${(err as Error).message}`);
  process.exit(1);
}
