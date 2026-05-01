# autoresearch for parameter-golf

## Setup

1. Agree on a run tag (e.g. `apr22`). Create branch: `git checkout -b autoresearch/<tag>`
2. Read these files for context:
   - `README.md` — challenge rules, 16MB constraint, leaderboard
   - `train_gpt.py` — the only file you edit
   - Current PR's `train_gpt.py` in `records/` if applicable
3. Verify data: `./data/datasets/fineweb10B_sp1024/` must exist. If not, run `python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 10`
4. Initialize `results.tsv` with header: `commit\tval_bpb\tsize_mb\tstatus\tdescription`
5. Confirm, then begin.

## Constraints (HARD RULES)

- **16MB artifact limit**: `code_bytes + compressed_model_bytes < 16,000,000`. Violating this = discard.
- **val_bpb**: lower is better. This is your primary optimization target.
- Do NOT modify `data/` or the evaluation harness. Only `train_gpt.py` is in scope.
- No external downloads during training or eval.

## Run command

For fast iteration (5-min budget):
```bash
RUN_ID=exp_$(git rev-parse --short HEAD) \
MAX_WALLCLOCK_SECONDS=300 \
DATA_PATH=./data/datasets/fineweb10B_sp1024/ \
TOKENIZER_PATH=./data/tokenizers/fineweb_1024_bpe.model \
VOCAB_SIZE=1024 \
torchrun --standalone --nproc_per_node=1 train_gpt.py > run.log 2>&1
```

## Extracting results

```bash
grep -E "val_bpb|compressed_size|code_bytes" run.log | tail -10
```

The model is a keeper only if both: (a) `val_bpb` improved, AND (b) total artifact bytes < 16,000,000.

## Results TSV format
commit  val_bpb  size_mb  status  description

- size_mb = (code_bytes + compressed_model_bytes) / 1_000_000, rounded to 2 decimal places
- status: keep / discard / crash / oversize

## Experiment loop

LOOP FOREVER:
1. Modify `train_gpt.py` with an idea
2. `git commit`
3. Run experiment → `run.log`
4. Parse val_bpb and artifact size
5. If size > 16MB → log as `oversize`, revert
6. If val_bpb improved AND size OK → keep commit, advance branch
7. If val_bpb worse → discard, `git reset --hard HEAD~1`
8. Log to results.tsv (do not git-track this file)

NEVER STOP. NEVER ASK IF YOU SHOULD CONTINUE.