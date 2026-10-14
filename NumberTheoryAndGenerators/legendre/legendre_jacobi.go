package legendre

import (
	"math/rand"
	"matstat2/primality"
)

var rngLeg = rand.New(rand.NewSource(456))

func gcdInt64(a, b int64) int64 {
	for b != 0 {
		a, b = b, a%b
	}
	if a < 0 {
		return -a
	}
	return a
}

func LegendreSymbol(a, p int64) int {
	a = ((a % p) + p) % p
	if a == 0 {
		return 0
	}
	exp := (p - 1) / 2
	if primality.PowMod(a, exp, p) == 1 {
		return 1
	}
	return -1
}

func JacobiSymbol(a, n int64) int {
	if n%2 == 0 {
		panic("Jacobi symbol: n must be odd")
	}
	a = ((a % n) + n) % n

	t := 1
	aVal := a
	nVal := n

	for aVal != 0 {
		for aVal%2 == 0 {
			aVal /= 2
			rem := nVal % 8
			if rem == 3 || rem == 5 {
				t = -t
			}
		}
		aVal, nVal = nVal, aVal
		if aVal%4 == 3 && nVal%4 == 3 {
			t = -t
		}
		aVal = aVal % nVal
	}

	if nVal == 1 {
		return t
	}
	return 0
}

func SolovayStrassenTest(n int64, k int) bool {
	if n < 2 {
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

	seen := make(map[int64]bool)
	for used := 0; used < maxK; used++ {
		var a int64
		for {
			a = rngLeg.Int63n(nMinus3) + 2
			if !seen[a] {
				break
			}
		}
		seen[a] = true
		if solovayStrassenWitness(a, n, nMinus1) {
			return false
		}
	}
	return true
}

func solovayStrassenWitness(a, n, nMinus1 int64) bool {
	one := int64(1)
	if gcdInt64(a, n) != one {
		return true
	}
	jacobi := JacobiSymbol(a, n)
	exp := (n - 1) / 2
	pow := primality.PowMod(a, exp, n)
	if jacobi == 1 && pow != one {
		return true
	}
	if jacobi == -1 && pow != nMinus1 {
		return true
	}
	return false
}
