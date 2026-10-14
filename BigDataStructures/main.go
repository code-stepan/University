package main

import (
	"fmt"
	"math/cmplx"
	"strconv"

	"github.com/code-stepan/BigDataStructures/bloomfilter"
	"github.com/code-stepan/BigDataStructures/bst"
	"github.com/code-stepan/BigDataStructures/btree"
	"github.com/code-stepan/BigDataStructures/countminsketch"
	"github.com/code-stepan/BigDataStructures/euler"
	"github.com/code-stepan/BigDataStructures/fenwicktree"
	"github.com/code-stepan/BigDataStructures/hashtable"
	"github.com/code-stepan/BigDataStructures/heaps"
	"github.com/code-stepan/BigDataStructures/segmenttree"
	"github.com/code-stepan/BigDataStructures/trie"
)

type task struct {
	name string
	fn   func()
}

var tasks = []task{
	{"BST", demoBST},
	{"B-дерево", demoBTree},
	{"Bloom Filter", demoBloomFilter},
	{"Trie", demoTrie},
	{"Hash Table", demoHashTable},
	{"Count-Min Sketch", demoCountMinSketch},
	{"Дерево отрезков", demoSegmentTree},
	{"Дерево Фенвика", demoFenwickTree},
	{"Binary Heap", demoBinaryHeap},
	{"Binomial Heap", demoBinomialHeap},
	{"Эйлер / ДПФ", demoEuler},
	{"Z_n корни / FFT", demoZRoots},
}

func main() {
	for {
		fmt.Println("\n=== Меню задач ===")
		for i, t := range tasks {
			fmt.Printf("  %d. %s\n", i+1, t.name)
		}
		fmt.Println("  0. Выход")
		fmt.Print(">> ")

		input, err := strconv.Atoi(scan())
		if err != nil {
			fmt.Println("Некорректный ввод")
			continue
		}
		if input == 0 {
			break
		}

		if input >= 1 && input <= len(tasks) {
			tasks[input-1].fn()
		} else {
			fmt.Println("Некорректная задача")
		}
	}
}

func scan() string {
	var s string
	fmt.Scan(&s)
	return s
}

func demoBST() {
	tree := bst.New[int, string](func(a, b int) int { return a - b })

	for _, v := range []int{50, 30, 70, 20, 40, 60, 80} {
		tree.Insert(v, fmt.Sprintf("val_%d", v))
	}

	if val, ok := tree.Get(40); ok {
		fmt.Println("Найдено 40:", val)
	}

	fmt.Println("Удаление 50:", tree.Delete(50))

	fmt.Print("InOrder: ")
	tree.InOrder(func(k int, v string) { fmt.Printf("%d(%s) ", k, v) })
	fmt.Println()
}

func demoBTree() {
	tree := btree.New[int, string](3, func(a, b int) int { return a - b })

	for _, v := range []int{50, 30, 70, 20, 40, 60, 80, 10, 25, 35} {
		tree.Insert(v, fmt.Sprintf("val_%d", v))
	}

	fmt.Print("InOrder после вставки: ")
	tree.InOrder(func(k int, v string) { fmt.Printf("%d(%s) ", k, v) })
	fmt.Println()

	if val, ok := tree.Get(40); ok {
		fmt.Println("Найдено 40:", val)
	}

	fmt.Println("Удаление 50:", tree.Delete(50))
	fmt.Println("Удаление 50 повторно:", tree.Delete(50))

	fmt.Print("InOrder после удаления 50: ")
	tree.InOrder(func(k int, v string) { fmt.Printf("%d(%s) ", k, v) })
	fmt.Println()

	if _, ok := tree.Get(50); !ok {
		fmt.Println("Поиск удалённого 50: не найден")
	}

	tree.Clear()
	if _, ok := tree.Get(30); !ok {
		fmt.Println("После Clear, поиск 30: не найден")
	}
}

