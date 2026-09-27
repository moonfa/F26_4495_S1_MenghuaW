# Step 6：按照你的 GitHub 项目安装（Mac / VS Code）

**适用版本**：`moonfa/F26_4495_S1_MenghuaW` → `Implementation/MVP_Demo/slice2_new/`；GitHub `main` 分支的已读取文件。**这是针对你现有项目的补丁，不要再安装之前那个通用 Step6 ZIP，也不需要复制 Muse 的 UUID model.py。**

## A. 最简单的 7 步

### 第 1 步：关闭目前的服务器

在运行 Uvicorn 的 Terminal 按 `Control + C`。不要在正在写入 SQLite 时安装/迁移。

### 第 2 步：保护现有代码

打开 VS Code 的 Terminal，进入你电脑上的仓库目录：

```bash
cd /你的本地路径/F26_4495_S1_MenghuaW
# 如果你的最新改动还没提交，先保存/提交到自己的仓库。
git status
# 新建一个安全的工作分支
# （假如你已经在这个分支，可以跳过）
git switch -c feature/step6-research-history
cd Implementation/MVP_Demo/slice2_new
```

请勿将 `.env` 中的 API Key 发到 GitHub。当前仓库中跟踪了 `slice1.db`；**别把包含个人投资笔记的数据库或备份提交到公开仓库**。

### 第 3 步：下载并解压补丁包

下载对话里提供的 `Step6_MVP_Demo_Ready.zip`，双击解压到 Downloads 文件夹。你会看到 `Step6_MVP_Demo_Ready/install_into_repo.py`。

### 第 4 步：执行自动安装

保持 Terminal 的当前目录为 `.../Implementation/MVP_Demo/slice2_new`，执行：

```bash
python3 ~/Downloads/Step6_MVP_Demo_Ready/install_into_repo.py .
```

安装器只替换现有 `app/routes.py`、`app/main.py`、`app/static/index.html`，并新增 `app/step6/`。**不会覆盖**原来的 `app/models.py`、`app/database.py`、`app/adapters/`、`app/ai/`、`.env` 或 `slice1.db`。

安装器先核对当前代码是否与你 GitHub 上的版本一致，并把将要替换的旧文件、现有 SQLite 数据库备份到 `~/Step6_Project_Backups/`。如果提示文件与 GitHub 版本不同，先查看/提交你的本地改动；只有确认同意覆盖本地版本时才执行：

```bash
python3 ~/Downloads/Step6_MVP_Demo_Ready/install_into_repo.py . --allow-modified
```

### 第 5 步：执行数据库升级及历史数据导入

仍在 `slice2_new/` 目录，使用你当前项目正在用的虚拟环境：

```bash
python3 -m app.step6.migrate
```

预期会显示：

```text
SQLite backup: ...slice1.db.before_step6_....bak
Successfully imported Master Research Reports: N
Done. Existing AnalysisDraft/EvidenceSnapshot rows were not deleted or overwritten.
```

N 是你的数据库里已有的、成功生成的 Master Research Reports 数量；不是固定数字。脚本可再次运行，不会重复导入已有报告。原来的 `analysis_drafts` 和 `evidence_snapshots` 原封不动保留。

如果你以前从另一个目录启动程序，注意 `sqlite:///./slice1.db` **相对于启动目录**。务必从 `Implementation/MVP_Demo/slice2_new/` 执行迁移和启动命令，避免意外创建另一份空数据库。

### 第 6 步：启动原来的项目

```bash
python3 -m uvicorn app.main:app --reload
```

如果报缺少 `dotenv`，先运行 `python3 -m pip install python-dotenv`。不要新建第二个 FastAPI app，也不要用旧的 `app.app:app` 命令启动。

浏览器打开：

```text
http://127.0.0.1:8000/
```

### 第 7 步：不花 Token 的第一轮验收

1. 默认 WMT，点击 **Load Saved Research**。已有 Snapshot、历史 Master Reports 都应显示；这是读数据库，不调用 OpenBB 或 Gemini。
2. 点击历史报告列表，查看旧报告；确认旧报告的 `Snapshot #`、时间、Key Takeaways 与 Thread Actions。
3. 如果旧报告提出 `Create` 类型的 Thread Action，选择 **Approve**。右侧 Research Threads 会出现新的专题；点击专题，能看到第一次 `ThreadVersion`。
4. 在 **Personal Research Journal** 输入自己的判断，按 **Save my note**。重新加载后，这条笔记应仍存在。
5. 如需新增数据，才点击 **Sync Evidence**；需要新分析，才点击 **Generate AI Review**。若新 Snapshot 的标准化 Evidence 没变化，且模型/Prompt/已批准 Thread 状态都未变化，系统会直接复用旧报告。
6. **Force Full Review** 应创建一份新的完整报告；如 Gemini 报错，历史报告和页面上原有报告仍应可访问。

