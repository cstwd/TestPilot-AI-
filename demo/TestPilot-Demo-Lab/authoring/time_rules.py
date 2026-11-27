
from spec import E, f, group

m = group("time")

m("g","date_calculator",f("leap(year: int) -> bool","Use Gregorian leap-year rules.",
"return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)",
"days_in_year(year: int) -> int","Return the length of a Gregorian year.",
"return 366 if leap(year) else 365"),
[("leap(2000)",True,"combination"),("leap(1900)",False,"boundary"),("days_in_year(2023)",365,"normal"),("leap(None)",E("TypeError"),"exception")])

m("g","booking_validator",f("valid_slot(start: int, end: int, latest: int) -> bool","Accept a positive-width interval within the booking day.",
"return 0 <= start < end <= latest",
"booking_length(start: int, end: int, latest: int) -> int","Return duration for a valid booking.",
"if not valid_slot(start, end, latest):\n    raise ValueError('outside booking hours')\nreturn end - start"),
[("valid_slot(3,5,10)",True,"normal"),("valid_slot(0,7,7)",True,"boundary"),("valid_slot(2,2,7)",False,"boundary"),("booking_length(4,9,8)",E("ValueError"),"exception")])

m("g","timezone_converter",f("local_minute(utc_minute: int, offset: int) -> int","Apply a fixed offset and wrap within a day.",
"return (utc_minute + offset) % 1440",
"day_shift(utc_minute: int, offset: int) -> int","Return the offset-induced signed day shift.",
"return (utc_minute + offset) // 1440"),
[("local_minute(30,-60)",1410,"boundary"),("day_shift(30,-60)",-1,"special"),("day_shift(1400,40)",1,"boundary"),("local_minute('30',5)",E("TypeError"),"exception")])

m("g","retry_policy",f("retry_delay(base: int, attempt: int, cap: int) -> int","Use capped exponential waits for one-based retry attempts.",
"if attempt < 1:\n    raise ValueError('attempt must be positive')\nreturn min(cap, base * 2 ** (attempt - 1))",
"retry_budget(base: int, count: int, cap: int) -> int","Sum the waits across the planned retries.",
"return sum(retry_delay(base, attempt, cap) for attempt in range(1, count + 1))"),
[("retry_delay(3,3,10)",10,"combination"),("retry_delay(3,1,10)",3,"boundary"),("retry_budget(2,3,5)",11,"normal"),("retry_delay(3,0,10)",E("ValueError"),"exception")])

m("b","working_days",f("is_workday(day: int) -> bool","Interpret Monday as day zero and repeat weekly.",
"return day % 7 < 5",
"business_days(start: int, end: int) -> int","Count weekdays in a half-open day range.",
"return sum(is_workday(day) for day in range(start, end))"),
[("is_workday(5)",False,"boundary",(True,"day % 7 < 5","day % 7 <= 5","weekday_threshold")),("business_days(1,3)",2,"normal",(3,"range(start, end)","range(start, end + 1)","end_inclusion")),("business_days(6,6)",0,"boundary"),("is_workday(7)",True,"boundary")])

m("b","delivery_scheduler",f("delivery_day(order_day: int, minute: int, cutoff: int) -> int","Send same day strictly before cutoff, otherwise next day.",
"return order_day + (minute >= cutoff)",
"delivery_range(ship_day: int, min_days: int, max_days: int) -> list[int]","Return earliest and latest delivery days.",
"return [ship_day + min_days, ship_day + max_days]"),
[("delivery_day(5,600,600)",6,"boundary",(5,"minute >= cutoff","minute > cutoff","cutoff")),("delivery_range(5,2,4)",[7,9],"normal",([7,7],"ship_day + max_days","ship_day + min_days","latest_date")),("delivery_day(0,0,1)",0,"normal"),("delivery_range(5,0,0)",[5,5],"boundary")])

