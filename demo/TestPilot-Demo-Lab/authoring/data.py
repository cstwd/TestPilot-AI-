
from spec import E, f, group

m = group("data")

m("g","csv_processor",f("rows(text: str) -> list[list[str]]","Read CSV from literal text, including quoted fields.",
"import csv\nimport io\n\nreturn list(csv.reader(io.StringIO(text, newline='')))",
"header_width(text: str) -> int","Return first-record width, or zero for empty text.",
"parsed = rows(text)\nreturn len(parsed[0]) if parsed else 0"),
[("rows('a,\"b,c\"\\n')",[["a","b,c"]],"normal"),("header_width('')",0,"boundary"),("header_width('a,b\\r\\n1,2')",2,"special"),("rows(1)",E("TypeError"),"exception")])

m("g","text_analyzer",f("word_count(text: str) -> int","Count whitespace-delimited tokens.",
"return len(text.split())",
"longest_token(text: str) -> str","Return the first longest token, or empty text.",
"return max(text.split(), key=len, default='')"),
[("word_count('one  two')",2,"normal"),("word_count('')",0,"boundary"),("longest_token('éé 字字')","éé","special"),("word_count(None)",E("AttributeError"),"exception")])

m("g","record_projection",f("project(row: dict, keys: list[str]) -> dict","Select requested fields, requiring each to be present.",
"return {key: row[key] for key in keys}",
"complete(row: dict, keys: list[str]) -> bool","Indicate whether all requested fields are present.",
"return all(key in row for key in keys)"),
[("project({'a':1,'b':2},['b'])",{"b":2},"normal"),("complete({},[])",True,"boundary"),("complete({'a':None},['a'])",True,"special"),("project({},['id'])",E("KeyError"),"exception")])

m("g","encoding_converter",f("as_hex(text: str) -> str","Encode text as UTF-8 and represent its bytes in lowercase hex.",
"return text.encode('utf-8').hex()",
"from_hex(encoded: str) -> str","Decode UTF-8 text from a hex representation.",
"return bytes.fromhex(encoded).decode('utf-8')"),
[("as_hex('café')","636166c3a9","normal"),("as_hex('')","","boundary"),("from_hex('e5ad97')","字","special"),("from_hex('ff')",E("UnicodeDecodeError"),"exception")])

m("b","json_processor",f("parse_record(text: str) -> dict","Load a JSON object from a supplied string.",
"import json\n\nresult = json.loads(text)\nif not isinstance(result, dict):\n    raise ValueError('expected object')\nreturn result",
"field_or(row: dict, key: str, default: int) -> int","Use the default only for an absent key.",
"return row.get(key, default)"),
[("parse_record('[]')",E("ValueError"),"exception",([],"isinstance(result, dict)","isinstance(result, (dict, list))","shape_validation")),("field_or({'n':0},'n',5)",0,"boundary",(5,"row.get(key, default)","row.get(key) or default","falsy_data")),("parse_record('{}')",{},"boundary"),("field_or({},'n',5)",5,"normal")])

m("b","data_cleaner",f("clean_tags(tags: list[str]) -> list[str]","Trim tags and drop whitespace-only entries.",
"return [tag.strip() for tag in tags if tag.strip()]",
"coalesce(values: list[int | None], fill: int) -> list[int]","Replace nulls while preserving valid zeros.",
"return [fill if value is None else value for value in values]"),
[("clean_tags([' x ',' '])",["x"],"boundary",(["x",""],"if tag.strip()]","if tag]","whitespace_filter")),("coalesce([0,None,2],9)",[0,9,2],"special",([9,9,2],"value is None else value","not value else value","null_handling")),("clean_tags([])",[],"boundary"),("coalesce([2],0)",[2],"normal")])

m("b","log_parser",f("message(line: str) -> str","Extract everything after the first pipe.",
"return line.split('|', 1)[1]",
"error_lines(lines: list[str]) -> int","Count lines whose level field is exactly ERROR.",
"return sum(line.split('|', 1)[0] == 'ERROR' for line in lines)"),
[("message('INFO|A|B')","A|B","normal",("A","split('|', 1)[1]","split('|')[1]","delimiter_limit")),("error_lines(['ERROR|A','INFO|ERROR'])",1,"combination",(2,"line.split('|', 1)[0] == 'ERROR'","'ERROR' in line","field_scope")),("message('INFO|')","","boundary"),("message('INFO')",E("IndexError"),"exception")])

