const TOKEN_SECRET = "geo-demo-token-secret";
const NOW = "2026-08-30T22:00:00+08:00";

const USERS = {
  admin: { id: "u-admin", username: "admin", role: "ADMIN", display_name: "系统管理员" },
  manager: { id: "u-manager", username: "manager", role: "MANAGER", display_name: "项目负责人" },
  member: { id: "u-member", username: "member", role: "MEMBER", display_name: "执行人员" },
  client: { id: "u-client", username: "client", role: "CLIENT", display_name: "客户查看" },
};

const PASSWORDS = {
  admin: "admin123",
  manager: "manager123",
  member: "member123",
  client: "client123",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}

function error(detail, status) {
  return json({ detail }, status);
}

async function readBody(request) {
  try {
    return await request.json();
  } catch {
    return {};
  }
}

async function readForm(request) {
  try {
    return await request.formData();
  } catch {
    return new FormData();
  }
}

function tokenFor(user) {
  return btoa(JSON.stringify({ sub: user.id, name: user.username, secret: TOKEN_SECRET }));
}

function userFromToken(token) {
  if (!token) {
    return null;
  }
  try {
    const payload = JSON.parse(atob(token));
    if (payload.secret !== TOKEN_SECRET || !USERS[payload.name]) {
      return null;
    }
    return USERS[payload.name];
  } catch {
    return null;
  }
}

function requireUser(request) {
  const header = request.headers.get("Authorization") || "";
  const token = header.replace(/^Bearer\s+/i, "");
  return userFromToken(token);
}

const businessLines = [
  {
    business_name: "自动开箱机解决方案",
    products: ["自动开箱机"],
    target_customers: ["食品企业", "物流企业", "制造企业"],
    customer_problems: ["人工开箱效率低", "开箱破损率偏高", "开箱环节与产线衔接不顺畅"],
    buying_intent: ["采购自动开箱机", "自动开箱机厂家", "自动开箱机报价", "自动开箱机供应商"],
    keywords_direction: ["自动开箱机", "自动开箱机厂家", "自动开箱机解决方案", "自动开箱机定制", "自动开箱机案例"],
    content_direction: ["自动开箱机选型指南", "自动开箱机实施案例", "自动开箱机常见问题"],
  },
  {
    business_name: "自动包装设备解决方案",
    products: ["自动包装设备"],
    target_customers: ["食品企业", "物流企业", "制造企业"],
    customer_problems: ["人工包装成本高", "包装规格切换慢", "包装质量一致性不足"],
    buying_intent: ["采购自动包装设备", "自动包装设备厂家", "自动包装设备报价", "自动包装设备供应商"],
    keywords_direction: ["自动包装设备", "自动包装设备厂家", "自动包装设备解决方案", "自动包装设备定制", "自动包装设备案例"],
    content_direction: ["自动包装设备选型指南", "自动包装设备实施案例", "自动包装设备常见问题"],
  },
  {
    business_name: "自动化包装生产线解决方案",
    products: ["自动化包装生产线"],
    target_customers: ["食品企业", "物流企业", "制造企业"],
    customer_problems: ["整线自动化程度不足", "多设备协同困难", "产线升级周期长"],
    buying_intent: ["采购自动化包装生产线", "自动化包装生产线厂家", "自动化包装生产线报价", "自动化包装生产线供应商"],
    keywords_direction: ["自动化包装生产线", "自动化包装生产线厂家", "自动化包装生产线解决方案", "自动化包装生产线定制", "自动化包装生产线案例"],
    content_direction: ["自动化包装生产线选型指南", "自动化包装生产线实施案例", "自动化包装生产线常见问题"],
  },
];

