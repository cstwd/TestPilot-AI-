
from spec import E, f, group

m = group("commerce")

m("g","shopping_cart",f("cart_total(lines: list[list[int]]) -> int","Total integer-cent prices multiplied by quantities.",
"return sum(price * count for price, count in lines)",
"item_count(lines: list[list[int]]) -> int","Sum quantities across the cart.",
"return sum(count for _, count in lines)"),
[("cart_total([[120,2],[40,3]])",360,"normal"),("cart_total([])",0,"boundary"),("item_count([[0,1]])",1,"boundary"),("cart_total([[2]])",E("ValueError"),"exception")])

m("g","inventory_manager",f("available(on_hand: int, reserved: int) -> int","Return stock available for promise, floored at zero.",
"return max(0, on_hand - reserved)",
"shortfall(requested: int, on_hand: int, reserved: int) -> int","Return unfilled quantity for a proposed line.",
"return max(0, requested - available(on_hand, reserved))"),
[("available(7, 2)",5,"normal"),("available(7, 8)",0,"boundary"),("shortfall(9, 11, 5)",3,"combination"),("available(4, None)",E("TypeError"),"exception")])

m("g","shipping_calculator",f("shipping_fee(cents: int, remote: bool) -> int","Charge 500 below 5000 cents and add 200 to every remote shipment.",
"return (500 if cents < 5000 else 0) + (200 if remote else 0)",
"grand_total(cents: int, remote: bool) -> int","Add shipping to the subtotal.",
"return cents + shipping_fee(cents, remote)"),
[("shipping_fee(5000, False)",0,"boundary"),("shipping_fee(4999, True)",700,"combination"),("grand_total(5000,True)",5200,"combination"),("shipping_fee(None,False)",E("TypeError"),"exception")])

m("g","order_status",f("advance(status: str, event: str) -> str","Apply pay, pack or deliver in the stated order.",
"transitions = {('new','pay'):'paid', ('paid','pack'):'packed', ('packed','deliver'):'delivered'}\nreturn transitions[(status,event)]",
"replay(events: list[str]) -> str","Replay events starting with a new order.",
"status = 'new'\nfor event in events:\n    status = advance(status, event)\nreturn status"),
[("advance('new','pay')","paid","normal"),("replay([])","new","boundary"),("replay(['pay','pack','deliver'])","delivered","combination"),("advance('new','deliver')",E("KeyError"),"exception")])

m("b","volume_discount",f("discount(cents: int, quantity: int) -> int","Award 10 percent at five units or more, rounded down to cents.",
"return cents // 10 if quantity >= 5 else 0",
"net_total(cents: int, quantity: int, fee: int) -> int","Subtract the discount then add the handling fee.",
"return cents - discount(cents, quantity) + fee"),
[("discount(500,5)",50,"boundary",(0,"quantity >= 5","quantity > 5","tier_threshold")),("net_total(500,6,20)",470,"combination",(430,"quantity) + fee","quantity) - fee","fee_sign")),("discount(390,4)",0,"boundary"),("net_total(0,0,0)",0,"boundary")])

m("b","coupon_validator",f("valid_on(day: int, first: int, last: int) -> bool","Require day to fall within inclusive coupon dates.",
"return first <= day <= last",
"offer_discount(cents: int, fixed: int) -> int","Limit the fixed discount to the subtotal.",
"return min(cents, fixed)"),
[("valid_on(10,3,10)",True,"boundary",(False,"day <= last","day < last","expiry_boundary")),("offer_discount(300,500)",300,"boundary",(500,"min(cents, fixed)","fixed","cap")),("valid_on(11,3,10)",False,"boundary"),("offer_discount(800,0)",0,"normal")])

m("b","refund_processor",f("refund_amount(unit: int, returned: int, restocking: int) -> int","Deduct one restocking fee from the returned line and floor at zero.",
"return max(0, unit * returned - restocking)",
"return_units(ordered: int, prior_returns: int) -> int","Return maximum remaining returnable units.",
"return max(0, ordered - prior_returns)"),
[("refund_amount(350,3,20)",1030,"normal",(990,"- restocking)","- restocking * returned)","fee_application")),("return_units(2,3)",0,"boundary",(-1,"max(0, ordered - prior_returns)","ordered - prior_returns","quantity_floor")),("refund_amount(2,1,10)",0,"boundary"),("return_units(5,2)",3,"normal")])

