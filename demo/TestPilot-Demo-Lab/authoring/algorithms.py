
from spec import E, f, group

m = group("algorithms")

m("g","stack",f("push(stack: list[int], value: int) -> list[int]","Return a stack with value on top, leaving the input alone.",
"return stack + [value]",
"top(stack: list[int]) -> int","Read the top item of a nonempty stack.",
"return stack[-1]"),
[("push([2],4)",[2,4],"normal"),("push([],0)",[0],"boundary"),("top([1,-1])",-1,"special"),("top([])",E("IndexError"),"exception")])

m("g","stable_priority",f("ordered(tasks: list[list]) -> list[list]","Order by descending priority, with ties in submission order.",
"return sorted(tasks, key=lambda task: -task[1])",
"next_task(tasks: list[list]) -> str","Return the ID of the first scheduled task.",
"return ordered(tasks)[0][0]"),
[("ordered([['z',3],['a',3],['b',4]])",[["b",4],["z",3],["a",3]],"normal"),("ordered([])",[],"boundary"),("next_task([['u',-1],['v',0]])","v","special"),("next_task([])",E("IndexError"),"exception")])

m("g","run_length",f("pack(values: list[int]) -> list[list[int]]","Encode adjacent equal values as value/count records.",
"packed = []\nfor value in values:\n    if packed and packed[-1][0] == value:\n        packed[-1][1] += 1\n    else:\n        packed.append([value, 1])\nreturn packed",
"unpack(records: list[list[int]]) -> list[int]","Expand value/count records into the corresponding sequence.",
"return [value for value, count in records for _ in range(count)]"),
[("pack([1,1,2,1])",[[1,2],[2,1],[1,1]],"normal"),("pack([])",[],"boundary"),("unpack([[1,0],[5,2]])",[5,5],"boundary"),("unpack([[5]])",E("ValueError"),"exception")])

m("g","interval_overlap",f("overlaps(a0: int, a1: int, b0: int, b1: int) -> bool","Detect intersection of two half-open ranges.",
"return max(a0, b0) < min(a1, b1)",
"overlap_width(a0: int, a1: int, b0: int, b1: int) -> int","Return the nonnegative size of their intersection.",
"return max(0, min(a1, b1) - max(a0, b0))"),
[("overlaps(1,4,2,7)",True,"normal"),("overlaps(1,2,2,3)",False,"boundary"),("overlap_width(-2,3,0,5)",3,"combination"),("overlaps(None,1,0,2)",E("TypeError"),"exception")])

m("b","binary_search",f("locate(values: list[int], target: int) -> int","Find a target in a sorted sequence of distinct integers.",
"left, right = 0, len(values) - 1\nwhile left <= right:\n    mid = (left + right) // 2\n    if values[mid] == target:\n        return mid\n    if values[mid] < target:\n        left = mid + 1\n    else:\n        right = mid - 1\nreturn -1",
"insertion_point(values: list[int], target: int) -> int","Return the index before any existing equal elements.",
"from bisect import bisect_left, bisect_right\n\nreturn bisect_left(values, target)"),
[("locate([1,3,5],5)",2,"boundary",(-1,"while left <= right","while left < right","last_candidate")),("insertion_point([1,3,3],3)",1,"boundary",(3,"return bisect_left","return bisect_right","duplicate_position")),("locate([],3)",-1,"boundary"),("locate([1,3,5],3)",1,"normal")])

m("b","sorting_algorithms",f("ranked(rows: list[list]) -> list[list]","Sort by score ascending, preserving tie order.",
"return sorted(rows, key=lambda row: row[1])",
"lowest(values: list[int], count: int) -> list[int]","Return the count smallest values in ascending order.",
"return sorted(values)[:count]"),
[("ranked([['z',1],['a',1]])",[["z",1],["a",1]],"boundary",([["a",1],["z",1]],"lambda row: row[1]","lambda row: (row[1], row[0])","tie_stability")),("lowest([8,1,4],2)",[1,4],"normal",([4,8],"sorted(values)[:count]","sorted(values)[-count:]","wrong_tail")),("ranked([])",[],"boundary"),("lowest([1,2],2)",[1,2],"boundary")])

