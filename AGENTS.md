# AGENTS.md — Holon-Bench（Codex 執行協定）

你在 Holon-Bench 上工作：holon 的 benchmark／falsification 層（Python runners
＋ YAML cases）。

**重要**：本 repo 根目錄的 `CLAUDE.md` 是給「解單一 benchmark case」的 agent
persona 看的，**不適用於維護 bench harness 本身**（如 RM-F1 這種卡）。維護
harness 時的規則以 `/home/taichi/holon-world/CLAUDE.md` 的 Holon-Bench 段為準，
加上本檔。

## 目前任務

- 卡片：gitea `taichi/holon-bench` issue **#44（RM-F1，P6.2 五個穩定基準設定
  檔）**。卡片全文在 holon repo：
  `/home/taichi/holon-world/holon/docs/plans/roadmap_2026-07_sonnet5.md` 的
  「RM-F1」段（wave-2 roadmap RM2-F 段沿用原文）。
- **#45（F2改量測）不要碰**——那是 owner 觸發的操作卡，設計已定稿在 issue。

## 執行協定

1. 開工前 `git status --short` 乾淨；工作分支 `rm2/f1`（**不在 main 上
   commit**，commit 前先 `git branch --show-current`）。
2. 在 issue #44 留言五要素（目標層／預定檔案／不變式／驗證命令／停止條件）
   → 實作 → 驗證全綠 → commit → push → 開 PR（base=main，body 繁中）→
   issue 留言完成摘要 → **停**。你不 merge。
3. 卡片停止條件觸發：issue 留言記錄後停下。

## 驗證（全綠才 commit）

```bash
python3 -m py_compile runners/*.py
python3 runners/schema_check.py .
python3 runners/docs_check.py .
python3 runners/ci_smoke.py .
```

## 硬禁

- 不弱化任何 validator／pass criteria／case 判準。
- 產生的報告**不得覆寫** `reports/` 頂層既有基準線（報告路徑帶 profile 名＋
  時間戳）；結果 metadata 只做向後相容新增。
- 保持 agent-agnostic／OpenAI-compatible，不綁特定 agent。
- profile 只存引用（模型 tag／端點名），不複製參數（防與 model-registry 漂移）。
- 絕不動 `~/models` 模型權重；不落 mock 數據充真實量測報告。

## 備註

- `origin` 同時設 gitea＋GitHub 兩個 pushurl，`git push origin <branch>` 會
  同時推兩邊——既有設定，照用即可。
- Commit 主旨英文；PR／issue 留言繁體中文（台灣用語）。
