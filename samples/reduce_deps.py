#!/usr/bin/env python
from mavendeps import parse_dot_graph, dot_to_maven_graph, maven_to_dot_graph, filter_artifacts

__author__ = 'Tony Ganchev'


def reduce_deps(source_file, target_file, filter_chain, style_functions):
    in_graph = parse_dot_graph(source_file)

    artifacts = dot_to_maven_graph(in_graph)

    artifacts = filter_artifacts(artifacts, filter_chain)

    out_graph = maven_to_dot_graph(artifacts, style_functions)

    out_graph.write(target_file)
    out_graph.write_svg(target_file + '.svg')
