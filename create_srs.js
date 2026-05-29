const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak
} = require("docx");

const out = "E:/code/2026实训/智能传媒内容分析与推荐系统/智能传媒内容分析与推荐系统_需求规格说明书.docx";

const bd = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
const bds = { top: bd, bottom: bd, left: bd, right: bd };
const cm = { top: 80, bottom: 80, left: 120, right: 120 };
const blue = "1F4E78";
const lb = "D6E4F0";
const lg = "F2F2F2";
const wh = "FFFFFF";

const hdr = (txt, w) => new TableCell({ borders: bds, width: { size: w, type: WidthType.DXA }, shading: { fill: blue, type: ShadingType.CLEAR }, margins: cm,
  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: txt, font: "Microsoft YaHei", bold: true, color: wh, size: 20 })] })] });

const dc = (txt, w, o = {}) => new TableCell({ borders: bds, width: { size: w, type: WidthType.DXA },
  shading: o.sh ? { fill: o.sh, type: ShadingType.CLEAR } : undefined, margins: cm,
  children: [new Paragraph({ alignment: o.ct ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({ text: txt || "", font: "Microsoft YaHei", bold: !!o.b, size: 20 })] })] });

const tr = (cells) => new TableRow({ children: cells });

const pp = (txt, o = {}) => new Paragraph({ spacing: { before: o.b4 || 60, after: o.af || 60 },
  alignment: o.ct ? AlignmentType.CENTER : AlignmentType.LEFT, heading: o.hd || undefined,
  children: [new TextRun({ text: txt, font: "Microsoft YaHei", bold: !!o.b, size: o.sz || 20, color: o.cl || "333333" })] });

const bi = (txt, lv = 0) => new Paragraph({ numbering: { reference: "bullets", level: lv }, spacing: { before: 40, after: 40 },
  children: [new TextRun({ text: txt, font: "Microsoft YaHei", size: 20, color: "333333" })] });

const ni = (txt, lv = 0) => new Paragraph({ numbering: { reference: "numbers", level: lv }, spacing: { before: 40, after: 40 },
  children: [new TextRun({ text: txt, font: "Microsoft YaHei", size: 20, color: "333333" })] });

const T = (colWidths, rows) => new Table({ width: { size: colWidths.reduce((a,b)=>a+b,0), type: WidthType.DXA }, columnWidths: colWidths, rows });

// helper: build header + data table
const makeTable = (colWidths, headers, data) => T(colWidths, [
  tr(headers.map((h,i) => hdr(h, colWidths[i]))),
  ...data.map(r => tr(r.map((c,i) => dc(c, colWidths[i], i===0 ? { b: true, sh: lg } : {}))))
]);

