package primality

import "math/rand"

var rngMR = rand.New(rand.NewSource(123))

func MillerRabinTest(n int64, k int) bool {
	if n <= 1 {
		return false
	}
	if n <= 3 {
		return true
	}
	if n%2 == 0 {
		return false
	}

	nMinus1 := n - 1
	s := 0
	d := nMinus1
	for d%2 == 0 {
		s++
		d /= 2
	}

	nMinus3 := n - 3
	if nMinus3 <= 0 {
		return false
	}

	maxK := k
	if int(nMinus3) < maxK {
		maxK = int(nMinus3)
	}
	if maxK <= 0 {
		return false
	}

	seen := make(map[int64]bool)
	for used := 0; used < maxK; used++ {
		var a int64
		for {
			a = rngMR.Int63n(nMinus3) + 2
			if !seen[a] {
				break
			}
		}
		seen[a] = true
		// свидетель составности
		if millerRabinWitness(a, d, n, nMinus1, s) {
			return false
		}
	}
	return true
}

func millerRabinWitness(a, d, n, nMinus1 int64, s int) bool {
	one := int64(1)
	x := PowMod(a, d, n)
	if x == one || x == nMinus1 {
		return false
	}
	for r := 0; r < s-1; r++ {
		x = (x * x) % n
		if x == nMinus1 {
			return false
		}
	}
	return true
}
