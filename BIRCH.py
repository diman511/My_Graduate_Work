import warnings
import numpy as np
from numbers import Integral, Real
from scipy import sparse
from math import sqrt

def _iterate_sparse_X(X):
    n_samples = X.shape[0]
    X_indices = X.indices
    X_data = X.data
    X_indptr = X.indptr

    for i in range(n_samples):
        row = np.zeros(X.shape[1])
        startptr, endptr = X_indptr[i], X_indptr[i + 1]
        nonzero_indices = X_indices[startptr:endptr]
        row[nonzero_indices] = X_data[startptr:endptr]
        yield row


def _split_node(node, threshold, branching_factor):
    new_subcluster1 = _CFSubcluster()
    new_subcluster2 = _CFSubcluster()
    new_node1 = _CFNode(
        threshold=threshold,
        branching_factor=branching_factor,
        is_leaf=node.is_leaf,
        n_features=node.n_features,
        dtype=node.init_centroids_.dtype,
    )
    new_node2 = _CFNode(
        threshold=threshold,
        branching_factor=branching_factor,
        is_leaf=node.is_leaf,
        n_features=node.n_features,
        dtype=node.init_centroids_.dtype,
    )
    new_subcluster1.child_ = new_node1
    new_subcluster2.child_ = new_node2

    if node.is_leaf:
        if node.prev_leaf_ is not None:
            node.prev_leaf_.next_leaf_ = new_node1
        new_node1.prev_leaf_ = node.prev_leaf_
        new_node1.next_leaf_ = new_node2
        new_node2.prev_leaf_ = new_node1
        new_node2.next_leaf_ = node.next_leaf_
        if node.next_leaf_ is not None:
            node.next_leaf_.prev_leaf_ = new_node2

    dist = euclidean_distances(
        node.centroids_, Y_norm_squared=node.squared_norm_, squared=True
    )
    n_clusters = dist.shape[0]

    farthest_idx = np.unravel_index(dist.argmax(), (n_clusters, n_clusters))
    node1_dist, node2_dist = dist[(farthest_idx,)]

    node1_closer = node1_dist < node2_dist
    node1_closer[farthest_idx[0]] = True

    for idx, subcluster in enumerate(node.subclusters_):
        if node1_closer[idx]:
            new_node1.append_subcluster(subcluster)
            new_subcluster1.update(subcluster)
        else:
            new_node2.append_subcluster(subcluster)
            new_subcluster2.update(subcluster)
    return new_subcluster1, new_subcluster2


class _CFNode:
    def __init__(self, *, threshold, branching_factor, is_leaf, n_features, dtype):
        self.threshold = threshold
        self.branching_factor = branching_factor
        self.is_leaf = is_leaf
        self.n_features = n_features

        self.subclusters_ = []
        self.init_centroids_ = np.zeros((branching_factor + 1, n_features), dtype=dtype)
        self.init_sq_norm_ = np.zeros((branching_factor + 1), dtype)
        self.squared_norm_ = []
        self.prev_leaf_ = None
        self.next_leaf_ = None

    def append_subcluster(self, subcluster):
        n_samples = len(self.subclusters_)
        self.subclusters_.append(subcluster)
        self.init_centroids_[n_samples] = subcluster.centroid_
        self.init_sq_norm_[n_samples] = subcluster.sq_norm_

        self.centroids_ = self.init_centroids_[: n_samples + 1, :]
        self.squared_norm_ = self.init_sq_norm_[: n_samples + 1]

    def update_split_subclusters(self, subcluster, new_subcluster1, new_subcluster2):

        ind = self.subclusters_.index(subcluster)
        self.subclusters_[ind] = new_subcluster1
        self.init_centroids_[ind] = new_subcluster1.centroid_
        self.init_sq_norm_[ind] = new_subcluster1.sq_norm_
        self.append_subcluster(new_subcluster2)

    def insert_cf_subcluster(self, subcluster):
        if not self.subclusters_:
            self.append_subcluster(subcluster)
            return False

        threshold = self.threshold
        branching_factor = self.branching_factor
        dist_matrix = np.dot(self.centroids_, subcluster.centroid_)
        dist_matrix *= -2.0
        dist_matrix += self.squared_norm_
        closest_index = np.argmin(dist_matrix)
        closest_subcluster = self.subclusters_[closest_index]

        if closest_subcluster.child_ is not None:
            split_child = closest_subcluster.child_.insert_cf_subcluster(subcluster)

            if not split_child:
                closest_subcluster.update(subcluster)
                self.init_centroids_[closest_index] = self.subclusters_[
                    closest_index
                ].centroid_
                self.init_sq_norm_[closest_index] = self.subclusters_[
                    closest_index
                ].sq_norm_
                return False
            else:
                new_subcluster1, new_subcluster2 = _split_node(
                    closest_subcluster.child_,
                    threshold,
                    branching_factor,
                )
                self.update_split_subclusters(
                    closest_subcluster, new_subcluster1, new_subcluster2
                )

                if len(self.subclusters_) > self.branching_factor:
                    return True
                return False
        else:
            merged = closest_subcluster.merge_subcluster(subcluster, self.threshold)
            if merged:
                self.init_centroids_[closest_index] = closest_subcluster.centroid_
                self.init_sq_norm_[closest_index] = closest_subcluster.sq_norm_
                return False

            elif len(self.subclusters_) < self.branching_factor:
                self.append_subcluster(subcluster)
                return False
            else:
                self.append_subcluster(subcluster)
                return True


