package primality

import "testing"

var mrPrimes = []int64{
	2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
	67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 997, 7919,
	1000000007,
}

var mrComposites = []int64{
	4, 6, 8, 9, 10, 12, 14, 15, 21, 25, 27, 33, 35, 49, 51, 65, 77, 85,
	91, 100, 121, 143, 169, 221, 289, 341, 561, 645, 1001, 1105,
	1000000008, 999999999,
}

func TestMillerRabinPrimes(t *testing.T) {
	for _, n := range mrPrimes {
		if !MillerRabinTest(n, 10) {
			t.Errorf("Miller-Rabin: %d объявлен составным", n)
		}
	}
}

func TestMillerRabinComposites(t *testing.T) {
	for _, n := range mrComposites {
		if MillerRabinTest(n, 10) {
			t.Errorf("Miller-Rabin: %d объявлен простым", n)
		}
	}
}

func TestMillerRabinEdgeCases(t *testing.T) {
	cases := []struct {
		n    int64
		want bool
	}{
		{0, false}, {1, false}, {2, true}, {3, true}, {4, false}, {-7, false},
	}
	for _, tc := range cases {
		got := MillerRabinTest(tc.n, 10)
		if got != tc.want {
			t.Errorf("MillerRabin(%d) = %v, want %v", tc.n, got, tc.want)
		}
	}
}

func TestMillerRabinDetectsCarmichael(t *testing.T) {
	for _, n := range []int64{561, 1105, 1729, 2465, 2821, 6601} {
		if MillerRabinTest(n, 10) {
			t.Errorf("Miller-Rabin: число Кармайкла %d объявлено простым", n)
		}
	}
}