function buildKeywords() {
  const keywords = [
    { keyword: "邦胜工业设备有限公司", type: "品牌词", intent: "品牌认知", priority: "A", business_line: "企业品牌", customer_type: "全客户", search_stage: "认知" },
    { keyword: "邦胜工业设备", type: "品牌词", intent: "品牌认知", priority: "A", business_line: "企业品牌", customer_type: "全客户", search_stage: "认知" },
    { keyword: "邦胜工业设备 工业自动化设备", type: "品牌词", intent: "品牌检索", priority: "A", business_line: "企业品牌", customer_type: "全客户", search_stage: "认知" },
  ];
  const patterns = [
    ["业务词", "采购决策", "A", "决策"],
    ["业务词", "采购决策", "A", "对比"],
    ["问答词", "信息了解", "B", "需求"],
    ["问答词", "价格对比", "A", "对比"],
    ["场景词", "场景需求", "A", "需求"],
    ["场景词", "场景需求", "A", "需求"],
    ["长尾词", "高意向采购", "A", "决策"],
    ["长尾词", "信任建立", "B", "决策"],
    ["业务词", "方案咨询", "B", "需求"],
    ["业务词", "方案咨询", "B", "需求"],
    ["业务词", "方案咨询", "B", "需求"],
  ];
  businessLines.forEach((line, index) => {
    const key = line.products[0];
    const patternsForLine = [
      [key, "业务词", "采购决策", "A", "决策"],
      [`${key}厂家`, "业务词", "采购决策", "A", "对比"],
      [`${key}怎么选`, "问答词", "信息了解", "B", "需求"],
      [`${key}多少钱`, "问答词", "价格对比", "A", "对比"],
      [`食品企业${key}`, "场景词", "场景需求", "A", "需求"],
      [`物流企业${key}`, "场景词", "场景需求", "A", "需求"],
      [`支持定制的${key}厂家`, "长尾词", "高意向采购", "A", "决策"],
      [`${key}解决方案客户案例`, "长尾词", "信任建立", "B", "决策"],
      [`${key}解决方案`, "业务词", "方案咨询", "B", "需求"],
      [`${key}定制`, "业务词", "方案咨询", "B", "需求"],
      [`${key}案例`, "业务词", "方案咨询", "B", "需求"],
    ];
    patternsForLine.forEach(([keyword, type, intent, priority, searchStage]) => {
      keywords.push({
        keyword,
        type,
        intent,
        priority,
        business_line: line.business_name,
        customer_type: index % 2 === 0 ? "食品企业" : "物流企业",
        search_stage: searchStage,
      });
    });
  });
  return keywords;
}

const personas = [
  {
    role: "老板",
    focus: ["投入产出", "市场竞争力", "品牌增长"],
    pain_points: ["获客依赖老客户", "品牌在AI搜索中不明显", "同行竞争加剧"],
    search_behavior: ["搜索行业趋势", "搜索知名厂家", "比较解决方案"],
    decision_factors: ["团队实力", "案例背书", "长期服务能力"],
    content_needs: ["企业实力内容", "行业案例", "差异化优势"],
  },
  {
    role: "采购负责人",
    focus: ["价格", "交期", "供应商可靠性"],
    pain_points: ["供应商报价不透明", "设备选型风险高", "售后保障不明"],
    search_behavior: ["搜索厂家", "搜索报价", "搜索采购注意事项"],
    decision_factors: ["资质", "案例", "报价", "交付周期"],
    content_needs: ["FAQ", "报价指南", "厂家对比", "客户案例"],
  },
  {
    role: "技术负责人",
    focus: ["设备稳定性", "技术参数", "产线兼容性"],
    pain_points: ["自动化方案落地难", "设备与现有产线兼容差", "定制需求沟通成本高"],
    search_behavior: ["搜索技术方案", "搜索设备参数", "搜索实施案例"],
    decision_factors: ["技术能力", "定制能力", "现场实施经验"],
    content_needs: ["自动开箱机、自动包装设备、自动化包装生产线技术解析", "解决方案", "技术白皮书"],
  },
  {
    role: "实际使用人员",
    focus: ["操作便捷", "故障率", "培训支持"],
    pain_points: ["设备操作复杂", "故障处理慢", "培训资料不足"],
    search_behavior: ["搜索操作教程", "搜索常见故障", "搜索保养方法"],
    decision_factors: ["易用性", "稳定性", "售后服务"],
    content_needs: ["操作指南", "FAQ", "维护保养内容"],
  },
];

