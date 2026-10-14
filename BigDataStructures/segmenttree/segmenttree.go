package segmenttree

type SegmentTree[T any] struct {
	n    int
	tree []T
	op   func(a, b T) T
	id   T
}

func New[T any](n int, op func(a, b T) T, id T) *SegmentTree[T] {
	tree := make([]T, 4*n)
	for i := range tree {
		tree[i] = id
	}
	return &SegmentTree[T]{n: n, tree: tree, op: op, id: id}
}

func (st *SegmentTree[T]) Update(pos int, value T) {
	st.update(1, 0, st.n-1, pos, value)
}

func (st *SegmentTree[T]) update(v, tl, tr, pos int, value T) {
	if tl == tr {
		st.tree[v] = value
		return
	}
	tm := (tl + tr) / 2
	if pos <= tm {
		st.update(2*v, tl, tm, pos, value)
	} else {
		st.update(2*v+1, tm+1, tr, pos, value)
	}
	st.tree[v] = st.op(st.tree[2*v], st.tree[2*v+1])
}

func (st *SegmentTree[T]) Query(l, r int) T {
	return st.query(1, 0, st.n-1, l, r)
}

func (st *SegmentTree[T]) query(v, tl, tr, l, r int) T {
	if l > r {
		return st.id
	}
	if l == tl && r == tr {
		return st.tree[v]
	}
	tm := (tl + tr) / 2
	return st.op(
		st.query(2*v, tl, tm, l, min(r, tm)),
		st.query(2*v+1, tm+1, tr, max(l, tm+1), r),
	)
}
