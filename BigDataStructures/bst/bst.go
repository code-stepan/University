package bst

type Node[K any, V any] struct {
	key   K
	value V
	left  *Node[K, V]
	right *Node[K, V]
}

type BST[K any, V any] struct {
	root    *Node[K, V]
	compare func(a, b K) int
}

func New[K any, V any](cmp func(a, b K) int) *BST[K, V] {
	return &BST[K, V]{
		compare: cmp,
	}
}

func (t *BST[K, V]) Clear() {
	t.root = nil
}

func (t *BST[K, V]) Insert(key K, value V) {
	t.root = t.insertNode(t.root, key, value)
}

func (t *BST[K, V]) insertNode(node *Node[K, V], key K, value V) *Node[K, V] {
	if node == nil {
		return &Node[K, V]{key: key, value: value}
	}

	cmp := t.compare(key, node.key)
	if cmp < 0 {
		node.left = t.insertNode(node.left, key, value)
	} else if cmp > 0 {
		node.right = t.insertNode(node.right, key, value)
	} else {
		node.value = value
	}

	return node
}

func (t *BST[K, V]) Get(key K) (V, bool) {
	var zero V
	node := t.searchNode(t.root, key)
	if node == nil {
		return zero, false
	}
	return node.value, true
}

func (t *BST[K, V]) searchNode(node *Node[K, V], key K) *Node[K, V] {
	if node == nil {
		return nil
	}
	cmp := t.compare(key, node.key)
	if cmp == 0 {
		return node
	} else if cmp < 0 {
		return t.searchNode(node.left, key)
	}
	return t.searchNode(node.right, key)
}

func (t *BST[K, V]) Delete(key K) bool {
	if t.searchNode(t.root, key) == nil {
		return false
	}
	t.root = t.deleteNode(t.root, key)
	return true
}

func (t *BST[K, V]) deleteNode(node *Node[K, V], key K) *Node[K, V] {
	if node == nil {
		return nil
	}

	cmp := t.compare(key, node.key)
	if cmp < 0 {
		node.left = t.deleteNode(node.left, key)
	} else if cmp > 0 {
		node.right = t.deleteNode(node.right, key)
	} else {
		if node.left == nil {
			return node.right
		}
		if node.right == nil {
			return node.left
		}

		successor := t.minNode(node.right)
		node.key = successor.key
		node.value = successor.value
		node.right = t.deleteNode(node.right, successor.key)
	}
	return node
}

func (t *BST[K, V]) minNode(node *Node[K, V]) *Node[K, V] {
	for node.left != nil {
		node = node.left
	}
	return node
}

// Обходы

func (t *BST[K, V]) PreOrder(visit func(K, V)) {
	t.preOrder(t.root, visit)
}

func (t *BST[K, V]) preOrder(n *Node[K, V], visit func(K, V)) {
	if n == nil {
		return
	}
	visit(n.key, n.value)
	t.preOrder(n.left, visit)
	t.preOrder(n.right, visit)
}

func (t *BST[K, V]) InOrder(visit func(K, V)) {
	t.inOrder(t.root, visit)
}

func (t *BST[K, V]) inOrder(n *Node[K, V], visit func(K, V)) {
	if n == nil {
		return
	}
	t.inOrder(n.left, visit)
	visit(n.key, n.value)
	t.inOrder(n.right, visit)
}

func (t *BST[K, V]) PostOrder(visit func(K, V)) {
	t.postOrder(t.root, visit)
}

func (t *BST[K, V]) postOrder(n *Node[K, V], visit func(K, V)) {
	if n == nil {
		return
	}
	t.postOrder(n.left, visit)
	t.postOrder(n.right, visit)
	visit(n.key, n.value)
}
