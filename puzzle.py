import sys
import time
import random
import collections


def read_fragments(path):
    with open(path, encoding="utf-8-sig") as fh:
        words = fh.read().replace(",", " ").split()
    return [w.strip() for w in words if w.strip().isdigit()]


def build_edges(frags):
    return [(int(f[:2]), int(f[-2:]), len(f) - 2) for f in frags]


def chain_string(frags, order):
    out = ""
    for i in order:
        out += frags[i] if not out else frags[i][2:]
    return out


def greedy_solution(edges, rnd, tries):
    n = len(edges)
    out_adj = collections.defaultdict(list)
    for i, (u, v, w) in enumerate(edges):
        out_adj[u].append(i)
    best_order, best_w = [], -1
    for _ in range(tries):
        used = [False] * n
        order, w = [], 0
        cur = rnd.randrange(100)
        for _ in range(n):
            cands = [i for i in out_adj.get(cur, ()) if not used[i]]
            if not cands:
                break
            if len(cands) > 1:
                pick = min(cands, key=lambda i: (len([j for j in out_adj.get(edges[i][1], ()) if not used[j]]), rnd.random()))
            else:
                pick = cands[0]
            used[pick] = True
            order.append(pick)
            w += edges[pick][2]
            cur = edges[pick][1]
        if w > best_w:
            best_w, best_order = w, order
    return best_order, best_w


def search(edges, start_order, time_limit):
    n = len(edges)
    tail = [e[1] for e in edges]
    out_adj = collections.defaultdict(list)
    for i, (u, v, w) in enumerate(edges):
        out_adj[u].append(i)
    out_r = [0] * 100
    in_r = [0] * 100
    for u, v, w in edges:
        out_r[u] += 1
        in_r[v] += 1
    S = sum(min(out_r[x], in_r[x]) for x in range(100))
    used = [False] * n
    path = []
    best_order = list(start_order)
    best_k = len(start_order)
    deadline = time.time() + time_limit
    stop = False

    def touch(v, d_out, d_in):
        nonlocal S
        old = min(out_r[v], in_r[v])
        out_r[v] += d_out
        in_r[v] += d_in
        S += min(out_r[v], in_r[v]) - old

    def reachable(cur):
        seen = [False] * 100
        seen[cur] = True
        stack = [cur]
        cnt = 0
        while stack:
            x = stack.pop()
            for ei in out_adj.get(x, ()):
                if used[ei]:
                    continue
                cnt += 1
                y = tail[ei]
                if not seen[y]:
                    seen[y] = True
                    stack.append(y)
        return cnt

    def dfs(cur, k):
        nonlocal best_k, best_order, stop
        if k > best_k:
            best_k = k
            best_order = list(path)
            if best_k == n:
                stop = True
                return
        if k + S + 1 <= best_k:
            return
        if k + reachable(cur) <= best_k:
            return
        cands = [ei for ei in out_adj.get(cur, ()) if not used[ei]]
        if not cands:
            return
        if len(cands) > 1:
            cands.sort(key=lambda ei: (max(out_r[tail[ei]] - in_r[tail[ei]], 0), len([j for j in out_adj.get(tail[ei], ()) if not used[j]])))
        for ei in cands:
            v = tail[ei]
            used[ei] = True
            path.append(ei)
            touch(cur, -1, 0)
            touch(v, 0, -1)
            dfs(v, k + 1)
            touch(v, 0, 1)
            touch(cur, 1, 0)
            path.pop()
            used[ei] = False
            if stop or time.time() > deadline:
                stop = True
                return

    for start in range(100):
        if not out_adj.get(start):
            continue
        used[:] = [False] * n
        path[:] = []
        for i in range(100):
            out_r[i] = 0
            in_r[i] = 0
        for u, v, w in edges:
            out_r[u] += 1
            in_r[v] += 1
        S = sum(min(out_r[x], in_r[x]) for x in range(100))
        dfs(start, 0)
        if stop:
            break
    return best_order, best_k


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "fragments.txt"
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    frags = read_fragments(path)
    edges = build_edges(frags)
    rnd = random.Random(20260928)
    start_order, _ = greedy_solution(edges, rnd, 30000)
    order, k = search(edges, start_order, limit)
    result = chain_string(frags, order)
    print("fragments:", len(frags))
    print("used:", k)
    print("length:", len(result))
    print(result)
    with open("answer.txt", "w", encoding="utf-8") as fh:
        fh.write(result)


if __name__ == "__main__":
    main()
