
from spec import E, f, group

m = group("time")

m("c","maintenance_calendar",f("service_due(hours: int, days: int, heavy: bool) -> bool","Trigger service at the adjusted hours limit or after 90 days.",
"return hours >= (120 if heavy else 200) or days >= 90",
"service_slot(due: bool, parts: bool, minutes: int) -> str","Reserve a slot only when due, stocked, and long enough.",
"return 'reserve' if due and parts and minutes >= 45 else 'defer'"),
[("service_due(120,30,True)",True,"combination",(False,"120 if heavy else 200","200 if heavy else 120","heavy_limit")),("service_slot(True,True,45)","reserve","combination",("defer","minutes >= 45","minutes > 45","slot_minimum")),("service_due(5,90,False)",True,"boundary"),("service_slot(True,False,90)","defer","normal")])

m = group("algorithms")

m("c","filtered_pagination",f("eligible(rows: list[list], min_score: int, archived: bool) -> list[str]","Select scored records and include archived ones only when requested.",
"return [name for name, score, old in rows if score >= min_score and (archived or not old)]",
"result_page(rows: list[list], min_score: int, archived: bool, page: int, size: int) -> list[str]","Apply eligibility before slicing a one-based page.",
"items = eligible(rows, min_score, archived)\nstart = (page - 1) * size\nreturn items[start:start + size]"),
[("eligible([['A',4,True],['B',4,False]],4,True)",["A","B"],"combination",(["B"],"archived or not old","not old","archival_filter")),("result_page([['A',0,False],['B',1,False],['C',2,False]],1,False,2,1)",["C"],"combination",([],"(page - 1) * size","page * size","filtered_offset")),("eligible([],1,True)",[],"boundary"),("eligible([['B',1,False]],1,False)",["B"],"boundary")])

m("c","cache_versioning",f("accepted_write(current: int, proposed: int, live: bool) -> bool","Require a newer version while a cache entry is live.",
"return not live or proposed > current",
"serve(value: str, inserted: int, ttl: int, now: int, min_version: int, version: int) -> str","Serve a still-live value with a sufficient version.",
"return value if inserted + ttl > now and version >= min_version else ''"),
[("accepted_write(9,9,True)",False,"combination",(True,"proposed > current","proposed >= current","same_version")),("serve('x',2,3,5,7,8)","","combination",("x","inserted + ttl > now","inserted + ttl >= now","expiry_boundary")),("accepted_write(9,2,False)",True,"boundary"),("serve('x',2,3,4,8,8)","x","normal")])

m("c","weighted_routes",f("cheapest(paths: list[list], load: int, deadline: int) -> str","Pick the cheapest route that meets both load and deadline, preferring the first tie.",
"choices = [(cost, i, name) for i, (name,cost,cap,eta) in enumerate(paths) if cap >= load and eta <= deadline]\nreturn min(choices)[2] if choices else ''",
"cost_with_toll(distance: int, rate: int, toll: int, exempt: bool) -> int","Apply a toll only when the load is not exempt.",
"return distance * rate + (0 if exempt else toll)"),
[("cheapest([['slow',2,10,9],['fast',5,10,5]],10,5)","fast","combination",("slow","cap >= load and eta <= deadline","cap >= load","deadline_filter")),("cost_with_toll(10,2,5,True)",20,"combination",(25,"0 if exempt else toll","toll","toll_exemption")),("cheapest([],0,0)","","boundary"),("cost_with_toll(0,2,0,False)",0,"boundary")])

m("c","batched_queue",f("drain(queue: list[list], slots: int, expedited_only: bool) -> list[str]","Sort priority descending with stable ties, filter if requested, then take available slots.",
"ranked = sorted(queue, key=lambda job: -job[1])\nreturn [name for name, priority in ranked if not expedited_only or priority > 0][:slots]",
"spill(queue_size: int, slots: int, reserve: int) -> int","Return remaining queue length after capacity is reserved.",
"return max(0, queue_size - max(0, slots - reserve))"),
[("drain([['Z',2],['A',2],['W',0]],1,True)",["Z"],"combination",(["A"],"lambda job: -job[1]","lambda job: (-job[1], job[0])","priority_tie")),("spill(5,4,2)",3,"combination",(1,"slots - reserve","slots","reserved_capacity")),("drain([],0,False)",[],"boundary"),("spill(0,9,0)",0,"boundary")])

m = group("data")

m("c","conditional_dedup",f("deduplicate(rows: list[list], keep_newest: bool) -> dict[str,int]","Keep the newest timestamp for each key or retain the first observation.",
"result = {}\nfor key, timestamp in rows:\n    if key not in result or (keep_newest and timestamp > result[key]):\n        result[key] = timestamp\nreturn result",
"export_keys(rows: list[list], keep_newest: bool, minimum: int) -> list[str]","Return deduplicated keys whose chosen timestamps meet the minimum.",
"return sorted(key for key, date in deduplicate(rows, keep_newest).items() if date >= minimum)"),
[("deduplicate([['a',5],['a',9]],False)",{"a":5},"combination",({"a":9},"keep_newest and timestamp > result[key]","timestamp > result[key]","dedup_policy")),("export_keys([['z',5],['z',8]],True,8)",["z"],"combination",([],"date >= minimum","date > minimum","export_threshold")),("deduplicate([],True)",{},"boundary"),("export_keys([['z',6]],True,3)",["z"],"normal")])

