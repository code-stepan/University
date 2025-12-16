using System.Text;

namespace HyperGraphs
{
    public static class Graph
    {
        #region Validation

        /// <summary>
        /// Проверяет корректность вектора графа
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <returns></returns>
        public static bool CheckVectorGraphical(in int[] degreeVector)
        {
            return (CheckVectorGraphical(degreeVector, out var _));
        }

        /// <summary>
        /// Проверяет корректность вектора графа
        /// </summary>
        /// <param name="degreeVector">Вектора графа</param>
        /// <param name="errmes">Передаваемая причина некорректности</param>
        /// <returns></returns>
        public static bool CheckVectorGraphical(in int[] degreeVector, out string errmes)
        {
            if (degreeVector == null)
            {
                errmes = "degreeVector is null";
                return false;
            }

            var tempDegreeVector = degreeVector.ToArray();
            var degreeVectorSum = tempDegreeVector.Sum();
            if (degreeVectorSum % 2 != 0)
            {
                errmes = $"Sum {degreeVectorSum} % 2 != 0";
                return false;
            }

            for (var i = 0; i < tempDegreeVector.Length; i++)
            {
                if (tempDegreeVector[i] >= tempDegreeVector.Length)
                {
                    errmes = $"degreeVector[{i}] >= {tempDegreeVector.Length}";
                    return false;
                }
            }

            for (var i = 0; i < tempDegreeVector.Length; i++)
            {
                while (tempDegreeVector[i] > 0)
                {
                    for (var j = i + 1; j < tempDegreeVector.Length; j++)
                    {
                        if (tempDegreeVector[i] > 0 && tempDegreeVector[j] > 0)
                        {
                            tempDegreeVector[i]--;
                            tempDegreeVector[j]--;
                        }
                    }

                    if (tempDegreeVector[i] > 0)
                    {
                        errmes = $"Not Enough connections: degreeVector[{i}] > 0";
                        return false;
                    }
                }
            }

            errmes = string.Empty;
            return true;
        }

        /// <summary>
        /// Проверяет корректность матрицы смежности
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <returns></returns>
        public static bool CheckAdjacencyGraphical(in int[,] adjacencyMatrix)
        {
            var vertices = adjacencyMatrix.GetLength(0);
            var degreeVector = new int[vertices];

            for (int i = 0; i < vertices; i++)
            {
                var degree = 0;
                for (int j = 0; j < vertices; j++)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        degree++;
                    }
                    else if (adjacencyMatrix[i, j] > 1)
                    {
                        return false;
                    }

                    degreeVector[i] = degree;
                }
            }

