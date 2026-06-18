# Tao arm — mechanics (token cost counts into M1/M2)

You act ONLY through the `tao-port` CLI. All output is JSON. Per prereg §5 the
tokens of this document are counted into the edit-cycle accounting — it is part
of your context, not free.

Store: a fresh `--store <run-dir>/.tao` is created by the harness with
`tao-port init`; the world manifest (stdlib + task contexts, the integer/bool/
list/pair entries, and the `prim_defs` table) is printed by `tao-port manifest`.
The harness has already trusted the three SIGNED `tool_version`s from the
trusted-toolchain registry.

## Command surface

- `tao-port txn --store DIR` — reads a **Txn JSON on stdin**, returns a receipt
  `{inserted:[id...], entries:[id...], hole_events:[...]}` (exit 0) or
  `{rejected:[diagnostic...]}` (exit 2). This is your only *edit* primitive.
- `tao-port check DEF_HEX [--ctx task|stdlib] [--mint-for ENTRY_HEX]` —
  typecheck a definition; `{ok:true,type:...}` or `{ok:false,diagnostics:[...]}`.
- `tao-port test LAW_HEX [--covers ...]` — run a law as a test;
  `{passed:bool}` (exit 3 if it does not pass).
- `tao-port law LAW_HEX` — run a law as a property/proposition.
- `tao-port ctx TARGET_HEX [--budget N]` — assemble a context bundle for a
  target; returns `{bundle_id, tokens, bundle}`. Use this to read signatures
  before fetching bodies.
- `tao-port node ID`, `tao-port facts ID`, `tao-port holes`,
  `tao-port discharge HOLE_HEX`, `tao-port manifest`, `tao-port versions`.

Acceptance verifier (your "cargo test"): once you have declared your def ids in
`solution.json`, run the suite as a black box — this is NOT a tao-port command,
call it directly (it records itself):
`python3 <bench>/runners/run_killtest.py verify-acceptance --run-dir <run-dir> --store <run-dir>/.tao`
It instantiates and runs the full acceptance suite for you and returns
`{green, passed, failed, failing:[names]}`. You do not instantiate the
`acceptance/*.json` templates yourself; just keep `solution.json` current and
re-run `verify-acceptance` until `green:true`.

## Txn JSON shape

```
{
  "inserts":  [ <Node>, ... ],      // typed AST nodes (Def/App/Lit/Lam/...)
  "vocab":    [ <VocabEntry>, ... ],// abstract type + constructors + laws
  "lexicon":  [ {"Propose": {"context": <ctx-id>, "name": "...",
                              "entry": <entry-id>, "constructors": [...],
                              "laws": [...]}} ],
  "holes":    [ {"Open": {"hole": <Node>}}, ... ],
  "expects":  [ <Precondition>, ... ],
  "agent":    "you"
}
```

A `Node` is `{"schema_version":0,"payload":{<Kind>:{...}}}`. Literals are
`{"Lit":{"Int":N}}`; primitive references are `{"Def":"<prim-id-from-manifest>"}`;
application is `{"App":[<fn>,<arg>]}`; a vocab-entry reference inside a law over
clause is its entry id.

## What you submit + the loop

Declare your submitted def ids in `solution.json` in your run dir:

```
{ "entry": "<VocabEntry id>", "empty": "<def id>", "insert": "<def id>",
  "member": "<def id>", "size": "<def id>" }
```

Loop: submit/refine defs via `txn`, `check` them, keep `solution.json` current,
then run `verify-acceptance` (above). Iterate on its `failing` list until
`green:true`. The runner is the only fact writer; the scorer later runs the
held-out suite against the same `solution.json`.