// helper: stories table
const storyTable = (colWidths, headers, data) => T(colWidths, [
  tr(headers.map((h,i) => hdr(h, colWidths[i]))),
  ...data.map(r => tr([
    dc(r[0], colWidths[0], { ct: true, b: true, sh: lg }),
    dc(r[1], colWidths[1]),
    dc(r[2], colWidths[2])
  ]))
]);

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Microsoft YaHei", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Microsoft YaHei", color: blue },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Microsoft YaHei", color: blue },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Microsoft YaHei", color: "2E75B6" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1440, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [
    // ===== COVER =====
    {
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      children: [
        new Paragraph({ spacing: { before: 3600 }, children: [] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
          new TextRun({ text: "智能传媒内容分析与推荐系统", font: "Microsoft YaHei", bold: true, size: 52, color: blue })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [
          new TextRun({ text: "需求规格说明书 (SRS)", font: "Microsoft YaHei", size: 36, color: "2E75B6" })
        ]}),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600, after: 80 }, children: [
          new TextRun({ text: "Software Requirements Specification", font: "Microsoft YaHei", size: 24, color: "808080", italics: true })
        ]}),
        new Paragraph({ spacing: { before: 1200 }, children: [] }),
        T([2400, 3600], [
          tr([dc("文档版本", 2400, { b: true, sh: lb }), dc("V1.0", 3600)]),
          tr([dc("编制日期", 2400, { b: true, sh: lb }), dc("2026-05-28", 3600)]),
          tr([dc("编制团队", 2400, { b: true, sh: lb }), dc("第013组", 3600)]),
          tr([dc("组长", 2400, { b: true, sh: lb }), dc("王淦", 3600)]),
          tr([dc("组员", 2400, { b: true, sh: lb }), dc("朱自豪、秦梓洋", 3600)]),
        ]),
      ]
    },

    // ===== MAIN =====
    {
      properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: blue, space: 1 } },
        children: [new TextRun({ text: "智能传媒内容分析与推荐系统 \u2014 需求规格说明书", font: "Microsoft YaHei", size: 16, color: "808080", italics: true })]
      })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF", space: 1 } },
        children: [new TextRun({ text: "第 ", font: "Microsoft YaHei", size: 16, color: "808080" }),
                   new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 16, color: "808080" }),
                   new TextRun({ text: " 页", font: "Microsoft YaHei", size: 16, color: "808080" })] })] }) },
      children: [
        // ===== 1 =====
        pp("1. 文档概述", { hd: HeadingLevel.HEADING_1 }),
        pp("1.1 项目背景", { hd: HeadingLevel.HEADING_2 }),
        pp("随着新闻资讯、短视频、图文内容等传媒数据快速增长，传统人工管理内容和简单列表展示方式已无法满足用户个性化获取信息、平台内容运营分析和后台管理的需求。本项目计划搭建一个智能传媒内容分析与推荐系统，通过新闻内容采集、内容智能分析、用户行为记录、用户画像构建和推荐算法，实现内容管理、内容分析、用户个性化推荐和管理员后台管理等能力。"),
        pp("1.2 文档目的", { hd: HeadingLevel.HEADING_2 }),
        pp("本文档旨在明确智能传媒内容分析与推荐系统的功能需求、非功能需求以及用户故事，为后续系统设计、开发、测试和验收提供依据。文档面向项目团队成员（开发人员、测试人员、项目管理）。"),
        pp("1.3 适用范围", { hd: HeadingLevel.HEADING_2 }),
        pp("本文档适用于智能传媒内容分析与推荐系统第一阶段的开发与实施，覆盖从用户认证、内容管理、智能分析、推荐算法到管理员后台和数据统计的全流程功能范围。"),
        pp("1.4 术语与缩写", { hd: HeadingLevel.HEADING_2 }),
        makeTable([2000, 7026], ["术语", "说明"], [
          ["JWT", "JSON Web Token，用于用户登录认证的令牌机制"],
          ["RSS", "Really Simple Syndication，新闻聚合标准格式"],
          ["CTR", "Click-Through Rate，推荐内容点击率"],
          ["NLP", "Natural Language Processing，自然语言处理"],
          ["CRUD", "Create/Read/Update/Delete，数据基本操作"],
          ["SRS", "Software Requirements Specification，需求规格说明书"],
        ]),

        // ===== 2 =====
        pp("2. 系统概述", { hd: HeadingLevel.HEADING_1 }),
        pp("2.1 系统定位", { hd: HeadingLevel.HEADING_2 }),
        pp("面向新闻、图文、视频、融媒体内容平台的智能内容分析与推荐系统；重点不是普通 CRUD 后台，而是内容分析、用户画像和推荐能力。"),
        pp("2.2 建设目标", { hd: HeadingLevel.HEADING_2 }),
        ni("建立完整的智能传媒内容管理与推荐平台"),
        ni("支持从新闻源采集真实新闻内容，减少系统内容完全依赖模拟数据"),
        ni("支持用户浏览、点赞、收藏等行为记录，并根据行为动态更新用户画像"),
        ni("支持基于用户画像、内容标签、内容热度和内容质量的个性化推荐"),
        ni("支持内容智能分析，包括摘要、关键词、分类、情感和敏感词识别"),
        ni("支持内容审核流程，保证内容发布安全"),
        ni("建立真实可用的管理员后台，支持用户管理、角色权限、账号状态管理和操作日志审计"),
        pp("2.3 技术架构", { hd: HeadingLevel.HEADING_2 }),
        makeTable([2400, 6626], ["层次", "技术选型"], [
          ["前端框架", "Vue 3 + Vite + Element Plus + ECharts"],
          ["后端框架", "Python FastAPI"],
          ["ORM", "SQLAlchemy"],
          ["数据库", "SQLite（可扩展 MySQL/PostgreSQL）"],
          ["认证", "JWT Token"],
          ["文本分析", "jieba、规则算法、scikit-learn"],
          ["推荐算法", "画像匹配 + 内容标签 + 热度质量 + 新鲜度混合推荐"],
          ["新闻采集", "RSS 源采集"],
        ]),
        pp("2.4 用户角色", { hd: HeadingLevel.HEADING_2 }),
        makeTable([1800, 1600, 5626], ["角色", "标识", "权限说明"], [
          ["管理员", "admin", "系统最高权限：用户管理、角色管理、内容审核、新闻采集、操作日志、系统统计"],
          ["编辑", "editor", "内容新增/编辑、新闻采集、内容分析、推荐分析查看"],
          ["审核员", "auditor", "内容审核、行为日志查看、推荐效果查看、部分统计"],
          ["普通用户", "viewer", "浏览内容、点赞、收藏、触发行为记录、查看个人推荐和画像"],
        ]),

        // ===== 3 =====
        new Paragraph({ children: [new PageBreak()] }),
        pp("3. 功能需求", { hd: HeadingLevel.HEADING_1 }),

        pp("3.1 登录认证与权限管理", { hd: HeadingLevel.HEADING_2 }),
        pp("系统需要实现完整的身份认证和基于角色的访问控制（RBAC）。", { b: true }),
        pp("3.1.1 功能描述", { hd: HeadingLevel.HEADING_3 }),
        bi("用户通过账号密码登录系统"),
        bi("登录成功后返回 JWT Token，用于后续接口认证"),
        bi("系统根据用户角色动态展示不同菜单和页面"),
        bi("后端所有敏感接口进行真实权限校验（非仅前端隐藏菜单）"),
        bi("管理员可修改用户角色"),
        bi("管理员可禁用/启用用户账号"),
        bi("被禁用账号不能登录，已有 Token 访问接口也被拦截"),
        pp("3.1.2 接口列表", { hd: HeadingLevel.HEADING_3 }),
        bi("POST /api/auth/login \u2014 用户登录"),
        bi("GET /api/auth/me \u2014 获取当前登录用户信息"),

        pp("3.2 管理员后台", { hd: HeadingLevel.HEADING_2 }),
        pp("管理员后台是系统管理入口，需具备真实管理能力，而非静态展示页面。", { b: true }),
        pp("3.2.1 功能描述", { hd: HeadingLevel.HEADING_3 }),
        bi("系统指标总览（用户数、内容数、待审核数、行为日志数等）"),
        bi("用户数量统计及正常/禁用账号统计"),
        bi("内容总数及状态分布统计"),
        bi("待审核内容数量统计"),
        bi("用户行为日志数量统计"),
        bi("操作审计日志数量统计"),
        bi("角色分布统计"),
        bi("新闻来源分布统计"),
        bi("后台操作日志查询（支持时间范围筛选和关键词搜索）"),
        pp("3.2.2 接口列表", { hd: HeadingLevel.HEADING_3 }),
        bi("GET /api/admin/summary \u2014 管理员后台概览数据"),
        bi("GET /api/admin/logs \u2014 操作审计日志查询"),
        bi("GET /api/admin/roles \u2014 角色选项"),

        pp("3.3 用户管理", { hd: HeadingLevel.HEADING_2 }),
        pp("3.3.1 功能描述", { hd: HeadingLevel.HEADING_3 }),
        bi("查看用户列表（分页）"),
        bi("按用户名或昵称搜索用户"),
        bi("按角色筛选用户"),
        bi("按账号状态（正常/禁用）筛选用户"),
        bi("新增用户"),
        bi("编辑用户基本信息"),
        bi("修改用户角色"),
        bi("禁用/启用用户账号"),
        bi("删除用户"),
        bi("查看用户画像"),
        pp("3.3.2 约束条件", { hd: HeadingLevel.HEADING_3 }),
        bi("管理员不能禁用当前登录的自己的账号"),
        bi("管理员不能将自己的角色降级，以避免系统无管理员可用"),

        pp("3.4 新闻采集", { hd: HeadingLevel.HEADING_2 }),
        pp("系统通过 RSS 新闻源采集真实新闻内容，避免所有内容完全依赖模拟数据。", { b: true }),
        pp("3.4.1 功能描述", { hd: HeadingLevel.HEADING_3 }),
        bi("提供内置新闻源列表"),
        bi("支持用户输入自定义 RSS 地址进行采集"),
        bi("采集新闻标题、摘要、正文、发布时间、来源名称和原文链接"),
        bi("采集后的新闻自动进入内容资产库"),
        bi("采集操作记录到操作审计日志"),
        bi("采集功能仅限管理员和编辑使用"),

        pp("3.5 内容管理", { hd: HeadingLevel.HEADING_2 }),
        pp("3.5.1 功能描述", { hd: HeadingLevel.HEADING_3 }),
        bi("内容列表查看（分页、搜索、筛选）"),
        bi("内容详情查看"),
        bi("新增内容"),
        bi("编辑内容"),
        bi("删除内容（带确认弹窗）"),
        bi("内容封面图或附件上传"),
        bi("内容来源链接展示"),
        bi("内容状态管理（草稿/待审核/已发布/已拒绝/已下架）"),
        pp("3.5.2 内容字段", { hd: HeadingLevel.HEADING_3 }),
        pp("内容核心字段包括：标题、摘要、正文、作者、分类、标签、来源名称、来源链接、内容类型、发布时间、浏览数、点赞数、收藏数、评论数、热度分、质量分、情感倾向、审核状态。"),

        pp("3.6 内容智能分析", { hd: HeadingLevel.HEADING_2 }),
        pp("系统提供基于规则算法和轻量 NLP 的内容智能分析能力，当前阶段以规则和轻量模型为主，保留后续扩展接口。", { b: true }),
        pp("3.6.1 分析能力", { hd: HeadingLevel.HEADING_3 }),
        bi("自动摘要：取正文前 100-200 字，或按关键词匹配句子权重生成"),
        bi("关键词提取：使用 jieba.analyse.extract_tags 或 TF-IDF"),
        bi("分类识别：根据关键词规则识别科技、财经、体育、娱乐、社会等类别"),
        bi("情感分析：positive / neutral / negative 三分类"),
        bi("敏感词识别：基于敏感词词典匹配"),
        bi("热度分计算：view_count x 0.4 + like_count x 2 + favorite_count x 3 + comment_count x 2.5"),
        bi("质量分计算：综合标题长度、正文长度、摘要、标签、封面图、互动数据等"),
        bi("相似内容推荐：基于关键词、分类和标签的相似度计算"),

        pp("3.7 内容审核", { hd: HeadingLevel.HEADING_2 }),
        pp("3.7.1 功能描述", { hd: HeadingLevel.HEADING_3 }),
        bi("查看待审核内容列表"),
        bi("查看敏感词命中结果"),
        bi("审核通过"),
        bi("审核拒绝（需填写审核意见）"),
        bi("内容下架"),
        bi("记录审核人和审核时间"),
        bi("管理员和审核员可审核，编辑不能直接审核发布"),

        pp("3.8 用户行为记录", { hd: HeadingLevel.HEADING_2 }),
        pp("3.8.1 行为类型与权重", { hd: HeadingLevel.HEADING_3 }),
        makeTable([2000, 1500, 2000, 3526], ["行为", "标识", "画像权重", "说明"], [
          ["浏览", "view", "+1", "记录内容浏览行为"],
          ["点赞", "like", "+3", "增加对应标签权重"],
          ["收藏", "favorite", "+5", "较高权重增加"],
          ["评论", "comment", "+4", "较高权重增加"],
          ["分享", "share", "+4", "较高权重增加"],
          ["不喜欢", "dislike", "-5", "降低对应标签权重"],
        ]),

        pp("3.9 用户画像", { hd: HeadingLevel.HEADING_2 }),
        pp("用户画像必须由用户行为驱动动态更新，不能完全静态填写。", { b: true }),
        pp("3.9.1 画像内容", { hd: HeadingLevel.HEADING_3 }),
        bi("用户基本信息（昵称、年龄、性别、城市）"),
        bi("兴趣标签权重（正面）"),
        bi("负向兴趣标签"),
        bi("分类偏好分布"),
        bi("行为类型统计（浏览/点赞/收藏/评论/分享/不感兴趣）"),
        bi("最近浏览/互动内容列表"),
        bi("活跃分"),
        bi("最近活跃时间"),

        pp("3.10 个性化推荐", { hd: HeadingLevel.HEADING_2 }),
        pp("3.10.1 推荐策略", { hd: HeadingLevel.HEADING_3 }),
        bi("热门推荐：按 heat_score 降序排列"),
        bi("个性化推荐：基于用户画像兴趣标签匹配内容标签"),
        bi("相似内容推荐：基于关键词、分类和标签的相似度"),
        bi("混合推荐：综合多策略排序"),
        bi("冷启动推荐：对新用户推荐热门 + 最新 + 人工精选内容"),
        bi("多样性调整：推荐列表不全部来自同一分类"),
        pp("3.10.2 推荐排序公式", { hd: HeadingLevel.HEADING_3 }),
        pp("综合分 = 标签匹配分 x 0.45 + 热度分 x 0.25 + 质量分 x 0.20 + 新鲜度分 x 0.10"),
        pp("", { b4: 30, af: 30 }),
        pp("注意：已浏览内容降低权重或过滤；用户不感兴趣的标签降低推荐分；推荐结果须返回推荐原因。", { b: true }),
        pp("3.10.3 推荐接口", { hd: HeadingLevel.HEADING_3 }),
        bi("GET /api/recommendations/hot \u2014 热门推荐"),
        bi("GET /api/recommendations/user/{user_id} \u2014 用户个性化推荐"),
        bi("GET /api/recommendations/content/{content_id} \u2014 相似内容推荐"),
        bi("GET /api/recommendations/mixed/{user_id} \u2014 混合推荐"),
        bi("GET /api/recommendations/analytics/summary \u2014 推荐效果分析"),

        pp("3.11 数据统计与可视化", { hd: HeadingLevel.HEADING_2 }),
        bi("内容总数统计"),
        bi("用户总数统计"),
        bi("用户行为趋势"),
        bi("热门内容 Top 10 排行"),
        bi("推荐曝光量 / 推荐点击量 / CTR 点击率"),
        bi("内容分类分布"),
        bi("用户活跃度排行"),
        bi("前端使用 ECharts 绘制趋势图、柱状图、饼图"),

        pp("3.12 文件上传", { hd: HeadingLevel.HEADING_2 }),
        bi("支持上传内容相关文件（封面图、附件）"),
        bi("文件存储在项目目录 backend/uploads/ 内"),
        bi("上传接口需要权限控制（管理员和编辑可上传）"),

        // ===== 4 =====
        new Paragraph({ children: [new PageBreak()] }),
        pp("4. 非功能需求", { hd: HeadingLevel.HEADING_1 }),

        pp("4.1 易用性", { hd: HeadingLevel.HEADING_2 }),
        bi("页面结构清晰，功能入口明确"),
        bi("不同角色看到的菜单和功能入口不同"),
        bi("前端视觉风格偏向数据分析平台，使用蓝色、白色、浅灰为主色调"),
        bi("采用卡片式布局，图表直观"),
        bi("表格操作清晰，具备搜索和筛选能力"),

        pp("4.2 安全性", { hd: HeadingLevel.HEADING_2 }),
        bi("所有重要接口必须登录后访问"),
        bi("管理员接口必须限制管理员角色才能访问"),
        bi("操作日志需要记录关键后台操作（用户管理、内容审核、新闻采集等）"),
        bi("禁用账号后应立即无法继续使用系统（包括已有 Token）"),
        bi("后端权限控制必须真实有效，不能只依赖前端菜单隐藏"),
        bi("密码使用哈希存储，不存明文"),

        pp("4.3 可维护性", { hd: HeadingLevel.HEADING_2 }),
        bi("后端采用 API - Service - Model 分层架构"),
        bi("前端采用 views - api - router - store 分层结构"),
        bi("推荐算法和内容分析算法独立存放于 algorithms 目录"),
        bi("数据库结构便于后续扩展为 MySQL/PostgreSQL"),
        bi("代码需包含必要注释，命名清晰"),

        pp("4.4 可扩展性", { hd: HeadingLevel.HEADING_2 }),
        bi("推荐算法采用策略模式，便于添加新推荐策略"),
        bi("内容分析模块预留大模型 API 接入接口"),
        bi("数据库支持从 SQLite 平滑迁移至 MySQL/PostgreSQL"),
        bi("支持新增用户角色和权限配置"),

        pp("4.5 部署与环境要求", { hd: HeadingLevel.HEADING_2 }),
        bi("Python 虚拟环境放在项目目录内 (backend/.venv/)"),
        bi("SQLite 数据库放在项目目录内 (backend/data/)"),
        bi("前端依赖 node_modules 放在项目目录内 (frontend/node_modules/)"),
        bi("提供一键初始化脚本和启动脚本"),
        bi("提供完整 README 说明启动和使用方式"),
        bi("运行环境：Windows 10/11, Python 3.10+, Node.js 18+"),

        pp("4.6 API 规范", { hd: HeadingLevel.HEADING_2 }),
        bi('所有接口统一返回 JSON 格式：{ "code": 0, "message": "success", "data": {} }'),
        bi('分页接口返回：{ "code": 0, "data": { "items": [], "total": N, "page": M, "page_size": K } }'),
        bi('错误返回：{ "code": 400, "message": "错误描述", "data": null }'),
        bi("异常处理需完善，避免接口崩溃时返回 HTML 或堆栈信息"),

        // ===== 5 =====
        new Paragraph({ children: [new PageBreak()] }),
        pp("5. 用户故事", { hd: HeadingLevel.HEADING_1 }),

        pp("5.1 管理员 (admin)", { hd: HeadingLevel.HEADING_2 }),
        storyTable([1200, 3800, 4026], ["编号", "用户故事", "验收标准"], [
          ["US-01", "作为管理员，我想要查看系统总览数据看板，以便快速了解平台的用户规模、内容数量和审核状态。", "首页展示用户总数、内容总数、待审核数和行为日志数等关键指标；数据与实际一致。"],
          ["US-02", "作为管理员，我想要管理所有用户账号（新增、编辑、禁用、删除），以便控制平台访问权限。", "可新增用户并设定角色；可禁用用户，被禁用用户无法登录和访问接口。"],
          ["US-03", "作为管理员，我想要查看用户的角色分布和账号状态统计，以便了解团队构成和系统活跃度。", "可看到各角色人数和正常/禁用账号数量。"],
          ["US-04", "作为管理员，我想要查看后台操作审计日志，以便追溯关键操作的执行人和时间。", "日志包含操作人、操作类型、操作对象、时间；支持按时间筛选。"],
        ]),

        pp("5.2 编辑 (editor)", { hd: HeadingLevel.HEADING_2 }),
        storyTable([1200, 3800, 4026], ["编号", "用户故事", "验收标准"], [
          ["US-05", "作为编辑，我想要新增和编辑新闻内容，以便丰富平台的内容库。", "可填写标题、正文、分类、标签等信息并保存；编辑后内容实时更新。"],
          ["US-06", "作为编辑，我想要从 RSS 新闻源采集新闻，以便快速获取真实资讯内容。", "输入 RSS 地址后可采集新闻；支持内置新闻源和自定义 URL。"],
          ["US-07", "作为编辑，我想要对内容执行一键智能分析，以便自动生成摘要、关键词、分类和情感判断。", "分析后返回摘要、关键词、分类、情感倾向、热度分和质量分。"],
          ["US-08", "作为编辑，我想要查看推荐效果分析数据，以便了解哪些内容受到用户欢迎。", "可查看推荐曝光量、点击量和 CTR 数据。"],
        ]),

        pp("5.3 审核员 (auditor)", { hd: HeadingLevel.HEADING_2 }),
        storyTable([1200, 3800, 4026], ["编号", "用户故事", "验收标准"], [
          ["US-09", "作为审核员，我想要查看待审核内容列表，以便对提交的内容进行审核。", "列表显示待审核内容，展示标题、作者、分类和敏感词命中情况。"],
          ["US-10", "作为审核员，我想要审核通过或拒绝内容并填写审核意见，以便保证平台内容质量和安全。", "通过后内容变为已发布状态；拒绝时填写审核意见；记录审核人和审核时间。"],
          ["US-11", "作为审核员，我想要下架已发布的内容，以便移除不当或过时内容。", "下架后内容不再对普通用户展示；操作记录可追溯。"],
        ]),

        pp("5.4 普通用户 (viewer)", { hd: HeadingLevel.HEADING_2 }),
        storyTable([1200, 3800, 4026], ["编号", "用户故事", "验收标准"], [
          ["US-12", "作为普通用户，我想要浏览新闻内容并查看详情，以便获取感兴趣的信息。", "可按分类筛选内容；点击标题进入详情页查看完整内容。"],
          ["US-13", "作为普通用户，我想要对内容点赞、收藏或表示不感兴趣，以便表达偏好并获得更好的推荐。", "点击操作按钮后，对应行为被记录，内容互动数更新。"],
          ["US-14", "作为普通用户，我想要查看系统为我生成的个性化推荐，以便发现可能感兴趣的新闻内容。", "推荐列表包含推荐原因（如'因为你喜欢科技'）；不显示已浏览内容。"],
          ["US-15", "作为普通用户，我想要查看自己的用户画像，以便了解系统如何理解我的兴趣偏好。", "画像页面展示兴趣标签权重、分类偏好、行为统计和最近互动内容。"],
        ]),

        // ===== 6 =====
        new Paragraph({ children: [new PageBreak()] }),
        pp("6. 功能优先级", { hd: HeadingLevel.HEADING_1 }),

        pp("6.1 P0 \u2014 必须完成", { hd: HeadingLevel.HEADING_2 }),
        bi("后端 FastAPI 基础框架"),
        bi("数据库模型（内容、用户、行为、分类、标签）"),
        bi("内容管理 API（增删改查）"),
        bi("内容分析基础能力（摘要、关键词、分类、情感）"),
        bi("推荐 API（热门推荐、个性化推荐）"),
        bi("Vue 前端基础布局"),
        bi("内容管理页面"),
        bi("推荐结果页面"),

        pp("6.2 P1 \u2014 应该完成", { hd: HeadingLevel.HEADING_2 }),
        bi("用户画像生成与展示"),
        bi("用户行为日志记录"),
        bi("首页数据仪表盘"),
        bi("ECharts 图表（趋势图、分类分布、推荐效果）"),
        bi("数据初始化脚本"),

        pp("6.3 P2 \u2014 可后续增强", { hd: HeadingLevel.HEADING_2 }),
        bi("JWT 登录认证（已提前实现）"),
        bi("视频内容智能分析"),
        bi("深度学习推荐模型"),
        bi("Elasticsearch 全文搜索"),
        bi("Redis 缓存层"),
        bi("Kafka / Flink 实时行为处理"),
        bi("A/B 测试框架"),

        // ===== 7 =====
        pp("7. 系统验收标准", { hd: HeadingLevel.HEADING_1 }),
        makeTable([1200, 5200, 2626], ["编号", "验收项", "负责人"], [
          ["AC-01", "后端服务可正常启动，/docs 可访问，核心 API 返回统一 JSON 格式", "朱自豪"],
          ["AC-02", "前端服务可正常启动，核心页面可访问，菜单随角色动态变化", "秦梓洋"],
          ["AC-03", "内容可新增、编辑、删除、查询，支持分页和筛选", "朱自豪"],
          ["AC-04", "内容可执行一键智能分析，返回摘要、关键词、分类和情感结果", "朱自豪"],
          ["AC-05", "用户行为可记录（浏览/点赞/收藏/评论/不喜欢），行为影响内容互动数", "朱自豪"],
          ["AC-06", "用户画像可根据行为动态更新，展示兴趣标签权重和分类偏好", "朱自豪"],
          ["AC-07", "可根据用户画像生成个性化推荐结果，每条推荐包含推荐原因", "朱自豪"],
          ["AC-08", "首页仪表盘展示关键指标卡片和 ECharts 图表", "秦梓洋"],
          ["AC-09", "管理员后台具备真实的用户管理、角色管理和操作日志查询能力", "朱自豪"],
          ["AC-10", "项目 README 清楚说明启动步骤、演示账号、功能说明和已知问题", "王淦"],
        ]),

        // ===== 8 =====
        pp("8. 附录", { hd: HeadingLevel.HEADING_1 }),
        pp("8.1 参考文档", { hd: HeadingLevel.HEADING_2 }),
        bi("智能传媒内容分析与推荐系统 AI Coding 开发提示词"),
        bi("第013组项目需求初步讨论会议纪要"),
        bi("智能传媒内容分析与推荐系统 README.md"),
        bi("智能传媒内容分析与推荐系统_14天项目计划"),
        pp("8.2 待确认问题", { hd: HeadingLevel.HEADING_2 }),
        ni("新闻源是否固定，还是需要管理员后台维护新闻源"),
        ni("是否需要支持定时自动采集新闻"),
        ni("是否需要评论内容管理和评论审核"),
        ni("推荐算法是否需要加入 A/B 测试"),
        ni("是否需要支持多租户或多组织管理"),
        ni("是否需要导出统计报表"),
        ni("是否需要接入真实大模型 API 进行摘要和分类"),
        ni("是否需要部署到服务器并支持公网访问"),
        new Paragraph({ spacing: { before: 400 }, children: [] }),
        pp("\u2014\u2014 文档结束 \u2014\u2014", { ct: true, cl: "808080", sz: 18 }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(out, buf);
  console.log("OK:", out);
});
