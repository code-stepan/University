from collections import defaultdict
from copy import deepcopy

import networkx as nx

# Алгоритм Хопкрофта — Тарьяна

__all__ = ["check_planarity", "is_planar", "PlanarEmbedding"]


def is_planar(G):
    return check_planarity(G)[0]


def check_planarity(G, counterexample=False):
    planarity_state = _LRPlanarity(G)
    embedding = planarity_state.lr_planarity()
    if embedding is None:
        if counterexample:
            return False, get_counterexample(G)
        return False, None
    return True, embedding


def get_counterexample(G):
    G_copy = nx.Graph(G)
    if check_planarity(G_copy)[0]:
        raise nx.NetworkXException("Граф планарен - контрпримера не существует.")

    subgraph = nx.Graph()
    # Итерация по копии списка ребер для безопасного удаления
    for u, v in list(G_copy.edges()):
        G_copy.remove_edge(u, v)
        if check_planarity(G_copy)[0]:
            G_copy.add_edge(u, v)
            subgraph.add_edge(u, v)

    return subgraph


class _Interval:
    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high

    def is_empty(self):
        return self.low is None and self.high is None

    def copy(self):
        return _Interval(self.low, self.high)

    def is_conflicting(self, b, state):
        return not self.is_empty() and state.lowpt[self.high] > state.lowpt[b]


class _ConflictPair:
    def __init__(self, left=_Interval(), right=_Interval()):
        self.left = left
        self.right = right

    def swap(self):
        self.left, self.right = self.right, self.left

    def lowest(self, state):
        if self.left.is_empty():
            return state.lowpt[self.right.low]
        if self.right.is_empty():
            return state.lowpt[self.left.low]
        return min(state.lowpt[self.left.low], state.lowpt[self.right.low])


def _top_of_stack(l):
    return l[-1] if l else None


