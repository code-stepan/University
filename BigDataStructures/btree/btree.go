package btree

type Node[K any, V any] struct {
	keys     []K
	values   []V
	children []*Node[K, V]
	leaf     bool
}

type BTree[K any, V any] struct {
	root    *Node[K, V]
	t       int
	compare func(a, b K) int
}

func New[K any, V any](t int, cmp func(a, b K) int) *BTree[K, V] {
	if t < 2 {
		t = 2
	}
	return &BTree[K, V]{t: t, compare: cmp}
}

func (tree *BTree[K, V]) Clear() {
	tree.root = nil
}

// --- Поиск ---

func (tree *BTree[K, V]) Get(key K) (V, bool) {
	var zero V
	node, idx := tree.search(tree.root, key)
	if node == nil {
		return zero, false
	}
	return node.values[idx], true
}

func (tree *BTree[K, V]) search(node *Node[K, V], key K) (*Node[K, V], int) {
	if node == nil {
		return nil, -1
	}
	i := 0
	for i < len(node.keys) {
		cmp := tree.compare(key, node.keys[i])
		if cmp == 0 {
			return node, i
		}
		if cmp < 0 {
			break
		}
		i++
	}
	if node.leaf {
		return nil, -1
	}
	return tree.search(node.children[i], key)
}

// --- Вставка ---

func (tree *BTree[K, V]) Insert(key K, value V) {
	if tree.root == nil {
		tree.root = &Node[K, V]{leaf: true, keys: []K{key}, values: []V{value}}
		return
	}
	if len(tree.root.keys) == 2*tree.t-1 {
		newRoot := &Node[K, V]{leaf: false, children: []*Node[K, V]{tree.root}}
		tree.splitChild(newRoot, 0)
		tree.root = newRoot
	}
	tree.insertNonFull(tree.root, key, value)
}

func (tree *BTree[K, V]) insertNonFull(node *Node[K, V], key K, value V) {
	i := len(node.keys) - 1
	if node.leaf {
		node.keys = append(node.keys, key)
		node.values = append(node.values, value)
		for i >= 0 && tree.compare(key, node.keys[i]) < 0 {
			node.keys[i+1] = node.keys[i]
			node.values[i+1] = node.values[i]
			i--
		}
		node.keys[i+1] = key
		node.values[i+1] = value
		return
	}
	for i >= 0 && tree.compare(key, node.keys[i]) < 0 {
		i--
	}
	i++
	if len(node.children[i].keys) == 2*tree.t-1 {
		tree.splitChild(node, i)
		if tree.compare(key, node.keys[i]) > 0 {
			i++
		}
	}
	tree.insertNonFull(node.children[i], key, value)
}

func (tree *BTree[K, V]) splitChild(parent *Node[K, V], i int) {
	t := tree.t
	child := parent.children[i]

	newNode := &Node[K, V]{leaf: child.leaf}
	newNode.keys = make([]K, t-1)
	newNode.values = make([]V, t-1)
	copy(newNode.keys, child.keys[t:])
	copy(newNode.values, child.values[t:])
	if !child.leaf {
		newNode.children = make([]*Node[K, V], t)
		copy(newNode.children, child.children[t:])
	}

	promoKey := child.keys[t-1]
	promoVal := child.values[t-1]

	child.keys = child.keys[:t-1]
	child.values = child.values[:t-1]
	if !child.leaf {
		child.children = child.children[:t]
	}

	parent.keys = append(parent.keys, promoKey)
	copy(parent.keys[i+1:], parent.keys[i:])
	parent.keys[i] = promoKey

	parent.values = append(parent.values, promoVal)
	copy(parent.values[i+1:], parent.values[i:])
	parent.values[i] = promoVal

	parent.children = append(parent.children, nil)
	copy(parent.children[i+2:], parent.children[i+1:])
	parent.children[i+1] = newNode
}

// --- Удаление ---

func (tree *BTree[K, V]) Delete(key K) bool {
	if tree.root == nil {
		return false
	}
	if !tree.containsKey(tree.root, key) {
		return false
	}
	tree.deleteNode(tree.root, key)
	if len(tree.root.keys) == 0 && !tree.root.leaf {
		tree.root = tree.root.children[0]
	}
	return true
}

func (tree *BTree[K, V]) containsKey(node *Node[K, V], key K) bool {
	for _, k := range node.keys {
		if tree.compare(key, k) == 0 {
			return true
		}
	}
	if node.leaf {
		return false
	}
	for _, child := range node.children {
		if tree.containsKey(child, key) {
			return true
		}
	}
	return false
}

