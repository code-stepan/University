package primality

import "testing"

var smallPrimes = []int64{
	2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
	67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 997, 7919,
}

var smallComposites = []int64{
	4, 6, 8, 9, 10, 12, 14, 15, 21, 25, 27, 33, 35, 49, 51, 65, 77, 85,
	91, 100, 121, 143, 169, 221, 289, 341, 1001,
}

func TestFermatPrimes(t *testing.T) {
	for _, n := range smallPrimes {
		if !FermatTest(n, 5) {
			t.Errorf("Fermat: %d объявлен составным", n)
		}
	}
}

func TestFermatComposites(t *testing.T) {
	for _, n := range smallComposites {
		if FermatTest(n, 5) {
			t.Errorf("Fermat: %d объявлен простым", n)
		}
	}
}

func TestFermatEdgeCases(t *testing.T) {
	cases := []struct {
		n    int64
		want bool
	}{
		{0, false}, {1, false}, {2, true}, {3, true}, {4, false}, {-7, false},
	}
	for _, tc := range cases {
		got := FermatTest(tc.n, 5)
		if got != tc.want {
			t.Errorf("Fermat(%d) = %v, want %v", tc.n, got, tc.want)
		}
	}
}

func TestFermatLargePrime(t *testing.T) {
	const p int64 = 1000000007
	if !FermatTest(p, 10) {
		t.Error("10^9+7 должен быть простым по Ферма")
	}
}

func TestFermatLargeComposite(t *testing.T) {
	const n int64 = 1000000008
	if FermatTest(n, 10) {
		t.Error("10^9+8 составное, но Ферма считает иначе")
	}
}

func TestPowMod(t *testing.T) {
	cases := []struct {
		base, exp, mod, want int64
	}{
		{2, 10, 1000, 24},
		{3, 0, 7, 1},
		{0, 0, 7, 1},
		{5, 1, 13, 5},
		{2, 100, 13, 3},
		{-2, 3, 7, 6},
		{1, 0, 1, 0},
	}
	for _, tc := range cases {
		got := PowMod(tc.base, tc.exp, tc.mod)
		if got != tc.want {
			t.Errorf("PowMod(%d,%d,%d) = %d, want %d", tc.base, tc.exp, tc.mod, got, tc.want)
		}
	}
}
