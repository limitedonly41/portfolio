import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, KFold
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error as mse, accuracy_score
from xgboost import XGBClassifier

class Node:
    def __init__(self, predicted_class):
        self.predicted_class = predicted_class
        self.feature_index = 0
        self.threshold = 0
        self.left = None
        self.right = None


class DecisionTreeClassifier:
    def __init__(self, max_depth=None):
        self.max_depth = max_depth

    def fit(self, X, y):
        self.n_classes_ = len(set(y))
        self.n_features_ = X.shape[1]
        self.tree_ = self._grow_tree(X, y)

    def predict(self, X):
        y = np.zeros(X.shape[0])
        y = [self._predict(inputs) for inputs in X]
        p = np.array(y)
        return p

    def _best_split(self, X, y):
        m = y.size
        if m <= 1:
            return None, None
        num_parent = [np.sum(y == c) for c in range(self.n_classes_)]
        best_gini = 1.0 - sum((n / m) ** 2 for n in num_parent)
        best_idx, best_thr = None, None
        for idx in range(self.n_features_):
            thresholds, classes = zip(*sorted(zip(X[:, idx], y)))
            num_left = [0] * self.n_classes_
            num_right = num_parent.copy()
            for i in range(1, m):
                c = classes[i - 1]
                c = int(c)
                num_left[c] += 1
                num_right[c] -= 1
                gini_left = 1.0 - sum(
                    (num_left[x] / i) ** 2 for x in range(self.n_classes_)
                )
                gini_right = 1.0 - sum(
                    (num_right[x] / (m - i)) ** 2 for x in range(self.n_classes_)
                )
                gini = (i * gini_left + (m - i) * gini_right) / m
                if thresholds[i] == thresholds[i - 1]:
                    continue
                if gini < best_gini:
                    best_gini = gini
                    best_idx = idx
                    best_thr = (thresholds[i] + thresholds[i - 1]) / 2
        return best_idx, best_thr

    def _grow_tree(self, X, y, depth=0):
        num_samples_per_class = [np.sum(y == i) for i in range(self.n_classes_)]
        predicted_class = np.argmax(num_samples_per_class)
        node = Node(predicted_class=predicted_class)
        if depth < self.max_depth:
            idx, thr = self._best_split(X, y)
            if idx is not None:
                indices_left = X[:, idx] < thr
                X_left, y_left = X[indices_left], y[indices_left]
                X_right, y_right = X[~indices_left], y[~indices_left]
                node.feature_index = idx
                node.threshold = thr
                node.left = self._grow_tree(X_left, y_left, depth + 1)
                node.right = self._grow_tree(X_right, y_right, depth + 1)
        return node

    def _predict(self, inputs):
        node = self.tree_
        while node.left:
            if inputs[node.feature_index] < node.threshold:
                node = node.left
            else:
                node = node.right
        return node.predicted_class

# наш класс отвечаюющий за градиентный бустинг
class GradientBoosting():

    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3,
                 random_state=17, n_samples=15, min_size=5, base_tree='Bagging'):

        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.initialization = lambda y: np.mean(y) * np.ones([y.shape[0]])
        self.min_size = min_size
        self.loss_by_iter = []
        self.trees_ = []
        self.loss_by_iter_test = []
        self.n_samples = n_samples
        self.base_tree = base_tree

    def fit(self, X, y):
        self.X = X
        self.y = y
        b = self.initialization(y)

        prediction = b.copy()

        for t in range(self.n_estimators):

            if t == 0:
                resid = y
            else:
                # сразу пишем антиградиент
                resid = (y - prediction)

            # выбираем базовый алгоритм
            #if self.base_tree == 'Bagging':
            #    tree = Bagging(max_depth=self.max_depth,
            #                   min_size=self.min_size)
            tree = DecisionTreeClassifier(max_depth=self.max_depth)

            # обучаемся на векторе антиградиента
            tree.fit(X, resid)
            # делаем предикт и добавляем алгоритм к ансамблю

            b = tree.predict(X).reshape([X.shape[0]])
            # b = tree.predict(X)
            self.trees_.append(tree)
            prediction += self.learning_rate * b
            # добавляем только если не первая итерация
            if t > 0:
                self.loss_by_iter.append(mse(y, prediction))

        return self

    def predict(self, X):
        pred = np.ones([X.shape[0]]) * np.mean(self.y)
        for t in range(self.n_estimators):
            pred += self.learning_rate * self.trees_[t].predict(X).reshape([X.shape[0]])
        return [1 if i > 0.5 else 0 for i in pred]

if __name__ == "__main__":
    import sys
    from sklearn.datasets import load_iris

    dataset = load_iris()
    X, y = dataset.data, dataset.target  # pylint: disable=no-member
    clf = DecisionTreeClassifier(max_depth=3)
    train = pd.read_csv("train2.csv", header=None)
    test = pd.read_csv("test2.csv", header=None)

    y = np.asarray(train[14])
    X = np.asarray(train.drop(14, axis=1))


    print(X.shape)
    print(y.shape)

    tmp = [1, 3, 5, 6, 7, 8, 9, 13]

    imp = SimpleImputer(missing_values=' ?', strategy='most_frequent')
    #
    X = imp.fit_transform(X)
    test = imp.transform(test)
    print(test.shape)

    encoder = LabelEncoder()
    for i in tmp:
        X[:, i] = encoder.fit_transform(X[:,[i]])
        test[:, i] = encoder.transform(test[:, [i]])
    print(X.shape)
    print(test.shape)
    std = StandardScaler()
    std.fit(X)
    X = std.transform(X)
    min_max = MinMaxScaler()
    min_max.fit(X)
    X = min_max.transform(X)
    GDB = GradientBoosting(n_estimators=5)
    Xtrain, Xtest, ytrain, ytest = train_test_split(X, y, test_size=0.2, random_state=42)

    # print('training')
    # #обучаем классификатор
    # clf.fit(Xtrain, ytrain)
    # #предсказываем данные с помощью обученного классификатора
    # y_pred = clf.predict(Xtest)
    # #считаем точность предсказнных данных и имеющихся(истинных)
    # print(accuracy_score(ytest, y_pred))

    print('training')
    #обучаем классификатор
    GDB.fit(Xtrain, ytrain)
    #предсказываем данные с помощью обученного классификатора
    y_pred = GDB.predict(Xtest)
    #считаем точность предсказнных данных и имеющихся(истинных)
    print(accuracy_score(ytest, y_pred))
    # clf = DecisionTreeClassifier(max_depth=1)
    # clf.fit(X, y)
    # print(clf.predict([[0, 0, 5, 1.5]]))

    clf_xg = XGBClassifier(n_estimators=50)
    clf_xg.fit(Xtrain, ytrain)
    y_pred_xgb = clf_xg.predict(Xtest)
    print(accuracy_score(ytest, y_pred_xgb))