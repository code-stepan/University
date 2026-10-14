package legendre

import (
	"testing"

	"matstat2/primality"
)

func TestLegendreSymbol(t *testing.T) {
	cases := []struct {
		a, p, want int64
	}{
		{0, 7, 0},
		{1, 7, 1},
		{2, 7, 1},
		{3, 7, -1},
		{4, 7, 1},
		{5, 7, -1},
		{6, 7, -1},
		{1, 13, 1},
		{2, 13, -1},
		{3, 13, 1},
		{4, 13, 1},
		{5, 13, -1},
		{6, 13, -1},
		{7, 13, -1},
		{9, 13, 1},
		{12, 13, 1},
	}
	for _, tc := range cases {
		got := LegendreSymbol(tc.a, tc.p)
		if int64(got) != tc.want {
			t.Errorf("(%d/%d) = %d, want %d", tc.a, tc.p, got, tc.want)
		}
	}
}

func TestLegendreSymbolIsEulerCriterion(t *testing.T) {
	cases := [][2]int64{{2, 7}, {3, 11}, {5, 13}, {7, 17}, {10, 19}, {14, 23}}
	for _, tc := range cases {
		got := LegendreSymbol(tc[0], tc[1])
		pow := primality.PowMod(tc[0], (tc[1]-1)/2, tc[1])
		var expected int
		if pow == 1 {
			expected = 1
		} else {
			expected = -1
		}
		if got != expected {
			t.Errorf("(%d/%d) символ=%d, a^((p-1)/2)=%d", tc[0], tc[1], got, pow)
		}
	}
}

func TestJacobiSymbol(t *testing.T) {
	cases := []struct {
		a, n, want int64
	}{
		{2, 15, 1},
		{3, 15, 0},
		{4, 15, 1},
		{7, 15, -1},
		{2, 21, -1},
		{5, 21, 1},
		{1, 9, 1},
		{2, 9, 1},
		{4, 9, 1},
		{5, 9, 1},
		{7, 9, 1},
		{8, 9, 1},
		{1, 1, 1},
		{1, 3, 1},
		{2, 3, -1},
	}
	for _, tc := range cases {
		got := JacobiSymbol(tc.a, tc.n)
		if int64(got) != tc.want {
			t.Errorf("(%d/%d)_J = %d, want %d", tc.a, tc.n, got, tc.want)
		}
	}
}

func TestJacobiMatchesLegendreForPrime(t *testing.T) {
	cases := [][2]int64{{2, 7}, {3, 7}, {4, 7}, {5, 7}, {6, 7}, {2, 13}, {3, 13}, {4, 13}}
	for _, tc := range cases {
		if LegendreSymbol(tc[0], tc[1]) != JacobiSymbol(tc[0], tc[1]) {
			t.Errorf("(%d/%d): Лежандр != Якоби", tc[0], tc[1])
		}
	}
}

var solovayPrimes = []int64{
	2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
	67, 71, 73, 79, 83, 89, 97, 101, 103, 997, 7919,
}

var solovayComposites = []int64{
	4, 6, 8, 9, 10, 12, 14, 15, 21, 25, 27, 35, 49, 51, 65, 77, 91, 121,
	143, 169, 221, 341, 561, 1105, 1001, 1000000008,
}

func TestSolovayStrassenPrimes(t *testing.T) {
	for _, n := range solovayPrimes {
		if !SolovayStrassenTest(n, 8) {
			t.Errorf("Solovay-Strassen: %d объявлен составным", n)
		}
	}
}

func TestSolovayStrassenComposites(t *testing.T) {
	for _, n := range solovayComposites {
		if SolovayStrassenTest(n, 8) {
			t.Errorf("Solovay-Strassen: %d объявлен простым", n)
		}
	}
}

func TestSolovayStrassenEdgeCases(t *testing.T) {
	cases := []struct {
		n    int64
		want bool
	}{
		{0, false}, {1, false}, {2, true}, {3, true}, {4, false}, {-5, false},
	}
	for _, tc := range cases {
		got := SolovayStrassenTest(tc.n, 5)
		if got != tc.want {
			t.Errorf("SolovayStrassen(%d) = %v, want %v", tc.n, got, tc.want)
		}
	}
}

func TestGcdInt64(t *testing.T) {
	cases := []struct{ a, b, want int64 }{
		{48, 18, 6}, {100, 75, 25}, {17, 13, 1}, {0, 5, 5}, {0, 0, 0}, {-12, 8, 4},
	}
	for _, tc := range cases {
		if got := gcdInt64(tc.a, tc.b); got != tc.want {
			t.Errorf("gcd(%d,%d) = %d, want %d", tc.a, tc.b, got, tc.want)
		}
	}
}