const contentDirections = [
  { direction: "官网文章", content_topic: "自动开箱机选型指南与厂家实力解析", target_keyword: "自动开箱机", target_user: "老板", publish_suggestion: "发布到官网行业文章栏目，并同步AI搜索优化" },
  { direction: "官网文章", content_topic: "工业自动化设备如何做自动化升级", target_keyword: "自动开箱机怎么选", target_user: "采购负责人", publish_suggestion: "官网方案中心重点展示" },
  { direction: "FAQ", content_topic: "自动开箱机怎么选？", target_keyword: "自动开箱机怎么选", target_user: "采购负责人", publish_suggestion: "官网FAQ页面并形成问答结构化数据" },
  { direction: "案例", content_topic: "食品与物流行业食品企业自动开箱机实施案例", target_keyword: "食品企业自动开箱机", target_user: "技术负责人", publish_suggestion: "案例页面加入数据、图片和客户见证" },
  { direction: "长尾内容", content_topic: "支持定制的自动开箱机厂家服务介绍", target_keyword: "支持定制的自动开箱机厂家", target_user: "实际使用人员", publish_suggestion: "官网新闻与第三方行业平台同步发布" },
];

function buildContentPlan() {
  return Array.from({ length: 30 }, (_, index) => {
    const item = contentDirections[index % contentDirections.length];
    return {
      "日期": `Day ${index + 1}`,
      "内容主题": `第${index + 1}天：${item.content_topic}`,
      "目标关键词": item.target_keyword,
      "目标用户": item.target_user,
      "发布建议": item.publish_suggestion,
    };
  });
}

const priorityActions = [
  { priority: "P1", action: "官网首页与产品页补齐企业定位、产品卖点和案例证据", reason: "品牌词和业务词决定AI回答中第一轮品牌曝光", related_keywords: ["邦胜工业设备有限公司", "邦胜工业设备", "自动开箱机", "自动开箱机厂家"], target_users: ["老板", "采购负责人"], content_needed: "企业定位文案、产品介绍、客户证据页", expected_value: "提高品牌词和核心业务词被AI推荐的概率" },
  { priority: "P1", action: "建设FAQ与结构化问答内容", reason: "采购和选型阶段常以问答方式检索，结构化内容更容易被引用", related_keywords: ["自动开箱机怎么选", "自动开箱机多少钱", "自动包装设备怎么选", "自动化包装生产线多少钱"], target_users: ["采购负责人", "技术负责人"], content_needed: "FAQ页面、问答结构化数据、价格与选型说明", expected_value: "覆盖采购决策期的AI问答检索" },
  { priority: "P1", action: "发布3条业务线客户案例", reason: "场景词和信任类长尾词需要真实案例作为可引用证据", related_keywords: ["食品企业自动开箱机", "物流企业自动开箱机", "食品企业自动包装设备", "物流企业自动包装设备"], target_users: ["老板", "技术负责人"], content_needed: "食品、物流、制造行业案例内容", expected_value: "增强品牌在方案对比场景中的可信度" },
  { priority: "P2", action: "为每条业务线建立专题页面", reason: "独立业务专题可以承接不同搜索意图，提升内容相关性", related_keywords: ["食品企业自动开箱机", "物流企业自动开箱机", "食品企业自动化包装生产线"], target_users: ["采购负责人", "技术负责人"], content_needed: "业务线介绍、技术参数、定制流程、案例入口", expected_value: "让每条业务线都有可被AI抓取的专题页面" },
  { priority: "P2", action: "执行30天内容计划，首批完成4个核心主题", reason: "持续更新是扩大AI搜索覆盖的基础动作", related_keywords: ["支持定制的自动开箱机厂家", "自动开箱机解决方案客户案例", "支持定制的自动包装设备厂家"], target_users: ["采购负责人", "技术负责人"], content_needed: "30天官网文章、FAQ和案例内容", expected_value: "形成稳定的内容输出和关键词覆盖节奏" },
  { priority: "P2", action: "统一官网元信息、品牌资料和第三方平台企业信息", reason: "品牌信息一致性能提高AI对企业的识别置信度", related_keywords: ["邦胜工业设备有限公司", "邦胜工业设备"], target_users: ["老板"], content_needed: "官网Title/Description、公司简介、资质证书", expected_value: "降低品牌信息冲突，增强GEO证据一致性" },
  { priority: "P3", action: "建立AI搜索可见度监测与验证机制", reason: "只有持续监测ChatGPT、Claude、Gemini等回答，才能判断GEO策略效果", related_keywords: ["品牌出现率", "竞品出现率", "推荐理由"], target_users: ["项目负责人"], content_needed: "GEO验证问题集、月度监测记录", expected_value: "形成可量化的GEO可见度评分" },
  { priority: "P3", action: "持续沉淀行业研究、竞品对比和长尾内容", reason: "AI搜索更倾向于引用有数据、有对比、有行业深度的内容", related_keywords: ["自动开箱机", "自动包装设备", "自动化包装生产线"], target_users: ["技术负责人", "行业客户"], content_needed: "行业趋势、竞品对比、技术白皮书", expected_value: "扩大非品牌词的长期搜索覆盖" },
  { priority: "P3", action: "把客户成功数据转化为可引用的GEO证据", reason: "真实效率、案例数据比营销语言更可能被AI引用", related_keywords: ["客户案例数据", "自动化效率提升", "设备交期案例"], target_users: ["老板", "采购负责人"], content_needed: "客户证言、效率数据、现场图片与视频", expected_value: "建立长期差异化品牌证据池" },
];

