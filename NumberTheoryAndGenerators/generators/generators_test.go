package generators

import "testing"

func TestLCGNext(t *testing.T) {
	g := NewLCG(5, 3, 16, 0)
	want := []uint64{3, 2, 13, 4, 7, 6, 1, 8, 11, 10, 5, 12, 15, 14, 9, 0}
	for i, w := range want {
		got := g.Next()
		if got != w {
			t.Errorf("Next #%d: got %d, want %d", i+1, got, w)
		}
	}
}

func TestLCGPeriodKnown(t *testing.T) {
	cases := []struct {
		a, b, m, seed uint64
		want          int
	}{
		{5, 3, 16, 0, 16},
		{7, 5, 32, 1, 8},
		{3, 7, 64, 2, 32},
	}
	for _, tc := range cases {
		got := LCGPeriod(tc.a, tc.b, tc.m, tc.seed)
		if got != tc.want {
			t.Errorf("LCGPeriod(%d,%d,%d,%d) = %d, want %d",
				tc.a, tc.b, tc.m, tc.seed, got, tc.want)
		}
	}
}

func TestLCGPeriodBoundedByM(t *testing.T) {
	for _, m := range []uint64{16, 32, 64, 100, 256} {
		p := LCGPeriod(5, 3, m, 1)
		if p <= 0 || p > int(m) {
			t.Errorf("LCG период=%d вне диапазона (1..%d)", p, m)
		}
	}
}

func TestICGPeriodKnown(t *testing.T) {
	cases := []struct {
		a, b, n, seed uint64
		want          int
	}{
		{2, 1, 7, 1, 5},
		{3, 2, 11, 1, 9},
		{4, 3, 13, 2, 3},
	}
	for _, tc := range cases {
		got := ICGPeriod(tc.a, tc.b, tc.n, tc.seed)
		if got != tc.want {
			t.Errorf("ICGPeriod(%d,%d,%d,%d) = %d, want %d",
				tc.a, tc.b, tc.n, tc.seed, got, tc.want)
		}
	}
}

func TestICGNext(t *testing.T) {
	g := NewICG(2, 1, 7, 1)
	want := []uint64{3, 4, 5, 0, 1, 3}
	for i, w := range want {
		got := g.Next()
		if got != w {
			t.Errorf("ICG.Next #%d: got %d, want %d", i+1, got, w)
		}
	}
}

func TestBBSNext(t *testing.T) {
	b := NewBBS(3, 5, 2)
	if got := b.Next(); got != 4 {
		t.Errorf("BBS(p=3,q=5,seed=2).Next() = %d, want 4", got)
	}
	if got := b.Next(); got != 1 {
		t.Errorf("BBS(p=3,q=5,seed=2).Next() = %d, want 1", got)
	}
}

func TestBBSPeriodPositive(t *testing.T) {
	p := FindPrime3Mod4(100)
	q := FindPrime3Mod4(80)
	if p == 0 || q == 0 {
		t.Skip("Blum-простые не найдены")
	}
	period := BBSPeriod(p, q, 1)
	if period <= 0 {
		t.Errorf("BBS период не положительный: %d", period)
	}
}

func TestFindPrime3Mod4(t *testing.T) {
	p := FindPrime3Mod4(100)
	if p == 0 {
		t.Fatal("Не найдено ни одной простой 3 (mod 4) в диапазоне")
	}
	if p%4 != 3 {
		t.Errorf("Найдено %d, но %d mod 4 = %d, ожидалось 3", p, p, p%4)
	}
	if !isPrimeUint64(p) {
		t.Errorf("Найденное число %d не является простым", p)
	}
	if p < 3 || p > 100 {
		t.Errorf("Найденное %d вне диапазона [3,100]", p)
	}
}

func TestEstimateLCGVariance(t *testing.T) {
	v := EstimateLCGVariance(20)
	if v < 0 {
		t.Errorf("D(P) для LCG отрицательная: %f", v)
	}
}

func TestEstimateICGVariance(t *testing.T) {
	v := EstimateICGVariance(20)
	if v < 0 {
		t.Errorf("D(P) для ICG отрицательная: %f", v)
	}
}

func TestEstimateBBSVariance(t *testing.T) {
	v := EstimateBBSVariance(10)
	if v < 0 {
		t.Errorf("D(P) для BBS отрицательная: %f", v)
	}
}

func TestComputeVariance(t *testing.T) {
	if v := computeVariance([]float64{2, 4, 4, 4, 5, 5, 7, 9}); v < 3.99 || v > 4.01 {
		t.Errorf("computeVariance = %f, ожидалось ~4", v)
	}
	if v := computeVariance([]float64{5, 5, 5, 5}); v != 0 {
		t.Errorf("computeVariance(одинаковые) = %f, want 0", v)
	}
}

func TestModInverse(t *testing.T) {
	if inv := modInverse(3, 11); inv != 4 {
		t.Errorf("3^-1 mod 11 = %d, want 4", inv)
	}
	if inv := modInverse(7, 26); inv != 15 {
		t.Errorf("7^-1 mod 26 = %d, want 15", inv)
	}
	if inv := modInverse(2, 4); inv != 0 {
		t.Errorf("2^-1 mod 4 должно быть 0, got %d", inv)
	}
}

func TestExtendedGCD(t *testing.T) {
	g, x, y := extendedGCD(35, 15)
	if g != 5 {
		t.Errorf("gcd = %d, want 5", g)
	}
	if 35*x+15*y != 5 {
		t.Errorf("Безье: 35*%d+15*%d = %d, want 5", x, y, 35*x+15*y)
	}
}

func TestIsPrimeUint64(t *testing.T) {
	primes := []uint64{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97, 101, 7919}
	comps := []uint64{0, 1, 4, 6, 8, 9, 10, 15, 21, 25, 49, 100, 1001}
	for _, p := range primes {
		if !isPrimeUint64(p) {
			t.Errorf("%d не признано простым", p)
		}
	}
	for _, c := range comps {
		if isPrimeUint64(c) {
			t.Errorf("%d не признано составным", c)
		}
	}
}

func TestGCDUint64(t *testing.T) {
	cases := []struct {
		a, b, want uint64
	}{
		{48, 18, 6},
		{100, 75, 25},
		{17, 13, 1},
		{0, 5, 5},
		{0, 0, 0},
	}
	for _, tc := range cases {
		if got := gcdUint64(tc.a, tc.b); got != tc.want {
			t.Errorf("gcd(%d,%d) = %d, want %d", tc.a, tc.b, got, tc.want)
		}
	}
}

func TestICGPeriodComposite(t *testing.T) {
	got := ICGPeriod(2, 1, 9, 1)
	if got <= 0 {
		t.Errorf("ICG период для составного n=9 не положительный: %d", got)
	}
}
