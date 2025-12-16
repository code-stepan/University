import random
import math
import matplotlib.pyplot as plt


class KMeans:
    def __init__(self, points, k=None):
        self.points = points
        self.k = k if k else random.randint(3, 5)
        self.centroids = random.sample(self.points, self.k)
        self.clusters = [[] for _ in range(self.k)]
        self.iterations = 0
        self.history = []

    def _distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def _assign_clusters(self):
        self.clusters = [[] for _ in range(self.k)]
        for point in self.points:
            distances = [self._distance(point, centroid) for centroid in self.centroids]
            min_index = distances.index(min(distances))
            self.clusters[min_index].append(point)

    def _update_centroids(self):
        new_centroids = []
        for cluster in self.clusters:
            if cluster:
                x_mean = sum(p[0] for p in cluster) / len(cluster)
                y_mean = sum(p[1] for p in cluster) / len(cluster)
                new_centroids.append((x_mean, y_mean))
            else:
                new_centroids.append(random.choice(self.points))
        return new_centroids

    def fit(self):
        while True:
            self._assign_clusters()

            if self.iterations == 0:
                self.history.append((self.clusters.copy(), self.centroids.copy()))

            new_centroids = self._update_centroids()
            self.iterations += 1

            if all(self._distance(new_centroids[i], self.centroids[i]) < 1e-4 for i in range(self.k)):
                break

            self.centroids = new_centroids

        self.history.append((self.clusters.copy(), self.centroids.copy()))

    def plot_clusters(self):
        colors = ['red', 'green', 'blue', 'orange', 'purple']
        titles = ['Первая итерация k-means', f'Финальная итерация k-means\nИтераций: {self.iterations}']

        plt.figure(figsize=(12, 5))
        for idx, (clusters, centroids) in enumerate(self.history):
            plt.subplot(1, 2, idx + 1)
            for i, cluster in enumerate(clusters):
                xs = [p[0] for p in cluster]
                ys = [p[1] for p in cluster]
                plt.scatter(xs, ys, c=colors[i % len(colors)], label=f'Кластер {i + 1}')
            for cx, cy in centroids:
                plt.scatter(cx, cy, c='black', marker='x', s=100)
            plt.title(titles[idx])
            plt.legend()
        plt.show()

if __name__ == "__main__":
    data = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(100)]

    model = KMeans(points=data)
    model.fit()
    model.plot_clusters()
