## B. 两次真实分析与长期研究连续性验收

只有上述基础功能通过后，再启用你原来的 Gemini 配置（不要把 API Key 放进命令截图/提交）。

- 第一次：WMT → Sync Evidence → Generate AI Review → 历史报告出现 Report A。
- 在 Report A 审核批准一个重要的 `Create` Thread Action。
- 第二次：WMT → Sync Evidence。如果 Evidence 完全一致但你要测试新的完整复盘，按 **Force Full Review**；若数据确实变化，按普通 **Generate AI Review**。历史报告出现 Report B。
- Report B 应能显示 `previous_report_id` 对应 Report A；AI 上下文应包含已批准的 Thread。可以查看 Report B 的 `What Changed` 和针对原专题的建议。
- 审批该 Thread 的后续 `Update/Continue` 操作后，其时间线出现第二个版本。拒绝的操作不能改变 Thread。
- 第三次分析可重复；检查报告顺序、不同 Snapshot ID 与时间线是否仍然正确。

**我已用模拟 Evidence 和 Mock AI 验证这些数据库/API 流程，但无法直接使用你本地的 Gemini Key、OpenBB 网络以及真实数据库做两次真实分析。上面的真实验收需要你在本地完成。**

## C. 可以在 Swagger 中检查的接口

进入 `http://127.0.0.1:8000/docs`：

| API | 功能 |
|---|---|
| `GET /api/v1/companies/WMT/reports` | WMT 历史报告列表 |
| `GET /api/v1/reports/{report_id}` | 一份保存的完整报告与审核状态 |
| `GET /api/v1/reports/by-draft/{draft_id}` | 兼容原 AI Draft ID |
| `GET /api/v1/companies/WMT/threads` | 已审批建立的公司研究专题 |
| `GET /api/v1/threads/{thread_id}/timeline` | 某专题历次已批准版本 |
| `POST /api/v1/thread-actions/{action_id}/review` | 人工批准/编辑/拒绝 |
| `GET/POST /api/v1/companies/WMT/notes` | 你自己的研究笔记 |

## D. 遇到错误的处理办法

- **`No module named app`**：请确认终端的当前目录是 `slice2_new/`，而不是 `slice2_new/app/`。
- **`no such table: research_reports`**：先关闭服务器，执行 `python3 -m app.step6.migrate`，再重启。
- **历史报告为 0**：确认当前目录中的 `slice1.db` 与你之前运行项目时使用的是同一份；如果原来的分析只是失败状态或没有 `report_markdown`，导入 0 是正常的。
- **点击 Approve 返回 409**：可能已审核过、同名 Thread 已存在，或 `Update/Continue` 尚未关联目标 Thread；查看页面的错误提示与已批准的 Thread 列表。
- **GitHub 没出现改动**：补丁只安装在你本地；你需要自行 `git add`、commit、push。请勿提交数据库、备份或 `.env`。
- **迁移需要回滚**：停止服务器，保存当前出错状态，在 `~/Step6_Project_Backups/` 找到安装器备份的三个旧文件和 SQLite 数据库，恢复旧文件及 DB 后再启动。

## E. 提交 GitHub（验收之后）

在仓库根目录执行（或使用 VS Code Source Control），**只提交源码**：

```bash
git add Implementation/MVP_Demo/slice2_new/app/routes.py \
        Implementation/MVP_Demo/slice2_new/app/main.py \
        Implementation/MVP_Demo/slice2_new/app/static/index.html \
        Implementation/MVP_Demo/slice2_new/app/step6/
git status
git commit -m "Step 6: research report history and reviewed thread continuity"
git push -u origin feature/step6-research-history
```

在 GitHub 上创建 Pull Request，确认文件 diff、测试结果，再决定是否合并到 main。不要 `git add .`，因为你的仓库本来包含 `.db`、`__pycache__` 等本地生成文件。

## F. 这次已完成与暂未完成

已实现：整数 PK 的正式 `ResearchReport/ResearchThread/ThreadVersion/ThreadAction/PersonalResearchNote`、历史 Draft 幂等导入、正式报告前后关联、跨相同 Evidence 新 Snapshot 的报告复用、已批准 Thread 的 AI 上下文、人工审核 API、研究时间线、同页历史报告与笔记、Force Full Review 新报告和失败保留旧报告、自动迁移备份。

仍属于后续 Step 7/8：正式 Watchlist 侧栏、四个标签页的布局优化、自动刷新频率限制、行情/新闻独立过期策略、认证与多人权限、真实交易绩效回测。当前新增 API 只适用于个人本地运行，不可直接公开部署。
