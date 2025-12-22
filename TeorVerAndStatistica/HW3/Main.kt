import kotlin.math.*
import kotlin.random.Random

// Класс для представления выборки
data class Sample(val values: Map<Double, Int>) {
    val size: Int get() = values.values.sum()

    fun isValid(): Boolean {
        return values.all { it.key >= 0 && it.value >= 0 }
    }
}

// 1. Генераторы распределений
object DistributionGenerators {

    // a. Нормальное распределение
    fun normalDistribution(n: Int, mean: Double = 0.0, stdDev: Double = 1.0): Sample {
        val values = mutableMapOf<Double, Int>()
        repeat(n) {
            val u1 = Random.nextDouble()
            val u2 = Random.nextDouble()
            val z = sqrt(-2.0 * ln(u1)) * cos(2.0 * PI * u2)
            val value = mean + stdDev * z
            values[value] = values.getOrDefault(value, 0) + 1
        }
        return Sample(values)
    }

    // b. Распределение Пуассона
    fun poissonDistribution(n: Int, lambda: Double = 3.0): Sample {
        val values = mutableMapOf<Double, Int>()
        repeat(n) {
            var k = 0
            var p = 1.0
            val l = exp(-lambda)
            do {
                k++
                p *= Random.nextDouble()
            } while (p > l)
            val value = (k - 1).toDouble()
            values[value] = values.getOrDefault(value, 0) + 1
        }
        return Sample(values)
    }

    // c. Геометрическое распределение
    fun geometricDistribution(n: Int, p: Double = 0.3): Sample {
        val values = mutableMapOf<Double, Int>()
        repeat(n) {
            val u = Random.nextDouble()
            val value = floor(ln(1 - u) / ln(1 - p)).toDouble()
            values[value] = values.getOrDefault(value, 0) + 1
        }
        return Sample(values)
    }

    // d. Гипергеометрическое распределение
    fun hypergeometricDistribution(n: Int, N: Int = 50, K: Int = 20, nDraw: Int = 10): Sample {
        val values = mutableMapOf<Double, Int>()
        repeat(n) {
            val population = MutableList(N) { it < K }
            population.shuffle()
            val successes = population.take(nDraw).count { it }
            val value = successes.toDouble()
            values[value] = values.getOrDefault(value, 0) + 1
        }
        return Sample(values)
    }

    // e. Двойное распределение Пуассона
    fun doublePoissonDistribution(n: Int, lambda1: Double = 2.0, lambda2: Double = 5.0): Sample {
        val values = mutableMapOf<Double, Int>()
        repeat(n) {
            val poisson1 = generatePoisson(lambda1)
            val poisson2 = generatePoisson(lambda2)
            val value = (poisson1 + poisson2).toDouble()
            values[value] = values.getOrDefault(value, 0) + 1
        }
        return Sample(values)
    }

    // f. Двойное геометрическое распределение
    fun doubleGeometricDistribution(n: Int, p1: Double = 0.3, p2: Double = 0.4): Sample {
        val values = mutableMapOf<Double, Int>()
        repeat(n) {
            val geom1 = floor(ln(1 - Random.nextDouble()) / ln(1 - p1))
            val geom2 = floor(ln(1 - Random.nextDouble()) / ln(1 - p2))
            val value = (geom1 + geom2)
            values[value] = values.getOrDefault(value, 0) + 1
        }
        return Sample(values)
    }

    private fun generatePoisson(lambda: Double): Int {
        var k = 0
        var p = 1.0
        val l = exp(-lambda)
        do {
            k++
            p *= Random.nextDouble()
        } while (p > l)
        return k - 1
    }
}

// 2. Работа с файлами
object SampleFileHandler {

    // Формат файла: каждая строка содержит "значение количество"
    fun saveSample(sample: Sample, filename: String) {
        val content = sample.values.entries.joinToString("\n") { "${it.key} ${it.value}" }
        // В реальном приложении здесь был бы код записи в файл
        println("Сохранение в файл $filename:\n$content")
    }

    fun loadSample(content: String): Sample? {
        try {
            val values = mutableMapOf<Double, Int>()
            content.trim().lines().forEach { line ->
                val parts = line.trim().split("\\s+".toRegex())
                if (parts.size != 2) return null

                val value = parts[0].toDouble()
                val count = parts[1].toInt()

                if (value < 0 || count <= 0) {
                    println("Ошибка: некорректные значения (value=$value, count=$count)")
                    return null
                }

                if (values.containsKey(value)) {
                    println("Ошибка: дублирующееся значение $value")
                    return null
                }

                values[value] = count
            }

            val sample = Sample(values)
            return if (sample.isValid()) sample else null
        } catch (e: Exception) {
            println("Ошибка при загрузке: ${e.message}")
            return null
        }
    }
}


// 3. Статистические оценки
object StatisticalEstimates {

    // Выборочное среднее (несмещённая оценка)
    fun sampleMean(sample: Sample): Double {
        var sum = 0.0
        sample.values.forEach { (value, count) ->
            sum += value * count
        }
        return sum / sample.size
    }

    // Выборочная дисперсия (несмещённая оценка)
    fun sampleVariance(sample: Sample): Double {
        val mean = sampleMean(sample)
        var sumSq = 0.0
        sample.values.forEach { (value, count) ->
            sumSq += (value - mean).pow(2) * count
        }
        return sumSq / sample.size
    }