const demoAnalysis = {
  customer_profile: {
    task: "customer_profile",
    status: "success",
    result: {
      name: "邦胜工业设备有限公司",
      website: "sdhdktsb.com",
      industry: "工业自动化设备",
      products: ["自动开箱机", "自动包装设备", "自动化包装生产线"],
      services: ["自动化包装解决方案"],
      advantages: ["多年制造经验", "支持定制", "行业案例丰富"],
      cases: ["食品行业", "物流行业"],
      customers: ["食品企业", "物流企业", "制造企业"],
    },
  },
  company_profile: {
    task: "company_analysis",
    status: "success",
    confidence: 100,
    result: {
      company_name: "邦胜工业设备有限公司",
      company_positioning: "邦胜工业设备有限公司专注于工业自动化设备领域，主营自动开箱机、自动包装设备、自动化包装生产线，并提供自动化包装解决方案",
      industry: "工业自动化设备",
      products: ["自动开箱机", "自动包装设备", "自动化包装生产线"],
      services: ["自动化包装解决方案"],
      target_customers: ["食品企业", "物流企业", "制造企业"],
      advantages: ["多年制造经验", "支持定制", "行业案例丰富"],
      customer_pain_points: ["产线效率低", "人工成本高", "设备兼容性差", "定制需求响应慢"],
      evidence: ["官网：sdhdktsb.com", "客户案例：食品企业、物流企业、制造企业"],
    },
    next_action: "business_analysis",
  },
  business_analysis: { business_lines: businessLines },
  keywords: {
    task: "keyword_analysis",
    status: "success",
    result: { keywords: buildKeywords() },
    next_action: "persona_analysis",
  },
  personas: {
    task: "persona_analysis",
    status: "success",
    result: { personas },
    next_action: "content_planning",
  },
  content_plan: {
    task: "content_planning",
    status: "success",
    result: {
      content_directions: contentDirections,
      faq_list: ["自动开箱机怎么选？", "自动开箱机多少钱？", "自动包装设备怎么选？", "自动化包装生产线多少钱？"],
      case_list: ["食品企业自动开箱机客户案例", "物流企业自动开箱机客户案例", "食品企业自动包装设备客户案例", "物流企业自动化包装生产线客户案例"],
      plan: buildContentPlan(),
    },
    next_action: "strategy_planning",
  },
  strategy_plan: {
    summary: "围绕邦胜工业设备有限公司的3条业务线，先补齐品牌、问答和案例三类GEO基础，再通过30天内容计划持续扩大AI搜索中的可见度。",
    priority_actions: priorityActions,
    "30_day_plan": [
      { week: "第1周", tasks: ["发布企业定位与核心产品页内容", "完成FAQ问题清单并上线结构化问答", "启动3条业务线案例内容框架"] },
      { week: "第2周", tasks: ["发布业务词选型指南和厂家对比内容", "补齐关键词矩阵中的A级高价值主题", "统一官网元信息与品牌资料"] },
      { week: "第3周", tasks: ["发布食品、物流、制造行业场景案例", "围绕采购和技术画像输出决策型内容", "同步第三方行业平台与官网内容"] },
      { week: "第4周", tasks: ["完成30天内容计划第一轮复盘", "建立AI搜索可见度验证问题集", "输出下一周期关键词与内容优化清单"] },
    ],
  },
  monitor_report: {
    task: "geo_monitoring",
    status: "success",
    confidence: 85,
    result: {
      project_name: "邦胜工业设备有限公司",
      keyword_count: buildKeywords().length,
      content_count: 17,
      persona_count: personas.length,
      priority_action_count: priorityActions.length,
      optimization_suggestions: ["增加官网文章、FAQ、案例和知乎问题的内容覆盖。"],
      next_actions: ["启动30天内容计划，优先发布P1关键词相关内容。", "官网首页与产品页补齐企业定位、产品卖点和案例证据", "建设FAQ与结构化问答内容", "发布3条业务线客户案例", "每月运行GEO验证，检查AI搜索中的品牌出现率与推荐原因。"],
      monitor_summary: `当前已生成 ${buildKeywords().length} 个GEO关键词、17 个内容方向、${personas.length} 类用户画像和 ${priorityActions.length} 个策略动作，建议按P1动作优先落地内容与验证。`,
    },
    next_action: "score_evaluation",
  },
  geo_score: {
    task: "geo_score",
    status: "success",
    confidence: 100,
    result: {
      score: 88,
      level: "good",
      dimensions: {
        enterprise_info_completeness: 90,
        keyword_coverage: 92,
        content_coverage: 86,
        persona_completeness: 90,
        ai_recommendation_foundation: 82,
      },
      recommendations: ["优先补齐官网FAQ和案例证据页", "按P1动作完成核心业务词内容覆盖", "建立AI搜索可见度月度验证机制"],
    },
    next_action: "report_generation",
  },
};