            return CheckVectorGraphical(degreeVector);
        }

        /// <summary>
        /// Проверяеть корректность матрицы смежности
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="errmes">Передаваемая причина некорректности</param>
        /// <returns></returns>
        public static bool CheckAdjacencyGraphical(in int[,] adjacencyMatrix, out string errmes)
        {
            var vertices = adjacencyMatrix.GetLength(0);
            var degreeVector = new int[vertices];

            for (int i = 0; i < vertices; i++)
            {
                var degree = 0;
                for (int j = 0; j < vertices; j++)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        degree++;
                    }
                    else if (adjacencyMatrix[i, j] > 1)
                    {
                        errmes = $"adjacencyMatrix[{i}, {j}] > 1";
                        return false;
                    }

                    degreeVector[i] = degree;
                }
            }

            return CheckVectorGraphical(degreeVector, out errmes);
        }

        /// <summary>
        /// Проверяет корректность матрицы инцедентности
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <returns></returns>
        public static bool CheckIncidenceGraphical(in int[,] incidenceMatrix)
        {
            return TryIncidenceToVector(incidenceMatrix, out var _);
        }

        /// <summary>
        /// Проверяет корректность матрицы инцедентности
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <param name="errmes">Передаваемая причина некорректности</param>
        /// <returns></returns>
        public static bool CheckIncidenceGraphical(in int[,] incidenceMatrix, out string errmes)
        {
            return TryIncidenceToVector(incidenceMatrix, out var _, out errmes);
        }
        
        #endregion

        #region Safe

        /// <summary>
        /// Пытается конвертировать вектор графа в матрицу смежности с возвратом успеха результата
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <param name="adjacencyMatrix">Передаваемая матрица смежности</param>
        /// <returns></returns>
        public static bool TryVectorToAdjacency(in int[] degreeVector, out int[,] adjacencyMatrix)
        {
            return TryVectorToAdjacency(degreeVector, out adjacencyMatrix, out var _);
        }

        /// <summary>
        /// Пытается конвертировать вектор графа в матрицу смежности с возвратом успеха результата
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <param name="adjacencyMatrix">Передаваемая матрица смежности</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryVectorToAdjacency(in int[] degreeVector, out int[,] adjacencyMatrix, out string errmes)
        {
            if (degreeVector == null)
            {
                adjacencyMatrix = new int[0, 0];
                errmes = $"{nameof(degreeVector)} is null";
                return false;
            }

            var tempDegreeVector = degreeVector.ToArray();

            if (tempDegreeVector.Sum() % 2 != 0)
            {
                adjacencyMatrix = new int[0, 0];
                errmes = $"Sum {tempDegreeVector.Sum()} % 2 != 0";
                return false;
            }

            var vertices = tempDegreeVector.Length;
            adjacencyMatrix = new int[vertices, vertices];

            for (var i = 0; i < vertices; i++)
            {
                while (tempDegreeVector[i] > 0)
                {
                    if (tempDegreeVector[i] >= vertices)
                    {
                        adjacencyMatrix = new int[0, 0];
                        errmes = $"degreeVector[{i}] >= {tempDegreeVector.Length}";
                        return false;
                    }

                    for (var j = i + 1; j < vertices; j++)
                    {
                        if (tempDegreeVector[i] > 0 && tempDegreeVector[j] > 0)
                        {
                            adjacencyMatrix[i, j] = 1;
                            adjacencyMatrix[j, i] = 1;
                            tempDegreeVector[i]--;
                            tempDegreeVector[j]--;
                        }
                    }

                    if (tempDegreeVector[i] > 0)
                    {
                        adjacencyMatrix = new int[0, 0];
                        errmes = $"Not Enough connections: degreeVector[{i}] > 0";
                        return false;
                    }
                }
            }

            errmes = string.Empty;
            return true;
        }

        /// <summary>
        /// Пытается конвертировать матрицу смежности в вектор графа с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="degreeVector">Передаваемый вектор графа</param>
        /// <returns></returns>
        public static bool TryAdjacencyToVector(in int[,] adjacencyMatrix, out int[] degreeVector)
        {
            return TryAdjacencyToVector(adjacencyMatrix, out degreeVector);
        }

        /// <summary>
        /// Пытается конвертировать матрицу смежности в вектора графа с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="degreeVector">Передаваемый вектор графа</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryAdjacencyToVector(in int[,] adjacencyMatrix, out int[] degreeVector, out string errmes)
        {
            if (adjacencyMatrix == null)
            {
                degreeVector = new int[0];
                errmes = $"{nameof(adjacencyMatrix)} is null";
                return false;
            }

            var vertices = adjacencyMatrix.GetLength(0);
            degreeVector = new int[vertices];

            for (int i = 0; i < vertices; i++)
            {
                var degree = 0;
                for (int j = 0; j < vertices; j++)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        degree++;
                    }
                    else if (adjacencyMatrix[i, j] > 1)
                    {
                        degreeVector = new int[0];
                        errmes = $"adjacencyMatrix[{i}, {j}] > 1";
                        return false;
                    }

                    degreeVector[i] = degree;
                }
            }

            if (degreeVector.Sum() % 2 != 0)
            {
                degreeVector = new int[0];
                errmes = $"Sum {degreeVector.Sum()} % 2 != 0";
                return false;
            }

            errmes = string.Empty;
            return true;
        }

        /// <summary>
        /// Пытается конвертировать матрицу смежности в матрицу инцедентности с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="incidenceMatrix">Передаваемая матрица инцедентности</param>
        /// <returns></returns>
        public static bool TryAdjacencyToIncidence(in int[,] adjacencyMatrix, out int[,] incidenceMatrix)
        {
            return TryAdjacencyToIncidence(adjacencyMatrix, out incidenceMatrix, out var _);
        }

        /// <summary>
        /// Пытается конвертировать матрицу смежности в матрицу инцедентности с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="incidenceMatrix">Передаваемая матрица инцедентности</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryAdjacencyToIncidence(in int[,] adjacencyMatrix, out int[,] incidenceMatrix, out string errmes)
        {
            if (adjacencyMatrix == null)
            {
                incidenceMatrix = new int[0, 0];
                errmes = $"{nameof(adjacencyMatrix)} is null";
                return false;
            }

            var vertices = adjacencyMatrix.GetLength(0);
            if (TryAdjacencyToVector(adjacencyMatrix, out var degreeVector, out errmes))
            {
                var edges = degreeVector.Sum() / 2;

                incidenceMatrix = new int[vertices, edges];
                var k = 0;

                for (int i = 0; i < vertices; i++)
                {
                    for (int j = i; j < vertices; j++)
                    {
                        if (adjacencyMatrix[i, j] == 1)
                        {
                            incidenceMatrix[i, k] = 1;
                            incidenceMatrix[j, k] = 1;
                            k++;
                        }
                    }
                }

                return true;
            }

            incidenceMatrix = new int[0, 0];
            return false;
        }

        /// <summary>
        /// Пытается конвертировать вектор графа в матрицу инцедентности с возвратом успеха результата
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <param name="incidenceMatrix">Передаваемая матрица инцедентности</param>
        /// <returns></returns>
        public static bool TryVectorToIncidence(in int[] degreeVector, out int[,] incidenceMatrix)
        {
            return TryVectorToIncidence(degreeVector, out incidenceMatrix, out var _);
        }

        /// <summary>
        /// Пытается конвертировать вектора графа в матрицу инцедентности с возвратом успеха результата
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <param name="incidenceMatrix">Передаваемая матрица инцедентности</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryVectorToIncidence(in int[] degreeVector, out int[,] incidenceMatrix, out string errmes)
        {
            if (degreeVector == null)
            {
                incidenceMatrix = new int[0, 0];
                errmes = $"{nameof(degreeVector)} is null";
                return false;
            }

            if (TryVectorToAdjacency(degreeVector, out var adjacencyMatrix, out errmes))
            {
                var vertices = adjacencyMatrix.GetLength(0);
                var edges = degreeVector.Sum() / 2;

                incidenceMatrix = new int[vertices, edges];
                var k = 0;

                for (int i = 0; i < vertices; i++)
                {
                    for (int j = i; j < vertices; j++)
                    {
                        if (adjacencyMatrix[i, j] == 1)
                        {
                            incidenceMatrix[i, k] = 1;
                            incidenceMatrix[j, k] = 1;
                            k++;
                        }
                    }
                }

                return true;
            }

            incidenceMatrix = new int[0, 0];
            return false;
        }

        /// <summary>
        /// Пытается конвертировать матрицу инцедентности в вектор графа с возвратом успеха результата
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <param name="degreeVector">Передаваемый вектор графа</param>
        /// <returns></returns>
        public static bool TryIncidenceToVector(in int[,] incidenceMatrix, out int[] degreeVector)
        {
            return TryIncidenceToVector(incidenceMatrix, out degreeVector, out var _);
        }

        /// <summary>
        /// Пытается конвертировать матрицу инцедентности в вектор графа с возвратом успеха результата
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <param name="degreeVector">Передаваемый вектор графа</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryIncidenceToVector(in int[,] incidenceMatrix, out int[] degreeVector, out string errmes)
        {
            if (incidenceMatrix == null)
            {
                degreeVector = new int[0];
                errmes = $"{nameof(incidenceMatrix)} is null";
                return false;
            }

            int vertices = incidenceMatrix.GetLength(0);
            int edges = incidenceMatrix.GetLength(1);

            degreeVector = new int[vertices];

            for (int i = 0; i < vertices; i++)
            {
                for (int j = 0; j < edges; j++)
                {
                    if (incidenceMatrix[i, j] == 1)
                    {
                        degreeVector[i]++;
                    }
                }
            }

            if (!CheckVectorGraphical(degreeVector, out errmes))
            {
                degreeVector = new int[0];
                return false;
            }

            return true;
        }

        /// <summary>
        /// Пытается конвертировать матрицу инцедентности в матрицу смежности с возвратом успеха результата
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <param name="adjacencyMatrix">Передаваемая матрица смежности</param>
        /// <returns></returns>
        public static bool TryIncidenceToAdjacency(in int[,] incidenceMatrix, out int[,] adjacencyMatrix)
        {
            return TryIncidenceToAdjacency(incidenceMatrix, out adjacencyMatrix, out var _);
        }

        /// <summary>
        /// Пытается конвертировать матрицу инцедентности в матрицу смежности с возвратом успеха результата
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <param name="adjacencyMatrix">Передаваемая матрица смежности</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryIncidenceToAdjacency(in int[,] incidenceMatrix, out int[,] adjacencyMatrix, out string errmes)
        {
            if (incidenceMatrix == null)
            {
                adjacencyMatrix = new int[0, 0];
                errmes = $"{nameof(incidenceMatrix)} is null";
                return false;
            }

            if (!TryIncidenceToVector(incidenceMatrix, out var degreeVector, out errmes))
            {
                adjacencyMatrix = new int[0, 0];
                return false;
            }

            if (!TryVectorToAdjacency(degreeVector, out adjacencyMatrix, out errmes))
            {
                return false;
            }

            return true;
        }

        /// <summary>
        /// Пытается получить ребра из матрицыф смежности с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="ribs">Передаваемый список ребер</param>
        /// <param name="inverse">Обратное представление ребер (default = false)</param>
        /// <returns></returns>
        public static bool TryGetRibs(in int[,] adjacencyMatrix, out List<(int, int)> ribs, bool inverse = false)
        {
            return TryGetRibs(adjacencyMatrix, out ribs, out var _, inverse: inverse);
        }

        /// <summary>
        /// Пытается получить ребра из матрицы смежности с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="ribs">Передаваемый список ребер</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <param name="inverse">Обратное представление ребер (default = false)</param>
        /// <returns></returns>
        public static bool TryGetRibs(in int[,] adjacencyMatrix, out List<(int, int)> ribs, out string errmes, bool inverse = false)
        {
            if (adjacencyMatrix == null)
            {
                ribs = new();
                errmes = $"{nameof(adjacencyMatrix)} is null!";
                return false;
            }

            ribs = new List<(int, int)>();
            if (!CheckAdjacencyGraphical(adjacencyMatrix, out errmes))
            {
                return false;
            }

            var verticles = adjacencyMatrix.GetLength(0);

            for (var i = 0; i < verticles / 2; i++)
            {
                for (var j = verticles - 1; j > i; j--)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        ribs.Add(inverse ? (j, i) : (i, j));
                    }
                }
            }

            return true;
        }

        /// <summary>
        /// Пытается получить базы из матрицы смежности с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="bases">Передаваемый список баз</param>
        /// <param name="extreme">Для экстримального графа (default = true)</param>
        /// <param name="inverse">Обратное представление ребер (default = false)</param>
        /// <returns></returns>
        public static bool TryGetBases(in int[,] adjacencyMatrix, out List<(int, int)> bases, bool extreme = true, bool inverse = false)
        {
            return TryGetBases(adjacencyMatrix, out bases, out var _, extreme: extreme, inverse: inverse);
        }

        /// <summary>
        /// Пытается получить базы из матрицы смежности с возвратом успеха результата
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="bases">Передаваемый список баз</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <param name="extreme">Для экстримального графа (default = true)</param>
        /// <param name="inverse">Обратное представление ребер (default = false)</param>
        /// <returns></returns>
        public static bool TryGetBases(in int[,] adjacencyMatrix, out List<(int, int)> bases, out string errmes, bool extreme = true, bool inverse = false)
        {
            if (adjacencyMatrix == null)
            {
                bases = new();
                errmes = $"{nameof(adjacencyMatrix)} is null!";
                return false;
            }

            bases = new List<(int, int)>();
            if (!CheckAdjacencyGraphical(adjacencyMatrix, out errmes))
            {
                return false;
            }

            var verticles = adjacencyMatrix.GetLength(0);

            var i = 0;
            var j = verticles - 1;

            var prev_i = 0;
            var prev_j = 0;

            while (i < verticles / 2)
            {
                var prev = 0;
                for (var temp = j; temp > i; temp--)
                {
                    if (adjacencyMatrix[i, temp] == 1 && prev == 0)
                    {
                        if (extreme)
                        {
                            errmes = "Cant find bases for not extreme adjacency matrix.";
                            bases.Clear();
                            return false;
                        }

                        j = temp;
                    }
                    else if (adjacencyMatrix[i, temp] == 0)
                    {
                        j = -1;
                    }

                    prev = adjacencyMatrix[i, temp];
                }

                if (prev_j != j && prev_i != prev_j)
                {
                    bases.Add(inverse ? (prev_j, prev_i) : (prev_i, prev_j));
                }

                prev_i = i;
                prev_j = j;
                i++;
            }

            return true;
        }

        /// <summary>
        /// Пытается получить сигнатуру из матрицы смежности с возвратом успеха конвертации
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="signature">Передаваемая сигнатура</param>
        /// <returns></returns>
        public static bool TryGetSignature(int[,] adjacencyMatrix, out long signature)
        {
            return TryGetSignature(adjacencyMatrix, out signature, out _);
        }

        /// <summary>
        /// Пытается получить сигнатуру из матрицы смежности с возвратом успеха конвертации
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="signature">Передаваемая сигнатура</param>
        /// <param name="errmes">Передаваемое сообщеие об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryGetSignature(int[,] adjacencyMatrix, out long signature, out string errmes)
        {
            if (adjacencyMatrix == null)
            {
                signature = -1;
                errmes = $"{nameof(adjacencyMatrix)} is null!";
                return false;
            }

            int rowCount = adjacencyMatrix.GetLength(0);
            int colCount = adjacencyMatrix.GetLength(1);
            int i = 0, j = colCount - 1;
            signature = 0;

            while (i < j)
            {
                bool zeroFound = false;
                for (int k = 0; k < colCount; k++)
                {
                    if (adjacencyMatrix[i, k] == 0 && i != k)
                    {
                        zeroFound = true;
                    }
                    else if (zeroFound && adjacencyMatrix[i, k] == 1)
                    {
                        errmes = $"{nameof(adjacencyMatrix)} is not extreme!";
                        return false;
                    }
                }

                if (adjacencyMatrix[i, j] == 1)
                {
                    signature = (signature << 1) | 1;
                    i++;
                }
                else
                {
                    signature = (signature << 1);
                    j--;
                }
            }

            errmes = "";
            return true;
        }

        /// <summary>
        /// Пытается получить матрицу смежности из сигнатуры с возвратом успеха конвертации
        /// </summary>
        /// <param name="signature">Сигнатура</param>
        /// <param name="adjacencyMatrix">Передавемая матрица смежности</param>
        /// <returns></returns>
        public static bool TrySignatureToAdjacencyMatrix(long signature, out int[,] adjacencyMatrix)
        {
            return TrySignatureToAdjacencyMatrix(signature, out adjacencyMatrix, out _);
        }

        /// <summary>
        /// Пытается получить матрицу смежности из сигнатуры с возвратом успеха конвертации
        /// </summary>
        /// <param name="signature">Cигнатура</param>
        /// <param name="adjacencyMatrix">Передавемая матрица смежности</param>
        /// <param name="errmes">Передаваемое сообщение об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TrySignatureToAdjacencyMatrix(long signature, out int[,] adjacencyMatrix, out string errmes)
        {
            int bits = (int)Math.Ceiling(Math.Log(signature + 1, 2));
            int n = bits + 1;
            adjacencyMatrix = new int[n, n];

            string binaryString = Convert.ToString(signature, 2).PadLeft(bits, '0');

            int i = 0, j = n - 1;
            int index = 0;

            while (index < binaryString.Length && binaryString[index] == '0')
            {
                index++;
            }

            while (i < j && index < binaryString.Length)
            {
                if (binaryString[index] == '1')
                {
                    for (int k = i; k <= j; k++)
                    {
                        adjacencyMatrix[i, k] = 1;
                        adjacencyMatrix[k, i] = 1;
                    }
                    i++;
                }
                else
                {
                    j--;
                }
                index++;
            }

            for (int k = 0; k < n; k++)
            {
                adjacencyMatrix[k, k] = 0;
            }

            errmes = "";
            return true;
        }

        /// <summary>
        /// Пытается получить сигнатуры из списка баз с возвратом успеха конвертации
        /// </summary>
        /// <param name="baseList">Список баз</param>
        /// <param name="signature">Передаваемый вектор сигнатуры</param>
        /// <returns></returns>
        public static bool TryBaseToSignature(List<(int, int)> baseList, out long signature)
        {
            return TryBaseToSignature(baseList, out signature, out _);
        }

        /// <summary>
        /// Пытается получить сигнатуры из списка баз с возвратом успеха конвертации
        /// </summary>
        /// <param name="bases">Список баз</param>
        /// <param name="signature">Передаваемый вектор сигнатуры</param>
        /// <param name="errmes">Передаваемое сообщение об ошибке конвертации</param>
        /// <returns></returns>
        public static bool TryBaseToSignature(List<(int, int)> bases, out long signature, out string errmes)
        {
            if (bases == null)
            {
                signature = -1;
                errmes = $"{nameof(bases)} is null!";
                return false;
            }

            int n = 0;
            foreach (var (i, j) in bases)
            {
                n = Math.Max(n, Math.Max(i, j));
            }
            n += 1; // так как индексы нулевые

            // Построение матрицы смежности
            int[,] matrix = new int[n, n];
            foreach (var (i, j) in bases)
            {
                matrix[i, j] = 1;
                matrix[j, i] = 1; // Отражаем по диагонали
            }

            // Установка диагональных нулей
            for (int k = 0; k < n; k++)
            {
                matrix[k, k] = 0;
            }

            signature = 0;
            int row = 0, col = n - 1;
            while (row < col)
            {
                if (matrix[row, col] == 1)
                {
                    signature = (signature << 1) | 1;
                    row++;
                }
                else
                {
                    signature = (signature << 1);
                    col--;
                }
            }

            errmes = "";
            return true;
        }

        #endregion

        #region Standart

        /// <summary>
        /// Конвертирует вектор графа в матрицу смежности
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <returns>Матрица смежности</returns>
        /// <exception cref="ArgumentNullException"></exception>
        /// <exception cref="ArgumentException"></exception>
        public static int[,] VectorToAdjacency(in int[] degreeVector)
        {
            if (degreeVector == null)
            {
                throw new ArgumentNullException(nameof(degreeVector));
            }

            var tempDegreeVector = degreeVector.ToArray();

            if (tempDegreeVector.Sum() % 2 != 0)
            {
                throw new ArgumentException($"[Connections Sum: {tempDegreeVector.Sum()} % 2 != 0] Degree sequence is not graphical. Cannot reconstruct the adjacency graph.");
            }

            var vertices = tempDegreeVector.Length;
            var adjacencyMatrix = new int[vertices, vertices];

            for (var i = 0; i < vertices; i++)
            {
                while (tempDegreeVector[i] > 0)
                {
                    if (tempDegreeVector[i] >= vertices)
                    {
                        throw new ArgumentException($"[Connections in {i} > vector length] Degree sequence is not graphical. Cannot reconstruct the adjacency graph.");
                    }

                    for (var j = i + 1; j < vertices; j++)
                    {
                        if (tempDegreeVector[i] > 0 && tempDegreeVector[j] > 0)
                        {
                            adjacencyMatrix[i, j] = 1;
                            adjacencyMatrix[j, i] = 1;
                            tempDegreeVector[i]--;
                            tempDegreeVector[j]--;
                        }
                    }

                    if (tempDegreeVector[i] > 0)
                    {
                        throw new ArgumentException($"[Not enough other connections after {i}] Degree sequence is not graphical. Cannot reconstruct the adjacency graph.");
                    }
                }
            }

            return adjacencyMatrix;
        }

        /// <summary>
        /// Конветирует матрицу смежности в вектор графа
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <returns>Вектор графа</returns>
        /// <exception cref="ArgumentNullException"></exception>
        /// <exception cref="ArgumentException"></exception>
        public static int[] AdjacencyToVector(in int[,] adjacencyMatrix)
        {
            if (adjacencyMatrix == null)
            {
                throw new ArgumentNullException(nameof(adjacencyMatrix));
            }

            var vertices = adjacencyMatrix.GetLength(0);
            var degreeVector = new int[vertices];
            
            for (int i = 0; i < vertices; i++)
            {
                var degree = 0;
                for (int j = 0; j < vertices; j++)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        degree++;
                    }
                    else if (adjacencyMatrix[i, j] > 1)
                    {
                        throw new ArgumentException($"[Error: {i}, {j}] Adjacency matrix contains invalid value. Must be 0 or 1.");
                    }

                    degreeVector[i] = degree;
                }
            }

            if (degreeVector.Sum() % 2 != 0)
            {
                throw new ArgumentException($"[Connections Sum: {degreeVector.Sum()} % 2 != 0] Degree sequence is not graphical. Cannot construct vector graph.");
            }

            return degreeVector;
        }

        /// <summary>
        /// Конвертирует матрицу смежности в матрицу инцедентности
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <returns>Матрица инцедентности</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static int[,] AdjacencyToIncidence(in int[,] adjacencyMatrix)
        {
            if (adjacencyMatrix == null)
            {
                throw new ArgumentNullException(nameof(adjacencyMatrix));
            }

            var vertices = adjacencyMatrix.GetLength(0);
            var edges = AdjacencyToVector(adjacencyMatrix).Sum() / 2;

            var incidenceMatrix = new int[vertices, edges];
            var k = 0;

            for (int i = 0; i < vertices; i++)
            {
                for (int j = i; j < vertices; j++)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        incidenceMatrix[i, k] = 1;
                        incidenceMatrix[j, k] = 1;
                        k++;
                    }
                }
            }

            return incidenceMatrix;
        }

        /// <summary>
        /// Конвертирует вектор графа в матрицу инцедентности
        /// </summary>
        /// <param name="degreeVector">Вектор графа</param>
        /// <returns>Матрица инцедентности</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static int[,] VectorToIncidence(in int[] degreeVector)
        {
            if (degreeVector == null)
            {
                throw new ArgumentNullException(nameof(degreeVector));
            }

            var tempDegreeVector = degreeVector.ToArray();
            var adjacencyMatrix = VectorToAdjacency(tempDegreeVector);

            var vertices = adjacencyMatrix.GetLength(0);
            var edges = tempDegreeVector.Sum() / 2;

            var incidenceMatrix = new int[vertices, edges];
            var k = 0;

            for (int i = 0; i < vertices; i++)
            {
                for (int j = i; j < vertices; j++)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        incidenceMatrix[i, k] = 1;
                        incidenceMatrix[j, k] = 1;
                        k++;
                    }
                }
            }

            return incidenceMatrix;
        }

        /// <summary>
        /// Конвертирует матрицу инцедентности в матрицу смежности
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <returns>Матрица смежности</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static int[,] IncidenceToAdjacency(in int[,] incidenceMatrix)
        {
            if (incidenceMatrix == null)
            {
                throw new ArgumentNullException(nameof(incidenceMatrix));
            }

            var degreeVector = IncidenceToVector(incidenceMatrix);
            var adjacencyMatrix = VectorToAdjacency(degreeVector);

            return adjacencyMatrix;
        }

        /// <summary>
        /// Конвертирует матрицу инцедентности в вектор графа
        /// </summary>
        /// <param name="incidenceMatrix">Матрица инцедентности</param>
        /// <returns>Вектор графа</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static int[] IncidenceToVector(in int[,] incidenceMatrix)
        {
            if (incidenceMatrix == null)
            {
                throw new ArgumentNullException(nameof(incidenceMatrix));
            }

            int vertices = incidenceMatrix.GetLength(0);
            int edges = incidenceMatrix.GetLength(1);

            int[] degreeVector = new int[vertices];

            for (int i = 0; i < vertices; i++)
            {
                for (int j = 0; j < edges; j++)
                {
                    if (incidenceMatrix[i, j] == 1)
                    {
                        degreeVector[i]++;
                    }
                }
            }

            return degreeVector;
        }

        /// <summary>
        /// Получает список ребер из матрицы смежности
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="inverse">Обратное представление ребер (default = false)</param>
        /// <returns>Список ребер</returns>
        public static List<(int, int)> GetRibs(in int[,] adjacencyMatrix, bool inverse = false)
        {
            var ribs = new List<(int, int)>();
            if (!CheckAdjacencyGraphical(adjacencyMatrix))
            {
                return ribs;
            }

            var verticles = adjacencyMatrix.GetLength(0);

            for (var i = 0; i < verticles / 2; i++)
            {
                for (var j = verticles - 1; j > i; j--)
                {
                    if (adjacencyMatrix[i, j] == 1)
                    {
                        ribs.Add(inverse ? (j, i) : (i, j));
                    }
                }
            }

            return ribs;
        }

        /// <summary>
        /// Получает список баз из матрицы смежности
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <param name="extreme">Для экстримального графа (default = true)</param>
        /// <param name="inverse">Обратное представление ребер (default = false)</param>
        /// <returns>Список баз</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static List<(int, int)> GetBases(in int[,] adjacencyMatrix, bool extreme = true, bool inverse = false)
        {
            if (adjacencyMatrix == null)
            {
                throw new ArgumentNullException(nameof(adjacencyMatrix));
            }

            var bases = new List<(int, int)>();
            if (!CheckAdjacencyGraphical(adjacencyMatrix))
            {
                return bases;
            }

            var verticles = adjacencyMatrix.GetLength(0);

            var i = 0;
            var j = verticles - 1;

            var prev_i = 0;
            var prev_j = 0;

            while (i < verticles / 2)
            {
                var prev = 0;
                for (var temp = j; temp > i; temp--)
                {
                    if (adjacencyMatrix[i, temp] == 1 && prev == 0)
                    {
                        j = temp;
                        if (extreme)
                        {
                            throw new ArgumentNullException("Cant find bases for not extreme adjacency matrix.");
                        }
                    }
                    else if (adjacencyMatrix[i, temp] == 0)
                    {
                        j = -1;
                    }

                    prev = adjacencyMatrix[i, temp];
                }

                if (prev_j != j && prev_i != prev_j)
                {
                    bases.Add(inverse ? (prev_j, prev_i) : (prev_i, prev_j));
                }

                prev_i = i;
                prev_j = j;
                i++;
            }

            return bases;
        }

        /// <summary>
        /// Получает вектор сигнатуры из матрицы смежности
        /// </summary>
        /// <param name="adjacencyMatrix">Матрица смежности</param>
        /// <returns>Вектор сигнатуры</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static long GetSignature(int[,] adjacencyMatrix)
        {
            int rowCount = adjacencyMatrix.GetLength(0);
            int colCount = adjacencyMatrix.GetLength(1);
            int i = 0, j = colCount - 1;
            long signature = 0;

            while (i < j)
            {
                bool zeroFound = false;
                for (int k = 0; k < colCount; k++)
                {
                    if (adjacencyMatrix[i, k] == 0 && i != k)
                    {
                        zeroFound = true;
                    }
                    else if (zeroFound && adjacencyMatrix[i, k] == 1)
                    {
                        return -1;
                    }
                }

                if (adjacencyMatrix[i, j] == 1)
                {
                    signature = (signature << 1) | 1;
                    i++;
                }
                else
                {
                    signature = (signature << 1);
                    j--;
                }
            }
            return signature;
        }

        /// <summary>
        /// Конвертирует вектор сигнатуры в матрицу смежности
        /// </summary>
        /// <param name="signature">Вектор сигнатуры</param>
        /// <returns>Матрица смежности</returns>
        /// <exception cref="ArgumentNullException"></exception>
        /// <exception cref="ArgumentException"></exception>
        public static int[,] SignatureToAdjacency(long signature)
        {
            // Определение размера матрицы на основе длины сигнатуры
            int bits = (int)Math.Ceiling(Math.Log(signature + 1, 2));
            int n = bits + 1;
            int[,] matrix = new int[n, n];

            string binaryString = Convert.ToString(signature, 2).PadLeft(bits, '0');

            int i = 0, j = n - 1; // Начинаем с правого верхнего угла
            int index = 0;

            // Находим первую левую единицу в сигнатуре
            while (index < binaryString.Length && binaryString[index] == '0')
            {
                index++;
            }

            while (i < j && index < binaryString.Length)
            {
                if (binaryString[index] == '1')
                {
                    // Устанавливаем единицы до текущей позиции
                    for (int k = i; k <= j; k++)
                    {
                        matrix[i, k] = 1;
                        matrix[k, i] = 1; // Отражаем по диагонали
                    }
                    i++;
                }
                else
                {
                    j--;
                }
                index++;
            }

            // Устанавливаем диагональные нули
            for (int k = 0; k < n; k++)
            {
                matrix[k, k] = 0;
            }

            return matrix;
        }

        /// <summary>
        /// Конвертирует список баз в сигнатуру
        /// </summary>
        /// <param name="baseList">Список баз</param>
        /// <returns>Вектор сигнатуры</returns>
        /// <exception cref="ArgumentNullException"></exception>
        public static long BasesToSignature(List<(int, int)> bases)
        {
            if (bases == null || bases.Count == 0)
            {
                throw new ArgumentException("Bases cannot be null or empty.");
            }

            // Определение размера матрицы на основе наибольшего индекса в базах
            int n = 0;
            foreach (var (i, j) in bases)
            {
                n = Math.Max(n, Math.Max(i, j));
            }
            n += 1; // так как индексы нулевые

            // Построение матрицы смежности
            int[,] matrix = new int[n, n];
            foreach (var (i, j) in bases)
            {
                matrix[i, j] = 1;
                matrix[j, i] = 1; // Отражаем по диагонали
            }

            // Установка диагональных нулей
            for (int k = 0; k < n; k++)
            {
                matrix[k, k] = 0;
            }

            // Извлечение сигнатуры из матрицы
            long signature = 0;
            int row = 0, col = n - 1;
            while (row < col)
            {
                if (matrix[row, col] == 1)
                {
                    signature = (signature << 1) | 1;
                    row++;
                }
                else
                {
                    signature = (signature << 1);
                    col--;
                }
            }

            return signature;
        }

        #endregion

        #region Utility

        /// <summary>
        /// Формирует строку из матрицы
        /// </summary>
        /// <param name="matrix"></param>
        /// <exception cref="ArgumentNullException"></exception>
        public static string ToString(in int[,] matrix)
        {
            if (matrix == null)
            {
                throw new ArgumentNullException(nameof(matrix));
            }

            var vertices = matrix.GetLength(0);
            var edges = matrix.GetLength(1);

            var result = "";
            var isLine = false;
            for (int i = 0; i < vertices; i++)
            {
                if (isLine) result += "\n";
                var isSpace = false;
                for (int j = 0; j < edges; j++)
                {
                    if (isSpace) result += " ";
                    result += $"{matrix[i, j]}";
                    isSpace = true;
                }

                isLine = true;
            }

            return result;
        }

        /// <summary>
        /// Формирует строку из вектора
        /// </summary>
        /// <param name="matrix"></param>
        /// <exception cref="ArgumentNullException"></exception>
        public static string ToString(in int[] matrix)
        {
            if (matrix == null)
            {
                throw new ArgumentNullException(nameof(matrix));
            }

            var vertices = matrix.GetLength(0);
            var result = "";
            var space = false;
            for (int i = 0; i < vertices; i++)
            {
                if (space) result += " ";
                result += $"{matrix[i]}";
                space = true;
            }

            return result;
        }

        /// <summary>
        /// Формирует строку из списка
        /// </summary>
        /// <typeparam name="T"></typeparam>
        /// <param name="list"></param>
        /// <exception cref="ArgumentNullException"></exception>
        public static string ToString<T>(in List<T> list)
        {
            if (list == null)
            {
                throw new ArgumentNullException(nameof(list));
            }

            var result = "";
            var space = false;
            for (int i = 0; i < list.Count; i++)
            {
                if (space) result += " ";
                result += $"{list[i]}";
                space = true;
            }

            return result;
        }

        #endregion
    }
}