func (tree *BTree[K, V]) deleteNode(node *Node[K, V], key K) {
	i := 0
	for i < len(node.keys) && tree.compare(key, node.keys[i]) > 0 {
		i++
	}

	if i < len(node.keys) && tree.compare(key, node.keys[i]) == 0 {
		if node.leaf {
			node.keys = append(node.keys[:i], node.keys[i+1:]...)
			node.values = append(node.values[:i], node.values[i+1:]...)
		} else {
			tree.deleteInternal(node, i, key)
		}
		return
	}

	if node.leaf {
		return
	}

	isLast := i == len(node.children)-1
	tree.ensureChildHasMinKeys(node, i)
	if isLast && i > len(node.keys) {
		tree.deleteNode(node.children[i-1], key)
	} else {
		tree.deleteNode(node.children[i], key)
	}
}

func (tree *BTree[K, V]) deleteInternal(node *Node[K, V], i int, key K) {
	t := tree.t

	if len(node.children[i].keys) >= t {
		pred := node.children[i]
		for !pred.leaf {
			pred = pred.children[len(pred.children)-1]
		}
		node.keys[i] = pred.keys[len(pred.keys)-1]
		node.values[i] = pred.values[len(pred.values)-1]
		tree.deleteNode(node.children[i], pred.keys[len(pred.keys)-1])
	} else if len(node.children[i+1].keys) >= t {
		succ := node.children[i+1]
		for !succ.leaf {
			succ = succ.children[0]
		}
		node.keys[i] = succ.keys[0]
		node.values[i] = succ.values[0]
		tree.deleteNode(node.children[i+1], succ.keys[0])
	} else {
		tree.mergeChildren(node, i)
		tree.deleteNode(node.children[i], key)
	}
}

func (tree *BTree[K, V]) mergeChildren(parent *Node[K, V], i int) {
	left := parent.children[i]
	right := parent.children[i+1]

	left.keys = append(left.keys, parent.keys[i])
	left.values = append(left.values, parent.values[i])
	left.keys = append(left.keys, right.keys...)
	left.values = append(left.values, right.values...)
	if !left.leaf {
		left.children = append(left.children, right.children...)
	}

	parent.keys = append(parent.keys[:i], parent.keys[i+1:]...)
	parent.values = append(parent.values[:i], parent.values[i+1:]...)
	parent.children = append(parent.children[:i+1], parent.children[i+2:]...)
}

func (tree *BTree[K, V]) ensureChildHasMinKeys(node *Node[K, V], i int) {
	t := tree.t

	if len(node.children[i].keys) >= t {
		return
	}
	if i > 0 && len(node.children[i-1].keys) >= t {
		tree.borrowFromLeft(node, i)
		return
	}
	if i < len(node.children)-1 && len(node.children[i+1].keys) >= t {
		tree.borrowFromRight(node, i)
		return
	}
	if i > 0 {
		tree.mergeChildren(node, i-1)
	} else {
		tree.mergeChildren(node, i)
	}
}

func (tree *BTree[K, V]) borrowFromLeft(parent *Node[K, V], i int) {
	child := parent.children[i]
	leftSibling := parent.children[i-1]

	child.keys = append(child.keys, child.keys[0])
	copy(child.keys[1:], child.keys[:len(child.keys)-1])
	child.values = append(child.values, child.values[0])
	copy(child.values[1:], child.values[:len(child.values)-1])

	child.keys[0] = parent.keys[i-1]
	child.values[0] = parent.values[i-1]

	parent.keys[i-1] = leftSibling.keys[len(leftSibling.keys)-1]
	parent.values[i-1] = leftSibling.values[len(leftSibling.values)-1]

	if !child.leaf {
		child.children = append(child.children, child.children[0])
		copy(child.children[1:], child.children[:len(child.children)-1])
		child.children[0] = leftSibling.children[len(leftSibling.children)-1]
		leftSibling.children = leftSibling.children[:len(leftSibling.children)-1]
	}

	leftSibling.keys = leftSibling.keys[:len(leftSibling.keys)-1]
	leftSibling.values = leftSibling.values[:len(leftSibling.values)-1]
}

func (tree *BTree[K, V]) borrowFromRight(parent *Node[K, V], i int) {
	child := parent.children[i]
	rightSibling := parent.children[i+1]

	child.keys = append(child.keys, parent.keys[i])
	child.values = append(child.values, parent.values[i])

	parent.keys[i] = rightSibling.keys[0]
	parent.values[i] = rightSibling.values[0]

	rightSibling.keys = rightSibling.keys[1:]
	rightSibling.values = rightSibling.values[1:]

	if !child.leaf {
		child.children = append(child.children, rightSibling.children[0])
		rightSibling.children = rightSibling.children[1:]
	}
}

// --- Инфиксный обход ---

func (tree *BTree[K, V]) InOrder(visit func(K, V)) {
	tree.inOrder(tree.root, visit)
}

func (tree *BTree[K, V]) inOrder(node *Node[K, V], visit func(K, V)) {
	if node == nil {
		return
	}
	for i := 0; i < len(node.keys); i++ {
		if !node.leaf {
			tree.inOrder(node.children[i], visit)
		}
		visit(node.keys[i], node.values[i])
	}
	if !node.leaf {
		tree.inOrder(node.children[len(node.children)-1], visit)
	}
}
