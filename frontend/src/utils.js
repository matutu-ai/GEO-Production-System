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