m("b","payment_calculator",f("installment_schedule(cents: int, periods: int) -> list[int]","Distribute any remainder over the earliest installments.",
"base, remainder = divmod(cents, periods)\nreturn [base + (i < remainder) for i in range(periods)]",
"outstanding(cents: int, received: list[int]) -> int","Compute nonnegative unpaid cents from synthetic receipts.",
"return max(0, cents - sum(received))"),
[("installment_schedule(10,3)",[4,3,3],"boundary",([4,4,3],"i < remainder","i <= remainder","remainder_allocation")),("outstanding(100,[20,30])",50,"normal",(70,"sum(received)","max(received, default=0)","receipt_aggregation")),("installment_schedule(99,0)",E("ZeroDivisionError"),"exception"),("outstanding(100,[120])",0,"boundary")])

m("b","product_pricing",f("unit_price(base: int, markup: int, sale: bool) -> int","Return base price in a sale or base plus markup otherwise.",
"return base if sale else base + markup",
"tax_included(cents: int, rate: int) -> int","Add a whole percent tax, rounded down.",
"return cents + cents * rate // 100"),
[("unit_price(100,20,True)",100,"normal",(120,"return base if sale else base + markup","return base + markup if sale else base","sale_branch")),("tax_included(249,9)",271,"boundary",(258,"cents * rate // 100","rate","tax_basis")),("tax_included(99,0)",99,"boundary"),("unit_price(100,0,False)",100,"normal")])

m("b","order_processor",f("packing_slip(lines: list[list]) -> list[str]","List SKUs for all positive quantity lines in source order.",
"return [sku for sku, quantity in lines if quantity > 0]",
"parcel_count(total_items: int, capacity: int) -> int","Use as many full or partial parcels as needed.",
"return -(-total_items // capacity)"),
[("packing_slip([['A',0],['B',2]])",["B"],"boundary",(["A","B"],"quantity > 0","quantity >= 0","empty_line")),("parcel_count(11,5)",3,"boundary",(2,"-(-total_items // capacity)","total_items // capacity","partial_parcel")),("parcel_count(0,5)",0,"boundary"),("packing_slip([])",[],"boundary")])

m("b","merchant_settlement",f("settlement(gross: int, fee_bp: int) -> int","Deduct the fee in basis points, rounding down the fee.",
"return gross - gross * fee_bp // 10000",
"unsettled(rows: list[list]) -> int","Sum the amount of pending settlement rows.",
"return sum(amount for amount, state in rows if state == 'pending')"),
[("settlement(10000,250)",9750,"normal",(7500,"// 10000","// 1000","rate_scale")),("unsettled([[30,'paid'],[50,'pending']])",50,"combination",(80,"if state == 'pending'","if state != 'void'","status_filter")),("unsettled([])",0,"boundary"),("settlement(50,0)",50,"normal")])

m("b","backorder_queue",f("take_orders(queue: list[str], count: int) -> list[str]","Return the first count waiting orders.",
"return queue[:count]",
"waiting_after(queue: list[str], filled: list[str]) -> list[str]","Return still-open orders retaining queue order.",
"return [order for order in queue if order not in filled]"),
[("take_orders(['A','B','C'],2)",["A","B"],"normal",(["B","C"],"queue[:count]","queue[max(0, len(queue)-count):]","dispatch_order")),("waiting_after(['Z','B','A'],['B'])",["Z","A"],"combination",(["A","Z"],"for order in queue if","for order in sorted(queue) if","queue_order")),("take_orders(['A'],0)",[],"boundary"),("waiting_after([],[])",[],"boundary")])

m("b","loyalty_points",f("earn(cents: int, multiplier: int) -> int","Award points for complete cents-per-dollar units before multiplying.",
"return (cents // 100) * multiplier",
"spend(balance: int, points: int) -> int","Redeem at most the available balance.",
"if points > balance:\n    raise ValueError('insufficient points')\nreturn balance - points"),
[("earn(199,2)",2,"boundary",(3,"(cents // 100) * multiplier","cents * multiplier // 100","rounding_order")),("spend(10,10)",0,"boundary",(E("ValueError"),"points > balance","points >= balance","exact_redemption")),("spend(10,11)",E("ValueError"),"exception"),("earn(200,2)",4,"normal")])