const outputFiles = [
  "keyword_matrix.xlsx",
  "persona_report.docx",
  "content_plan.xlsx",
  "GEO客户分析报告.docx",
  "GEO客户分析报告.pdf",
  "customer_profile.json",
  "company_profile.json",
  "business_analysis.json",
  "keywords.json",
  "personas.json",
  "content_plan.json",
  "strategy_plan.json",
  "monitor_report.json",
  "geo_score.json",
];

function buildProject(taskId = "bf70d93a58e7", options = {}) {
  return {
    project_id: taskId,
    id: taskId,
    task_id: taskId,
    status: options.status || "COMPLETED",
    customer_name: options.customer_name || "邦胜工业设备有限公司",
    website: options.website || "sdhdktsb.com",
    industry: options.industry || "工业自动化设备",
    owner: options.owner || "admin",
    output_dir: `/mock/reports/${taskId}`,
    output_files: outputFiles.map((file) => `/mock/reports/${taskId}/${file}`),
    files: outputFiles.map((file) => `/mock/reports/${taskId}/${file}`),
    reports: ["GEO客户分析报告.docx", "GEO客户分析报告.pdf", "persona_report.docx"].map((file) => `/mock/reports/${taskId}/${file}`),
    error_message: "",
    message: "",
    created_time: options.created_time || NOW,
    updated_time: NOW,
    created_at: options.created_time || NOW,
    updated_at: NOW,
  };
}

function buildProjectDetail(taskId) {
  const project = buildProject(taskId);
  return { ...project, analysis: demoAnalysis };
}

