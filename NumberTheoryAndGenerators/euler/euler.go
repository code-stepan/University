package euler

import "math"

func gcd(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func factorize(n int) map[int]int {
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

func TotientByDefinition(n int) int {
	count := 0
	for k := 1; k <= n; k++ {
		if gcd(k, n) == 1 {
			count++
		}
	}
	return count
}

func TotientByFactorization(n int) int {
	if n <= 1 {
		return n
	}
	factors := factorize(n)
	result := float64(n)
	for p := range factors {
		result *= 1.0 - 1.0/float64(p)
	}
	return int(math.Round(result))
}

func TotientByDFT(n int) int {
	sum := 0.0
	for k := 1; k <= n; k++ {
		g := float64(gcd(k, n))
		angle := 2.0 * math.Pi * float64(k) / float64(n)
		sum += g * math.Cos(angle)
	}
	return int(math.Round(sum))
}
