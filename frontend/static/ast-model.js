// F02 returns definitions in lexical preorder. Ranges disambiguate repeated names.
function formatParameter(arg) {
  const prefix = {var_positional: "*", var_keyword: "**"}[arg.kind] || "";
  const annotation = arg.annotation ? ": " + arg.annotation : "";
  const defaultValue = arg.default == null ? "" : " = " + arg.default;
  return prefix + arg.name + annotation + defaultValue;
}

function signature(symbol) {
  if (symbol.kind === "class") return "class " + symbol.name;
  const parts = [];
  symbol.parameters.forEach((arg, index, args) => {
    if (arg.kind === "keyword_only" && !["var_positional", "keyword_only"].includes(args[index - 1]?.kind)) {
      parts.push("*");
    }
    parts.push(formatParameter(arg));
    if (arg.kind === "positional_only" && args[index + 1]?.kind !== "positional_only") parts.push("/");
  });
  const prefix = symbol.kind === "async_function" ? "async " : "";
  return prefix + symbol.name + "(" + parts.join(", ") + ")" + (symbol.returns ? " → " + symbol.returns : "");
}

export function buildGraph(data, file) {
  if (data.file_id !== file.id || data.revision !== file.revision || data.sha256 !== file.sha256 ||
      data.filename !== file.filename || typeof file.source !== "string") {
    throw new Error("分析与源码的文件版本不一致，请重新载入。");
  }
  const lines = file.source.split(/\r\n?|\n/);
  if (lines.at(-1) === "") lines.pop();
  const identity = {file_id: file.id, version_id: file.id, revision: file.revision};
  const root = {
    ...identity, id: "file:" + file.id, type: "file", kind: "file", name: file.filename,
    qualified_name: file.filename, parent_id: null, start_line: lines.length ? 1 : null,
    end_line: lines.length || null, signature: null, parameters: null, returns: null,
    docstring: null, topLevelEligible: false,
  };
  const nodes = [root], edges = [], ancestors = [], directFunctions = new Map();

  for (const symbol of data.symbols) {
    const lastDot = symbol.name.lastIndexOf(".");
    const parentName = symbol.name.slice(0, Math.max(0, lastDot));
    while (ancestors.length && ancestors.at(-1).end_line < symbol.line) ancestors.pop();
    const parent = ancestors.at(-1) || root;
    if (parentName !== (parent === root ? "" : parent.qualified_name) ||
        (parent !== root && symbol.end_line > parent.end_line)) {
      throw new Error("符号层级和行范围不一致，无法关联父定义。");
    }
    let type = "function";
    if (symbol.kind === "class") type = "class";
    else if (parent.type === "class") type = "method";
    const node = {
      ...identity, id: "symbol:" + file.id + ":" + symbol.line + ":" + symbol.name,
      type, kind: symbol.kind, name: symbol.name.slice(lastDot + 1), qualified_name: symbol.name,
      parent_id: parent.id, start_line: symbol.line, end_line: symbol.end_line,
      signature: signature(symbol), parameters: symbol.parameters, returns: symbol.returns,
      docstring: symbol.docstring, topLevelEligible: false,
    };
    nodes.push(node);
    edges.push({id: "contains:" + node.id, source: parent.id, target: node.id, relation_type: "contains"});
    ancestors.push(node);
    // F03's adapter accepts exactly one synchronous FunctionDef in Module.body.
    // A definition under if/try has an unqualified name too, but is indented.
    if (parent === root && symbol.kind === "function" && /^(?:[ \t\f]*\f)?def\b/u.test(lines[symbol.line - 1])) {
      if (!directFunctions.has(symbol.name)) directFunctions.set(symbol.name, []);
      directFunctions.get(symbol.name).push(node);
    }
  }
  for (const group of directFunctions.values()) {
    if (group.length === 1) group[0].topLevelEligible = true;
  }
  return {nodes, edges};
}