func demoBloomFilter() {
	hasher := bloomfilter.NewMurMur3Hasher()
	bf, err := bloomfilter.NewBloomFilter(1000, 0.01, hasher)
	if err != nil {
		fmt.Printf("Ошибка: %v\n", err)
		return
	}

	bf.Add([]byte("meme"))
	bf.Add([]byte("mem"))
	bf.Add([]byte("memes"))

	fmt.Println("contains 'ddjdghf':", bf.Test([]byte("ddjdghf")))
	fmt.Println("contains 'meme':", bf.Test([]byte("meme")))
}

func demoTrie() {
	t := trie.New[string]("abcdefghijklmnopqrstuvwxyz")
	t.Insert("hello", "привет")
	t.Insert("world", "мир")
	t.Insert("help", "помощь")
	t.Insert("heap", "куча")

	for _, word := range []string{"hello", "world"} {
		if val, ok := t.Get(word); ok {
			fmt.Printf("Найдено %s: %s\n", word, val)
		}
	}

	fmt.Println("StartsWith 'he':", t.StartsWith("he"))
	fmt.Println("StartsWith 'xyz':", t.StartsWith("xyz"))

	t.Delete("help")
	if _, ok := t.Get("help"); !ok {
		fmt.Println("help удалён и не найден")
	}
}

func demoHashTable() {
	h, err := hashtable.New[string, int](8, func(s string) uint64 {
		var hash uint64
		for i := 0; i < len(s); i++ {
			hash = hash*31 + uint64(s[i])
		}
		return hash
	})
	if err != nil {
		fmt.Printf("Ошибка: %v\n", err)
		return
	}

	h.Set("go", 1)
	h.Set("rust", 2)
	h.Set("zig", 3)

	fmt.Printf("Размер: %d\n", h.Len())

	if val, ok := h.Get("rust"); ok {
		fmt.Printf("rust: %d\n", val)
	}

	h.Delete("go")
	fmt.Printf("После удаления go, размер: %d\n", h.Len())
}

func demoCountMinSketch() {
	cms := countminsketch.New(0.01, 0.01)
	for _, word := range []string{"apple", "banana", "apple", "apple", "banana", "cherry"} {
		cms.Add([]byte(word))
	}

	for _, word := range []string{"apple", "banana", "cherry", "unknown"} {
		fmt.Printf("%s: %d\n", word, cms.Count([]byte(word)))
	}
}

func demoSegmentTree() {
	n := 8
	sum := func(a, b int) int { return a + b }
	st := segmenttree.New(n, sum, 0)

	values := []int{1, 3, 5, 7, 9, 11, 13, 15}
	for i, v := range values {
		st.Update(i, v)
	}

	fmt.Println("=== Дерево отрезков (сумма) ===")
	fmt.Printf("Массив: %v\n", values)

	fmt.Println("\nИнтервальные суммы:")
	ranges := [][2]int{{0, 3}, {2, 5}, {0, 7}, {4, 7}}
	for _, r := range ranges {
		fmt.Printf("  sum[%d..%d] = %d\n", r[0], r[1], st.Query(r[0], r[1]))
	}

	fmt.Println("\nОбновление: установить значение 10 в позиции 3")
	st.Update(3, 10)
	fmt.Printf("  sum[0..3] = %d (ожидается 1+3+5+10 = 19)\n", st.Query(0, 3))
	fmt.Printf("  sum[2..5] = %d (ожидается 5+10+9+11 = 35)\n", st.Query(2, 5))
}

func demoFenwickTree() {
	n := 10
	sum := func(a, b int) int { return a + b }
	sub := func(a, b int) int { return a - b }
	ft := fenwicktree.New(n, sum, sub, 0)

	values := []int{1, 3, 5, 7, 9, 11, 13, 15, 17, 19}
	for i, v := range values {
		ft.Update(i, v)
	}

	fmt.Println("=== Дерево Фенвика (сумма) ===")
	fmt.Printf("Массив: %v\n", values)

	fmt.Println("\nПрефиксные суммы:")
	for i := range n {
		fmt.Printf("  sum[0..%d] = %d\n", i, ft.Query(i))
	}

	fmt.Println("\nИнтервальные суммы:")
	ranges := [][2]int{{0, 4}, {2, 7}, {5, 9}, {0, 9}}
	for _, r := range ranges {
		fmt.Printf("  sum[%d..%d] = %d\n", r[0], r[1], ft.RangeQuery(r[0], r[1]))
	}

	fmt.Println("\nОбновление: установить значение 10 в позиции 3")
	ft.Update(3, 10)
	fmt.Printf("  sum[0..4] = %d (ожидается 1+3+5+10+9 = 28)\n", ft.RangeQuery(0, 4))
}

