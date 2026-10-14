package euler

import (
	"math"
	"math/cmplx"
)

func gcd(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func Factorize(n int) map[int]int {
	factors := make(map[int]int)
	temp := n
	for i := 2; i*i <= temp; i++ {
		for temp%i == 0 {
			factors[i]++
			temp /= i
		}
	}
	if temp > 1 {
		factors[temp]++
	}
	return factors
}

func EulerPhiByDefinition(n int) int {
	if n <= 0 {
		return 0
	}
	count := 0
	for k := 1; k <= n; k++ {
		if gcd(k, n) == 1 {
			count++
		}
	}
	return count
}

func EulerPhiByFactorization(n int) int {
	if n <= 0 {
		return 0
	}
	result := n
	for p := range Factorize(n) {
		result -= result / p
	}
	return result
}

func EulerPhiByDFT(n int) float64 {
	if n <= 0 {
		return 0
	}
	sum := 0.0
	for k := 1; k <= n; k++ {
		g := gcd(k, n)
		w := cmplx.Exp(complex(0, 2*math.Pi*float64(k)/float64(n)))
		sum += float64(g) * real(w)
	}
	return math.Round(sum)
}

func AllRootsOfUnity(n int) []complex128 {
	roots := make([]complex128, n)
	for k := range n {
		roots[k] = cmplx.Exp(complex(0, 2*math.Pi*float64(k)/float64(n)))
	}
	return roots
}

func PrimitiveRootsOfUnity(n int) []complex128 {
	allRoots := AllRootsOfUnity(n)
	primitive := make([]complex128, 0)
	for k := range n {
		if gcd(k, n) == 1 {
			primitive = append(primitive, allRoots[k])
		}
	}
	return primitive
}

func VandermondeMatrix(n int) [][]complex128 {
	w := cmplx.Exp(complex(0, 2*math.Pi/float64(n)))
	mat := make([][]complex128, n)
	for i := range n {
		mat[i] = make([]complex128, n)
		for j := range n {
			mat[i][j] = cmplx.Pow(w, complex(float64(i*j), 0))
		}
	}
	return mat
}

func InverseVandermondeMatrix(n int) [][]complex128 {
	w := cmplx.Exp(complex(0, 2*math.Pi/float64(n)))
	inv := make([][]complex128, n)
	for i := range n {
		inv[i] = make([]complex128, n)
		for j := range n {
			inv[i][j] = cmplx.Pow(w, complex(float64(-i*j), 0)) / complex(float64(n), 0)
		}
	}
	return inv
}

func multiplyMatrixVector(mat [][]complex128, vec []complex128) []complex128 {
	n := len(mat)
	result := make([]complex128, n)
	for i := range n {
		sum := complex(0, 0)
		for j := range n {
			sum += mat[i][j] * vec[j]
		}
		result[i] = sum
	}
	return result
}

func DFT(x []complex128) []complex128 {
	return multiplyMatrixVector(VandermondeMatrix(len(x)), x)
}

func InverseDFT(X []complex128) []complex128 {
	return multiplyMatrixVector(InverseVandermondeMatrix(len(X)), X)
}