class _CFSubcluster:
    def __init__(self, *, linear_sum=None):
        if linear_sum is None:
            self.n_samples_ = 0
            self.squared_sum_ = 0.0
            self.centroid_ = self.linear_sum_ = 0
        else:
            self.n_samples_ = 1
            self.centroid_ = self.linear_sum_ = linear_sum
            self.squared_sum_ = self.sq_norm_ = np.dot(
                self.linear_sum_, self.linear_sum_
            )
        self.child_ = None

    def update(self, subcluster):
        self.n_samples_ += subcluster.n_samples_
        self.linear_sum_ += subcluster.linear_sum_
        self.squared_sum_ += subcluster.squared_sum_
        self.centroid_ = self.linear_sum_ / self.n_samples_
        self.sq_norm_ = np.dot(self.centroid_, self.centroid_)

    def merge_subcluster(self, nominee_cluster, threshold):
        new_ss = self.squared_sum_ + nominee_cluster.squared_sum_
        new_ls = self.linear_sum_ + nominee_cluster.linear_sum_
        new_n = self.n_samples_ + nominee_cluster.n_samples_
        new_centroid = (1 / new_n) * new_ls
        new_sq_norm = np.dot(new_centroid, new_centroid)
        sq_radius = new_ss / new_n - new_sq_norm

        if sq_radius <= threshold ** 2:
            (
                self.n_samples_,
                self.linear_sum_,
                self.squared_sum_,
                self.centroid_,
                self.sq_norm_,
            ) = (new_n, new_ls, new_ss, new_centroid, new_sq_norm)
            return True
        return False

    @property
    def radius(self):
        sq_radius = self.squared_sum_ / self.n_samples_ - self.sq_norm_
        return sqrt(max(0, sq_radius))


