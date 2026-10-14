package euler

import "testing"

var phiCases = []struct {
	n, want int
}{
	{1, 1}, {2, 1}, {3, 2}, {4, 2}, {5, 4}, {6, 2}, {7, 6}, {8, 4},
	{9, 6}, {10, 4}, {12, 4}, {15, 8}, {20, 8}, {30, 8}, {36, 12},
	{100, 40}, {101, 100}, {997, 996},
}

func TestTotientByDefinition(t *testing.T) {
	for _, tc := range phiCases {
		got := TotientByDefinition(tc.n)
		if got != tc.want {
			t.Errorf("TotientByDefinition(%d) = %d, want %d", tc.n, got, tc.want)
		}
	}
}

func TestTotientByFactorization(t *testing.T) {
	for _, tc := range phiCases {
		got := TotientByFactorization(tc.n)
		if got != tc.want {
			t.Errorf("TotientByFactorization(%d) = %d, want %d", tc.n, got, tc.want)
		}
	}
}

func TestTotientByDFT(t *testing.T) {
	for _, tc := range phiCases {
		got := TotientByDFT(tc.n)
		if got != tc.want {
			t.Errorf("TotientByDFT(%d) = %d, want %d", tc.n, got, tc.want)
		}
	}
}

func TestTotientConsistency(t *testing.T) {
	for _, n := range []int{1, 2, 6, 36, 100, 360, 1024, 7919} {
		a := TotientByDefinition(n)
		b := TotientByFactorization(n)
		c := TotientByDFT(n)
		if a != b || b != c {
			t.Errorf("n=%d: definition=%d, factorization=%d, dft=%d", n, a, b, c)
		}
	}
}

func TestTotientEdgeCases(t *testing.T) {
	if got := TotientByDefinition(0); got != 0 {
		t.Errorf("phi(0) = %d, want 0", got)
	}
	if got := TotientByFactorization(0); got != 0 {
		t.Errorf("phi(0) = %d, want 0", got)
	}
	if got := TotientByDFT(0); got != 0 {
		t.Errorf("phi(0) = %d, want 0", got)
	}
	if got := TotientByDefinition(1); got != 1 {
		t.Errorf("phi(1) = %d, want 1", got)
	}
}