class _LRPlanarity:
    __slots__ = [
        "G", "roots", "height", "lowpt", "lowpt2", "nesting_depth",
        "parent_edge", "DG", "ordered_adjs", "ref", "side", "S",
        "stack_bottom", "lowpt_edge", "left_ref", "right_ref", "embedding",
    ]

    def __init__(self, G):
        # 1. Инициализация графа без петель
        self.G = nx.Graph(G)
        self.G.remove_edges_from(nx.selfloop_edges(self.G))

        # 2. Инициализация структур данных
        self.roots = []
        self.height = defaultdict(lambda: None)
        self.parent_edge = defaultdict(lambda: None)
        self.DG = nx.DiGraph()  # Ориентированный граф DFS
        self.DG.add_nodes_from(self.G.nodes)

        # Атрибуты, вычисляемые в ходе алгоритма
        self.lowpt = {}
        self.lowpt2 = {}
        self.nesting_depth = {}
        self.ordered_adjs = {}
        self.ref = defaultdict(lambda: None)
        self.side = defaultdict(lambda: 1)
        self.S = []  # Стек пар конфликтов
        self.stack_bottom = {}
        self.lowpt_edge = {}
        self.left_ref = {}
        self.right_ref = {}
        self.embedding = PlanarEmbedding()

    def lr_planarity(self):
        # Быстрая проверка на основе числа ребер
        if self.G.order() > 2 and self.G.size() > 3 * self.G.order() - 6:
            return None

        # Фаза 1: Ориентация графа с помощью DFS (поиск в глубину)
        for v in self.G:
            if self.height[v] is None:
                self.height[v] = 0
                self.roots.append(v)
                self._dfs_orientation(v)

        # Фаза 2: Тестирование на планарность
        # Сортировка смежных вершин по глубине вложенности
        for v in self.DG:
            self.ordered_adjs[v] = sorted(
                self.DG[v], key=lambda x: self.nesting_depth[(v, x)]
            )

        for v in self.roots:
            if not self._dfs_testing(v):
                return None  # Граф не планарен

        # Фаза 3: Построение вложения (embedding)
        for e in self.DG.edges:
            self.nesting_depth[e] *= self._get_side(e)

        self.embedding.add_nodes_from(self.DG.nodes)
        for v in self.DG:
            self.ordered_adjs[v] = sorted(
                self.DG[v], key=lambda x: self.nesting_depth[(v, x)]
            )
            # Инициализация вложения
            prev_node = None
            for w in self.ordered_adjs[v]:
                self.embedding.add_half_edge(v, w, ccw=prev_node)
                prev_node = w

        for v in self.roots:
            self._dfs_embedding(v)

        return self.embedding

    def _dfs_orientation(self, v):
        e = self.parent_edge[v]
        for w in self.G[v]:
            if (v, w) in self.DG.edges or (w, v) in self.DG.edges:
                continue

            vw = (v, w)
            self.DG.add_edge(v, w)
            self.lowpt[vw] = self.height[v]
            self.lowpt2[vw] = self.height[v]

            if self.height[w] is None:  # Ребро дерева
                self.parent_edge[w] = vw
                self.height[w] = self.height[v] + 1
                self._dfs_orientation(w)
            else:  # Обратное ребро
                self.lowpt[vw] = self.height[w]

            # Определение графа вложенности
            self.nesting_depth[vw] = 2 * self.lowpt[vw]
            if self.lowpt2[vw] < self.height[v]:  # Хорда
                self.nesting_depth[vw] += 1

            # Обновление lowpoints родительского ребра e
            if e is not None:
                if self.lowpt[vw] < self.lowpt[e]:
                    self.lowpt2[e] = min(self.lowpt[e], self.lowpt2[vw])
                    self.lowpt[e] = self.lowpt[vw]
                elif self.lowpt[vw] > self.lowpt[e]:
                    self.lowpt2[e] = min(self.lowpt2[e], self.lowpt[vw])
                else:
                    self.lowpt2[e] = min(self.lowpt2[e], self.lowpt2[vw])

    def _dfs_testing(self, v):
        e = self.parent_edge[v]
        for w in self.ordered_adjs[v]:
            ei = (v, w)
            self.stack_bottom[ei] = _top_of_stack(self.S)

            if ei == self.parent_edge.get(w):  # Ребро дерева
                if not self._dfs_testing(w):
                    return False
            else:  # Обратное ребро
                self.lowpt_edge[ei] = ei
                self.S.append(_ConflictPair(right=_Interval(ei, ei)))

            # Интеграция новых обратных ребер
            if self.lowpt[ei] < self.height[v]:
                if w == self.ordered_adjs[v][0]:
                    self.lowpt_edge[e] = self.lowpt_edge[ei]
                else:
                    if not self._add_constraints(ei, e):
                        return False  # Граф не планарен

        if e is not None:
            self._remove_back_edges(e)
        return True

    def _add_constraints(self, ei, e):
        P = _ConflictPair()
        # Слияние обратных ребер ei в P.right
        while True:
            Q = self.S.pop()
            if not Q.left.is_empty():
                Q.swap()
            if not Q.left.is_empty(): return False  # Не планарен

            if self.lowpt[Q.right.low] > self.lowpt[e]:
                if P.right.is_empty():
                    P.right = Q.right.copy()
                else:
                    self.ref[P.right.low] = Q.right.high
                P.right.low = Q.right.low
            else:
                self.ref[Q.right.low] = self.lowpt_edge[e]

            if _top_of_stack(self.S) == self.stack_bottom[ei]:
                break

        # Слияние конфликтующих обратных ребер e_1,...,e_i-1 в P.left
        while _top_of_stack(self.S).left.is_conflicting(ei, self) or \
                _top_of_stack(self.S).right.is_conflicting(ei, self):
            Q = self.S.pop()
            if Q.right.is_conflicting(ei, self):
                Q.swap()
            if Q.right.is_conflicting(ei, self): return False  # Не планарен

            self.ref[P.right.low] = Q.right.high
            if Q.right.low is not None:
                P.right.low = Q.right.low

            if P.left.is_empty():
                P.left = Q.left.copy()
            else:
                self.ref[P.left.low] = Q.left.high
            P.left.low = Q.left.low

        if not (P.left.is_empty() and P.right.is_empty()):
            self.S.append(P)
        return True

    def _remove_back_edges(self, e):
        u = e[0]
        while self.S and _top_of_stack(self.S).lowest(self) == self.height[u]:
            P = self.S.pop()
            if P.left.low is not None:
                self.side[P.left.low] = -1

        if self.S:
            P = self.S.pop()
            # Обрезка левого интервала
            while P.left.high is not None and P.left.high[1] == u:
                P.left.high = self.ref.get(P.left.high)
            if P.left.high is None and P.left.low is not None:
                self.ref[P.left.low] = P.right.low
                self.side[P.left.low] = -1
                P.left.low = None
            # Обрезка правого интервала
            while P.right.high is not None and P.right.high[1] == u:
                P.right.high = self.ref.get(P.right.high)
            if P.right.high is None and P.right.low is not None:
                self.ref[P.right.low] = P.left.low
                self.side[P.right.low] = -1
                P.right.low = None
            self.S.append(P)

        if self.lowpt[e] < self.height[u]:
            hl = _top_of_stack(self.S).left.high
            hr = _top_of_stack(self.S).right.high
            if hl is not None and (hr is None or self.lowpt[hl] > self.lowpt[hr]):
                self.ref[e] = hl
            else:
                self.ref[e] = hr

    def _dfs_embedding(self, v):
        for w in self.ordered_adjs[v]:
            ei = (v, w)
            if ei == self.parent_edge.get(w):  # Ребро дерева
                self.embedding.add_half_edge_first(w, v)
                self.left_ref[v] = w
                self.right_ref[v] = w
                self._dfs_embedding(w)
            else:  # Обратное ребро
                if self.side[ei] == 1:
                    self.embedding.add_half_edge(w, v, ccw=self.right_ref[w])
                else:
                    self.embedding.add_half_edge(w, v, cw=self.left_ref[w])
                    self.left_ref[w] = v

    def _get_side(self, e):
        if self.ref[e] is not None:
            self.side[e] *= self._get_side(self.ref[e])
            self.ref[e] = None
        return self.side[e]


