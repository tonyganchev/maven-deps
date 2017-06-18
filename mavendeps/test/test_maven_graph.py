import unittest

from mavendeps.maven_graph import *

__author__ = 'Tony Ganchev'


class ArtifactDescriptorTestCase(unittest.TestCase):
    def test_str_no_classifier(self):
        a = ArtifactDescriptor('grp', 'art', 'ver', 'pack')
        self.assertEqual('grp:art:pack:ver', str(a))

    def test_str_classifier(self):
        a = ArtifactDescriptor('grp', 'art', 'ver', 'pack', 'cls')
        self.assertEqual('grp:art:pack:cls:ver', str(a))

    def test_eq(self):
        a = ArtifactDescriptor('a', 'b', 'c', 'd', 'e')
        b = ArtifactDescriptor('a', 'b', 'c', 'd', 'e')
        self.assertEqual(a, b)


class FilterArtifactsTestCase(unittest.TestCase):
    def _create_artifact(self, artifact_id, in_reactor=False, packaging='jar'):
        return Artifact(ArtifactDescriptor('grp', artifact_id, '1.0.0', packaging), in_reactor)

    def _create_graph(self, artifact_ids, dependencies):
        artifacts = []
        artifacts_by_id = {}
        for artifact_id in artifact_ids:
            artifact = self._create_artifact(artifact_id)
            artifacts.append(artifact)
            artifacts_by_id[artifact_id] = artifact

        forward_dependencies = []
        inverse_dependencies = []
        for from_id, to_id in dependencies:
            dependency = ArtifactDependency(artifacts_by_id[to_id])
            from_art = artifacts_by_id[from_id]
            from_art.add_dependency(dependency)
            forward_dependencies.append(dependency)
            inverse_dependencies.append(ArtifactDependency(from_art))

        return artifacts, forward_dependencies, inverse_dependencies

    def _assert_graphs_equal(self, expected, actual):
        expected = tuple(expected)
        actual = tuple(actual)
        self.assertEqual(expected, actual)
        for i in xrange(0, len(expected)):
            self.assertSequenceEqual(tuple(expected[i].dependencies), tuple(actual[i].dependencies))
            self.assertSequenceEqual(tuple(expected[i].all_dependencies), tuple(actual[i].all_dependencies))
            self.assertSequenceEqual(tuple(expected[i].dependents), tuple(actual[i].dependents))
            self.assertSequenceEqual(tuple(expected[i].all_dependents), tuple(actual[i].all_dependents))

    def test_empty_list_no_filters(self):
        artifacts = filter_artifacts((), ())
        self.assertSequenceEqual(artifacts, ())

    def test_some_list_no_filters(self):
        art = self._create_artifact('foo')
        artifacts = filter_artifacts((art,), ())

        self.assertEqual((art,), artifacts)

    def test_some_list_accept(self):
        art = self._create_artifact('foo')
        artifacts = filter_artifacts((art,), (accept_any,))

        self.assertEqual((art,), artifacts)

    def test_some_list_ignore(self):
        art = self._create_artifact('foo')
        artifacts = filter_artifacts((art,), (ignore_any,))

        self.assertEqual((art,), artifacts)

    def test_some_list_reject(self):
        art = self._create_artifact('foo')
        artifacts = filter_artifacts((art,), (reject_any,))

        self.assertEqual((), artifacts)

    def test_simple_dep(self):
        (prod, cons), (dep,), _ = self._create_graph(('prod', 'cons'), (('cons', 'prod'),))
        self.assertSequenceEqual(tuple(cons.dependencies), (dep,))
        self.assertSequenceEqual(tuple(prod.dependents), (ArtifactDependency(cons),))

    def test_two_dependents(self):
        (prod, cons1, cons2), (dep1, dep2), _ = self._create_graph(('prod', 'cons1', 'cons2'),
                                                                   (('cons1', 'prod'), ('cons2', 'prod')))

        self.assertSequenceEqual(tuple(cons1.dependencies), (dep1,))
        self.assertSequenceEqual(tuple(cons2.dependencies), (dep2,))

        expected_dependents = (ArtifactDependency(cons1), ArtifactDependency(cons2))
        self.assertSequenceEqual(tuple(prod.dependents), expected_dependents)

    def test_remove_dependency(self):
        graph, _, _ = self._create_graph(('prod', 'cons1', 'cons2'), (('cons1', 'prod'), ('cons2', 'prod')))

        (prod, cons1, cons2) = graph
        cons1.remove_dependency(prod)

        expected, _, _ = self._create_graph(('prod', 'cons1', 'cons2'), (('cons2', 'prod'),))
        self._assert_graphs_equal(expected, graph)

    def test_filter_dependency(self):
        (prod, cons1, cons2), (dep1, dep2), _ = self._create_graph(('prod', 'cons1', 'cons2'),
                                                                   (('cons1', 'prod'), ('cons2', 'prod')))

        def f(a): return FilterAction.reject if a.descriptor.artifact_id == 'prod' else FilterAction.accept

        result = filter_artifacts((prod, cons1, cons2), (f,))

        expected, _, _ = self._create_graph(('cons1', 'cons2'), ())
        self._assert_graphs_equal(expected, result)

    def test_filter_dependent(self):
        (prod, cons1, cons2), _, _ = self._create_graph(('prod', 'cons1', 'cons2'),
                                                        (('cons1', 'prod'), ('cons2', 'prod')))

        def f(a): return FilterAction.reject if a.descriptor.artifact_id == 'cons1' else FilterAction.accept

        result = filter_artifacts((prod, cons1, cons2), (f,))

        expected, _, _ = self._create_graph(('prod', 'cons2'), (('cons2', 'prod'),))
        self._assert_graphs_equal(expected, result)

    def test_chained_dependencies(self):
        (a, b, c), (b_to_a, c_to_b), (a_from_b, b_from_c) = self._create_graph(('a', 'b', 'c'),
                                                                               (('b', 'a'), ('c', 'b')))

        self.assertSequenceEqual(tuple(a.dependencies), ())
        self.assertSequenceEqual(tuple(a.all_dependencies), ())
        self.assertSequenceEqual(tuple(a.dependents), (a_from_b,))
        self.assertSequenceEqual(tuple(a.all_dependents), (b, c))

        self.assertSequenceEqual(tuple(b.dependencies), (b_to_a,))
        self.assertSequenceEqual(tuple(b.all_dependencies), (a,))
        self.assertSequenceEqual(tuple(b.dependents), (b_from_c,))
        self.assertSequenceEqual(tuple(b.all_dependents), (c,))

        self.assertSequenceEqual(tuple(c.dependencies), (c_to_b,))
        self.assertSequenceEqual(tuple(c.all_dependencies), (b, a))
        self.assertSequenceEqual(tuple(c.dependents), ())
        self.assertSequenceEqual(tuple(c.all_dependents), ())


if __name__ == '__main__':
    unittest.main()
