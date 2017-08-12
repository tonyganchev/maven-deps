import unittest

from mavendeps import FilterAction, parse_dot_graph, dot_to_maven_graph, reject_any, filter_artifacts, \
    maven_to_dot_graph
from pydot import graph_from_dot_file

__author__ = 'Tony Ganchev'


class IntegrationTestCase(unittest.TestCase):
    def test_karaf_sample(self):
        def include_reactor_artifacts(artifact):
            return FilterAction.accept if artifact.in_reactor else FilterAction.no_action

        def exclude_non_reactor_dependencies(artifact):
            for a in artifact.dependents:
                if a.artifact.in_reactor:
                    return FilterAction.accept
            return FilterAction.no_action

        def in_reactor_style(artifact, node):
            if artifact.in_reactor:
                node.set_penwidth(2)
                node.set_fillcolor('"lightgreen"')

        def kar_style(artifact, node):
            if artifact.descriptor.packaging == 'kar':
                node.set_fillcolor('"pink"')

        def assembly_style(artifact, node):
            if artifact.descriptor.packaging == 'karaf-assembly':
                node.set_fillcolor('"yellow"')

        in_graph = parse_dot_graph('tests/karaf-sample.dot')

        artifacts = dot_to_maven_graph(in_graph)

        filter_functions = include_reactor_artifacts, exclude_non_reactor_dependencies, reject_any
        artifacts = filter_artifacts(artifacts, filter_functions)

        style_functions = in_reactor_style, kar_style, assembly_style
        out_graph = maven_to_dot_graph(artifacts, style_functions)

        self.maxDiff = None
        expected_graph = graph_from_dot_file('tests/karaf-sample-modified.expected.dot')[0]

        for key in 'attributes', 'suppress_disconnected', 'simplify', 'strict', 'subgraphs', 'name', 'type',\
                   'current_child_sequence':
            self.assertEqual(out_graph.obj_dict[key], expected_graph.obj_dict[key])
        for ek, actual_ev in out_graph.obj_dict['edges'].items():
            actual_ev = actual_ev[0]
            expected_ev = expected_graph.obj_dict['edges'][ek][0]
            for key in 'attributes', 'points', 'type':
                self.assertEqual(actual_ev[key], expected_ev[key])
        for nk, actual_nv in out_graph.obj_dict['nodes'].items():
            actual_nv = actual_nv[0]
            print(actual_ev)
            expected_nv = expected_graph.obj_dict['nodes'][nk][0]
            print(expected_ev)
            for key in 'name', 'type', 'port':
                self.assertAlmostEqual(actual_nv[key], expected_nv[key])