class Birch(ClassNamePrefixFeaturesOutMixin, ClusterMixin, TransformerMixin, BaseEstimator):
    _parameter_constraints: dict = {
        "threshold": [Interval(Real, 0.0, None, closed="neither")],
        "branching_factor": [Interval(Integral, 1, None, closed="neither")],
        "n_clusters": [None, ClusterMixin, Interval(Integral, 1, None, closed="left")],
        "compute_labels": ["boolean"],
        "copy": ["boolean"],
    }

    def __init__(
            self,
            *,
            threshold=0.5,
            branching_factor=50,
            n_clusters=3,
            compute_labels=True,
            copy=True,
    ):
        self.threshold = threshold
        self.branching_factor = branching_factor
        self.n_clusters = n_clusters
        self.compute_labels = compute_labels
        self.copy = copy

    @_fit_context(prefer_skip_nested_validation=True)
    def fit(self, X, y=None):
        return self._fit(X, partial=False)

    def _fit(self, X, partial):
        has_root = getattr(self, "root_", None)
        first_call = not (partial and has_root)

        X = self._validate_data(
            X,
            accept_sparse="csr",
            copy=self.copy,
            reset=first_call,
            dtype=[np.float64, np.float32],
        )
        threshold = self.threshold
        branching_factor = self.branching_factor

        n_samples, n_features = X.shape

        if first_call:
            self.root_ = _CFNode(
                threshold=threshold,
                branching_factor=branching_factor,
                is_leaf=True,
                n_features=n_features,
                dtype=X.dtype,
            )

            self.dummy_leaf_ = _CFNode(
                threshold=threshold,
                branching_factor=branching_factor,
                is_leaf=True,
                n_features=n_features,
                dtype=X.dtype,
            )
            self.dummy_leaf_.next_leaf_ = self.root_
            self.root_.prev_leaf_ = self.dummy_leaf_

        if not sparse.issparse(X):
            iter_func = iter
        else:
            iter_func = _iterate_sparse_X

        for sample in iter_func(X):
            subcluster = _CFSubcluster(linear_sum=sample)
            split = self.root_.insert_cf_subcluster(subcluster)

            if split:
                new_subcluster1, new_subcluster2 = _split_node(
                    self.root_, threshold, branching_factor
                )
                del self.root_
                self.root_ = _CFNode(
                    threshold=threshold,
                    branching_factor=branching_factor,
                    is_leaf=False,
                    n_features=n_features,
                    dtype=X.dtype,
                )
                self.root_.append_subcluster(new_subcluster1)
                self.root_.append_subcluster(new_subcluster2)

        centroids = np.concatenate([leaf.centroids_ for leaf in self._get_leaves()])
        self.subcluster_centers_ = centroids
        self._n_features_out = self.subcluster_centers_.shape[0]

        self._global_clustering(X)
        return self

    def _get_leaves(self):
        leaf_ptr = self.dummy_leaf_.next_leaf_
        leaves = []
        while leaf_ptr is not None:
            leaves.append(leaf_ptr)
            leaf_ptr = leaf_ptr.next_leaf_
        return leaves

    @_fit_context(prefer_skip_nested_validation=True)
    def partial_fit(self, X=None, y=None):
        if X is None:
            self._global_clustering()
            return self
        else:
            return self._fit(X, partial=True)

    def _check_fit(self, X):
        check_is_fitted(self)

        if (
                hasattr(self, "subcluster_centers_")
                and X.shape[1] != self.subcluster_centers_.shape[1]
        ):
            raise ValueError(
            )

    def predict(self, X):
        check_is_fitted(self)
        X = self._validate_data(X, accept_sparse="csr", reset=False)
        return self._predict(X)

    def _predict(self, X):
        kwargs = {"Y_norm_squared": self._subcluster_norms}

        with config_context(assume_finite=True):
            argmin = pairwise_distances_argmin(
                X, self.subcluster_centers_, metric_kwargs=kwargs
            )
        return self.subcluster_labels_[argmin]

    def transform(self, X):
        check_is_fitted(self)
        X = self._validate_data(X, accept_sparse="csr", reset=False)
        with config_context(assume_finite=True):
            return euclidean_distances(X, self.subcluster_centers_)

    def _global_clustering(self, X=None):

        clusterer = self.n_clusters
        centroids = self.subcluster_centers_
        compute_labels = (X is not None) and self.compute_labels

        not_enough_centroids = False
        if isinstance(clusterer, Integral):
            clusterer = AgglomerativeClustering(n_clusters=self.n_clusters)
            if len(centroids) < self.n_clusters:
                not_enough_centroids = True

        self._subcluster_norms = row_norms(self.subcluster_centers_, squared=True)

        if clusterer is None or not_enough_centroids:
            self.subcluster_labels_ = np.arange(len(centroids))
            if not_enough_centroids:
                warnings.warn((len(centroids), self.n_clusters), ConvergenceWarning)
        else:
            self.subcluster_labels_ = clusterer.fit_predict(self.subcluster_centers_)

        if compute_labels:
            self.labels_ = self._predict(X)




