package primality

import "math/rand"

var rng = rand.New(rand.NewSource(42))

func PowMod(base, exp, mod int64) int64 {
	if mod == 1 {
		return 0
	}
	result := int64(1)
	base = ((base % mod) + mod) % mod
	for exp > 0 {
		if exp&1 == 1 {
			result = (result * base) % mod
		}
		exp >>= 1
		base = (base * base) % mod
	}
	return result
}

func FermatTest(n int64, k int) bool {
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

	one := int64(1)
	seen := make(map[int64]bool)
	for used := 0; used < maxK; used++ {
		var a int64
		for {
			a = rng.Int63n(nMinus3) + 2
			if !seen[a] {
				break
			}
		}
		seen[a] = true
		if PowMod(a, nMinus1, n) != one {
			return false
		}
	}
	return true
}