function projectsPayload() {
  const projects = [
    buildProject("bf70d93a58e7"),
    buildProject("7e2dddaa025e", { created_time: "2026-08-30T14:38:00+08:00" }),
    buildProject("a1c3f9d2b8e7", {
      customer_name: "云岭食品科技有限公司",
      industry: "食品生产与包装",
      status: "ANALYZING",
      created_time: "2026-08-30T21:30:00+08:00",
    }),
  ];
  const keywordCount = buildKeywords().length;
  return {
    projects,
    stats: {
      total: projects.length,
      completed: 2,
      processing: 1,
      failed: 0,
      keyword_count: keywordCount,
      report_count: 5,
      avg_geo_score: 88,
    },
  };
}

function samplePdf() {
  const lines = [
    "GEO Production System",
    "Customer Delivery Report - Demo",
    "Bang Sheng Industrial Equipment Co., Ltd.",
    "Industry: Industrial Automation Equipment",
    "GEO Score: 88/100",
  ];
  const text = lines.map((line) => `BT /F1 14 Tf 60 760 Td (${line.replace(/[()\\]/g, "")}) Tj ET`).join("\n");
  return new TextEncoder().encode(
    `%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n4 0 obj<</Length ${text.length}>>stream\n${text}\nendstream\nendobj\n5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000271 00000 n \n0000000433 00000 n \ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n0\n%%EOF\n`
  );
}

function fileResponse(name, contentType, body, dispositionName) {
  return new Response(body, {
    status: 200,
    headers: {
      "Content-Type": contentType,
      "Content-Disposition": `attachment; filename="${encodeURIComponent(dispositionName || name)}"`,
      "Cache-Control": "no-store",
    },
  });
}

function route(request, pathname) {
  const method = request.method.toUpperCase();
  const path = pathname.replace(/^\/api/, "");

  if (method === "GET" && path === "/health") {
    return json({ status: "running", service: "geo-production-system", version: "2.2.0" });
  }

  if (method === "POST" && path === "/login") {
    return readBody(request).then((payload) => {
      const user = USERS[payload.username];
      if (!user || PASSWORDS[payload.username] !== payload.password) {
        return error("invalid username or password", 401);
      }
      return json({ token: tokenFor(user), token_type: "bearer", user });
    });
  }

  const user = requireUser(request);
  if (!user) {
    return error("authentication required", 401);
  }

  if (method === "GET" && path === "/users/me") {
    return json(user);
  }

  if (method === "GET" && path === "/projects") {
    return json(projectsPayload());
  }

  if (method === "POST" && path === "/projects/create") {
    return readForm(request).then((form) => {
      const customerName = String(form.get("customer_name") || "").trim() || "未命名客户";
      const taskId = "demo-" + Math.random().toString(16).slice(2, 8);
      const project = buildProject(taskId, {
        customer_name: customerName,
        website: String(form.get("website") || ""),
        industry: String(form.get("industry") || ""),
        status: "ANALYZING",
      });
      return json(project, 201);
    });
  }

  const downloadMatch = path.match(/^\/projects\/([^/]+)\/download\/([^/]+)$/);
  if (method === "GET" && downloadMatch) {
    const filename = decodeURIComponent(downloadMatch[2]);
    if (filename.toLowerCase().endsWith(".pdf")) {
      return fileResponse(filename, "application/pdf", samplePdf(), "GEO客户分析报告.pdf");
    }
    const text = `GEO Production System demo file: ${filename}\n本项目在 Cloudflare Pages 上使用演示接口运行，正式文件由 FastAPI 后端生成。\n`;
    return fileResponse(filename, "text/plain; charset=utf-8", text, filename);
  }

  const projectMatch = path.match(/^\/projects\/([^/]+)$/);
  if (method === "GET" && projectMatch) {
    return json(buildProjectDetail(projectMatch[1]));
  }

  const rerunMatch = path.match(/^\/projects\/([^/]+)\/rerun$/);
  if (method === "POST" && rerunMatch) {
    return json(buildProject(rerunMatch[1], { status: "ANALYZING" }));
  }

  if (method === "DELETE" && projectMatch) {
    return json({ id: projectMatch[1], status: "deleted" });
  }

  return error("not found", 404);
}

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const response = await route(request, url.pathname);
  response.headers.set("Access-Control-Allow-Origin", "*");
  response.headers.set("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS");
  response.headers.set("Access-Control-Allow-Headers", "Content-Type,Authorization");
  return response;
}
