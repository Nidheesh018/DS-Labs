from flask import Flask, render_template, request
import time
import sys
import heapq

sys.setrecursionlimit(2000)
app = Flask(__name__)


def bubble_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(0, n-i-1):
            if a[j] > a[j+1]: a[j], a[j+1] = a[j+1], a[j]
    return a

def selection_sort(arr):
    a = arr.copy()
    for i in range(len(a)):
        m = i
        for j in range(i+1, len(a)):
            if a[j] < a[m]: m = j
        a[i], a[m] = a[m], a[i]
    return a

def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        k, j = a[i], i-1
        while j >= 0 and a[j] > k:
            a[j+1] = a[j]; j -= 1
        a[j+1] = k
    return a

def merge_sort(arr):
    if len(arr) <= 1: return arr
    m = len(arr) // 2
    l, r = merge_sort(arr[:m]), merge_sort(arr[m:])
    res, i, j = [], 0, 0
    while i < len(l) and j < len(r):
        if l[i] < r[j]: res.append(l[i]); i += 1
        else: res.append(r[j]); j += 1
    return res + l[i:] + r[j:]

def quick_sort(arr):
    if len(arr) <= 1: return arr
    p = arr[len(arr)//2]
    return quick_sort([x for x in arr if x < p]) + [x for x in arr if x == p] + quick_sort([x for x in arr if x > p])

def heap_sort(arr):
    a = arr.copy()
    heapq.heapify(a)
    return [heapq.heappop(a) for _ in range(len(a))]

def shell_sort(arr):
    a, n = arr.copy(), len(arr)
    g = n // 2
    while g > 0:
        for i in range(g, n):
            t, j = a[i], i
            while j >= g and a[j-g] > t:
                a[j] = a[j-g]; j -= g
            a[j] = t
        g //= 2
    return a

def counting_sort(arr):
    if not arr: return []
    mx, mn = max(arr), min(arr)
    cnt = [0] * (mx - mn + 1)
    for x in arr: cnt[x-mn] += 1
    res = []
    for i, c in enumerate(cnt): res.extend([i+mn] * c)
    return res

def radix_sort(arr):
    if not arr: return []
    a, mx = arr.copy(), max(arr)
    exp = 1
    while mx // exp > 0:
        buckets = [[] for _ in range(10)]
        for x in a: buckets[(x // exp) % 10].append(x)
        a = [x for b in buckets for x in b]
        exp *= 10
    return a

def bucket_sort(arr):
    if not arr: return []
    mx, mn = max(arr), min(arr)
    if mx == mn: return arr
    bkts = [[] for _ in range(len(arr))]
    for x in arr:
        idx = int((x-mn)/(mx-mn) * (len(arr)-1))
        bkts[idx].append(x)
    res = []
    for b in bkts: res.extend(sorted(b))
    return res


def linear_search(arr, target):
    for i, x in enumerate(arr):
        if x == target: return f"Found {target} at Index {i}"
    return f"{target} Not Found"

def binary_search(arr, target):
    a = sorted(arr)
    l, r = 0, len(a)-1
    while l <= r:
        m = (l+r)//2
        if a[m] == target: return f"Found {target} at Index {m} (Sorted)"
        if a[m] < target: l = m+1
        else: r = m-1
    return f"{target} Not Found"

algorithms = {
    "bubble": {"f": bubble_sort, "b":"O(n)", "a":"O(n²)", "w":"O(n²)"},
    "selection": {"f": selection_sort, "b":"O(n²)", "a":"O(n²)", "w":"O(n²)"},
    "insertion": {"f": insertion_sort, "b":"O(n)", "a":"O(n²)", "w":"O(n²)"},
    "merge": {"f": merge_sort, "b":"O(n log n)", "a":"O(n log n)", "w":"O(n log n)"},
    "quick": {"f": quick_sort, "b":"O(n log n)", "a":"O(n log n)", "w":"O(n²)"},
    "heap": {"f": heap_sort, "b":"O(n log n)", "a":"O(n log n)", "w":"O(n log n)"},
    "shell": {"f": shell_sort, "b":"O(n log n)", "a":"O(n^1.5)", "w":"O(n²)"},
    "counting": {"f": counting_sort, "b":"O(n+k)", "a":"O(n+k)", "w":"O(n+k)"},
    "radix": {"f": radix_sort, "b":"O(nk)", "a":"O(nk)", "w":"O(nk)"},
    "bucket": {"f": bucket_sort, "b":"O(n+k)", "a":"O(n+k)", "w":"O(n²)"},
    "linear": {"f": linear_search, "b":"O(1)", "a":"O(n)", "w":"O(n)"},
    "binary": {"f": binary_search, "b":"O(1)", "a":"O(log n)", "w":"O(log n)"}
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/compare", methods=["POST"])
def compare():
    selected = request.form.getlist("algo")
    raw_arr = request.form.get("array", "")
    target = request.form.get("target", "")
    arr = [int(x.strip()) for x in raw_arr.split(",") if x.strip()]
    
    case_type = "avg"
    if arr == sorted(arr): case_type = "best"
    elif arr == sorted(arr, reverse=True): case_type = "worst"
    
    results = []
    for algo_id in selected:
        info = algorithms[algo_id]
        start = time.perf_counter()
        output = info["f"](arr, int(target) if target else 0) if algo_id in ["linear", "binary"] else info["f"](arr)
        
        results.append({
            "name": algo_id.upper(),
            "time": format(time.perf_counter() - start, '.8f'),
            "output": output,
            "best": info["b"], "avg": info["a"], "worst": info["w"],
            "current_case": case_type
        })
    return render_template("result.html", results=results, original=arr, case=case_type)

if __name__ == "__main__":
    app.run(debug=True, port=8080)


# this is a just made version this will be enhanced further and will be done 