m("b","subscription_manager",f("remaining_days(now: int, end: int) -> int","Report days left in a prepaid synthetic plan.",
"return max(0, end - now)",
"renewed_end(end: int, now: int, extension: int) -> int","Extend a current plan from its end and a lapsed plan from today.",
"return max(end, now) + extension"),
[("remaining_days(12,10)",0,"boundary",(-2,"max(0, end - now)","end - now","lapse_floor")),("renewed_end(5,8,30)",38,"combination",(35,"max(end, now)","end","renewal_base")),("renewed_end(10,8,30)",40,"normal"),("remaining_days(10,10)",0,"boundary")])

m("b","billing_cycle",f("cycle_number(day_index: int, length: int) -> int","Assign zero-based elapsed days to one-based billing cycles.",
"return day_index // length + 1",
"cycle_offset(day_index: int, length: int) -> int","Return the zero-based day within a cycle.",
"return day_index % length"),
[("cycle_number(30,30)",2,"boundary",(1,"day_index // length + 1","(day_index - 1) // length + 1","cycle_boundary")),("cycle_offset(35,30)",5,"normal",(1,"day_index % length","day_index // length","modulo")),("cycle_offset(0,30)",0,"boundary"),("cycle_offset(14,0)",E("ZeroDivisionError"),"exception")])

m("b","task_scheduler",f("next_tick(now: int, period: int) -> int","Return the first periodic tick strictly after now.",
"return (now // period + 1) * period",
"delayed_tasks(tasks: dict[str, int], now: int) -> list[str]","Find tasks with deadlines strictly before now.",
"return sorted(name for name, due in tasks.items() if due < now)"),
[("next_tick(10,5)",15,"boundary",(10,"(now // period + 1)","((now + period - 1) // period)","strict_next")),("delayed_tasks({'a':2,'b':3},3)",["a"],"boundary",(["a","b"],"due < now","due <= now","due_boundary")),("delayed_tasks({},3)",[],"boundary"),("next_tick(11,5)",15,"normal")])

m("b","event_windows",f("window_start(time: int, width: int) -> int","Align a tick to the start of its fixed-width window.",
"return time // width * width",
"events_in_window(times: list[int], start: int, width: int) -> int","Count ticks in a half-open time window.",
"return sum(start <= tick < start + width for tick in times)"),
[("window_start(-1,10)",-10,"special",(0,"time // width","int(time / width)","negative_alignment")),("events_in_window([0,9,10],0,10)",2,"boundary",(3,"tick < start","tick <= start","window_end")),("window_start(16,10)",10,"normal"),("events_in_window([],0,10)",0,"boundary")])

m("b","calendar_months",f("month_index(year: int, month: int) -> int","Encode a one-based calendar month as a linear index.",
"return year * 12 + month - 1",
"decode_month(index: int) -> list[int]","Decode the index into year and one-based month.",
"return [index // 12, index % 12 + 1]"),
[("month_index(2025,1)",24300,"boundary",(24301,"year * 12 + month - 1","year * 12 + month","month_origin")),("decode_month(24311)",[2025,12],"boundary",([2025,11],"index % 12 + 1","index % 12","decoded_origin")),("decode_month(None)",E("TypeError"),"exception"),("month_index(2025,None)",E("TypeError"),"exception")])

m("b","service_level",f("delay(actual: int, due: int) -> int","Return positive delay or zero for early completion.",
"return max(0, actual - due)",
"penalty(delay_minutes: int, grace: int, unit: int) -> int","Charge per minute beyond the grace period.",
"return max(0, delay_minutes - grace) * unit"),
[("delay(10,15)",0,"boundary",(5,"max(0, actual - due)","abs(actual - due)","early_delivery")),("penalty(7,2,10)",50,"combination",(70,"max(0, delay_minutes - grace)","delay_minutes","grace_period")),("delay(19,15)",4,"normal"),("penalty(0,2,10)",0,"boundary")])
