
from spec import E, f, group

m = group("people")

m("g","user_profile",f("display_name(given: str, family: str) -> str","Join and trim supplied names.",
"return ' '.join(part.strip() for part in (given, family) if part.strip())",
"initials(given: str, family: str) -> str","Return uppercase initials.",
"return ''.join(part[0].upper() for part in display_name(given, family).split())"),
[("display_name(' Ada ', 'Lovelace')","Ada Lovelace","normal"),("display_name('', '')","","boundary"),("initials('Émile','Zola')","ÉZ","special"),("initials(None,'Zola')",E("AttributeError"),"exception")])

m("g","user_validator",f("normalize_username(value: str) -> str","Trim and case-fold a nonempty display handle.",
"normalized = value.strip().casefold()\nif not normalized:\n    raise ValueError('empty handle')\nreturn normalized",
"handles_match(left: str, right: str) -> bool","Compare canonical display handles.",
"return normalize_username(left) == normalize_username(right)"),
[("handles_match(' Ada ', 'ADA')",True,"normal"),("normalize_username('X')","x","boundary"),("normalize_username('Straße')","strasse","special"),("normalize_username(' ')",E("ValueError"),"exception")])

m("g","role_manager",f("active_labels(roles: dict[str, bool]) -> list[str]","List labels marked active, in lexical order.",
"return sorted(name for name, active in roles.items() if active)",
"label_summary(roles: dict[str, bool]) -> str","Render active role labels for display.",
"return ', '.join(active_labels(roles))"),
[("active_labels({'z':True,'a':True,'m':False})",["a","z"],"normal"),("label_summary({})","","boundary"),("label_summary({'owner':True})","owner","boundary"),("label_summary(None)",E("AttributeError"),"exception")])

m("g","account_lock",f("remaining_wait(now: int, locked_until: int) -> int","Display remaining lock seconds for a synthetic account.",
"return max(0, locked_until - now)",
"lock_notice(now: int, locked_until: int) -> str","Render the lock countdown.",
"return f'{remaining_wait(now, locked_until)}s'"),
[("remaining_wait(3, 10)",7,"normal"),("remaining_wait(7, 7)",0,"boundary"),("lock_notice(10, 0)","0s","boundary"),("remaining_wait('4', 5)",E("TypeError"),"exception")])

m("b","user_registration",f("pending_labels(names: list[str]) -> list[str]","Deduplicate synthetic signup names while preserving first appearance.",
"return list(dict.fromkeys(names))",
"invitation_slots(limit: int, pending: int) -> int","Return nonnegative unreserved invitation slots.",
"return max(0, limit - pending)"),
[("pending_labels(['Li','Li','Wu'])",["Li","Wu"],"normal",(["Li","Li","Wu"],"list(dict.fromkeys(names))","list(names)","deduplication")),("invitation_slots(2, 3)",0,"boundary",(-1,"max(0, limit - pending)","limit - pending","clamping")),("pending_labels([])",[],"boundary"),("invitation_slots(3, 1)",2,"normal")])

m("b","session_summary",f("elapsed(start: int, now: int) -> int","Return nonnegative elapsed time for a dashboard stopwatch.",
"return max(0, now - start)",
"minute_bucket(seconds: int) -> int","Return complete minutes for a timeline display.",
"return seconds // 60"),
[("elapsed(5, 2)",0,"boundary",(-3,"max(0, now - start)","now - start","clamping")),("minute_bucket(119)",1,"boundary",(2,"seconds // 60","round(seconds / 60)","bucket_rounding")),("elapsed(2, 5)",3,"normal"),("minute_bucket(0)",0,"boundary")])

