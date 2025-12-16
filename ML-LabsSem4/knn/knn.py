import random
import matplotlib.pyplot as plt

class KNNClassifier:
    def __init__(self, k=5):
        self.k = k
        self.labeled_points = []

    def fit(self, class1_points, class2_points):
        self.labeled_points = [(p, 'class1') for p in class1_points] + [(p, 'class2') for p in class2_points]

    @staticmethod
    def _squared_euclidean_distance(p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return dx * dx + dy * dy

    def _classify_point(self, point):
        distances = [(self._squared_euclidean_distance(point, p), label) for p, label in self.labeled_points]
        distances.sort(key=lambda x: x[0])

        nearest = distances[:self.k]

        votes = {'class1': 0, 'class2': 0}
        for _, label in nearest:
            votes[label] += 1

        return 'class1' if votes['class1'] >= votes['class2'] else 'class2'

    def predict(self, points):
        return [(pt, self._classify_point(pt)) for pt in points]



if __name__ == '__main__':
    class1 = [(random.gauss(2, 0.5),
               random.gauss(2, 0.5))
              for _ in range(50)]

    class2 = [(random.gauss(7, 0.5),
               random.gauss(7, 0.5))
              for _ in range(50)]

    test_points = [(random.uniform(0, 9),
                    random.uniform(0, 9))
                   for _ in range(10)]

    knn = KNNClassifier(k=5)
    knn.fit(class1, class2)
    classified = knn.predict(test_points)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.scatter(*zip(*class1), color='blue', label='Класс 1')
    plt.scatter(*zip(*class2), color='red', label='Класс 2')
    plt.scatter(*zip(*test_points), color='green', label='Тестовые точки')
    plt.title("Исходные данные и тестовые точки без классификации")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.scatter(*zip(*class1), color='blue', label='Класс 1')
    plt.scatter(*zip(*class2), color='red', label='Класс 2')
    for pt, label in classified:
        color = 'blue' if label == 'class1' else 'red'
        plt.scatter(pt[0], pt[1], color=color, marker='*', s=100)
    plt.title("Результаты KNN классификации (k=5)")
    plt.legend()
    plt.grid(True)

    plt.show()