class PlanarEmbedding(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data=incoming_graph_data, **attr)
        self.add_edge = self.__forbidden
        self.add_edges_from = self.__forbidden
        self.add_weighted_edges_from = self.__forbidden

    def __forbidden(self, *args, **kwargs):
        raise NotImplementedError(
            "Use `add_half_edge` method to add edges to a PlanarEmbedding."
        )

    def get_data(self):
        embedding = {}
        for v in self:
            embedding[v] = list(self.neighbors_cw_order(v))
        return embedding

    def set_data(self, data):
        for v in data:
            ref = None
            for w in reversed(data[v]):
                self.add_half_edge(v, w, cw=ref)
                ref = w

    def remove_node(self, n):
        try:
            for u in self._pred[n]:
                succs_u = self._succ[u]
                un_cw = succs_u[n]["cw"]
                un_ccw = succs_u[n]["ccw"]
                del succs_u[n]
                del self._pred[u][n]
                if n != un_cw:
                    succs_u[un_cw]["ccw"] = un_ccw
                    succs_u[un_ccw]["cw"] = un_cw
            del self._node[n]
            del self._succ[n]
            del self._pred[n]
        except KeyError as err:  # NetworkXError if n not in self
            raise nx.NetworkXError(
                f"The node {n} is not in the planar embedding."
            ) from err
        nx._clear_cache(self)

    def remove_nodes_from(self, nodes):
        for n in nodes:
            if n in self._node:
                self.remove_node(n)

    def neighbors_cw_order(self, v):
        succs = self._succ[v]
        if not succs:
            return
        start_node = next(reversed(succs))
        yield start_node
        current_node = succs[start_node]["cw"]
        while start_node != current_node:
            yield current_node
            current_node = succs[current_node]["cw"]

    def add_half_edge(self, start_node, end_node, *, cw=None, ccw=None):
        succs = self._succ.get(start_node)
        if succs:
            leftmost_nbr = next(reversed(self._succ[start_node]))
            if cw is not None:
                if cw not in succs:
                    raise nx.NetworkXError("Invalid clockwise reference node.")
                if ccw is not None:
                    raise nx.NetworkXError("Only one of cw/ccw can be specified.")
                ref_ccw = succs[cw]["ccw"]
                super().add_edge(start_node, end_node, cw=cw, ccw=ref_ccw)
                succs[ref_ccw]["cw"] = end_node
                succs[cw]["ccw"] = end_node
                move_leftmost_nbr_to_end = cw != leftmost_nbr
            elif ccw is not None:
                if ccw not in succs:
                    raise nx.NetworkXError("Invalid counterclockwise reference node.")
                ref_cw = succs[ccw]["cw"]
                super().add_edge(start_node, end_node, cw=ref_cw, ccw=ccw)
                succs[ref_cw]["ccw"] = end_node
                succs[ccw]["cw"] = end_node
                move_leftmost_nbr_to_end = True
            else:
                raise nx.NetworkXError(
                    "Node already has out-half-edge(s), either cw or ccw reference node required."
                )
            if move_leftmost_nbr_to_end:
                succs[leftmost_nbr] = succs.pop(leftmost_nbr)
        else:
            if cw is not None or ccw is not None:
                raise nx.NetworkXError("Invalid reference node.")
            super().add_edge(start_node, end_node, ccw=end_node, cw=end_node)

    def check_structure(self):
        for v in self:
            try:
                sorted_nbrs = set(self.neighbors_cw_order(v))
            except KeyError as err:
                raise nx.NetworkXException(f"Bad embedding. Missing orientation for a neighbor of {v}") from err
            if sorted_nbrs != set(self[v]):
                raise nx.NetworkXException("Bad embedding. Edge orientations not set correctly.")
            for w in self[v]:
                if not self.has_edge(w, v):
                    raise nx.NetworkXException("Bad embedding. Opposite half-edge is missing.")
        counted_half_edges = set()
        for component in nx.connected_components(self):
            if len(component) == 1:
                continue
            num_nodes = len(component)
            num_half_edges = 0
            num_faces = 0
            for v in component:
                for w in self.neighbors_cw_order(v):
                    num_half_edges += 1
                    if (v, w) not in counted_half_edges:
                        num_faces += 1
                        self.traverse_face(v, w, counted_half_edges)
            num_edges = num_half_edges // 2
            if num_nodes - num_edges + num_faces != 2:
                raise nx.NetworkXException("Bad embedding. The graph does not match Euler's formula")

    def add_half_edge_ccw(self, start_node, end_node, reference_neighbor):
        self.add_half_edge(start_node, end_node, cw=reference_neighbor)

    def add_half_edge_cw(self, start_node, end_node, reference_neighbor):
        self.add_half_edge(start_node, end_node, ccw=reference_neighbor)

    def remove_edge(self, u, v):
        try:
            succs_u, succs_v = self._succ[u], self._succ[v]
            uv_cw, uv_ccw = succs_u[v]["cw"], succs_u[v]["ccw"]
            vu_cw, vu_ccw = succs_v[u]["cw"], succs_v[u]["ccw"]
            del succs_u[v], self._pred[v][u], succs_v[u], self._pred[u][v]
            if v != uv_cw:
                succs_u[uv_cw]["ccw"], succs_u[uv_ccw]["cw"] = uv_ccw, uv_cw
            if u != vu_cw:
                succs_v[vu_cw]["ccw"], succs_v[vu_ccw]["cw"] = vu_ccw, vu_cw
        except KeyError as err:
            raise nx.NetworkXError(f"The edge {u}-{v} is not in the planar embedding.") from err
        nx._clear_cache(self)

    def remove_edges_from(self, ebunch):
        for u, v in ebunch:
            if u in self._succ and v in self._succ[u]:
                self.remove_edge(u, v)

    def connect_components(self, v, w):
        ref_v = next(reversed(self._succ[v])) if v in self._succ and self._succ[v] else None
        self.add_half_edge(v, w, cw=ref_v)
        ref_w = next(reversed(self._succ[w])) if w in self._succ and self._succ[w] else None
        self.add_half_edge(w, v, cw=ref_w)

    def add_half_edge_first(self, start_node, end_node):
        succs = self._succ.get(start_node)
        leftmost_nbr = next(reversed(succs)) if succs else None
        self.add_half_edge(start_node, end_node, cw=leftmost_nbr)

    def next_face_half_edge(self, v, w):
        return w, self[w][v]["ccw"]

    def traverse_face(self, v, w, mark_half_edges=None):
        if mark_half_edges is None: mark_half_edges = set()
        face_nodes = [v]
        mark_half_edges.add((v, w))
        prev_node, cur_node = v, w
        incoming_node = self[v][w]["cw"]
        while cur_node != v or prev_node != incoming_node:
            face_nodes.append(cur_node)
            prev_node, cur_node = self.next_face_half_edge(prev_node, cur_node)
            if (prev_node, cur_node) in mark_half_edges:
                raise nx.NetworkXException("Bad planar embedding. Impossible face.")
            mark_half_edges.add((prev_node, cur_node))
        return face_nodes

    def is_directed(self):
        return False

    def copy(self, as_view=False):
        if as_view: return nx.graphviews.generic_graph_view(self)
        G = self.__class__()
        G.graph.update(self.graph)
        G.add_nodes_from((n, d.copy()) for n, d in self._node.items())
        super(self.__class__, G).add_edges_from(
            (u, v, datadict.copy())
            for u, nbrs in self._adj.items()
            for v, datadict in nbrs.items()
        )
        return G

    def to_undirected(self, reciprocal=False, as_view=False):
        if reciprocal or as_view:
            raise ValueError("Parameters 'reciprocal' and 'as_view' are not supported for PlanarEmbedding.")
        graph_class = self.to_undirected_class()
        G = graph_class()
        G.graph.update(deepcopy(self.graph))
        G.add_nodes_from((n, deepcopy(d)) for n, d in self._node.items())
        G.add_edges_from(
            (u, v, {k: deepcopy(v) for k, v in d.items() if k not in {"cw", "ccw"}})
            for u, nbrs in self._adj.items()
            for v, d in nbrs.items()
        )
        return G