m("b","profile_preferences",f("merged(base: dict[str, str], overrides: dict[str, str]) -> dict[str, str]","Apply new preferences over defaults.",
"return base | overrides",
"visible_keys(values: dict[str, str]) -> list[str]","Order nonempty preferences for display.",
"return sorted(key for key, value in values.items() if value != '')"),
[("merged({'language':'en'}, {'language':'zh'})",{"language":"zh"},"combination",({"language":"en"},"base | overrides","overrides | base","precedence")),("visible_keys({'mode':'','name':'A'})",["name"],"boundary",(["mode","name"],"if value != ''","if value is not None","empty_handling")),("merged({}, {})",{},"boundary"),("visible_keys({'b':'B','a':'A'})",["a","b"],"normal")])

m("b","team_roster",f("surname_key(name: str) -> str","Return the case-insensitive final component of a person's name.",
"return name.split()[-1].casefold()",
"team_capacity(members: list[str], limit: int) -> bool","Check whether a team can register another member.",
"return len(members) < limit"),
[("surname_key('Ada Lovelace')","lovelace","normal",("ada","split()[-1]","split()[0]","component_selection")),("team_capacity(['A','B'],2)",False,"boundary",(True,"len(members) < limit","len(members) <= limit","capacity")),("surname_key('')",E("IndexError"),"exception"),("team_capacity([],1)",True,"boundary")])

m("b","name_badges",f("badge_label(name: str, limit: int) -> str","Limit visible characters after trimming a name.",
"return name.strip()[:limit]",
"badge_rows(labels: list[str], columns: int) -> int","Return the number of rows needed to lay badges out.",
"return (len(labels) + columns - 1) // columns"),
[("badge_label(' Ada ',2)","Ad","boundary",("A","name.strip()[:limit]","name[:limit].strip()","operation_order")),("badge_rows(['A','B','C'],2)",2,"boundary",(1,"(len(labels) + columns - 1) // columns","len(labels) // columns","ceiling")),("badge_rows([],2)",0,"boundary"),("badge_rows(['A'],0)",E("ZeroDivisionError"),"exception")])

m("b","staff_directory",f("find_department(rows: dict[str, str], department: str) -> list[str]","List staff in exactly the requested department.",
"return sorted(name for name, dept in rows.items() if dept == department)",
"directory_counts(rows: dict[str, str]) -> dict[str, int]","Count staff by department.",
"counts = {}\nfor dept in rows.values():\n    counts[dept] = counts.get(dept, 0) + 1\nreturn counts"),
[("find_department({'Ana':'Art','Bea':'Arts'},'Art')",["Ana"],"normal",(["Ana","Bea"],"dept == department","dept.startswith(department)","matching")),("directory_counts({'Ana':'Art','Bea':'Art'})",{"Art":2},"normal",({"Art":1},"counts.get(dept, 0) + 1","1","aggregation")),("find_department({},'Art')",[],"boundary"),("directory_counts({'Ana':'Art'})",{"Art":1},"normal")])

m("b","contact_cards",f("extension_label(number: str, extension: str) -> str","Render a contact number with an optional extension.",
"return f'{number} x{extension}' if extension else number",
"initial_badge(name: str) -> str","Use the first visible character of the contact name.",
"return name.strip()[:1].upper()"),
[("extension_label('5550100','')","5550100","boundary",("5550100 x"," if extension else number","","optional_field")),("initial_badge('  Vega')","V","boundary",(" ","name.strip()[:1]","name[:1]","whitespace")),("extension_label('5550100','22')","5550100 x22","normal"),("initial_badge('')","","boundary")])

m("b","membership_display",f("renewal_year(start: int, years: int) -> int","Compute the first year after the prepaid term.",
"return start + years",
"tier_label(points: int) -> str","Show Gold at one hundred points and Standard below.",
"return 'Gold' if points >= 100 else 'Standard'"),
[("renewal_year(2024, 2)",2026,"normal",(2025,"start + years","start + years - 1","term_end")),("tier_label(100)","Gold","boundary",("Standard","points >= 100","points > 100","inclusive_threshold")),("tier_label(101)","Gold","normal"),("renewal_year(2024,None)",E("TypeError"),"exception")])
