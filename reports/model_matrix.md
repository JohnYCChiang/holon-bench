# Holon Benchmark Model Matrix

## qwen36-35b-a3b-mtp-q8 [artifact/holon-cli]

- Hard pass rate: 96.61%
- First-pass rate: 84.75%
- Final-pass rate: 96.61%
- Repair conversion rate: 77.78%
- Repaired cases: 14/18
- Total repair attempts: 16
- Repair tax: 0.14 attempts/case
- Protected/hidden verifier coverage: 46/118
- Mutation verifier coverage: 5/118
- Hidden/mutation failures: 3/2
- Avg repair attempts to pass: 1.07
- Max repair exhausted: 1
- Soft score avg: 99.79
- First failures: test_fail=11, missing_requirement=7, compile_fail=4, semantic_check_failed=4, hidden_verifier_failed=3, mutation_verifier_failed=2
- Final failures: hidden_verifier_failed=3, mutation_verifier_failed=2, extra_text=1

### Risk Summary

- Integration: artifact output sometimes needs recovery; keep strict contract checks and pollution tags enabled
- Integration: public verifiers can pass while hidden or mutation gates fail; expand hidden coverage before treating 100% public pass as production-ready
- Integration: protected/hidden and mutation coverage is partial (46/118 protected/hidden, 5/118 mutation)
- Deployment: 1 cases exhausted repair budget; enforce bounded loops, timeouts, and stop reasons
- Operations: track first-pass and repaired-pass separately; repaired success is useful but has higher operating cost

### flutter_cross_platform

- Hard pass rate: 100.00%
- First-pass rate: 93.33%
- Final-pass rate: 100.00%
- Repair conversion rate: 100.00%
- Repaired cases: 1/1
- Repair tax: 0.07 attempts/case
- Protected/hidden verifier coverage: 3/15
- Mutation verifier coverage: 0/15
- Soft score avg: 100.00

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

- Hard pass rate: 93.33%
- First-pass rate: 93.33%
- Final-pass rate: 93.33%
- Repair conversion rate: 0.00%
- Repaired cases: 0/1
- Repair tax: 0.07 attempts/case
- Protected/hidden verifier coverage: 4/15
- Mutation verifier coverage: 1/15
- Soft score avg: 99.67

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

- Hard pass rate: 93.33%
- First-pass rate: 93.33%
- Final-pass rate: 93.33%
- Repair conversion rate: 0.00%
- Repaired cases: 0/1
- Repair tax: 0.00 attempts/case
- Protected/hidden verifier coverage: 5/15
- Mutation verifier coverage: 0/15
- Soft score avg: 99.67

### rust_core

- Hard pass rate: 100.00%
- First-pass rate: 100.00%
- Final-pass rate: 100.00%
- Repair conversion rate: 0.00%
- Repaired cases: 0/0
- Repair tax: 0.00 attempts/case
- Protected/hidden verifier coverage: 4/15
- Mutation verifier coverage: 0/15
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
