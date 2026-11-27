
from spec import E, f, group

m = group("commerce")

m("c","member_checkout",f("subtotal_after_discount(cents: int, gold: bool, coupon: int) -> int","Apply the qualifying Gold discount before a fixed coupon and floor at zero.",
"loyalty = cents // 10 if gold and cents >= 2000 else 0\nreturn max(0, cents - loyalty - coupon)",
"checkout(cents: int, gold: bool, coupon: int, pickup: bool) -> int","Add shipping when delivery is requested and the discounted subtotal is below 3000.",
"subtotal = subtotal_after_discount(cents, gold, coupon)\nreturn subtotal + (400 if not pickup and subtotal < 3000 else 0)"),
[("subtotal_after_discount(2000,True,100)",1700,"combination",(1900,"cents >= 2000","cents > 2000","member_threshold")),("checkout(3200,False,300,False)",3300,"combination",(2900,"and subtotal < 3000","and cents < 3000","shipping_basis")),("checkout(3000,False,0,False)",3000,"boundary"),("subtotal_after_discount(100,False,999)",0,"boundary")])

m("c","stock_allocation",f("allocate(stock: int, reserved: int, request: int) -> int","Fill at most free stock and at most requested units.",
"return min(request, max(0, stock - reserved))",
"reorder(stock: int, reserved: int, incoming: int, threshold: int) -> bool","Reorder when projected free stock is strictly below the threshold.",
"return max(0, stock - reserved) + incoming < threshold"),
[("allocate(10,7,8)",3,"combination",(8,"min(request, max(0, stock - reserved))","min(request, stock)","reservation_omission")),("reorder(10,8,3,5)",False,"combination",(True,"+ incoming < threshold","+ incoming <= threshold","reorder_threshold")),("allocate(5,0,5)",5,"boundary"),("reorder(5,0,0,4)",False,"normal")])

m("c","tiered_returns",f("refund(cents: int, units: int, opened: bool, member: bool) -> int","Deduct a flat fee only for opened goods returned by nonmembers.",
"gross = cents * units\nreturn max(0, gross - (250 if opened and not member else 0))",
"return_window(delivered: int, requested: int, member: bool) -> bool","Allow requests from delivery through the member-adjusted final day.",
"return 0 <= requested - delivered <= (45 if member else 30)"),
[("refund(400,2,True,True)",800,"combination",(550,"opened and not member","opened","member_fee")),("return_window(3,48,True)",True,"combination",(False,"<= (45 if member else 30)","< (45 if member else 30)","member_deadline")),("refund(100,1,True,False)",0,"boundary"),("return_window(5,4,False)",False,"boundary")])

m("c","invoice_adjustment",f("taxable_subtotal(cents: int, discount: int, exempt: bool) -> int","Return the discounted taxable base unless the invoice is exempt.",
"return 0 if exempt else max(0, cents - discount)",
"invoice_total(cents: int, discount: int, exempt: bool, shipping: int) -> int","Add non-taxed shipping and ten percent of the taxable goods.",
"base = max(0, cents - discount)\nreturn base + shipping + taxable_subtotal(cents, discount, exempt) // 10"),
[("taxable_subtotal(1000,300,False)",700,"combination",(1000,"else max(0, cents - discount)","else cents","discounted_base")),("invoice_total(1000,0,True,200)",1200,"combination",(1220,"taxable_subtotal(cents, discount, exempt) // 10","(shipping + taxable_subtotal(cents, discount, exempt)) // 10","shipping_tax")),("invoice_total(1000,0,False,0)",1100,"normal"),("taxable_subtotal(0,5,True)",0,"boundary")])

m("c","order_transitions",f("next_state(current: str, action: str, balance: int) -> str","Accept dispatch only for packed and fully paid orders.",
"if action == 'dispatch' and current == 'packed' and balance == 0:\n    return 'shipped'\nreturn current",
"can_cancel(current: str, refunded: bool) -> bool","Cancel new orders, or packed orders after refund.",
"return current == 'new' or (current == 'packed' and refunded)"),
[("next_state('packed','dispatch',1)","packed","combination",("shipped","balance == 0","balance <= 1","dispatch_condition")),("can_cancel('new',False)",True,"combination",(False,"current == 'new' or (current == 'packed' and refunded)","current in ('new', 'packed') and refunded","cancel_precedence")),("next_state('packed','dispatch',0)","shipped","normal"),("can_cancel('shipped',True)",False,"boundary")])

m("c","split_delivery",f("choose_service(weight: int, rural: bool, express: bool) -> str","Use air for eligible express parcels outside rural routes.",
"if express and not rural and weight <= 20:\n    return 'air'\nreturn 'road'",
"route_fee(weight: int, rural: bool, express: bool) -> int","Use a service-specific base plus a rural surcharge.",
"service = choose_service(weight, rural, express)\nreturn (900 if service == 'air' else 400) + (300 if rural else 0)"),
[("choose_service(20,False,True)","air","combination",("road","weight <= 20","weight < 20","air_weight_limit")),("route_fee(8,True,True)",700,"combination",(400,"if rural else 0","if service == 'air' and rural else 0","surcharge_gate")),("choose_service(21,False,True)","road","boundary"),("route_fee(8,False,False)",400,"normal")])

m = group("people")

