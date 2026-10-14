package fenwicktree

type Fenwicktree[T any] struct {
	n      int
	tree   []T
	values []T
	op     func(a, b T) T
	inv    func(a, b T) T
	id     T
}

func New[T any](n int, op func(a, b T) T, inv func(a, b T) T, id T) *Fenwicktree[T] {
	tree := make([]T, n+1)
	values := make([]T, n)
	for i := range tree {
		tree[i] = id
	}
	for i := range values {
		values[i] = id
	}
	return &Fenwicktree[T]{n: n, tree: tree, values: values, op: op, inv: inv, id: id}
}

func (ft *Fenwicktree[T]) Update(i int, value T) {
	delta := ft.inv(value, ft.values[i])
	ft.values[i] = value
	for idx := i + 1; idx <= ft.n; idx += idx & -idx {
		ft.tree[idx] = ft.op(ft.tree[idx], delta)
	}
}

func (ft *Fenwicktree[T]) Query(i int) T {
	result := ft.id
	for idx := i + 1; idx > 0; idx -= idx & -idx {
		result = ft.op(result, ft.tree[idx])
	}
	return result
}

func (ft *Fenwicktree[T]) RangeQuery(l, r int) T {
	if l == 0 {
		return ft.Query(r)
	}
	return ft.inv(ft.Query(r), ft.Query(l-1))
}

func (ft *Fenwicktree[T]) Len() int {
	return ft.n
}