m("b","queue",f("pop_next(values: list[str]) -> list[str]","Return the remaining FIFO queue after one removal.",
"return values[1:]",
"queue_item(values: list[str], position: int) -> str","Read the item at a one-based queue position.",
"if position < 1:\n    raise ValueError('position must be positive')\nreturn values[position-1]"),
[("pop_next(['a','b','c'])",["b","c"],"normal",(["a","b"],"values[1:]","values[:-1]","fifo_removal")),("queue_item(['a','b'],1)","a","boundary",("b","values[position-1]","values[position]","index_origin")),("pop_next([])",[],"boundary"),("queue_item([],0)",E("ValueError"),"exception")])

m("b","tree_traversal",f("preorder(tree: list | None) -> list[int]","Visit a nested value/left/right tree root first.",
"if tree is None:\n    return []\nvalue, left, right = tree\nreturn [value] + preorder(left) + preorder(right)",
"leaf_count(tree: list | None) -> int","Count nodes with neither child.",
"if tree is None:\n    return 0\n_, left, right = tree\nif left is None and right is None:\n    return 1\nreturn leaf_count(left) + leaf_count(right)"),
[("preorder([1,[2,None,None],[3,None,None]])",[1,2,3],"normal",([1,3,2],"preorder(left) + preorder(right)","preorder(right) + preorder(left)","traversal_order")),("leaf_count([1,[2,None,None],[3,None,None]])",2,"combination",(1,"leaf_count(left) + leaf_count(right)","max(leaf_count(left), leaf_count(right))","subtree_aggregation")),("preorder(None)",[],"boundary"),("leaf_count([5,None,None])",1,"boundary")])

m("b","graph_search",f("reachable(edges: dict[str, list[str]], start: str) -> list[str]","Return the sorted reachable vertex set including start.",
"seen, pending = {start}, [start]\nwhile pending:\n    for node in edges.get(pending.pop(), []):\n        if node not in seen:\n            seen.add(node)\n            pending.append(node)\nreturn sorted(seen)",
"incoming(edges: dict[str, list[str]], target: str) -> int","Count vertices with a direct edge incoming to target.",
"return sum(target in destinations for destinations in edges.values())"),
[("reachable({'a':['b'],'b':['c']},'a')",["a","b","c"],"combination",(["a","b"],"            pending.append(node)","            continue","transitive_edges")),("incoming({'a':['x','x'],'b':['x']},'x')",2,"boundary",(3,"target in destinations","destinations.count(target)","parallel_edges")),("reachable({},'a')",["a"],"boundary"),("incoming({},'a')",0,"boundary")])

m("b","pagination",f("page_count(total: int, size: int) -> int","Count complete and partial pages.",
"return (total + size - 1) // size",
"page_items(items: list[int], page: int, size: int) -> list[int]","Select a one-based page.",
"start = (page - 1) * size\nreturn items[start:start + size]"),
[("page_count(11,5)",3,"boundary",(2,"(total + size - 1) // size","total // size","partial_page")),("page_items([1,2,3,4],1,2)",[1,2],"boundary",([3,4],"(page - 1) * size","page * size","page_origin")),("page_count(10,5)",2,"normal"),("page_count(1,0)",E("ZeroDivisionError"),"exception")])

m("b","cache_manager",f("remaining_ttl(inserted: int, ttl: int, now: int) -> int","Return nonnegative remaining lifetime of a cache entry.",
"return max(0, inserted + ttl - now)",
"eviction_order(last_used: dict[str, int]) -> list[str]","List eviction candidates oldest-first, then by name.",
"return sorted(last_used, key=lambda key: (last_used[key], key))"),
[("remaining_ttl(5,3,9)",0,"boundary",(-1,"max(0, inserted + ttl - now)","inserted + ttl - now","expiry_floor")),("eviction_order({'z':1,'a':1,'m':0})",["m","a","z"],"combination",(["m","z","a"],"(last_used[key], key)","last_used[key]","tie_breaking")),("remaining_ttl(5,3,6)",2,"normal"),("eviction_order({})",[],"boundary")])

m("b","sliding_extrema",f("window_peaks(values: list[int], width: int) -> list[int]","Return one maximum for each complete window.",
"return [max(values[i:i+width]) for i in range(len(values) - width + 1)]",
"rise_count(values: list[int]) -> int","Count strictly increasing adjacent pairs.",
"return sum(a < b for a, b in zip(values, values[1:]))"),
[("window_peaks([1,4,2],2)",[4,4],"normal",([4],"len(values) - width + 1","len(values) - width","last_window")),("rise_count([1,1,2])",1,"boundary",(2,"sum(a < b","sum(a <= b","plateau_count")),("window_peaks([1],2)",[],"boundary"),("rise_count([])",0,"boundary")])
