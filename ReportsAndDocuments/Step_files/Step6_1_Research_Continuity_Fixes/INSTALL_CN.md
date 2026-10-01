# Step 6.1：修复与验收（中文安装说明）

本包专门安装在 **已经成功运行 Step 6** 的 `Implementation/MVP_Demo/slice2_new`。不要重新安装旧 Step 6 ZIP，也不要删除现有数据库。

## 操作步骤

1. 关闭 Uvicorn（Terminal 按 Ctrl+C）。在 VS Code 的 Source Control 先提交或备份你的本地修改。
2. 下载并解压本 ZIP 到 Downloads；在 Terminal 进入你本地 Git 仓库的 `Implementation/MVP_Demo/slice2_new`。
3. 执行：

```bash
python3 ~/Downloads/Step6_1_Research_Continuity_Fixes/install_step61.py .
python3 -m app.step6.migrate
python3 -m uvicorn app.main:app --reload
```

如果浏览器仍然显示旧版，请强制刷新（Mac: Cmd+Shift+R）。安装脚本会在 `~/Step6_Project_Backups/step61_时间戳/` 备份被覆盖的文件和默认位置 `slice1.db`；迁移脚本也会对实际 SQLite 位置再次备份。**如果 DATABASE_URL 指向其他位置，请自行先备份该数据库。**

## 本次实际修改

- `app/static/index.html`：Edit & Approve 从连续浏览器弹窗改为页面内编辑表单；历史报告增加日期、类型和摘要；Evidence Delta 增加自然语言解释；展示轻量 Valuation implication。
- `app/step6/routes.py`：历史报告 API 返回摘要和估值影响；编辑批准可以更新已有 Thread 标题；同一份报告不能重复给同一个 Thread 增加版本；可以在批准 `create` 时指定现有 Thread 来合并。
- `app/step6/models.py` + `migrate.py`：仅向正式 `research_reports` 添加一个可空 JSON 字段 `valuation_implications`，保留所有原有整数主键及历史数据。
- `app/ai/schemas.py` + `prompts.py`：同一次 Gemini 响应可返回 base_metric/multiple 的方向、幅度、置信度、原因和整体 action；不自动计算或更新 Fair Value。
- `app/step6/service.py`：将成功的 AI 分析中的 valuation_implications 归档到正式历史报告。

**注意：你 GitHub 上读取到的 `app/models.py` 并没有 valuation_models/assumptions 表，本包不凭空创建估值计算器或假设更新功能。** 在未选择 active model 的情况下，Gemini 应返回 null，旧历史报告显示 Not assessed。未来真正加入模型选择后，才根据选中的 P/E、P/S 或 P/B 显示两个输入。

**财务单位核对：** 根据你贴的 WMT 页面，dividend_yield=0.92、debt_to_equity=71.65 的来源口径更符合“百分数”，旧 UI 误当比率分别显示 92% 和 71.65x；新 UI 将两者作为已是百分数的字段，分别显示 0.92% 和 71.65%。但不同数据提供方口径可能不同，使用其他 ticker/provider 前仍须检查 Adapter 归一化契约，不能仅凭数值大小猜测单位。

## 验收步骤

1. 打开 WMT → Load Saved Research。历史报告列表应显示可读日期、类型、简短摘要，仍保留技术 Report/Evidence ID。
2. 打开带 `proposed` Thread Action 的历史报告 → Edit & Approve。应展开页面内 Title/Summary/Importance/Reviewer note；保存后刷新历史与 Thread 列表。
3. 验证旧 AI proposal 的 `original_proposal` 仍未被人工编辑覆盖；重复批准同一 action 返回 HTTP 409。
4. 第一个报告批准 `create`，第二个不同报告批准针对相同 thread_id 的 `update`。Thread timeline 应有两个版本、两个不同 report_id、一个 thread_id。
5. 新生成的报告可带 valuation_implications；旧报告允许为 null，不修改用户估值假设。
6. 如需在本机运行自动测试：`python3 -m pytest tests/test_step6_integration.py -q`（测试文件需要对应 mock fixtures 和测试依赖；不会使用你的真实 SQLite）。

## 尚未包含

- 未增加新的估值模型表或自动 Fair Value 重算；未进行真实 Gemini/OpenBB 在线验证。
- 未更改 Evidence Adapter 源码：除前端格式外，其他 provider 的字段单位需单独验证。
- 未重做侧栏/标签页，不引入 React。
