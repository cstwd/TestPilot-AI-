const KEYWORDS = new Set("and as assert async await break case class continue def del elif else except finally for from global if import in is lambda match nonlocal not or pass raise return try type while with yield".split(" "));
const BUILTINS = new Set("False None True self cls bool bytes dict float int list object set str tuple".split(" "));

// Record line offsets in the unmodified source so copying preserves indentation and line endings.
export function splitSource(source) {
  const lines = [];
  const offsets = [];
  for (const part of source.matchAll(/[^\r\n]*(?:\r\n?|\n|$)/g)) {
    if (!part[0]) continue;
    offsets.push(part.index);
    lines.push(part[0].replace(/[\r\n]+$/, ""));
  }
  offsets.push(source.length);
  return {lines, offsets};
}

// A lightweight lexical display only. No imported text is interpreted as markup.
export function tokenize(lines) {
  let triple = "";
  const pattern = /#.*|"""|'''|"(?:\\.|[^"\\])*"?|'(?:\\.|[^'\\])*'?|[\p{L}_][\p{L}\p{M}\p{N}_]*|\b(?:0[xX][\da-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\d[\d_]*(?:\.[\d_]*)?(?:[eE][+-]?[\d_]+)?)[jJ]?/gu;
  return lines.map(line => {
    const spans = [];
    let pos = 0;
    let definition = false;
    function span(start, end, kind) {
      // Limit individual styled runs on pathological long lines, retaining every source character.
      if (spans.length < 240 && start < 8192) spans.push([start, end, kind]);
    }
    while (pos < line.length) {
      if (triple) {
        let end = line.indexOf(triple, pos);
        while (end >= 0) {
          let backslashes = 0;
          for (let i = end - 1; i >= 0 && line[i] === "\\"; i--) backslashes++;
          if (backslashes % 2 === 0) break;
          end = line.indexOf(triple, end + 1);
        }
        const next = end < 0 ? line.length : end + 3;
        span(pos, next, "string");
        if (end >= 0) triple = "";
        pos = next;
        continue;
      }
      pattern.lastIndex = pos;
      const match = pattern.exec(line);
      if (!match) break;
      const word = match[0];
      let kind;
      if (word === '"""' || word === "'''") {
        triple = word;
        kind = "string";
      } else if (/^['"]/.test(word)) kind = "string";
      else if (word[0] === "#") kind = "comment";
      else if (definition) kind = "name";
      else if (KEYWORDS.has(word)) kind = "keyword";
      else if (BUILTINS.has(word)) kind = "builtin";
      else if (/^\d/.test(word)) kind = "number";
      if (kind) span(match.index, pattern.lastIndex, kind);
      definition = word === "def" || word === "class";
      pos = pattern.lastIndex;
    }
    return spans;
  });
}

export function colorLine(text, spans) {
  const code = document.createElement("code");
  code.className = "ai-code";
  let pos = 0;
  for (const [start, end, kind] of spans) {
    const token = document.createElement("span");
    token.className = "ai-token-" + kind;
    token.textContent = text.slice(start, end);
    code.append(document.createTextNode(text.slice(pos, start)), token);
    pos = end;
  }
  code.append(document.createTextNode(text.slice(pos)));
  return code;
}