m("c","conference_roster",f("assign_track(talk: str, remote: bool, seats: int) -> str","Assign live talks only when room seats are available.",
"if remote or seats <= 0:\n    return 'online'\nreturn talk",
"room_count(onsite: int, remote: int, room_size: int, hybrid: bool) -> int","Round up room needs, including remote speakers only in hybrid recording rooms.",
"demand = onsite + (remote if hybrid else 0)\nreturn (demand + room_size - 1) // room_size"),
[("assign_track('math',False,0)","online","combination",("math","seats <= 0","seats < 0","room_capacity")),("room_count(10,2,10,True)",2,"combination",(1,"remote if hybrid else 0","remote if not hybrid else 0","hybrid_demand")),("room_count(20,0,10,True)",2,"normal"),("room_count(2,0,0,False)",E("ZeroDivisionError"),"exception")])

m("c","training_enrollment",f("placement(score: int, prerequisite: bool, sponsor: bool) -> str","Place in advanced with the prerequisite and a passing score or sponsor.",
"return 'advanced' if prerequisite and (score >= 80 or sponsor) else 'foundation'",
"stipend(days: int, remote: bool, funded: bool) -> int","Fund on-site training at 30 per day, capped at 150.",
"return min(150, days * 30) if funded and not remote else 0"),
[("placement(50,True,True)","advanced","combination",("foundation","score >= 80 or sponsor","score >= 80 and sponsor","sponsor_alternative")),("stipend(6,False,True)",150,"combination",(180,"min(150, days * 30)","days * 30","stipend_cap")),("stipend(6,True,True)",0,"boundary"),("placement(83,True,True)","advanced","normal")])

m("c","shift_assignment",f("assignment(available: bool, qualified: bool, hours: int) -> str","Assign only an available qualified worker below the weekly limit.",
"return 'assigned' if available and qualified and hours < 40 else 'waiting'",
"shift_credit(hours: int, holiday: bool, training: bool) -> int","Double holiday hours for regular work only.",
"return hours * (2 if holiday and not training else 1)"),
[("assignment(True,True,40)","waiting","combination",("assigned","hours < 40","hours <= 40","weekly_limit")),("shift_credit(5,True,True)",5,"combination",(10,"holiday and not training","holiday","training_rate")),("assignment(True,True,39)","assigned","boundary"),("shift_credit(5,False,False)",5,"normal")])

m("c","scholarship_awards",f("award(score: int, income: int, renewal: bool) -> int","Award a grant below the income ceiling with a renewal-adjusted score threshold.",
"return 500 if income < 30000 and score >= (75 if renewal else 85) else 0",
"disbursement(total: int, installments: int, late: bool) -> list[int]","Split an award with the remainder first, withholding the last part when late.",
"base, extra = divmod(total, installments)\nparts = [base + extra] + [base] * (installments - 1)\nreturn parts[:-1] if late else parts"),
[("award(75,25000,True)",500,"combination",(0,"75 if renewal else 85","85 if renewal else 75","renewal_threshold")),("disbursement(10,3,True)",[4,3],"combination",([3,3],"parts[:-1] if late","parts[1:] if late","withheld_installment")),("award(100,30000,False)",0,"boundary"),("disbursement(4,0,False)",E("ZeroDivisionError"),"exception")])

m = group("time")

m("c","booking_timezones",f("utc_window(start: int, minutes: int, offset: int) -> list[int]","Convert a local start and duration into absolute UTC minutes.",
"first = start - offset\nreturn [first, first + minutes]",
"conflict(a: list[int], b: list[int], cleanup: int) -> bool","Detect overlap after adding cleanup time to both UTC appointments.",
"a0, a1 = utc_window(*a)\nb0, b1 = utc_window(*b)\nreturn max(a0, b0) < min(a1 + cleanup, b1 + cleanup)"),
[("utc_window(30,20,60)",[-30,-10],"combination",([90,110],"start - offset","start + offset","offset_direction")),("conflict([5,5,0],[11,5,0],1)",False,"combination",(True,"max(a0, b0) <","max(a0, b0) <=","cleanup_boundary")),("conflict([5,10,0],[8,3,0],0)",True,"normal"),("utc_window(0,0,0)",[0,0],"boundary")])

m("c","holiday_dispatch",f("dispatch_day(day: int, late: bool, holidays: list[int]) -> int","Advance late orders then roll forward over weekends and holidays.",
"candidate = day + int(late)\nwhile candidate % 7 >= 5 or candidate in holidays:\n    candidate += 1\nreturn candidate",
"delivery_day(day: int, late: bool, holidays: list[int], transit: int) -> int","Add calendar days in transit after finding dispatch.",
"return dispatch_day(day, late, holidays) + transit"),
[("dispatch_day(4,True,[7])",8,"combination",(7,"candidate in holidays","(candidate in holidays and not late)","holiday_rollover")),("delivery_day(3,True,[],2)",6,"combination",(5,"dispatch_day(day, late, holidays) + transit","day + transit","dispatch_dependency")),("dispatch_day(5,False,[])",7,"boundary"),("delivery_day(1,False,[],0)",1,"normal")])

m("c","subscription_credit",f("credit(unused: int, monthly: int, term: int, prepaid: bool) -> int","Prorate prepaid unused days, limiting credit to the monthly charge.",
"return min(monthly, monthly * max(0, unused) // term) if prepaid else 0",
"rebill(unused: int, monthly: int, term: int, prepaid: bool, fee: int) -> int","Deduct credit from a new fee and floor at zero.",
"return max(0, fee - credit(unused, monthly, term, prepaid))"),
[("credit(35,300,30,True)",300,"combination",(350,"min(monthly, monthly * max(0, unused) // term)","monthly * max(0, unused) // term","credit_cap")),("rebill(15,300,30,True,70)",0,"combination",(-80,"max(0, fee - credit(unused, monthly, term, prepaid))","fee - credit(unused, monthly, term, prepaid)","rebill_floor")),("credit(5,300,0,False)",0,"boundary"),("credit(1,300,0,True)",E("ZeroDivisionError"),"exception")])