m("b","file_validator",f("suffix_allowed(name: str, suffix: str) -> bool","Match a case-insensitive suffix such as .csv on a supplied name.",
"return name.casefold().endswith(suffix.casefold())",
"fits_budget(length: int, limit: int) -> bool","Accept lengths up to and including the size budget.",
"return 0 <= length <= limit"),
[("suffix_allowed('sample.CSV','.csv')",True,"normal",(False,"name.casefold().endswith(suffix.casefold())","name.endswith(suffix)","case_normalization")),("fits_budget(128,128)",True,"boundary",(False,"length <= limit","length < limit","size_limit")),("suffix_allowed('sample.csv.bak','.csv')",False,"normal"),("fits_budget(-1,128)",False,"boundary")])

m("b","data_transformer",f("columns(values: list[list[int]]) -> list[list[int]]","Transpose equal length rows, rejecting ragged rows.",
"return [list(column) for column in zip(*values, strict=True)]",
"rename_field(row: dict, old: str, new: str) -> dict","Return a copy with the given field moved to its new key.",
"result = row.copy()\nresult[new] = result.pop(old)\nreturn result"),
[("columns([[1,2],[3]])",E("ValueError"),"exception",([[1,3]],", strict=True","","ragged_truncation")),("rename_field({'a':1},'a','b')",{"b":1},"normal",({"a":1,"b":1},"result.pop(old)","result[old]","stale_field")),("columns([])",[],"boundary"),("rename_field({},'a','b')",E("KeyError"),"exception")])

m("b","duplicate_detector",f("repeat_ids(values: list[str]) -> list[str]","Return unique repeated IDs in lexical order.",
"from collections import Counter\n\nreturn sorted(key for key, count in Counter(values).items() if count > 1)",
"first_position(values: list[str], key: str) -> int","Return the first index of an ID, or minus one.",
"return values.index(key) if key in values else -1"),
[("repeat_ids(['b','b','b','a','a'])",["a","b"],"normal",(["a"],"count > 1","count == 2","duplicate_count")),("first_position(['a','z','a'],'a')",0,"boundary",(2,"values.index(key)","len(values) - 1 - values[::-1].index(key)","first_vs_last")),("repeat_ids([])",[],"boundary"),("first_position([],'a')",-1,"boundary")])

m("b","date_parser",f("iso_date(text: str) -> str","Parse a valid date as YYYY-MM-DD.",
"from datetime import date\n\nreturn date.fromisoformat(text).isoformat()",
"month_key(text: str) -> str","Return the year and month of the parsed date.",
"return iso_date(text)[:7]"),
[("iso_date('2024-02-29')","2024-02-29","boundary",("2024-02-01","date.fromisoformat(text).isoformat()","date.fromisoformat(text).replace(day=1).isoformat()","date_truncation")),("month_key('2026-11-01')","2026-11","normal",("2026-1","iso_date(text)[:7]","iso_date(text)[:6]","key_width")),("iso_date('2023-02-29')",E("ValueError"),"exception"),("iso_date('2025-01-01')","2025-01-01","boundary")])

m("b","fixed_width_records",f("split_fields(line: str, width: int) -> list[str]","Split into fixed-width fields, retaining a partial tail.",
"return [line[i:i+width] for i in range(0, len(line), width)]",
"pad_field(value: str, width: int) -> str","Pad a field on the right with spaces.",
"return value.ljust(width)"),
[("split_fields('abcde',2)",["ab","cd","e"],"boundary",(["ab","cd"],"len(line), width","len(line) - width + 1, width","trailing_field")),("pad_field('x',3)","x  ","normal",("  x","value.ljust(width)","value.rjust(width)","padding_side")),("split_fields('',3)",[],"boundary"),("split_fields('a',0)",E("ValueError"),"exception")])

m("b","temperature_ingest",f("reading(text: str) -> float","Read a decimal measurement preserving its fractional part.",
"return float(text)",
"valid_readings(values: list[float]) -> list[float]","Retain finite readings in source order.",
"import math\n\nreturn [value for value in values if math.isfinite(value)]"),
[("reading('-1.75')",-1.75,"special",(-1,"float(text)","int(float(text))","fraction_truncation")),("valid_readings([0, -1, 5])",[0,-1,5],"boundary",([-1,5],"if math.isfinite(value)","if math.isfinite(value) and value","zero_filter")),("reading('x')",E("ValueError"),"exception"),("valid_readings([])",[],"boundary")])
