package heaps

type BinaryNode[K any, V any] struct {
	key K
	val V
}

type BinaryHeap[K any, V any] struct {
	data    []BinaryNode[K, V]
	compare func(a, b K) int
}

func NewBinaryHeap[K any, V any](cmp func(a, b K) int) *BinaryHeap[K, V] {
	return &BinaryHeap[K, V]{compare: cmp}
}

func (h *BinaryHeap[K, V]) Len() int {
	return len(h.data)
}

func (h *BinaryHeap[K, V]) IsEmpty() bool {
	return len(h.data) == 0
}

func (h *BinaryHeap[K, V]) Insert(key K, val V) {
	h.data = append(h.data, BinaryNode[K, V]{key: key, val: val})
	h.siftUp(len(h.data) - 1)
}

func (h *BinaryHeap[K, V]) Peek() (K, V, bool) {
	var zeroK K
	var zeroV V
	if h.IsEmpty() {
		return zeroK, zeroV, false
	}
	return h.data[0].key, h.data[0].val, true
}

func (h *BinaryHeap[K, V]) ExtractMax() (K, V, bool) {
	var zeroK K
	var zeroV V
	if h.IsEmpty() {
		return zeroK, zeroV, false
	}

	max := h.data[0]
	last := len(h.data) - 1
	h.data[0] = h.data[last]
	h.data = h.data[:last]

	if !h.IsEmpty() {
		h.siftDown(0)
	}

	return max.key, max.val, true
}

func (h *BinaryHeap[K, V]) siftUp(i int) {
	for i > 0 {
		parent := (i - 1) / 2
		if h.compare(h.data[i].key, h.data[parent].key) <= 0 {
			break
		}
		h.data[i], h.data[parent] = h.data[parent], h.data[i]
		i = parent
	}
}

func (h *BinaryHeap[K, V]) siftDown(i int) {
	n := len(h.data)
	for {
		largest := i
		left := 2*i + 1
		right := 2*i + 2

		if left < n && h.compare(h.data[left].key, h.data[largest].key) > 0 {
			largest = left
		}
		if right < n && h.compare(h.data[right].key, h.data[largest].key) > 0 {
			largest = right
		}
		if largest == i {
			break
		}
		h.data[i], h.data[largest] = h.data[largest], h.data[i]
		i = largest
	}
}
