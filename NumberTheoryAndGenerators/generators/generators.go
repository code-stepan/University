package generators

import (
	"math/rand"

	"matstat2/primality"
)

var rngGen = rand.New(rand.NewSource(789))

type LCG struct {
	a, b, m, x uint64
}

func NewLCG(a, b, m, seed uint64) *LCG {
	return &LCG{a: a, b: b, m: m, x: seed}
}

func (g *LCG) Next() uint64 {
	g.x = (g.a*g.x + g.b) % g.m
	return g.x
}

func LCGPeriod(a, b, m, seed uint64) int {
	seen := make(map[uint64]int)
	x := seed
	step := 0
	for {
		if _, ok := seen[x]; ok {
			return step - seen[x]
		}
		seen[x] = step
		x = (a*x + b) % m
		step++
		if step > 10000000 {
			return step
		}
	}
}

func EstimateLCGVariance(samples int) float64 {
	periods := make([]float64, samples)
	for i := 0; i < samples; i++ {
		a := uint64(rngGen.Intn(4095) + 1)
		b := uint64(rngGen.Intn(4096))
		m := uint64(rngGen.Intn(4095) + 1)
		seed := uint64(rngGen.Intn(4096))
		periods[i] = float64(LCGPeriod(a, b, m, seed))
	}
	return computeVariance(periods)
}

func gcdUint64(a, b uint64) uint64 {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func extendedGCD(a, b int64) (int64, int64, int64) {
	if b == 0 {
		return a, 1, 0
	}
	g, x1, y1 := extendedGCD(b, a%b)
	return g, y1, x1 - (a/b)*y1
}

func modInverse(a, n uint64) uint64 {
	aS, nS := int64(a), int64(n)
	g, x, _ := extendedGCD(aS, nS)
	if g != 1 {
		return 0
	}
	return uint64(((x % nS) + nS) % nS)
}

func isPrimeUint64(n uint64) bool {
	const maxInt64 = uint64(1<<63 - 1)
	if n > maxInt64 {
		return false
	}
	return primality.MillerRabinTest(int64(n), 10)
}

type ICG struct {
	a, b, n, x uint64
}

func NewICG(a, b, n, seed uint64) *ICG {
	return &ICG{a: a, b: b, n: n, x: seed}
}

func (g *ICG) Next() uint64 {
	if isPrimeUint64(g.n) {
		if g.x == 0 {
			g.x = g.b % g.n
		} else {
			inv := modInverse(g.x, g.n)
			g.x = (g.a*inv + g.b) % g.n
		}
	} else {
		if gcdUint64(g.a, g.n) == 1 {
			inv := modInverse(g.x, g.n)
			g.x = (g.a*inv + g.b) % g.n
		} else {
			g.x = (g.a*g.x + g.b) % g.n
		}
	}
	return g.x
}

func ICGPeriod(a, b, n, seed uint64) int {
	seen := make(map[uint64]int)
	x := seed
	step := 0
	for {
		if _, ok := seen[x]; ok {
			return step - seen[x]
		}
		seen[x] = step
		if isPrimeUint64(n) {
			if x == 0 {
				x = b % n
			} else {
				inv := modInverse(x, n)
				if inv == 0 {
					return step + 1
				}
				x = (a*inv + b) % n
			}
		} else {
			if gcdUint64(a, n) == 1 {
				inv := modInverse(x, n)
				if inv == 0 {
					return step + 1
				}
				x = (a*inv + b) % n
			} else {
				x = (a*x + b) % n
			}
		}
		step++
		if step > 5000000 {
			return step
		}
	}
}

func EstimateICGVariance(samples int) float64 {
	periods := make([]float64, samples)
	for i := 0; i < samples; i++ {
		a := uint64(rngGen.Intn(4095) + 1)
		b := uint64(rngGen.Intn(4096))
		n := uint64(rngGen.Intn(4095) + 1)
		seed := uint64(rngGen.Intn(4096))
		periods[i] = float64(ICGPeriod(a, b, n, seed))
	}
	return computeVariance(periods)
}

func FindPrime3Mod4(max uint64) uint64 {
	const maxInt64 = uint64(1<<63 - 1)
	if max > maxInt64 {
		max = maxInt64
	}
	for n := max; n >= 3; n-- {
		if n%4 != 3 {
			continue
		}
		if isPrimeUint64(n) {
			return n
		}
	}
	return 0
}

type BBS struct {
	p, q, M, x uint64
}

func NewBBS(p, q, seed uint64) *BBS {
	return &BBS{p: p, q: q, M: p * q, x: seed % (p * q)}
}

func (b *BBS) Next() uint64 {
	b.x = (b.x * b.x) % b.M
	return b.x
}

func BBSPeriod(p, q, seed uint64) int {
	b := NewBBS(p, q, seed)
	seen := make(map[uint64]int)
	x := b.x
	step := 0
	for {
		if _, ok := seen[x]; ok {
			return step - seen[x]
		}
		seen[x] = step
		x = b.Next()
		step++
		if step > 5000000 {
			return step
		}
	}
}

func EstimateBBSVariance(samples int) float64 {
	periods := make([]float64, samples)
	for i := 0; i < samples; i++ {
		p := FindPrime3Mod4(uint64(rngGen.Intn(4095) + 1))
		q := FindPrime3Mod4(uint64(rngGen.Intn(4095) + 1))
		if p == 0 || q == 0 {
			i--
			continue
		}
		seed := uint64(rngGen.Intn(4096))
		periods[i] = float64(BBSPeriod(p, q, seed))
	}
	return computeVariance(periods)
}

func computeVariance(data []float64) float64 {
	n := float64(len(data))
	sum := 0.0
	for _, v := range data {
		sum += v
	}
	mean := sum / n
	sumSq := 0.0
	for _, v := range data {
		diff := v - mean
		sumSq += diff * diff
	}
	return sumSq / n
}
