# TESTPILOT-FRONTEND-REFERENCE-001

| 日期（UTC+8） | 会话 ID | 工作包 | 实现或归档提交 | 证据 |
|---|---|---|---|---|
| 2026-11-27T12:16:02+08:00 | `01a21b37-6705-7041-b791-69105c8abe9e` | WP02 | d937d4b | [验收与产物](../docs/TESTPILOT-FRONTEND-REFERENCE-001/) |

## 用户 Prompt 原文

# TESTPILOT-FRONTEND-REFERENCE-001

## GitNexus 前端设计研究与产品设计提取

### 一、任务目标

对本地参考项目 GitNexus 进行完整的前端设计研究，为 TestPilot AI 的全站前端升级建立设计依据。



参考项目路径：



`E:\Frontend-References\gitnexus`



TestPilot AI 项目路径：使用当前实际工作区，不得猜测或修改路径。



本阶段只研究、分析和形成报告，不实施前端改造。

### 二、重点研究内容

1. 全局布局
   - 顶部导航栏
   - 左侧文件资源管理器
   - 中央工作区域
   - 右侧可视化区域
   - 面板宽度、分隔线、折叠和拖拽
2. 视觉设计系统
   - 背景颜色和层次
   - 主色、辅助色、状态色
   - 字体及字号
   - 圆角、边框、阴影
   - 间距与尺寸规范
   - 图标体系
3. 组件设计
   - 导航栏
   - 文件树
   - 搜索框
   - 标签
   - 按钮
   - 卡片
   - 弹窗
   - 悬浮操作栏
   - 代码编辑器
   - 图谱节点与连线
4. 交互体验
   - 搜索与筛选
   - 节点选择
   - 图谱缩放和拖拽
   - 面板展开与收起
   - 页面切换
   - 操作反馈
   - 加载和异常状态
5. 技术实现
   - 前端框架
   - 组件组织方式
   - 样式管理方式
   - 图谱可视化技术
   - 图标库
   - 动画实现
   - 响应式布局

### 三、映射到 TestPilot AI

结合 TestPilot AI 六大业务模块：



F01 项目中心\
F02 AST 代码分析\
F03 AI 测试生成\
F04 自动化测试执行\
F05 缺陷管理\
F06 质量分析



分析 GitNexus 哪些设计适合借鉴，哪些不适合直接使用，以及每个页面应该如何组织布局。



重点研究：

- AST 分析页面是否适合采用三栏工作台。
- 测试生成页面如何组合代码区、配置区和结果区。
- 测试执行页面如何展示实时日志、执行状态和测试结果。
- 缺陷管理如何组织列表、详情和代码 Diff。
- 质量分析如何展示图表和质量指标。
- 项目中心如何建立统一入口。

### 四、输出交付物

在 TestPilot AI 项目的独立文档目录中生成：

1. GITNEXUS_DESIGN_AUDIT.md
2. FRONTEND_DESIGN_SYSTEM_PROPOSAL.md
3. TESTPILOT_PAGE_LAYOUT_MAPPING.md
4. COMPONENT_INVENTORY.md
5. FRONTEND_UPGRADE_ROADMAP.md

要求包含真实源码定位、关键截图、组件分析、借鉴理由和具体实施建议。

### 五、严格约束

- GitNexus 仅作为设计参考。
- 不直接复制其业务代码、组件或商业资产。
- 不修改 GitNexus 源码。
- 不修改 TestPilot AI 现有前端。
- 不修改后端 API、数据库和业务逻辑。
- 不删除、不覆盖现有文件。
- 不虚构技术栈、组件和交互能力。
- 所有技术判断必须有源码或运行证据。
- 优先考虑 TestPilot AI 自身业务需求，而非盲目照搬参考项目。

### 六、最终验收

提交一份完整研究报告，并明确回答：

1. GitNexus 最值得借鉴的十项设计是什么？
2. 哪些设计不适合 TestPilot AI？
3. 六个页面分别应该采用什么布局？
4. 全站需要建立哪些公共组件？
5. 如何建立统一 Design System？
6. 如何分阶段改造，保证现有功能不受影响？

最终状态：



READY_FOR_TESTPILOT_FRONTEND_DESIGN_REVIEW



本阶段完成后停止，等待人工确认。

## 原始最终答复

已提交 **5 份研究文档和 6 张实拍截图**，WP02 独立提交为 `d937d4b`。提交内容仅包含研究材料。

**参考版本待确认。** 本机未找到 `E:\Frontend-References\gitnexus`。本次源码审计和运行截图使用 GitNexus 官方固定提交 `26a404f` 的独立本地副本。截图使用只读示例数据，报告已标明运行条件；指定 E 盘副本与该提交的一致性仍待确认。[官方提交](https://github.com/abhigyanpatwari/GitNexus/commit/26a404f21761925a13c4fa7cd0086465fa11f419)

**最值得借鉴的是选择联动。** 在 GitNexus 中点击文件，文件树、图中节点和源码检查器会同时定位。TestPilot 可把这一机制用于“符号 → 源码行”和“失败用例 → 原始运行 → 修复回归”。三栏应按实际可用宽度启用：实测 GitNexus 在 390 px 窗口同时打开左右栏后，中央图谱宽度降到了 0。[选中文件实拍](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/screenshots/selection.png>) · [双侧栏实拍](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/screenshots/panels.png>)

| 页面 | 建议布局 |
| --- | --- |
| F01 项目中心 | 项目列表 → 文件版本清单 → 选中版本预览与分析入口 |
| F02 AST 分析 | 宽屏采用符号索引、行号源码、符号详情三栏；窄屏按需切换 |
| F03 测试生成 | 上方并列目标源码与配置，下方全宽展示测试源码、静态检查和真实首跑结果 |
| F04 测试执行 | 执行表单与状态置顶，运行历史联动用例和日志。现有接口完成后一次返回日志，等待期间显示实际请求状态 |
| F05 缺陷管理 | 列表与详情并排；详情串起原失败、修复版本和回归记录，按需打开只读 Diff |
| F06 质量分析 | 围绕单次运行分别展示用例分布、通过率和行覆盖率，保留分母、原始证据与导出入口 |

**五份交付物**

1. [GitNexus 设计审计](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/GITNEXUS_DESIGN_AUDIT.md>) — 十项借鉴设计、不适用项、固定源码定位与截图。
2. [全站设计系统提案](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/FRONTEND_DESIGN_SYSTEM_PROPOSAL.md>) — 颜色、字体、间距、状态、响应式与键盘验收。
3. [六页布局映射](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/TESTPILOT_PAGE_LAYOUT_MAPPING.md>) — 各页的数据依据、布局、异常状态与验收场景。
4. [公共组件清单](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/COMPONENT_INVENTORY.md>) — 优先统一项目与版本选择、只读证据查看、请求反馈和运行结果。
5. [前端升级路线图](</D:/TestPilot AI/docs/TESTPILOT-FRONTEND-REFERENCE-001/FRONTEND_UPGRADE_ROADMAP.md>) — 按 F01–F06 独立迁移，逐页回归与回退，最后复验失败到修复的完整链路。

**公开提交版研究材料状态：`READY_FOR_TESTPILOT_FRONTEND_DESIGN_REVIEW`。** 本阶段停在人工评审，等待参考版本确认。
