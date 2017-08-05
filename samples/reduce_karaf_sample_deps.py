#!/usr/bin/env python

from reduce_deps import reduce_deps
from mavendeps import reject_any, FilterAction

__author__ = 'Tony Ganchev'


def include_reactor_artifacts(artifact):
    return FilterAction.accept if artifact.in_reactor else FilterAction.no_action


def exclude_non_reactor_dependencies(artifact):
    for a in artifact.dependents:
        if a.artifact.in_reactor:
            print [str(aa.artifact.descriptor) for aa in artifact.dependents]
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


def main():
    source_file = 'karaf-sample.dot'
    target_file = 'karaf-sample-modified.dot'
    filter_functions = include_reactor_artifacts, exclude_non_reactor_dependencies, reject_any
    style_functions = in_reactor_style, kar_style, assembly_style
    reduce_deps(source_file, target_file, filter_functions, style_functions)


if __name__ == '__main__':
    main()