m("c","csv_projection",f("select(lines: list[list], key: str, include_empty: bool) -> list[dict]","Project rows whose requested key exists and meets the empty-value rule.",
"return [{key: row[key]} for row in map(dict, lines) if key in row and (include_empty or row[key] != '')]",
"missing_count(lines: list[list], key: str, blank_missing: bool) -> int","Count absent keys and optionally blank values.",
"return sum(key not in row or (blank_missing and row[key] == '') for row in map(dict, lines))"),
[("select([[['a','']],[['b','y']]],'a',True)",[{"a":""}],"combination",([],"include_empty or row[key] != ''","row[key] != ''","blank_policy")),("missing_count([[['a','']],[['b','y']]],'a',False)",1,"combination",(2,"(blank_missing and row[key] == '')","row[key] == ''","missing_classification")),("select([],'a',False)",[],"boundary"),("missing_count([[['x','y']]],'x',True)",0,"normal")])

m("c","telemetry_rollup",f("accepted(rows: list[list], low: int, high: int, calibrated: bool) -> list[int]","Keep in-range readings, requiring calibrated rows when requested.",
"return [value for value, ready in rows if low <= value <= high and (ready or not calibrated)]",
"alert_count(rows: list[list], low: int, high: int, calibrated: bool, alarm: int) -> int","Count accepted readings strictly above the alarm threshold.",
"return sum(value > alarm for value in accepted(rows, low, high, calibrated))"),
[("accepted([[9,True],[9,False]],1,9,True)",[9],"combination",([9,9],"and (ready or not calibrated)","","calibration_filter")),("alert_count([[5,True],[6,True]],0,9,True,5)",1,"combination",(2,"value > alarm","value >= alarm","alarm_boundary")),("accepted([],0,9,True)",[],"boundary"),("alert_count([[6,True]],0,9,True,2)",1,"normal")])

m("c","import_reconciliation",f("eligible_id(row: dict, active_only: bool, minimum: int) -> bool","Require an ID meeting the minimum and, when requested, an active row.",
"return 'id' in row and row['id'] >= minimum and (not active_only or row.get('active', False))",
"join_name(row: dict, directory: dict[int,str], fallback: str) -> str","Prefer the directory name, then a nonempty supplied name, then the fallback.",
"return directory.get(row['id'], row.get('name') or fallback)"),
[("eligible_id({'id':3,'active':False},True,3)",False,"combination",(True,"row.get('active', False)","not row.get('active', False)","active_flag")),("join_name({'id':3,'name':'P'},{3:'Q'},'N')","Q","combination",("P","directory.get(row['id'], row.get('name') or fallback)","row.get('name') or directory.get(row['id'], fallback)","join_priority")),("eligible_id({},True,0)",False,"boundary"),("join_name({'id':7},{},'N')","N","normal")])

m = group("math")

m("c","weighted_grade",f("grade(exam: int, project: int, excused: bool) -> int","Weight exam at 60 percent, or use it alone if project is excused.",
"return exam if excused else (6 * exam + 4 * project) // 10",
"passed(exam: int, project: int, excused: bool, incomplete: bool) -> bool","Require a complete submission and a computed score of at least 60.",
"return not incomplete and grade(exam, project, excused) >= 60"),
[("grade(70,40,False)",58,"combination",(52,"6 * exam + 4 * project","4 * exam + 6 * project","grade_weights")),("passed(60,0,True,False)",True,"combination",(False,">= 60","> 60","pass_threshold")),("grade(70,0,True)",70,"boundary"),("passed(100,100,True,True)",False,"normal")])

m("c","budget_split",f("allocation(total: int, ratio: int, minimum: int) -> int","Apply a percentage then clamp to the minimum and available total.",
"return min(total, max(minimum, total * ratio // 100))",
"reserve(total: int, ratio: int, minimum: int, locked: int) -> int","Return remainder after allocation and locked commitments.",
"return max(0, total - allocation(total, ratio, minimum) - locked)"),
[("allocation(200,10,40)",40,"combination",(20,"max(minimum, total * ratio // 100)","total * ratio // 100","minimum_allocation")),("reserve(200,25,0,175)",0,"combination",(-25,"max(0, total - allocation(total, ratio, minimum) - locked)","total - allocation(total, ratio, minimum) - locked","commitment_floor")),("allocation(0,10,0)",0,"boundary"),("reserve(200,25,0,50)",100,"normal")])

m("c","sensor_calibration",f("calibrated(raw: int, zero: int, gain: int, limit: int) -> int","Adjust offset before gain, then clamp to the signed limit.",
"value = (raw - zero) * gain\nreturn max(-limit, min(limit, value))",
"within_band(value: int, center: int, tolerance: int, inclusive: bool) -> bool","Compare the absolute residual with the selected boundary policy.",
"delta = abs(value - center)\nreturn delta <= tolerance if inclusive else delta < tolerance"),
[("calibrated(8,3,2,12)",10,"combination",(12,"(raw - zero) * gain","raw * gain - zero","calibration_order")),("within_band(3,5,2,False)",False,"combination",(True,"else delta < tolerance","else delta <= tolerance","band_policy")),("calibrated(0,0,4,2)",0,"boundary"),("within_band(3,5,2,True)",True,"boundary")])