    // Исправленная дисперсия (смещённая оценка для малых выборок)
    fun correctedVariance(sample: Sample): Double {
        val mean = sampleMean(sample)
        var sumSq = 0.0
        sample.values.forEach { (value, count) ->
            sumSq += (value - mean).pow(2) * count
        }
        return sumSq / (sample.size - 1)
    }

    fun printEstimates(sample: Sample) {
        println("Несмещённые оценки:")
        println("  Выборочное среднее: ${sampleMean(sample)}")
        println("  Выборочная дисперсия: ${sampleVariance(sample)}")
        println("Смещённая оценка:")
        println("  Исправленная дисперсия: ${correctedVariance(sample)}")
    }
}

// 4. Проверка гипотез (критерий хи-квадрат)
object HypothesisTest {

    fun chiSquareTest(
        sample: Sample,
        expectedProbabilities: Map<Double, Double>,
        significanceLevel: Double = 0.05
    ): Boolean {
        var chiSquare = 0.0
        val n = sample.size

        expectedProbabilities.forEach { (value, prob) ->
            val observed = sample.values.getOrDefault(value, 0)
            val expected = n * prob

            if (expected > 5) { // Условие применимости критерия
                chiSquare += (observed - expected).pow(2) / expected
            }
        }

        val degreesOfFreedom = expectedProbabilities.size - 1
        val criticalValue = chiSquareCriticalValue(degreesOfFreedom, significanceLevel)

        println("Статистика хи-квадрат: $chiSquare")
        println("Критическое значение: $criticalValue")
        println("Степени свободы: $degreesOfFreedom")

        val accepted = chiSquare < criticalValue
        println(if (accepted) "Гипотеза ПРИНИМАЕТСЯ" else "Гипотеза ОТВЕРГАЕТСЯ")

        return accepted
    }

    // Упрощённая таблица критических значений для α=0.05
    private fun chiSquareCriticalValue(df: Int, alpha: Double): Double {
        val table = mapOf(
            1 to 3.841, 2 to 5.991, 3 to 7.815, 4 to 9.488,
            5 to 11.070, 10 to 18.307, 15 to 24.996, 20 to 31.410
        )
        return table[df] ?: (df * 2.0) // Приближение для больших df
    }
}

// 5. Оценка параметров распределения
object ParameterEstimation {

    // Метод максимального правдоподобия для нормального распределения
    fun estimateNormalParameters(sample: Sample): Pair<Double, Double> {
        val mean = StatisticalEstimates.sampleMean(sample)
        val variance = StatisticalEstimates.sampleVariance(sample)
        return Pair(mean, sqrt(variance))
    }

    // Оценка параметра λ для распределения Пуассона
    fun estimatePoissonParameter(sample: Sample): Double {
        return StatisticalEstimates.sampleMean(sample)
    }

    // Оценка параметра p для геометрического распределения
    fun estimateGeometricParameter(sample: Sample): Double {
        val mean = StatisticalEstimates.sampleMean(sample)
        return 1.0 / (mean + 1.0)
    }

    fun estimateParameters(sample: Sample, distributionType: String) {
        println("\nОценка параметров для распределения: $distributionType")
        when (distributionType.lowercase()) {
            "normal", "нормальное" -> {
                val (mean, stdDev) = estimateNormalParameters(sample)
                println("  μ (среднее) = $mean")
                println("  σ (стандартное отклонение) = $stdDev")
            }
            "poisson", "пуассоновское" -> {
                val lambda = estimatePoissonParameter(sample)
                println("  λ = $lambda")
            }
            "geometric", "геометрическое" -> {
                val p = estimateGeometricParameter(sample)
                println("  p = $p")
            }
            else -> println("  Оценка параметров для этого распределения не реализована")
        }
    }
}

fun main() {
    println("=== ЗАДАНИЕ 1: Генерация выборок ===\n")

    val normalSample = DistributionGenerators
        .normalDistribution(100, mean = 5.0, stdDev = 2.0)
    println("Нормальное распределение (первые 5 значений):")
    normalSample.values.entries
        .take(5)
        .forEach { println("  ${it.key}: ${it.value} раз") }

    val poissonSample = DistributionGenerators
        .poissonDistribution(100, lambda = 3.0)
    println("\nПуассоновское распределение (первые 5 значений):")
    poissonSample.values.entries
        .take(5)
        .forEach { println("  ${it.key}: ${it.value} раз") }

    println("\n=== ЗАДАНИЕ 2: Работа с файлами ===\n")

    val testContent = "1.0 10\n2.0 20\n3.0 15"
    val loadedSample = SampleFileHandler.loadSample(testContent)
    println("Загружена выборка: ${loadedSample?.values}")

    println("\n=== ЗАДАНИЕ 3: Статистические оценки ===\n")

    loadedSample?.let { StatisticalEstimates.printEstimates(it) }

    println("\n=== ЗАДАНИЕ 4: Проверка гипотез ===\n")

    // Пример для дискретного распределения
    val expectedProbs = mapOf(1.0 to 0.3, 2.0 to 0.5, 3.0 to 0.2)
    loadedSample?.let { HypothesisTest.chiSquareTest(it, expectedProbs) }

    println("\n=== ЗАДАНИЕ 5: Оценка параметров ===")

    poissonSample.let { ParameterEstimation.estimateParameters(it, "poisson") }
    normalSample.let { ParameterEstimation.estimateParameters(it, "normal") }
}