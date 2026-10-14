package heaps

type BinomialNode[K any, V any] struct {
	key     K
	val     V
	degree  int
	child   *BinomialNode[K, V]
	sibling *BinomialNode[K, V]
}

type BinomialHeap[K any, V any] struct {
	roots   map[int]*BinomialNode[K, V]
	compare func(a, b K) int
	size    int
}

func NewBinomialHeap[K any, V any](cmp func(a, b K) int) *BinomialHeap[K, V] {
	return &BinomialHeap[K, V]{
		roots:   make(map[int]*BinomialNode[K, V]),
		compare: cmp,
	}
}

func (h *BinomialHeap[K, V]) Len() int {
	return h.size
}

func (h *BinomialHeap[K, V]) IsEmpty() bool {
	return h.size == 0
}

func (h *BinomialHeap[K, V]) Insert(key K, val V) {
	node := &BinomialNode[K, V]{key: key, val: val}
	h.mergeSingle(node)
	h.size++
}

func (h *BinomialHeap[K, V]) Peek() (K, V, bool) {
	var zeroK K
	var zeroV V
	if h.IsEmpty() {
		return zeroK, zeroV, false
	}

	var maxNode *BinomialNode[K, V]
	for _, r := range h.roots {
		if maxNode == nil || h.compare(r.key, maxNode.key) > 0 {
			maxNode = r
		}
	}
	return maxNode.key, maxNode.val, true
}

func (h *BinomialHeap[K, V]) ExtractMax() (K, V, bool) {
	var zeroK K
	var zeroV V
	if h.IsEmpty() {
		return zeroK, zeroV, false
	}

	var maxDeg int
	var maxNode *BinomialNode[K, V]
	for deg, r := range h.roots {
		if maxNode == nil || h.compare(r.key, maxNode.key) > 0 {
			maxDeg = deg
			maxNode = r
		}
	}

	key, val := maxNode.key, maxNode.val
	delete(h.roots, maxDeg)

	// Дети удалённого корня — деревья B_0..B_{k-1} в цепочке sibling
	child := maxNode.child
	for child != nil {
		next := child.sibling
		child.sibling = nil
		h.mergeSingle(child)
		child = next
	}

	h.size--
	return key, val, true
}

func (h *BinomialHeap[K, V]) Merge(other *BinomialHeap[K, V]) {
	if other.IsEmpty() {
		return
	}
	for _, node := range other.roots {
		h.mergeSingle(node)
	}
	h.size += other.size
	other.roots = make(map[int]*BinomialNode[K, V])
	other.size = 0
}

func (h *BinomialHeap[K, V]) mergeSingle(node *BinomialNode[K, V]) {
	carry := node
	for carry != nil {
		deg := carry.degree
		if existing, ok := h.roots[deg]; ok {
			// Два дерева одной степени -> связываем в дерево степени deg+1
			delete(h.roots, deg)
			carry = linkTrees(existing, carry, h.compare)
		} else {
			// Свободный слот -> ставим дерево и завершаем
			h.roots[deg] = carry
			carry = nil
		}
	}
}

func linkTrees[K any, V any](a, b *BinomialNode[K, V], cmp func(a, b K) int) *BinomialNode[K, V] {
	if cmp(a.key, b.key) < 0 {
		a, b = b, a
	}
	b.sibling = a.child
	a.child = b
	a.degree++
	return a
}
