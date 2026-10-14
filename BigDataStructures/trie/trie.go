package trie

type node[V any] struct {
	children []*node[V]
	value    V
	isEnd    bool
}

type Trie[V any] struct {
	root    *node[V]
	chars   []rune
	indexOf map[rune]int
}

func New[V any](alphabet string) *Trie[V] {
	chars := make([]rune, 0, len(alphabet))
	indexOf := make(map[rune]int, len(alphabet))
	for i, ch := range alphabet {
		chars = append(chars, ch)
		indexOf[ch] = i
	}
	return &Trie[V]{
		root:    &node[V]{children: make([]*node[V], len(alphabet))},
		chars:   chars,
		indexOf: indexOf,
	}
}

func (t *Trie[V]) Insert(key string, value V) {
	cur := t.root
	for _, ch := range key {
		idx, ok := t.indexOf[ch]
		if !ok {
			panic("trie: symbol not in alphabet")
		}
		if cur.children[idx] == nil {
			cur.children[idx] = &node[V]{children: make([]*node[V], len(t.chars))}
		}
		cur = cur.children[idx]
	}
	cur.value = value
	cur.isEnd = true
}

func (t *Trie[V]) Get(key string) (V, bool) {
	cur := t.root
	for _, ch := range key {
		idx, ok := t.indexOf[ch]
		if !ok || cur.children[idx] == nil {
			var zero V
			return zero, false
		}
		cur = cur.children[idx]
	}
	if !cur.isEnd {
		var zero V
		return zero, false
	}
	return cur.value, true
}

func (t *Trie[V]) StartsWith(prefix string) bool {
	cur := t.root
	for _, ch := range prefix {
		idx, ok := t.indexOf[ch]
		if !ok || cur.children[idx] == nil {
			return false
		}
		cur = cur.children[idx]
	}
	return true
}

func (t *Trie[V]) Delete(key string) bool {
	if _, ok := t.Get(key); !ok {
		return false
	}
	runes := []rune(key)
	indices := make([]int, len(runes))
	cur := t.root
	for i, ch := range runes {
		indices[i] = t.indexOf[ch]
		cur = cur.children[indices[i]]
	}
	cur.isEnd = false

	for i := len(runes) - 1; i >= 0; i-- {
		parent := t.root
		for j := 0; j < i; j++ {
			parent = parent.children[indices[j]]
		}
		child := parent.children[indices[i]]
		if !child.isEnd && allNil(child.children) {
			parent.children[indices[i]] = nil
		} else {
			break
		}
	}
	return true
}

func allNil[V any](nodes []*node[V]) bool {
	for _, n := range nodes {
		if n != nil {
			return false
		}
	}
	return true
}

func (t *Trie[V]) Clear() {
	t.root = &node[V]{children: make([]*node[V], len(t.chars))}
}