func demoBinaryHeap() {
	bh := heaps.NewBinaryHeap[int, string](func(a, b int) int { return a - b })

	items := []struct {
		k int
		v string
	}{
		{20, "двадцать"}, {50, "пятьдесят"}, {30, "тридцать"},
		{10, "десять"}, {40, "сорок"},
	}
	for _, item := range items {
		bh.Insert(item.k, item.v)
	}

	if k, v, ok := bh.Peek(); ok {
		fmt.Printf("Max: %d (%s)\n", k, v)
	}

	fmt.Println("Извлечение:")
	for !bh.IsEmpty() {
		k, v, _ := bh.ExtractMax()
		fmt.Printf("  %d (%s)\n", k, v)
	}
}

func demoBinomialHeap() {
	bn := heaps.NewBinomialHeap[int, string](func(a, b int) int { return a - b })
	for _, item := range []struct {
		k int
		v string
	}{
		{20, "двадцать"}, {50, "пятьдесят"}, {30, "тридцать"},
		{10, "десять"}, {40, "сорок"},
	} {
		bn.Insert(item.k, item.v)
	}

	if k, v, ok := bn.Peek(); ok {
		fmt.Printf("Max: %d (%s)\n", k, v)
	}

	fmt.Println("Извлечение:")
	for !bn.IsEmpty() {
		k, v, _ := bn.ExtractMax()
		fmt.Printf("  %d (%s)\n", k, v)
	}

	fmt.Println("\nСлияние двух куч:")
	bn1 := heaps.NewBinomialHeap[int, string](func(a, b int) int { return a - b })
	bn1.Insert(100, "сто")
	bn1.Insert(5, "пять")

	bn2 := heaps.NewBinomialHeap[int, string](func(a, b int) int { return a - b })
	bn2.Insert(50, "пятьдесят")
	bn2.Insert(25, "двадцать пять")

	bn1.Merge(bn2)
	fmt.Printf("Размер после слияния: %d\n", bn1.Len())

	for !bn1.IsEmpty() {
		k, v, _ := bn1.ExtractMax()
		fmt.Printf("  %d (%s)\n", k, v)
	}
}

func demoEuler() {
	n := 12
	fmt.Printf("=== Функция Эйлера φ(%d) ===\n", n)
	fmt.Printf("По определению:  %d\n", euler.EulerPhiByDefinition(n))
	fmt.Printf("Факторизация:    %d\n", euler.EulerPhiByFactorization(n))
	fmt.Printf("Через ДПФ:       %.0f\n", euler.EulerPhiByDFT(n))
	fmt.Printf("Множители:       %v\n", euler.Factorize(n))

	nRoots := 6
	fmt.Printf("\n=== Корни степени %d ===\n", nRoots)
	for i, r := range euler.AllRootsOfUnity(nRoots) {
		fmt.Printf("  z_%d = %.4f + %.4fi\n", i, real(r), imag(r))
	}

	fmt.Printf("\n=== Первобразные корни ===\n")
	for i, r := range euler.PrimitiveRootsOfUnity(nRoots) {
		fmt.Printf("  ζ_%d = %.4f + %.4fi\n", i, real(r), imag(r))
	}

	matSize := 4
	fmt.Printf("\n=== Вандрмонда %dx%d ===\n", matSize, matSize)
	printMatrix(euler.VandermondeMatrix(matSize))

	fmt.Printf("\n=== Обратная Вандрмонда ===\n")
	printMatrix(euler.InverseVandermondeMatrix(matSize))

	fmt.Printf("\n=== ДПФ (прямое + обратное) ===\n")
	input := make([]complex128, matSize)
	for i := range input {
		input[i] = complex(float64(i+1), 0)
	}
	printVector("Вход", input)
	printVector("ДПФ", euler.DFT(input))
	printVector("Обратное", euler.InverseDFT(euler.DFT(input)))
}

