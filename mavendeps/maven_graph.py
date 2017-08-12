#!/usr/bin/env python

__author__ = 'Tony Ganchev'


class ArtifactDescriptor:
    """
    Identifies a Maven artifact.
    """

    def __init__(self, group_id, artifact_id, version, packaging='jar', classifier=None):
        self._group_id = group_id
        self._artifact_id = artifact_id
        self._version = version
        self._packaging = packaging
        self._classifier = classifier

    @property
    def group_id(self):
        return self._group_id

    @property
    def artifact_id(self):
        return self._artifact_id

    @property
    def packaging(self):
        return self._packaging

    @property
    def version(self):
        return self._version

    @property
    def classifier(self):
        return self._classifier

    def __str__(self):
        packaging = self._packaging if self._classifier is None else '{}:{}'.format(self._packaging, self._classifier)
        return '{}:{}:{}:{}'.format(self._group_id, self._artifact_id, packaging, self._version)

    def __eq__(self, other):
        return str(self) == str(other) if isinstance(other, ArtifactDescriptor) else False

    def __hash__(self):
        return hash(str(self))


class Artifact:
    """
    Holds an artifact with all its Artifact dependencies
    """

    def __init__(self, descriptor, in_reactor=False):
        self._descriptor = descriptor
        self._dependencies = []
        self._dependents = []
        self._tags = set()
        self._in_reactor = in_reactor

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def dependencies(self):
        return (d for d in self._dependencies)

    @property
    def all_dependencies(self):
        for d in self._dependencies:
            yield d.artifact
            for a in d.artifact.all_dependencies:
                yield a

    @property
    def dependents(self):
        return (d for d in self._dependents)

    @property
    def all_dependents(self):
        for d in self._dependents:
            yield d.artifact
            for a in d.artifact.all_dependents:
                yield a

    @property
    def tags(self):
        return self._tags

    @property
    def in_reactor(self):
        return self._in_reactor

    def __str__(self):
        return '<Artifact {}>'.format(str(self._descriptor))

    def __eq__(self, other):
        return str(self._descriptor) == str(other.descriptor) if isinstance(other, Artifact) else False

    def add_dependency(self, dep):
        self._dependencies.append(dep)
        dep.artifact.add_dependent(ArtifactDependency(self, dep.scope))

    def add_dependent(self, dep):
        self._dependents.append(dep)

    def remove_dependency(self, artifact):
        for d in self._dependencies:
            if d.artifact == artifact:
                # print('{} dropping dependency to {}'.format(self._descriptor, d.artifact.descriptor))
                self._dependencies.remove(d)
                d.artifact.remove_dependent(self)
                break

    def remove_dependent(self, artifact):
        for d in self._dependents:
            if d.artifact == artifact:
                # print('{} dropping dependency from {}'.format(self._descriptor, d.artifact.descriptor))
                self._dependents.remove(d)
                break


class ArtifactDependency:
    """
    Identifies a maven artifact dependency
    """

    def __init__(self, artifact, scope='compile'):
        self._artifact = artifact
        self._scope = scope

    @property
    def artifact(self):
        return self._artifact

    @property
    def scope(self):
        return self._scope

    def __eq__(self, other):
        """
        Checks two ArtifactDependency instances for equality.

        :type other: ArtifactDependency
        """
        if isinstance(other, ArtifactDependency):
            return self._artifact == other.artifact and self._scope == other.scope
        else:
            return False


class FilterAction:
    """
    Return value type for filtering functions. Determines whether the artifact passed to the filter function should be
    accepted, rejected, or further processed.
    """
    accept = 'accept'
    reject = 'reject'
    no_action = 'no_action'

    def __init__(self):
        raise NotImplemented


def filter_artifacts(in_artifacts, filter_chain):
    """
    Generates a set of Maven artifacts from an incoming set of artifacts by
    passing the incoming set through a chain of filter functions.
    """
    from sys import getrecursionlimit, setrecursionlimit
    rl = getrecursionlimit()
    setrecursionlimit(10000)
    from copy import deepcopy
    artifacts = [a for a in deepcopy(in_artifacts)]
    setrecursionlimit(rl)

    # descriptors of the artifacts that need to be preserved.
    required_artifacts = set()
    for filter_func in filter_chain:
        # filter_name = filter_func.__name__
        # print('{}: applying for {} artifact(s).'.format(filter_name, len(artifacts)))
        for artifact_idx in range(0, len(artifacts)):
            artifact = artifacts[artifact_idx]
            if artifact.descriptor not in required_artifacts:
                filter_action = filter_func(artifact)
                # print('{}: {} {}'.format(filter_name, filter_action, artifact.descriptor))
                if filter_action == FilterAction.no_action:
                    pass
                elif filter_action == FilterAction.accept:
                    required_artifacts.add(artifact.descriptor)
                elif filter_action == FilterAction.reject:
                    artifacts[artifact_idx] = None
                    for dependency in tuple(artifact.dependencies):
                        dependency.artifact.remove_dependent(artifact)
                    for dependent in tuple(artifact.dependents):
                        dependent.artifact.remove_dependency(artifact)
            else:
                # print('{}: skipping {}'.format(filter_name, artifact.descriptor))
                pass
        artifacts = [artifact for artifact in artifacts if artifact is not None]
    return tuple(artifacts)


def ignore_any(_):
    """
    Stock filter function that skips processing the passed artifact. The artifact
    proceeds further down the filter chain.
    """
    return FilterAction.no_action


def accept_any(_):
    """
    Stock filter function that accepts the passed artifact. The artifact remains
    part of the resulting graph and is not a subject to further filtering.
    """
    return FilterAction.accept


def reject_any(_):
    """
    Stock filter function that rejects the passed artifact. The artifact is
    removed from the resulting graph and is not a subject to further filtering.
    """
    return FilterAction.reject
