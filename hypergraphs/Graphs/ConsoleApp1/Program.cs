using HyperGraphs;

class Program
{
    static void Main(string[] args)
    {
        var errmes = string.Empty;
        var adj = new int[8, 8] {
            { 0, 1, 1, 1, 1, 1, 1, 1 },
            { 1, 0, 1, 1, 1, 1, 1, 0 },
            { 1, 1, 0, 1, 1, 1, 0, 0 },
            { 1, 1, 1, 0, 0, 0, 0, 0 },
            { 1, 1, 1, 0, 0, 0, 0, 0 },
            { 1, 1, 1, 0, 0, 0, 0, 0 },
            { 1, 1, 0, 0, 0, 0, 0, 0 },
            { 1, 0, 0, 0, 0, 0, 0, 0 }};

        if (Graph.CheckAdjacencyGraphical(adj, out errmes))
        {
            Console.WriteLine(Graph.ToString(adj));
            var bases = Graph.GetRibs(in adj);
            foreach (var basa in bases)
            {
                Console.WriteLine($"base: {basa}");
            }

            Console.WriteLine("Error Message: " + (errmes != string.Empty ? errmes : "None"));
        }

        Console.WriteLine();

        var degreeVector = new int[] { 7, 6, 6, 4, 3, 3, 3, 2 };

        if (Graph.TryVectorToAdjacency(degreeVector, out var adjacencyMatrix, out errmes))
        {
            Console.WriteLine(Graph.ToString(adjacencyMatrix));
            Console.WriteLine("Error Message: " + (errmes != string.Empty ? errmes : "None"));
        }

        Console.WriteLine();

        if (Graph.TryVectorToIncidence(degreeVector, out var incidenceMatrix, out errmes))
        {
            Console.WriteLine(Graph.ToString(incidenceMatrix));
            Console.WriteLine("Error Message: " + (errmes != string.Empty ? errmes : "None"));
        }

        Console.WriteLine();

        if (Graph.TryIncidenceToAdjacency(incidenceMatrix, out var aab, out errmes))
        {
            Console.WriteLine(Graph.ToString(aab));
            Console.WriteLine("Error Message: " + (errmes != string.Empty ? errmes : "None"));
        }

        Console.WriteLine();

        if (Graph.TryGetSignature(adjacencyMatrix, out var bba, out errmes))
        {
            Console.WriteLine(bba);
            Console.WriteLine("Error Message: " + (errmes != string.Empty ? errmes : "None"));
        }

        Console.WriteLine();

        if (Graph.TryGetBases(adjacencyMatrix, out var bbc, out errmes, extreme: false))
        {
            Console.WriteLine(Graph.ToString(bbc));
            Console.WriteLine("Error Message: " + (errmes != string.Empty ? errmes : "None"));
        }



        Console.ReadLine();
    }
}