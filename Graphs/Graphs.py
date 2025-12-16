import concurrent.futures
import sys # Для рекурсии в тестах
import heapq
import threading
import random
from collections import deque, defaultdict
import networkx as nx
from planarity import is_planar as nx_is_planar


class Graph:
    def __init__(self, filepath: str, filetype: str):
        self._size = 0
        self._adjacency_matrix = None
        self._adjacency_list = None
        self._directed = None
        self._load_graph(filepath, filetype)
        self._check_directed()
        self._planarity_inspector = None

    def _load_graph(self, filepath, filetype):
        with open(filepath, 'r') as f:
            lines = f.read().strip().split('\n')
        self._size = int(lines[0])

        if filetype == 'edges':
            self._adjacency_matrix = [[0] * self._size for _ in range(self._size)]
            self._adjacency_list = [[] for _ in range(self._size)]
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) == 2:
                    u, v = map(int, parts)
                    w = 1
                elif len(parts) == 3:
                    u, v, w = map(int, parts)
                else:
                    raise ValueError(f"Некорректная строка с ребром: '{line}'")
                self._adjacency_matrix[u - 1][v - 1] = w
                self._adjacency_list[u - 1].append((v, w))

        elif filetype == 'adjacency_list':
            self._adjacency_list = [[] for _ in range(self._size)]
            self._adjacency_matrix = [[0] * self._size for _ in range(self._size)]
            for i, line in enumerate(lines[1:]):
                if line.strip():
                    parts = line.split()
                    for p in parts:
                        if ':' in p:
                            v_str, w_str = p.split(':')
                            v, w = int(v_str), int(w_str)
                        else:
                            v = int(p)
                            w = 1
                        self._adjacency_list[i].append((v, w))
                        self._adjacency_matrix[i][v - 1] = w

        elif filetype == 'adjacency_matrix':
            matrix = [list(map(int, line.split())) for line in lines[1:]]
            self._adjacency_matrix = matrix
            self._adjacency_list = [[] for _ in range(self._size)]
            for i in range(self._size):
                for j in range(self._size):
                    if matrix[i][j] != 0:
                        self._adjacency_list[i].append((j + 1, matrix[i][j]))

        else:
            raise ValueError(f"Неизвестный тип файла: {filetype}")

    def _check_directed(self):
        for u in range(self._size):
            for v, w in self._adjacency_list[u]:
                found = False
                for vv, ww in self._adjacency_list[v-1]:
                    if vv == u+1 and ww == w:
                        found = True
                        break
                if not found:
                    self._directed = True
                    return
        self._directed = False

    def size(self):
        return self._size

    def weight(self, u, v):
        return self._adjacency_matrix[u-1][v-1]

    def is_edge(self, u, v):
        return self._adjacency_matrix[u-1][v-1] != 0

    def adjacency_matrix(self):
        return self._adjacency_matrix

    def adjacency_list(self, u):
        return [v for v, w in self._adjacency_list[u-1]]

    def list_of_edges(self, u=None):
        edges = []
        if u is None:
            for i in range(self._size):
                for v, w in self._adjacency_list[i]:
                    edges.append((i+1, v, w))
        else:
            for v, w in self._adjacency_list[u-1]:
                edges.append((u, v, w))
        return edges

    def is_directed(self):
        return self._directed

    # Task1
    def connected_components(self):
        visited = [False] * self._size
        components = []

        adjacency = [[] for _ in range(self._size)]
        if self._directed:
            for u in range(self._size):
                for v, _ in self._adjacency_list[u]:
                    adjacency[u].append(v - 1)
                    adjacency[v - 1].append(u)
        else:
            for u in range(self._size):
                for v, _ in self._adjacency_list[u]:
                    adjacency[u].append(v - 1)

        def dfs(u, component):
            visited[u] = True
            component.append(u + 1)
            for v in adjacency[u]:
                if not visited[v]:
                    dfs(v, component)

        for i in range(self._size):
            if not visited[i]:
                component = []
                dfs(i, component)
                components.append(component)

        if self._directed:
            if len(components) == 1:
                print("Digraph is weakly connected")
            else:
                print("Digraph is not connected")
        else:
            if len(components) == 1:
                print("Graph is connected")
            else:
                print("Graph is not connected")

        print("\nConnected components:")
        for comp in components:
            comp.sort()
            print(comp)

        return components

    # Task5 + Task13
    def is_bipartite(self):
        color = [-1] * self._size
        for start in range(self._size):
            if color[start] == -1:
                queue = deque([start])
                color[start] = 0
                while queue:
                    u = queue.popleft()
                    for v, w in self._adjacency_list[u]:
                        v_index = v - 1
                        if color[v_index] == -1:
                            color[v_index] = 1 - color[u]
                            queue.append(v_index)
                        elif color[v_index] == color[u]:
                            return False, None
        part1 = [i+1 for i in range(self._size) if color[i] == 0]
        part2 = [i+1 for i in range(self._size) if color[i] == 1]
        return True, (part1, part2)

    def maximum_bipartite_matching(self):
        is_bipartite, parts = self.is_bipartite()
        if not is_bipartite:
            return None, None

        left, right = parts
        right_set = set(right)

        adj = {u: [] for u in left}
        for u in left:
            for v, w in self._adjacency_list[u - 1]:
                if v in right_set:
                    adj[u].append(v)
            adj[u].sort()

        pair_u = {u: None for u in left}
        pair_v = {v: None for v in right}
        dist = {}

        def bfs():
            queue = deque()
            for u in left:
                if pair_u[u] is None:
                    dist[u] = 0
                    queue.append(u)
                else:
                    dist[u] = float('inf')
            dist[None] = float('inf')

            while queue:
                u = queue.popleft()
                if dist[u] < dist[None]:
                    for v in adj[u]:
                        pv = pair_v[v]
                        if pv is None:
                            dist[None] = dist[u] + 1
                        elif dist[pv] == float('inf'):
                            dist[pv] = dist[u] + 1
                            queue.append(pv)
            return dist[None] != float('inf')

        def dfs(u):
            if u is not None:
                for v in adj[u]:
                    pv = pair_v[v]
                    if pv is None or (dist[pv] == dist[u] + 1 and dfs(pv)):
                        pair_u[u] = v
                        pair_v[v] = u
                        return True
                dist[u] = float('inf')
                return False
            return True

        matching = 0
        while bfs():
            for u in sorted(left):
                if pair_u[u] is None and dfs(u):
                    matching += 1

        result = [(u, pair_u[u], None) for u in sorted(left) if pair_u[u] is not None]
        return matching, result

    # Task7
    def find_sccs_kosaraju(self):
        if not self._directed:
            print("Предупреждение: Алгоритм Косараджу обычно применяется к ориентированным графам.")
            print("Для неориентированного графа каждая связная компонента является SCC.")

        num_vertices = self._size
        visited = [False] * num_vertices
        finish_order_stack = []

        def dfs1(u_0_indexed):
            visited[u_0_indexed] = True
            for v_1_indexed, _ in self._adjacency_list[u_0_indexed]:
                v_0_indexed = v_1_indexed - 1
                if not visited[v_0_indexed]:
                    dfs1(v_0_indexed)
            finish_order_stack.append(u_0_indexed)

        for i in range(num_vertices):
            if not visited[i]:
                dfs1(i)

        g_transpose_adj_list = [[] for _ in range(num_vertices)]
        for u_0_indexed in range(num_vertices):
            for v_1_indexed, _ in self._adjacency_list[u_0_indexed]:
                v_0_indexed = v_1_indexed - 1
                g_transpose_adj_list[v_0_indexed].append(u_0_indexed)

        visited = [False] * num_vertices
        sccs = []

        while finish_order_stack:
            u_0_indexed = finish_order_stack.pop()
            if not visited[u_0_indexed]:
                current_scc = []

                def dfs2(v_0_indexed):
                    visited[v_0_indexed] = True
                    current_scc.append(v_0_indexed + 1)
                    for neighbor_0_indexed in g_transpose_adj_list[v_0_indexed]:
                        if not visited[neighbor_0_indexed]:
                            dfs2(neighbor_0_indexed)

                dfs2(u_0_indexed)
                sccs.append(current_scc)

        return sccs

    # Task8 + Task2
    def find_bridges_and_articulations(self):
        self._time = 0
        tin = [-1] * self._size
        low = [-1] * self._size
        visited = [False] * self._size
        bridges = []
        articulations = set()

        def dfs(u, parent):
            visited[u] = True
            tin[u] = low[u] = self._time
            self._time += 1
            children = 0

            for v, _ in self._adjacency_list[u]:
                v -= 1
                if v == parent:
                    continue
                if visited[v]:
                    low[u] = min(low[u], tin[v])
                else:
                    dfs(v, u)
                    low[u] = min(low[u], low[v])
                    if low[v] > tin[u]:
                        bridges.append((u + 1, v + 1))
                    if low[v] >= tin[u] and parent != -1:
                        articulations.add(u + 1)
                    children += 1

            if parent == -1 and children > 1:
                articulations.add(u + 1)

        for i in range(self._size):
            if not visited[i]:
                dfs(i, -1)

        bridges.sort()
        articulations = sorted(articulations)

        print("Bridges:")
        print(bridges)
        print("Cut vertices:")
        print(articulations)

        return bridges, articulations

    # Task9 + Task3
    def _is_connected(self):
        visited = [False] * self._size

        def dfs(u):
            visited[u] = True
            for v, w in self._adjacency_list[u]:
                if not visited[v - 1]:
                    dfs(v - 1)

        dfs(0)  # начинаем обход с вершины 0 (нумерация с 0)
        return all(visited)

    def minimum_spanning_tree_kruskal(self):
        if self._directed:
            raise ValueError("Минимальное остовное дерево не определено для ориентированных графов")

        if not self._is_connected():
            raise ValueError("Граф несвязный — минимальное остовное дерево не существует")

        parent = list(range(self._size))
        rank = [0] * self._size

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        def union(u, v):
            ru, rv = find(u), find(v)
            if ru == rv:
                return False
            if rank[ru] < rank[rv]:
                parent[ru] = rv
            else:
                parent[rv] = ru
                if rank[ru] == rank[rv]:
                    rank[ru] += 1
            return True

        edges = self.list_of_edges()
        edges.sort(key=lambda x: x[2])

        mst = []
        total_weight = 0
        for u, v, w in edges:
            if union(u - 1, v - 1):
                mst.append((u, v, w))
                total_weight += w
                if len(mst) == self._size - 1:
                    break

        print("Minimal spanning tree:")
        for u, v, w in mst:
            print(f"{u}-{v}: {w}")

        return mst, total_weight

    # Task10 + Task4
    def floyd_warshall(self):
        n = self._size
        INF = float('inf')

        dist = [[INF] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
        for u in range(n):
            for v, w in self._adjacency_list[u]:
                dist[u][v - 1] = w

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        self._dist = dist
        return dist

    def degree_vector(self):
        return [len(self._adjacency_list[i]) for i in range(self._size)]

    def eccentricities(self):
        if not hasattr(self, '_dist'):
            self.floyd_warshall()

        n = self._size
        ecc = []
        INF = float('inf')
        for i in range(n):
            max_dist = max(self._dist[i][j] for j in range(n) if self._dist[i][j] != INF)
            ecc.append(max_dist)
        return ecc

    def diameter_and_peripheral(self):
        ecc = self.eccentricities()
        diameter = max(ecc)
        peripheral = [i + 1 for i, e in enumerate(ecc) if e == diameter]
        return diameter, peripheral

    def radius_and_central(self):
        ecc = self.eccentricities()
        radius = min(ecc)
        central = [i + 1 for i, e in enumerate(ecc) if e == radius]
        return radius, central

    def reconstruct_path(self, u, v):
        u -= 1
        v -= 1
        if not hasattr(self, '_next'):
            self.floyd_warshall()

        if self._next[u][v] is None:
            return None

        path = [u]
        while u != v:
            u = self._next[u][v]
            path.append(u)

        return [x + 1 for x in path]

    def component_characteristics(self):
        if not hasattr(self, '_dist'):
            self.floyd_warshall()

        components = self.connected_components()
        INF = float('inf')

        for idx, comp in enumerate(components):
            print(f"\nComponent {idx + 1}:" if len(components) > 1 else "")
            sub_indices = [v - 1 for v in comp]  # 0-based индексы вершин
            degrees = [len(self._adjacency_list[i]) for i in sub_indices]
            print("Vertices degrees:")
            print(degrees)

            ecc = []
            for u in sub_indices:
                max_dist = max(
                    self._dist[u][v] for v in sub_indices if self._dist[u][v] != INF
                )
                ecc.append(max_dist)
            print("Eccentricity:")
            print(ecc)

            radius = min(ecc)
            diameter = max(ecc)

            central = [comp[i] for i, e in enumerate(ecc) if e == radius]
            peripheral = [comp[i] for i, e in enumerate(ecc) if e == diameter]

            print(f"R = {radius}")
            print("Central vertices:")
            print(sorted(central))
            print(f"D = {diameter}")
            print("Peripherial vertices:")
            print(sorted(peripheral))

    # Task11
    def bellman_ford_moor(self, start):
        start -= 1
        dist = [float('inf')] * self._size
        dist[start] = 0

        edges = []
        for u in range(self._size):
            for v, w in self._adjacency_list[u]:
                edges.append((u, v - 1, w))

        for _ in range(self._size - 1):
            for u, v, w in edges:
                if dist[u] != float('inf') and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w

        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                print("Graph contains a negative-weight cycle")
                return

        result = {i + 1: (int(dist[i]) if dist[i] != float('inf') else float('inf')) for i in range(self._size)}
        print(f"Shotest paths lengths from {start + 1}:\n{result}")
        return result

    # Task14
    def ford_fulkerson(self, source, sink):
        if not self._directed:
            raise ValueError("Метод Форда-Фалкерсона применяется только к ориентированным графам.")

        source -= 1
        sink -= 1
        size = self._size

        residual = [row[:] for row in self._adjacency_matrix]
        original = [row[:] for row in self._adjacency_matrix]  # для восстановления потока
        max_flow = 0
        parent = [-1] * size

        def bfs():
            visited = [False] * size
            queue = []
            queue.append(source)
            visited[source] = True
            while queue:
                u = queue.pop(0)
                for v in range(size):
                    if not visited[v] and residual[u][v] > 0:
                        queue.append(v)
                        visited[v] = True
                        parent[v] = u
                        if v == sink:
                            return True
            return False

        while bfs():
            path_flow = float('inf')
            v = sink
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                v = u

            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = parent[v]

            max_flow += path_flow

        flow_result = {}
        for u in range(size):
            for v in range(size):
                if original[u][v] > 0 and residual[u][v] < original[u][v]:
                    flow_value = original[u][v] - residual[u][v]
                    flow_result[(u + 1, v + 1)] = flow_value

        return max_flow, flow_result

    # Task15 + Task19
    def ant_colony_traversal(self, num_ants=10, num_iterations=100, alpha=1.0, beta=5.0, evaporation=0.5, q=100):
        n = self._size
        pheromone = [[1 for _ in range(n)] for _ in range(n)]
        distance = [[float('inf') if i != j and self._adjacency_matrix[i][j] == 0 else self._adjacency_matrix[i][j]
                     for j in range(n)] for i in range(n)]

        best_path = None
        best_length = float('inf')
        lock = threading.Lock()

        def ant_thread():
            nonlocal best_path, best_length
            path = []
            visited = set()
            current = random.randint(0, n - 1)
            start = current
            path.append(current)
            visited.add(current)

            while len(visited) < n:
                probabilities = []
                denom = 0
                for j in range(n):
                    if j not in visited and distance[current][j] != float('inf'):
                        tau = pheromone[current][j] ** alpha
                        eta = (1.0 / distance[current][j]) ** beta
                        prob = tau * eta
                        denom += prob
                        probabilities.append((j, prob))
                    else:
                        probabilities.append((j, 0))

                if denom == 0:
                    return

                r = random.random()
                acc = 0
                for j, prob in probabilities:
                    acc += prob / denom
                    if r <= acc:
                        next_city = j
                        break
                else:
                    return

                path.append(next_city)
                visited.add(next_city)
                current = next_city

            path.append(start)
            length = sum(distance[path[i]][path[i + 1]] for i in range(len(path) - 1))

            with lock:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    pheromone[u][v] += q / length
                    if not self._directed:
                        pheromone[v][u] += q / length

                if length < best_length:
                    best_length = length
                    best_path = path[:]

        for _ in range(num_iterations):
            threads = [threading.Thread(target=ant_thread) for _ in range(num_ants)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            for i in range(n):
                for j in range(n):
                    pheromone[i][j] *= (1 - evaporation)

        print(f"Length of shortest traveling salesman path is: {int(best_length)}.")
        print("Path:")
        for i in range(len(best_path) - 1):
            u = best_path[i] + 1
            v = best_path[i + 1] + 1
            w = self.weight(u, v)
            print(f"{u}-{v} : {w}")

    # Task16
    def boruvka_mst_parallel(self):
        parent = list(range(self._size))  # union-find parent
        rank = [0] * self._size  # union-find rank

        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u

        def union(u, v):
            ru, rv = find(u), find(v)
            if ru != rv:
                if rank[ru] < rank[rv]:
                    parent[ru] = rv
                elif rank[ru] > rank[rv]:
                    parent[rv] = ru
                else:
                    parent[rv] = ru
                    rank[ru] += 1
                return True
            return False

        mst_edges = []
        num_components = self._size

        while num_components > 1:
            cheapest = [None] * self._size

            def find_min_edge(u):
                u_root = find(u)
                min_edge = None
                for v, w in self._adjacency_list[u]:
                    v_root = find(v - 1)
                    if u_root != v_root:
                        if (min_edge is None) or (w < min_edge[2]):
                            min_edge = (u + 1, v, w)
                return (u_root, min_edge)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(find_min_edge, range(self._size)))

            # Если ни у какого компонента нет минимального ребра, значит граф несвязный
            if all(edge is None for _, edge in results):
                print("Graph is not connected")
                return []

            for comp, edge in results:
                if edge is not None:
                    idx = comp
                    if cheapest[idx] is None or edge[2] < cheapest[idx][2]:
                        cheapest[idx] = edge

            for edge in cheapest:
                if edge is not None:
                    u, v, w = edge
                    if union(u - 1, v - 1):
                        mst_edges.append(edge)
                        num_components -= 1

        total_weight = sum(w for _, _, w in mst_edges)
        print(f"Weight of minimal spanning tree: {total_weight}")
        print("Minimal spanning tree:")
        for u, v, w in mst_edges:
            print(f"{u}-{v}: {w}")

        return mst_edges

    # Task17
    def areas_from_vertex(self, start_vertex: int):
        size = self._size
        adj = self._adjacency_list

        all_weights_one = all(w == 1 for edges in adj for _, w in edges)

        dist = [float('inf')] * size
        dist[start_vertex - 1] = 0

        if all_weights_one:
            queue = deque([start_vertex - 1])
            while queue:
                u = queue.popleft()
                for v, w in adj[u]:
                    if dist[v - 1] == float('inf'):
                        dist[v - 1] = dist[u] + 1
                        queue.append(v - 1)
        else:
            heap = [(0, start_vertex - 1)]
            while heap:
                cur_d, u = heapq.heappop(heap)
                if cur_d > dist[u]:
                    continue
                for v, w in adj[u]:
                    nd = cur_d + w
                    if nd < dist[v - 1]:
                        dist[v - 1] = nd
                        heapq.heappush(heap, (nd, v - 1))

        reachable_dist = [d for d in dist if d != float('inf')]
        if not reachable_dist:
            return {1: [], 2: [], 3: [], 4: []}

        max_dist = max(reachable_dist)

        areas = {1: [], 2: [], 3: [], 4: []}

        for i, d in enumerate(dist):
            if d == float('inf'):
                areas[4].append(i + 1)
            else:
                if d <= max_dist / 4:
                    areas[1].append(i + 1)
                elif d <= max_dist / 2:
                    areas[2].append(i + 1)
                elif d <= 3 * max_dist / 4:
                    areas[3].append(i + 1)
                else:
                    areas[4].append(i + 1)

        return areas

    # Task18
    def tsp_branch_and_bound_fast(self):
        n = self._size
        adj = self._adjacency_matrix
        best_cost = float('inf')
        best_path = []

        min_two = []
        for i in range(n):
            row = sorted([adj[i][j] for j in range(n) if adj[i][j] > 0])
            if len(row) >= 2:
                min_two.append((row[0], row[1]))
            elif len(row) == 1:
                min_two.append((row[0], row[0]))
            else:
                min_two.append((0, 0))

        def lower_bound(path, visited, cost_so_far):
            bound = cost_so_far
            for i in range(n):
                if i in visited:
                    continue
                bound += sum(min_two[i]) / 2
            return bound

        heap = []
        start = 0
        heapq.heappush(heap, (0, 0, [start], {start}))

        while heap:
            est, cost, path, visited = heapq.heappop(heap)

            if est >= best_cost:
                continue

            if len(path) == n:
                back_cost = adj[path[-1]][start]
                if back_cost == 0:
                    continue
                total = cost + back_cost
                if total < best_cost:
                    best_cost = total
                    best_path = path + [start]
                continue

            last = path[-1]
            for next_v in range(n):
                if next_v not in visited and adj[last][next_v] > 0:
                    new_cost = cost + adj[last][next_v]
                    new_path = path + [next_v]
                    new_visited = visited | {next_v}
                    lb = lower_bound(new_path, new_visited, new_cost)
                    if lb < best_cost:
                        heapq.heappush(heap, (lb, new_cost, new_path, new_visited))

        print(f"Length of shortest traveling salesman path is: {int(best_cost)}.")
        print("Path:")
        for i in range(len(best_path) - 1):
            u, v = best_path[i], best_path[i + 1]
            print(f"{u + 1}-{v + 1} : {adj[u][v]}")

    # Task20
    def is_planar(self):
        G = nx.Graph() if not self._directed else nx.DiGraph()

        for u in range(1, self._size + 1):
            for v, _ in self._adjacency_list[u - 1]:
                if self._directed or u < v:
                    G.add_edge(u, v)

        return nx_is_planar(G)

class Map:
    def __init__(self, filepath: str):
        with open(filepath, 'r') as f:
            lines = f.read().strip().split('\n')
        if len(lines[0].split()) == 2 and all(x.isdigit() for x in lines[0].split()):
            lines = lines[1:]

        self._matrix = [list(map(int, line.split())) for line in lines]
        self._rows = len(self._matrix)
        self._cols = len(self._matrix[0]) if self._rows else 0

    def __getitem__(self, pos):
        i, j = pos
        return self._matrix[i][j]

    def size(self):
        return self._rows, self._cols

    def neighbors(self, i, j):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # вверх, вниз, влево, вправо
        result = []
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < self._rows and 0 <= nj < self._cols:
                if self._matrix[ni][nj] > 0:
                    result.append((ni, nj))
        return result

    @staticmethod
    def heuristic_manhattan(i, j, s, p):
        return abs(s - i) + abs(p - j)

    @staticmethod
    def heuristic_chebyshev(i, j, s, p):
        return max(abs(s - i), abs(p - j))

    @staticmethod
    def heuristic_euclidean(i, j, s, p):
        return ((s - i) ** 2 + (p - j) ** 2) ** 0.5

    @staticmethod
    def distance(aij, akl, i, j, k, l):
        return abs(k - i) + abs(l - j) + abs(akl - aij)

    # Task6
    def find_path_bfs(self, start, goal):
        rows, cols = self.size()
        queue = deque([start])
        came_from = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            i, j = current
            for ni, nj in self.neighbors(i, j):
                if (ni, nj) not in came_from:
                    came_from[(ni, nj)] = current
                    queue.append((ni, nj))

        return None

    # Task12
    def find_path_a_star(self, start, goal, heuristic):
        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {start: None}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                path = []
                total_cost = g_score[current]
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                path.reverse()

                print(f"{total_cost} - length of path between {start} and {goal} points.")
                print("Path:")
                print(path)
                return path

            i, j = current
            for ni, nj in self.neighbors(i, j):
                tentative_g = g_score[current] + self.distance(self[i, j], self[ni, nj], i, j, ni, nj)

                if (ni, nj) not in g_score or tentative_g < g_score[(ni, nj)]:
                    g_score[(ni, nj)] = tentative_g
                    f_score = tentative_g + heuristic(ni, nj, goal[0], goal[1])
                    heapq.heappush(open_set, (f_score, (ni, nj)))
                    came_from[(ni, nj)] = current

        print("No path found")
        return None

g1 = Graph('tests/task20/list_of_edges_t20_010.txt', 'edges') # 11001111101111111
# g2 = Graph('tests/task5/list_of_adjacency_t5_006.txt', 'adjacency_list')
# g3 = Graph('tests/task1/matrix_t1_001.txt', 'adjacency_matrix')

# Task1
# sys.setrecursionlimit(10000)
# g1.connected_components()

# Task4
# print(g1.degree_vector())
# print(g1.eccentricities())
# print(g1.diameter_and_peripheral())
# print(g1.radius_and_central())

# Task5
# print(g1.is_bipartite())

# Task6
# m = Map('tests/task6/maze_t6_007.txt')
# start = (1409, 21)
# goal = (6503, 59)
# path = m.find_path_bfs(start, goal)
#
# if path:
#     print("Путь найден:", path)
# else:
#     print("Путь не найден")
# print(len(path) - 1)

# Task7
# sys.setrecursionlimit(10000)
# print(g1.find_sccs_kosaraju())

# Task8
# g1.find_bridges_and_articulations()

# Task9
# g1.minimum_spanning_tree_kruskal()

# Task10
# g1.floyd_warshall()
# g1.component_characteristics()

# Task11
# g1.bellman_ford_moor(13)

# Task12
# m = Map("tests/task12/map_006.txt")
# start = (400, 200)
# goal = (50, 400)
# path_manhattan = m.find_path_a_star(start, goal, Map.heuristic_manhattan)
# path_c = m.find_path_a_star(start, goal, Map.heuristic_chebyshev)
# path_e = m.find_path_a_star(start, goal, Map.heuristic_euclidean)

# Task13
# size, matching = g1.maximum_bipartite_matching()
#
# if matching is None:
#     print("Graph is not bipartite.")
# else:
#     print(f"Size of maximum matching: {size}.")
#     print("Maximum matching:")
#     print(matching)


# Task14
# source = 333
# sink = 418
# max_flow, flow_result = g1.ford_fulkerson(source, sink)
# print(max_flow, flow_result)
#
# print(f"Maximum flow value: {max_flow}.")
# print(f"Source: {source}, sink: {sink}.")
# print("Flow:")
# for (u, v), f in flow_result.items():
#     print(f"{u}-{v} : {f}")

# Task16
# g1.boruvka_mst_parallel()

# Task17
# print(g1.areas_from_vertex(43))

# Task18
# Работает до 5 теста включительно
# g1.tsp_branch_and_bound_fast()

# Task19
# g1.ant_colony_traversal(num_ants=48, num_iterations=300)

# Task20
print(g1.is_planar())

# print(g1.size() == g2.size() == g3.size())
# print(g1.weight(1, 3) == g2.weight(1, 3) == g3.weight(1, 3))
# print(g1.is_edge(1, 2) == g2.is_edge(1, 2) == g3.is_edge(1, 2))
# print(g1.adjacency_matrix() == g2.adjacency_matrix() == g3.adjacency_matrix())
# print(g1.adjacency_list(6) == g2.adjacency_list(6) == g3.adjacency_list(6))
# print(g1.list_of_edges() == g2.list_of_edges() == g3.list_of_edges())
# print(g1.is_directed() == g2.is_directed() == g3.is_directed())