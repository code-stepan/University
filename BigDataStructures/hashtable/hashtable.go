package hashtable

import (
	"errors"
)

type entry[K comparable, V any] struct {
	key   K
	value V
	next  *entry[K, V]
}

type HashMap[K comparable, V any] struct {
	buckets  []*entry[K, V]
	size     int
	capacity int
	hashFunc func(K) uint64
}

func New[K comparable, V any](capacity int, hashFunc func(K) uint64) (*HashMap[K, V], error) {
	if capacity <= 0 {
		return nil, errors.New("capacity должно быть больше 0")
	}
	if hashFunc == nil {
		return nil, errors.New("не определена hashFunc")
	}
	return &HashMap[K, V]{
		buckets:  make([]*entry[K, V], capacity),
		capacity: capacity,
		hashFunc: hashFunc,
	}, nil
}

func (h *HashMap[K, V]) index(key K) int {
	return int(h.hashFunc(key) % uint64(h.capacity))
}

func (h *HashMap[K, V]) Set(key K, value V) {
	idx := h.index(key)
	head := h.buckets[idx]

	for e := head; e != nil; e = e.next {
		if e.key == key {
			e.value = value
			return
		}
	}

	h.buckets[idx] = &entry[K, V]{
		key:   key,
		value: value,
		next:  head,
	}
	h.size++
}

func (h *HashMap[K, V]) Get(key K) (V, bool) {
	idx := h.index(key)
	for e := h.buckets[idx]; e != nil; e = e.next {
		if e.key == key {
			return e.value, true
		}
	}
	var zero V
	return zero, false
}

func (h *HashMap[K, V]) Delete(key K) bool {
	idx := h.index(key)
	head := h.buckets[idx]
	var prev *entry[K, V]

	for e := head; e != nil; e = e.next {
		if e.key == key {
			if prev == nil {
				h.buckets[idx] = e.next
			} else {
				prev.next = e.next
			}
			h.size--
			return true
		}
		prev = e
	}
	return false
}

func (h *HashMap[K, V]) Len() int {
	return h.size
}
