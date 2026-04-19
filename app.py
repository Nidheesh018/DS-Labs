from flask import Flask, render_template, request
import time
import sys

# Increase recursion depth for Deep QuickSort/MergeSort on large arrays
sys.setrecursionlimit(2000)

app = Flask(__name__)

def detect_case(arr):
    if arr == sorted(arr): return "best"
    if arr == sorted(arr, reverse=True): return "worst"
    return "avg"

# --- ACTUAL LOGIC FOR ALL 10 ALGORITHMS ---

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
        min_idx = i
        for j in range(i+1, len(a)):
            if a[j] < a[min_idx]: min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a

def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i-1
        while j >= 0 and a[j] > key:
            a[j+1] = a[j]
            j -= 1
        a[j+1] = key
    return a

def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Merge logic
    res, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    return res + left[i:] + right[j:]

def quick_sort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def heap_sort(arr):
    import heapq
    a = arr.copy()
    heapq.heapify(a)
    return [heapq.heappop(a) for _ in range(len(a))]

def shell_sort(arr):
    a = arr.copy()
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 2
    return a

def counting_sort(arr):
    if not arr: return []
    max_val, min_val = max(arr), min(arr)
    rng = max_val - min_val + 1
    count = [0] * rng
    for x in arr: count[x - min_val] += 1
    res = []
    for i in range(rng):
        res.extend([i + min_val] * count[i])
    return res

def radix_sort(arr):
    if not arr: return []
    a = arr.copy()
    max_val = max(a)
    exp = 1
    while max_val // exp > 0:
        # Standard Counting Sort for Radix
        buckets = [[] for _ in range(10)]
        for x in a:
            index = (x // exp) % 10
            buckets[index].append(x)
        a = [item for sub in buckets for item in sub]
        exp *= 10
    return a

def bucket_sort(arr):
    if not arr: return []
    n = len(arr)
    max_val, min_val = max(arr), min(arr)
    if max_val == min_val: return arr
    bucket_count = n
    buckets = [[] for _ in range(bucket_count)]
    for x in arr:
        idx = int((x - min_val) / (max_val - min_val) * (bucket_count - 1))
        buckets[idx].append(x)
    res = []
    for b in buckets:
        res.extend(sorted(b))
    return res

algorithms = {
    "bubble": {"func": bubble_sort, "best":"O(n)", "avg":"O(n²)", "worst":"O(n²)"},
    "selection": {"func": selection_sort, "best":"O(n²)", "avg":"O(n²)", "worst":"O(n²)"},
    "insertion": {"func": insertion_sort, "best":"O(n)", "avg":"O(n²)", "worst":"O(n²)"},
    "merge": {"func": merge_sort, "best":"O(n log n)", "avg":"O(n log n)", "worst":"O(n log n)"},
    "quick": {"func": quick_sort, "best":"O(n log n)", "avg":"O(n log n)", "worst":"O(n²)"},
    "heap": {"func": heap_sort, "best":"O(n log n)", "avg":"O(n log n)", "worst":"O(n log n)"},
    "shell": {"func": shell_sort, "best":"O(n log n)", "avg":"O(n^1.5)", "worst":"O(n²)"},
    "counting": {"func": counting_sort, "best":"O(n+k)", "avg":"O(n+k)", "worst":"O(n+k)"},
    "radix": {"func": radix_sort, "best":"O(nk)", "avg":"O(nk)", "worst":"O(nk)"},
    "bucket": {"func": bucket_sort, "best":"O(n+k)", "avg":"O(n+k)", "worst":"O(n²)"}
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/compare", methods=["POST"])
def compare():
    selected = request.form.getlist("algo")
    arr = [int(x.strip()) for x in request.form["array"].split(",") if x.strip()]
    case_type = detect_case(arr)
    
    results = []
    for algo in selected:
        algo_info = algorithms[algo]
        start = time.perf_counter() # More precise than time.time()
        output = algo_info["func"](arr)
        end = time.perf_counter()
        
        results.append({
            "name": algo.capitalize(),
            "time": format(end - start, '.10f'), # High precision for small arrays
            "complexity": algo_info[case_type],
            "output": output
        })

    return render_template("result.html", results=results, case=case_type, original=arr)

if __name__ == "__main__":
    # Use port 8080 or 5001 instead of 5000
    app.run(debug=True, host='127.0.0.1', port=8080)