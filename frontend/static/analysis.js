function describeParameter(value) {
  const prefix = {var_positional: "*", var_keyword: "**"}[value.kind] || "";
  const annotation = value.annotation ? ": " + value.annotation : "";
  const defaultValue = value.default == null ? "" : " = " + value.default;
  return prefix + value.name + annotation + defaultValue;
}

export async function showAnalysis({$, api, link, fileId}) {
  const data = await api("/api/files/" + fileId + "/analysis");
  $("analysis-meta").textContent = data.filename + " · v" + data.revision;
  if (!data.valid) {
    const error = data.error || {};
    $("symbols").textContent = "语法错误 · 行 " + (error.line ?? "—") + "，列 " +
      (error.column ?? "—") + " · " + (error.message || "请检查语法");
    return;
  }
  $("symbol-count").textContent = data.symbols.length + " 个符号";
  if (!data.symbols.length) $("symbols").textContent = "此文件没有可展示的函数或类。";
  for (const symbol of data.symbols) {
    const row = document.createElement("article");
    const heading = document.createElement("h3");
    const args = [];
    const parameters = symbol.parameters || [];
    parameters.forEach((arg, index) => {
      if (arg.kind === "keyword_only" && !["keyword_only", "var_positional"].includes(parameters[index - 1]?.kind)) args.push("*");
      args.push(describeParameter(arg));
      if (arg.kind === "positional_only" && parameters[index + 1]?.kind !== arg.kind) args.push("/");
    });
    heading.textContent = symbol.kind === "class" ? "class " + symbol.name :
      symbol.name + "(" + args.join(", ") + ")" + (symbol.returns ? " → " + symbol.returns : "");
    const meta = document.createElement("p");
    meta.className = "hint";
    meta.textContent = symbol.kind + " · 第 " + symbol.line + "–" + (symbol.end_line ?? symbol.line) + " 行";
    row.append(heading, meta);
    if (symbol.docstring) {
      const doc = document.createElement("p");
      doc.className = "hint";
      doc.textContent = symbol.docstring;
      row.append(doc);
    }
    if (symbol.kind === "function" && !symbol.name.includes(".")) {
      const next = document.createElement("a");
      next.href = link("generation", {symbol: symbol.name});
      next.textContent = "为此函数生成测试";
      row.append(next);
    }
    $("symbols").append(row);
  }
}
