export function unwrap(item) {
  if (item && typeof item === "object" && "result" in item) {
    return item.result || {};
  }
  return item || {};
}

export function joinText(items) {
  if (!items) return "-";
  const list = Array.isArray(items) ? items : [items];
  return list.filter(Boolean).join("、") || "-";
}

export const ACTIVE_STATUSES = new Set([
  "CREATED",
  "PARSING",
  "ANALYZING",
  "GENERATING",
]);

export function isActiveStatus(status) {
  return ACTIVE_STATUSES.has(status) || status === "queued" || status === "running";
}

export function getProjectId(record) {
  return record?.id || record?.task_id;
}

export function getStatusMeta(status) {
  const meta = {
    CREATED: { color: "default", label: "已创建" },
    PARSING: { color: "processing", label: "解析资料" },
    ANALYZING: { color: "processing", label: "分析中" },
    GENERATING: { color: "processing", label: "生成报告" },
    COMPLETED: { color: "success", label: "已完成" },
    FAILED: { color: "error", label: "失败" },
    queued: { color: "default", label: "排队中" },
    running: { color: "processing", label: "处理中" },
    success: { color: "success", label: "已完成" },
    error: { color: "error", label: "失败" },
  };
  return meta[status] || { color: "default", label: status };
}
