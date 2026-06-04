# Holon Benchmark Model Matrix

## qwen36-35b-a3b-mtp-q8 [artifact/holon-cli]

- Hard pass rate: 94.07%
- First-pass rate: 82.20%
- Final-pass rate: 94.07%
- Repair conversion rate: 66.67%
- Repaired cases: 14/21
- Total repair attempts: 16
- Repair tax: 0.14 attempts/case
- Protected/hidden verifier coverage: 50/118
- Mutation verifier coverage: 10/118
- Hidden/mutation failures: 3/5
- Avg repair attempts to pass: 1.07
- Max repair exhausted: 1
- Soft score avg: 99.66
- First failures: test_fail=11, missing_requirement=7, mutation_verifier_failed=5, compile_fail=4, semantic_check_failed=4, hidden_verifier_failed=3
- Final failures: mutation_verifier_failed=5, hidden_verifier_failed=3, extra_text=1

### Risk Summary

- Integration: artifact output sometimes needs recovery; keep strict contract checks and pollution tags enabled
- Integration: public verifiers can pass while hidden or mutation gates fail; expand hidden coverage before treating 100% public pass as production-ready
- Integration: protected/hidden and mutation coverage is partial (50/118 protected/hidden, 10/118 mutation)
- Deployment: 1 cases exhausted repair budget; enforce bounded loops, timeouts, and stop reasons
- Deployment: final pass rate is below 95%; use staged rollout or human approval for higher-impact changes
- Operations: track first-pass and repaired-pass separately; repaired success is useful but has higher operating cost

### flutter_cross_platform

- Hard pass rate: 93.33%
- First-pass rate: 86.67%
- Final-pass rate: 93.33%
- Repair conversion rate: 50.00%
- Repaired cases: 1/2
- Repair tax: 0.07 attempts/case
- Protected/hidden verifier coverage: 4/15
- Mutation verifier coverage: 1/15
- Soft score avg: 99.67

### go_core

- Hard pass rate: 100.00%
- First-pass rate: 100.00%
- Final-pass rate: 100.00%
- Repair conversion rate: 0.00%
- Repaired cases: 0/0
- Repair tax: 0.00 attempts/case
- Protected/hidden verifier coverage: 4/15
- Mutation verifier coverage: 1/15
- Soft score avg: 100.00

### go_game_server

- Hard pass rate: 86.67%
- First-pass rate: 80.00%
- Final-pass rate: 86.67%
- Repair conversion rate: 33.33%
- Repaired cases: 1/3
- Repair tax: 0.07 attempts/case
- Protected/hidden verifier coverage: 7/15
- Mutation verifier coverage: 2/15
- Soft score avg: 99.33

### graph_memory_workflow

- Hard pass rate: 100.00%
- First-pass rate: 100.00%
- Final-pass rate: 100.00%
- Repair conversion rate: 0.00%
- Repaired cases: 0/0
- Repair tax: 0.00 attempts/case
- Protected/hidden verifier coverage: 3/3
- Mutation verifier coverage: 0/3
- Soft score avg: 100.00

### python_tool_engineering

- Hard pass rate: 86.67%
- First-pass rate: 86.67%
- Final-pass rate: 86.67%
- Repair conversion rate: 0.00%
- Repaired cases: 0/2
- Repair tax: 0.07 attempts/case
- Protected/hidden verifier coverage: 5/15
- Mutation verifier coverage: 2/15
- Soft score avg: 99.33

### repair_needed

- Hard pass rate: 100.00%
- First-pass rate: 0.00%
- Final-pass rate: 100.00%
- Repair conversion rate: 100.00%
- Repaired cases: 10/10
- Repair tax: 1.00 attempts/case
- Protected/hidden verifier coverage: 10/10
- Mutation verifier coverage: 0/10
- Soft score avg: 99.50

### rust_bevy

- Hard pass rate: 86.67%
- First-pass rate: 86.67%
- Final-pass rate: 86.67%
- Repair conversion rate: 0.00%
- Repaired cases: 0/2
- Repair tax: 0.00 attempts/case
- Protected/hidden verifier coverage: 7/15
- Mutation verifier coverage: 2/15
- Soft score avg: 99.33

### rust_core

- Hard pass rate: 100.00%
- First-pass rate: 100.00%
- Final-pass rate: 100.00%
- Repair conversion rate: 0.00%
- Repaired cases: 0/0
- Repair tax: 0.00 attempts/case
- Protected/hidden verifier coverage: 4/15
- Mutation verifier coverage: 1/15
- Soft score avg: 100.00

### rust_porting

- Hard pass rate: 100.00%
- First-pass rate: 86.67%
- Final-pass rate: 100.00%
- Repair conversion rate: 100.00%
- Repaired cases: 2/2
- Repair tax: 0.20 attempts/case
- Protected/hidden verifier coverage: 6/15
- Mutation verifier coverage: 1/15
- Soft score avg: 100.00
