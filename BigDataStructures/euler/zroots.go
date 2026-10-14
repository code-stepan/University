package euler

import (
	"math"
	"math/cmplx"
)

func ModPow(base, exp, mod int) int {
	result := 1
	base %= mod
	for exp > 0 {
		if exp&1 == 1 {
			result = result * base % mod
		}
		base = base * base % mod
		exp >>= 1
	}
	return result
}

func HasPrimitiveRoot(n int) bool {
	if n < 2 {
		return false
	}
	if n == 2 || n == 4 {
		return true
	}
	factors := Factorize(n)
	if _, hasTwo := factors[2]; hasTwo {
		if factors[2] > 1 {
			return false
		}
		if len(factors) != 2 {
			return false
		}
	}
	oddPrimes := 0
	for p := range factors {
		if p != 2 {
			oddPrimes++
		}
	}
	return oddPrimes == 1
}

func FindPrimitiveRoot(n int) (int, bool) {
	if !HasPrimitiveRoot(n) {
		return 0, false
	}
	phi := EulerPhiByFactorization(n)
	factors := Factorize(phi)
	for g := 2; g < n; g++ {
		if gcd(g, n) != 1 {
			continue
		}
		isRoot := true
		for p := range factors {
			if ModPow(g, phi/p, n) == 1 {
				isRoot = false
				break
			}
		}
		if isRoot {
			return g, true
		}
	}
	return 0, false
}

func AllPrimitiveRootsInZn(n int) []int {
	g, ok := FindPrimitiveRoot(n)
	if !ok {
		return nil
	}
	phi := EulerPhiByFactorization(n)
	roots := make([]int, 0)
	for i := 1; i < phi; i++ {
		if gcd(i, phi) == 1 {
			roots = append(roots, ModPow(g, i, n))
		}
	}
	return roots
}

func VandermondeMatrixFromRoot(n int) ([][]complex128, bool) {
	if _, ok := FindPrimitiveRoot(n); !ok {
		return nil, false
	}
	w := cmplx.Exp(complex(0, 2*math.Pi/float64(n)))
	mat := make([][]complex128, n)
	for i := range n {
		mat[i] = make([]complex128, n)
		for j := range n {
			mat[i][j] = cmplx.Pow(w, complex(float64(i*j), 0))
		}
	}
	return mat, true
}

func InverseVandermondeMatrixFromRoot(n int) ([][]complex128, bool) {
	if _, ok := FindPrimitiveRoot(n); !ok {
		return nil, false
	}
	w := cmplx.Exp(complex(0, 2*math.Pi/float64(n)))
	inv := make([][]complex128, n)
	for i := range n {
		inv[i] = make([]complex128, n)
		for j := range n {
			inv[i][j] = cmplx.Pow(w, complex(float64(-i*j), 0)) / complex(float64(n), 0)
		}
	}
	return inv, true
}

func fftRadix2(x []complex128, invert bool) []complex128 {
	n := len(x)
	if n == 1 {
		return x
	}

	even := make([]complex128, n/2)
	odd := make([]complex128, n/2)
	for i := 0; i < n/2; i++ {
		even[i] = x[2*i]
		odd[i] = x[2*i+1]
	}

	evenFFT := fftRadix2(even, invert)
	oddFFT := fftRadix2(odd, invert)

	angle := 2 * math.Pi / float64(n)
	if invert {
		angle = -angle
	}

	result := make([]complex128, n)
	w := complex(1, 0)
	wn := cmplx.Exp(complex(0, angle))

	for k := 0; k < n/2; k++ {
		t := w * oddFFT[k]
		result[k] = evenFFT[k] + t
		result[k+n/2] = evenFFT[k] - t
		w *= wn
	}
	return result
}

func FFT(x []complex128) []complex128 {
	n := len(x)
	if n == 0 {
		return x
	}
	if n&(n-1) != 0 {
		return DFT(x)
	}
	return fftRadix2(x, false)
}

func InverseFFT(X []complex128) []complex128 {
	n := len(X)
	if n == 0 {
		return X
	}
	if n&(n-1) != 0 {
		return InverseDFT(X)
	}
	result := fftRadix2(X, true)
	for i := range result {
		result[i] /= complex(float64(n), 0)
	}
	return result
}
