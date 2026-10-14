package main

import (
	"fmt"
	"matstat2/euler"
	"matstat2/generators"
	"matstat2/legendre"
	"matstat2/primality"
)

func main() {
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 1: Функция Эйлера φ(n)")
	fmt.Println("========================================")
	testNumbers := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 36, 100}
	for _, n := range testNumbers {
		d1 := euler.TotientByDefinition(n)
		d2 := euler.TotientByFactorization(n)
		d3 := euler.TotientByDFT(n)
		fmt.Printf("φ(%2d) = %2d (опр.) = %2d (факт.) = %2d (DFT)\n", n, d1, d2, d3)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 2: Тест простоты Ферма")
	fmt.Println("========================================")
	testPrimes := []int64{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 97, 101, 103}
	testComposites := []int64{4, 6, 8, 9, 10, 12, 14, 15, 21, 25, 27, 49, 100, 341}
	fmt.Println("Проверка простых чисел:")
	for _, n := range testPrimes {
		res := primality.FermatTest(n, 5)
		fmt.Printf("  %3d: простое? %v\n", n, res)
	}
	fmt.Println("Проверка составных чисел:")
	for _, n := range testComposites {
		res := primality.FermatTest(n, 5)
		fmt.Printf("  %3d: простое? %v\n", n, res)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 3: Символы Лежандра/Якоби и")
	fmt.Println("  тест Соловея-Штрассена")
	fmt.Println("========================================")
	fmt.Println("Символ Лежандра (a/p):")
	for _, pair := range [][2]int64{{2, 7}, {3, 7}, {4, 7}, {5, 7}, {6, 7}, {1, 13}, {2, 13}, {3, 13}, {4, 13}} {
		l := legendre.LegendreSymbol(pair[0], pair[1])
		fmt.Printf("  (%d/%d) = %d\n", pair[0], pair[1], l)
	}
	fmt.Println("Символ Якоби (a/n):")
	for _, pair := range [][2]int64{{2, 15}, {3, 15}, {4, 15}, {7, 15}, {2, 21}, {5, 21}} {
		j := legendre.JacobiSymbol(pair[0], pair[1])
		fmt.Printf("  (%d/%d) = %d\n", pair[0], pair[1], j)
	}
	fmt.Println("Тест Соловея-Штрассена:")
	for _, n := range testPrimes {
		res := legendre.SolovayStrassenTest(n, 5)
		fmt.Printf("  %3d: простое? %v\n", n, res)
	}
	for _, n := range testComposites {
		res := legendre.SolovayStrassenTest(n, 5)
		fmt.Printf("  %3d: простое? %v\n", n, res)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 4: Тест простоты Миллера-Рабина")
	fmt.Println("========================================")
	fmt.Println("Тест Миллера-Рабина:")
	for _, n := range testPrimes {
		res := primality.MillerRabinTest(n, 5)
		fmt.Printf("  %3d: простое? %v\n", n, res)
	}
	for _, n := range testComposites {
		res := primality.MillerRabinTest(n, 5)
		fmt.Printf("  %3d: простое? %v\n", n, res)
	}

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 5: LCG — период и D(P)")
	fmt.Println("========================================")
	fmt.Println("Примеры периодов LCG:")
	lcgExamples := []struct{ a, b, m, seed uint64 }{
		{5, 3, 16, 0},
		{7, 5, 32, 1},
		{3, 7, 64, 2},
		{1103515245, 12345, 1 << 31, 0},
	}
	for _, ex := range lcgExamples {
		period := generators.LCGPeriod(ex.a, ex.b, ex.m, ex.seed)
		fmt.Printf("  LCG(a=%d, b=%d, m=%d, seed=%d): период=%d\n", ex.a, ex.b, ex.m, ex.seed, period)
	}
	lcgVar := generators.EstimateLCGVariance(200)
	fmt.Printf("  D(P) для LCG (200 выборок): %.2f\n", lcgVar)

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 6: ICG — период и D(P)")
	fmt.Println("========================================")
	fmt.Println("Примеры периодов ICG:")
	icgExamples := []struct{ a, b, n, seed uint64 }{
		{2, 1, 7, 1},
		{3, 2, 11, 1},
		{4, 3, 13, 2},
		{2, 1, 9, 1},
	}
	for _, ex := range icgExamples {
		period := generators.ICGPeriod(ex.a, ex.b, ex.n, ex.seed)
		fmt.Printf("  ICG(a=%d, b=%d, n=%d, seed=%d): период=%d\n", ex.a, ex.b, ex.n, ex.seed, period)
	}
	icgVar := generators.EstimateICGVariance(100)
	fmt.Printf("  D(P) для ICG (100 выборок): %.2f\n", icgVar)

	fmt.Println()
	fmt.Println("========================================")
	fmt.Println("  ЗАДАНИЕ 7: BBS — период и D(P)")
	fmt.Println("========================================")
	fmt.Println("Примеры периодов BBS:")
	pExam := generators.FindPrime3Mod4(100)
	qExam := generators.FindPrime3Mod4(80)
	if pExam > 0 && qExam > 0 {
		period := generators.BBSPeriod(pExam, qExam, 1)
		fmt.Printf("  BBS(p=%d, q=%d, seed=1): период=%d\n", pExam, qExam, period)
	}
	pExam2 := generators.FindPrime3Mod4(200)
	qExam2 := generators.FindPrime3Mod4(150)
	if pExam2 > 0 && qExam2 > 0 {
		period2 := generators.BBSPeriod(pExam2, qExam2, 2)
		fmt.Printf("  BBS(p=%d, q=%d, seed=2): период=%d\n", pExam2, qExam2, period2)
	}

	bbsVar := generators.EstimateBBSVariance(50)
	fmt.Printf("  D(P) для BBS (50 выборок): %.2f\n", bbsVar)
}
