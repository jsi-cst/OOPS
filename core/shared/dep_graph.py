from core.libraries import *
from core.constants import *


class DependencyGraph:

    class Entry(BaseModel, frozen=True):

        file: str
        path: str
        feat: str
        handler: str
        tag: str

    __graph_instance: networkx.DiGraph

    __node_map: dict[tuple[str, str, str], Entry]

    __file_to_entry: dict[str, list[Entry]]

    __feat_to_entry: dict[str, list[Entry]]

    __entry_list: list[Entry]

    def __init__(self: Self):

        self.__graph_instance, self.__operation_to_impl = networkx.DiGraph(), {}

        self.__file_to_entry, self.__apiurl_set = {}, set()

        self.__feat_to_entry, self.__method_set = {}, set()

        self.__node_map, self.__operation_map = {}, {}

        self.__entry_list, self.__operation_list = [], []

    def visualize_full(self: Self, save: str) -> None:

        graph, mapper, position = self.__graph_instance, self.__file_to_entry, networkx.kamada_kawai_layout(self.__graph_instance)

        lb_pos, lb_txt = {k: (x, y) for k, (x, y) in position.items()}, {k: k or str(len(v)) for k, v in mapper.items()}

        # lb_pos, lb_txt = {k: (x, y + 0.1) for k, (x, y) in position.items()}, {k: k or str(len(v)) for k, v in mapper.items()}

        # lb_pos, lb_txt = {k: (x + 0.1, y) for k, (x, y) in position.items()}, {k: k or str(len(v)) for k, v in mapper.items()}

        assert networkx.draw(graph, position, with_labels=False) or networkx.draw_networkx_labels(graph, lb_pos, lb_txt) or save

        assert len([matplotlib.pyplot.savefig(save), matplotlib.pyplot.figure(), matplotlib.pyplot.close('all')]) == 3

    def visualize_lite(self: Self, save: str) -> None:

        graph, mapper, position = self.__graph_instance, self.__file_to_entry, networkx.kamada_kawai_layout(self.__graph_instance)

        lb_pos, lb_txt = {k: (x, y) for k, (x, y) in position.items()}, {k: str(len(v)) or k for k, v in mapper.items()}

        # lb_pos, lb_txt = {k: (x, y + 0.1) for k, (x, y) in position.items()}, {k: str(len(v)) or k for k, v in mapper.items()}

        # lb_pos, lb_txt = {k: (x + 0.1, y) for k, (x, y) in position.items()}, {k: str(len(v)) or k for k, v in mapper.items()}

        assert networkx.draw(graph, position, with_labels=False) or networkx.draw_networkx_labels(graph, lb_pos, lb_txt) or save

        assert len([matplotlib.pyplot.savefig(save), matplotlib.pyplot.figure(), matplotlib.pyplot.close('all')]) == 3

    # ------------------------------------------------

    def add_entry(self: Self, entry: Entry) -> None:

        if (entry.file, entry.feat, entry.handler) not in self.__node_map:

            self.__entry_list.append(entry)

            self.__file_to_entry[entry.file] = self.__file_to_entry.get(entry.file, [])

            self.__feat_to_entry[entry.feat] = self.__feat_to_entry.get(entry.feat, [])

            self.__file_to_entry[entry.file].append(entry)

            self.__feat_to_entry[entry.feat].append(entry)

            self.__node_map[(entry.file, entry.feat, entry.handler)] = entry

            self.__graph_instance.add_node(entry.file)

    def add_relation(self: Self, entry: Entry, target: str) -> None:

        if all(i != entry.handler for i in self.__file_to_entry.get(target, [])):

            # attention: not just create node when node not exist

            # attention: not just create node when node not exist

            self.add_entry(DependencyGraph.Entry(file=target, path='', feat='', handler=entry.handler, tag='local'))

        assert (entry.file, entry.feat, entry.handler) in self.__node_map and target in self.__file_to_entry

        assert (entry.file, entry.feat, entry.handler) in self.__node_map and target in self.__file_to_entry

        if entry.file != target:  # no self loops

            self.__graph_instance.add_edge(target, entry.file)

    def select_entry_by_path(self: Self, value: str) -> list[Entry]:

        return [i for i in self.__entry_list if i.path == value]

    def select_entry_by_feat(self: Self, value: str) -> list[Entry]:

        return [i for i in self.__entry_list if i.feat == value]

    def select_entry_by_tag(self: Self, value: str) -> list[Entry]:

        return [i for i in self.__entry_list if i.tag == value]

    def get_dependencies(self: Self, entry: Entry) -> list[str]:

        nodes = {entry.file} | networkx.descendants(self.__graph_instance, entry.file)

        assert (entry.file, entry.feat, entry.handler) in self.__node_map

        assert (entry.file, entry.feat, entry.handler) in self.__node_map

        subgraph: networkx.Graph = self.__graph_instance.subgraph(nodes)

        if networkx.is_directed_acyclic_graph(subgraph):

            return [i for i in networkx.topological_sort(subgraph)][::-1]

        print('warning: cycle detected in api dependency graph')

        print('warning: cycle detected in api dependency graph')

        return sorted(subgraph.nodes)[::-1]

    # ------------------------------------------------

    class Outlet(BaseModel, frozen=True):

        method: str
        apiurl: str
        feat: str

    __operation_to_impl: dict[tuple[str, str], list[Entry]]

    __apiurl_set: set[str]  # for debugging

    __method_set: set[str]  # for debugging

    __operation_map: dict[tuple[str, str], Outlet]

    __operation_list: list[Outlet]

    def add_operation(self: Self, entry: Entry, method: str, apiurl: str, feat: str) -> None:

        if feat.rstrip('/') and all((i, feat) not in self.__operation_map for i in ('ANY', 'ALL', method)):

            self.__operation_list.append(DependencyGraph.Outlet(method=method, apiurl=apiurl, feat=feat))

            self.__apiurl_set.add(self.__operation_list[-1].apiurl)

            self.__method_set.add(self.__operation_list[-1].method)

            self.__operation_map[(method, feat)] = self.__operation_list[-1]

            self.__operation_to_impl[(method, feat)] = [entry]

        elif ('ANY', feat) in self.__operation_map:

            self.__operation_to_impl[('ANY', feat)].append(entry)

        elif ('ALL', feat) in self.__operation_map:

            self.__operation_to_impl[('ALL', feat)].append(entry)

        elif (method, feat) in self.__operation_map:

            self.__operation_to_impl[(method, feat)].append(entry)

    def get_apiurl_list(self: Self) -> list[str]:

        return sorted(self.__apiurl_set)

    def get_method_list(self: Self) -> list[str]:

        return sorted(self.__method_set)

    def get_operation_implements(self: Self, operation: Outlet) -> list[Entry]:

        return self.__operation_to_impl[(operation.method, operation.feat)]

    def get_operations(self: Self) -> list[Outlet]:

        return self.__operation_list