func demoZRoots() {
	n := 7
	fmt.Printf("=== Первобразные корни из 1 в Z_%d ===\n", n)

	if euler.HasPrimitiveRoot(n) {
		fmt.Printf("Z_%d имеет первобразные корни\n", n)
		phi := euler.EulerPhiByFactorization(n)
		fmt.Printf("φ(%d) = %d\n", n, phi)

		g, _ := euler.FindPrimitiveRoot(n)
		fmt.Printf("Первый первобразный корень: %d\n", g)
		fmt.Printf("Проверка: %d^%d mod %d = %d\n", g, phi, n, euler.ModPow(g, phi, n))

		for _, p := range euler.Factorize(phi) {
			fmt.Printf("  %d^%d mod %d = %d (≠ 1)\n", g, phi/p, n, euler.ModPow(g, phi/p, n))
		}

		roots := euler.AllPrimitiveRootsInZn(n)
		fmt.Printf("Все первобразные корни: %v\n", roots)
		fmt.Printf("Количество: φ(φ(%d)) = φ(%d) = %d\n", n, phi, len(roots))
	} else {
		fmt.Printf("Z_%d не имеет первобразных корней\n", n)
	}

	matSize := 4
	fmt.Printf("\n=== Вандрмонда %dx%d (через первобразный корень Z_%d) ===\n", matSize, matSize, matSize)
	if mat, ok := euler.VandermondeMatrixFromRoot(matSize); ok {
		printMatrix(mat)
	} else {
		fmt.Printf("Z_%d не имеет первобразного корня, матрица не построена\n", matSize)
	}

	fmt.Printf("\n=== Обратная Вандрмонда ===\n")
	if inv, ok := euler.InverseVandermondeMatrixFromRoot(matSize); ok {
		printMatrix(inv)
	}

	fftSize := 8
	input := make([]complex128, fftSize)
	for i := range input {
		input[i] = complex(float64(i+1), 0)
	}

	fmt.Printf("\n=== ДПФ vs БПФ (n=%d) ===\n", fftSize)
	printVector("Вход", input)

	dftResult := euler.DFT(input)
	printVector("ДПФ (матрица)", dftResult)

	fftResult := euler.FFT(input)
	printVector("БПФ (Cooley-Tukey)", fftResult)

	fmt.Printf("Совпадают: %v\n", vectorsEqual(dftResult, fftResult))

	ifftResult := euler.InverseFFT(fftResult)
	printVector("Обратная БПФ", ifftResult)

	dftInv := euler.InverseDFT(dftResult)
	fmt.Printf("Обратная ДПФ == Обратная БПФ: %v\n", vectorsEqual(dftInv, ifftResult))

	nonPow2Size := 6
	input6 := make([]complex128, nonPow2Size)
	for i := range input6 {
		input6[i] = complex(float64(i+1), 0)
	}
	fmt.Printf("\n=== БПФ для n=%d (не степень двойки, fallback на ДПФ) ===\n", nonPow2Size)
	printVector("Вход", input6)
	fft6 := euler.FFT(input6)
	dft6 := euler.DFT(input6)
	printVector("БПФ", fft6)
	fmt.Printf("Совпадает с ДПФ: %v\n", vectorsEqual(fft6, dft6))
}

func vectorsEqual(a, b []complex128) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if cmplx.Abs(a[i]-b[i]) > 1e-9 {
			return false
		}
	}
	return true
}

func printMatrix(m [][]complex128) {
	for _, row := range m {
		for _, v := range row {
			fmt.Printf("(%6.3f+%6.3fi) ", real(v), imag(v))
		}
		fmt.Println()
	}
}

func printVector(label string, v []complex128) {
	fmt.Printf("%12s: ", label)
	for _, x := range v {
		fmt.Printf("(%.4f+%.4fi) ", real(x), imag(x))
	}
	fmt.Println()
}
