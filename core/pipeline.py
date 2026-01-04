from core.agents import TechnologyAnalyzeAgent

from core.agents import APIEntryDetectionAgent

from core.agents import FileDependencyAnalyzeAgent

from core.agents import EndpointMethodExtractAgent

from core.agents import SwaggerGenerationAgent

from core.shared import OASBuilder

from core.shared import LLMFactory

from core.shared import DependencyGraph

from core.shared import FileHandler

from core.libraries import *

from core.constants import *


class MainPipeline:

    class Config(BaseModel, frozen=True, arbitrary_types_allowed=True):

        default_llm_worker_client: LLMFactory | None = Field(default=None)
        default_llm_parser_client: LLMFactory | None = Field(default=None)

        technology_analyze_worker_client: LLMFactory | None = Field(default=None)
        api_entry_detection_worker_client: LLMFactory | None = Field(default=None)
        file_dependency_analyze_worker_client: LLMFactory | None = Field(default=None)
        endpoint_method_extract_worker_client: LLMFactory | None = Field(default=None)
        swagger_generation_worker_client: LLMFactory | None = Field(default=None)

        technology_analyze_parser_client: LLMFactory | None = Field(default=None)
        api_entry_detection_parser_client: LLMFactory | None = Field(default=None)
        file_dependency_analyze_parser_client: LLMFactory | None = Field(default=None)
        endpoint_method_extract_parser_client: LLMFactory | None = Field(default=None)
        swagger_generation_parser_client: LLMFactory | None = Field(default=None)

        ignore_sufx: list[str] | None = Field(default=None)
        ignore_path: list[str] | None = Field(default=None)

    __api_entries: dict[str, list[APIEntryDetectionAgent.Bean]]

    __file_dependencies: dict[DependencyGraph.Entry, FileDependencyAnalyzeAgent.Bean]

    __endpoint_methods: dict[DependencyGraph.Entry, EndpointMethodExtractAgent.Bean]

    __swagger_components: dict[DependencyGraph.Outlet, SwaggerGenerationAgent.Bean]

    __plang: str  # no need to wrap into pydantic model

    __frame: str  # no need to wrap into pydantic model

    __state: str  # no need to wrap into pydantic model

    __log_base: str  # no need to wrap into pydantic model

    __upg_base: str  # no need to wrap into pydantic model

    __dependency_graph: DependencyGraph

    __file_handler: FileHandler

    __oas_builder: OASBuilder

    __common_config: Config

    def __init__(self: Self, title: str, version: str, project: str, log_base: str, upg_base: str, config: Config):

        self.__api_entries, self.__file_dependencies, self.__endpoint_methods, self.__swagger_components = {}, {}, {}, {}

        self.__common_config, self.__log_base, self.__plang = config, log_base, 'Unknown'

        self.__common_config, self.__upg_base, self.__frame = config, upg_base, 'Unknown'

        self.__oas_builder = OASBuilder(title, upg_base, version)  # remove timestamp

        self.__state, self.__dependency_graph = 'pre_technology_analyze', DependencyGraph()

        self.__file_handler = FileHandler(
            ignore_sufx=config.ignore_sufx,
            ignore_path=config.ignore_path,
            directory=project
        )

    def get_log_base(self: Self) -> str:

        return self.__log_base

    def get_upg_base(self: Self) -> str:

        return self.__upg_base

    def get_plang(self: Self) -> str:

        return self.__plang

    def get_frame(self: Self) -> str:

        return self.__frame

    def get_state(self: Self) -> str:

        return self.__state

    def dump_states(self: Self, target: str, full: bool = True) -> None:

        converter = lambda x: list(x) if isinstance(x, set) else x

        assert os.path.isdir(self.__log_base)  # check log directories

        assert os.path.isdir(self.__upg_base)  # check log directories

        technology_analyze_states = {'programming-language': self.__plang, 'development-framework': self.__frame}

        api_entry_detection_states = {k: [i.model_dump() for i in v] for k, v in self.__api_entries.items()}

        file_dependency_analyze_states = [[k.model_dump(), v.model_dump()] for k, v in self.__file_dependencies.items()]

        endpoint_method_extract_states = [[k.model_dump(), v.model_dump()] for k, v in self.__endpoint_methods.items()]

        swagger_generation_states = [[k.model_dump(), v.model_dump()] for k, v in self.__swagger_components.items()]

        with open(f'{target}/technology-analyze.json', 'w', encoding='utf-8') as file:  # fix set fields
            json.dump(technology_analyze_states, file, indent=4, ensure_ascii=False, default=converter)

        with open(f'{target}/api-entry-detection.json', 'w', encoding='utf-8') as file:  # fix set fields
            json.dump(api_entry_detection_states, file, indent=4, ensure_ascii=False, default=converter)

        with open(f'{target}/file-dependency-analyze.json', 'w', encoding='utf-8') as file:  # fix set fields
            json.dump(file_dependency_analyze_states, file, indent=4, ensure_ascii=False, default=converter)

        with open(f'{target}/endpoint-method-extract.json', 'w', encoding='utf-8') as file:  # fix set fields
            json.dump(endpoint_method_extract_states, file, indent=4, ensure_ascii=False, default=converter)

        with open(f'{target}/swagger-generation.json', 'w', encoding='utf-8') as file:  # fix set fields
            json.dump(swagger_generation_states, file, indent=4, ensure_ascii=False, default=converter)

        self.visualize_dependency_graph_full()  # use png by default

        self.visualize_dependency_graph_lite()  # use png by default

        if full:  # extra pickle dump for state recovery in the following steps

            with open(f'{target}/states.pickle', 'wb') as file:

                pickle.dump(self, file)  # serialize

    @staticmethod
    def load_states(target: str) -> 'MainPipeline':

        with open(f'{target}/states.pickle', 'rb') as file:

            # attention: only trusted files can be deserialized

            # attention: only trusted files can be deserialized

            return pickle.load(file)  # unserialize

    # ================================================
    # ============== technology analyze ==============
    # ================================================

    async def pre_technology_analyze(self: Self) -> None:

        worker_factory = self.__common_config.technology_analyze_worker_client or self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.technology_analyze_parser_client or self.__common_config.default_llm_parser_client

        worker_model = worker_factory.build(f'{self.__log_base}/technology-analyze')

        parser_model = parser_factory.build(f'{self.__log_base}/technology-analyze')

        result = await TechnologyAnalyzeAgent.run(self.__file_handler, worker_model, parser_model)

        self.__plang, self.__frame = result.plang, result.frame

    # ================================================
    # ============= api entry detection ==============
    # ================================================

    async def run_api_entry_detection(self: Self) -> None:

        tasks = [i for i in self.__file_handler.get_files()]  # the order doesn't matter

        worker_factory = self.__common_config.api_entry_detection_worker_client or self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.api_entry_detection_parser_client or self.__common_config.default_llm_parser_client

        self.__api_entries = {k: v for k, v in zip(tasks, await APIEntryDetectionAgent.batch_run_lite(
            self.__file_handler,
            worker_factory.build(f'{self.__log_base}/api-entry-detection'),
            parser_factory.build(f'{self.__log_base}/api-entry-detection'),
            self.__plang,  # all the same
            self.__frame,  # all the same
            [i for i in tasks]
        ))}

    # ================================================
    # =========== file dependency analyze ============
    # ================================================

    async def run_file_dependency_analyze(self: Self) -> None:

        tasks = self.__dependency_graph.select_entry_by_tag('ref')  # the order doesn't matter

        worker_factory = self.__common_config.file_dependency_analyze_worker_client or self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.file_dependency_analyze_parser_client or self.__common_config.default_llm_parser_client

        self.__file_dependencies = {k: v for k, v in zip(tasks, await FileDependencyAnalyzeAgent.batch_run_lite(
            self.__file_handler,
            worker_factory.build(f'{self.__log_base}/file-dependency-analyze'),
            parser_factory.build(f'{self.__log_base}/file-dependency-analyze'),
            self.__plang,  # all the same
            self.__frame,  # all the same
            [i.file for i in tasks],
            [i.path for i in tasks],
            [i.handler for i in tasks]
        ))}

    # ================================================
    # =========== endpoint method extract ============
    # ================================================

    async def run_endpoint_method_extract(self: Self) -> None:

        tasks = self.__dependency_graph.select_entry_by_tag('local')  # the order doesn't matter

        worker_factory = self.__common_config.endpoint_method_extract_worker_client or self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.endpoint_method_extract_parser_client or self.__common_config.default_llm_parser_client

        self.__endpoint_methods = {k: v for k, v in zip(tasks, await EndpointMethodExtractAgent.batch_run_lite(
            self.__file_handler,
            worker_factory.build(f'{self.__log_base}/endpoint-method-extract'),
            parser_factory.build(f'{self.__log_base}/endpoint-method-extract'),
            self.__plang,  # all the same
            self.__frame,  # all the same
            [self.__dependency_graph.get_dependencies(i) for i in tasks],
            [i.file for i in tasks],
            [i.path for i in tasks],
            [i.handler for i in tasks]
        ))}

    # ================================================
    # ============== swagger generation ==============
    # ================================================

    async def run_swagger_generation(self: Self) -> None:

        tasks, mapper = self.__dependency_graph.get_operations(), self.__dependency_graph.get_operation_implements

        worker_factory = self.__common_config.swagger_generation_worker_client or self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.swagger_generation_parser_client or self.__common_config.default_llm_parser_client

        self.__swagger_components = {k: v for k, v in zip(tasks, await SwaggerGenerationAgent.batch_run_lite(
            self.__file_handler,
            worker_factory.build(f'{self.__log_base}/swagger-generation'),
            parser_factory.build(f'{self.__log_base}/swagger-generation'),
            self.__plang,  # all the same
            self.__frame,  # all the same
            [i.apiurl for i in tasks],
            [i.method for i in tasks],
            [mapper(i) for i in tasks]
        ))}

    # ================================================
    # ================ common methods ================
    # ================================================

    def add_swagger_component(self: Self) -> None:

        for k, v in self.__swagger_components.items():

            # expand all references in oas, rebuild them after version upgrade at last

            # expand all references in oas, rebuild them after version upgrade at last

            if k.method not in ('ANY', 'ALL'):

                self.__oas_builder.emplace_apidoc(k.apiurl, k.method, v.req, v.res)

            else:  # expand HTTP methods

                self.__oas_builder.emplace_apidoc(k.apiurl, 'HEAD', v.req, v.res)
                self.__oas_builder.emplace_apidoc(k.apiurl, 'POST', v.req, v.res)
                self.__oas_builder.emplace_apidoc(k.apiurl, 'OPTIONS', v.req, v.res)
                self.__oas_builder.emplace_apidoc(k.apiurl, 'TRACE', v.req, v.res)

                self.__oas_builder.emplace_apidoc(k.apiurl, 'GET', v.req, v.res)
                self.__oas_builder.emplace_apidoc(k.apiurl, 'PUT', v.req, v.res)
                self.__oas_builder.emplace_apidoc(k.apiurl, 'DELETE', v.req, v.res)
                self.__oas_builder.emplace_apidoc(k.apiurl, 'PATCH', v.req, v.res)

    def add_openapi_operation(self: Self) -> None:

        updater = self.__dependency_graph.add_operation

        for k, v in self.__endpoint_methods.items():

            assert isinstance([updater(k, i, v.path, v.feat) for i in v.methods if i == 'ANY'], list)

        for k, v in self.__endpoint_methods.items():

            assert isinstance([updater(k, i, v.path, v.feat) for i in v.methods if i != 'ANY'], list)

        # attention: method ANY will override all other methods

        # attention: method ANY will override all other methods

    def visualize_dependency_graph_full(self: Self, fmt: str = 'png') -> None:

        assert os.path.isdir(self.__log_base)  # check log directories

        assert os.path.isdir(self.__upg_base)  # check log directories

        save = f'{self.__log_base}/api-graph-full.{fmt}'

        self.__dependency_graph.visualize_full(save)

    def visualize_dependency_graph_lite(self: Self, fmt: str = 'png') -> None:

        assert os.path.isdir(self.__log_base)  # check log directories

        assert os.path.isdir(self.__upg_base)  # check log directories

        save = f'{self.__log_base}/api-graph-lite.{fmt}'

        self.__dependency_graph.visualize_lite(save)

    def add_dependency_graph_edge(self: Self) -> None:

        for k, v in self.__file_dependencies.items():

            for i in v.files:

                assert k  # auto create node and entry when i not in api graph

                assert i  # auto create node and entry when i not in api graph

                self.__dependency_graph.add_relation(k, i)

    def add_dependency_graph_node(self: Self) -> None:

        for k, v in self.__api_entries.items():

            for i in v:

                assert k  # unique key of entry: (file, feat, handler)

                assert i  # unique key of entry: (file, feat, handler)

                self.__dependency_graph.add_entry(DependencyGraph.Entry(
                    file=k,
                    path=i.path,
                    feat=i.feat,
                    handler=i.handler,
                    tag=i.tag
                ))

    # ================================================
    # ================= main methods =================
    # ================================================

    async def run(self: Self, confirm_each: bool = False, on_complete: Any = None) -> OpenAPI:

        async def forward(target: Any, *args: Any) -> Any:

            if inspect.iscoroutinefunction(target):
                return await target(*args)

            if inspect.isfunction(target):
                return target(*args)

            if inspect.ismethod(target):
                return target(*args)

            if target is None or isinstance(target, BaseModel):
                return target  # return target value directly

            if target is None or isinstance(target, RootModel):
                return target  # return target value directly

            raise RuntimeError()

        nexts = {
            'pre_technology_analyze': 'run_api_entry_detection',
            'run_api_entry_detection': 'add_dependency_graph_node',
            'add_dependency_graph_node': 'run_file_dependency_analyze',
            'run_file_dependency_analyze': 'add_dependency_graph_edge',
            'add_dependency_graph_edge': 'run_endpoint_method_extract',
            'run_endpoint_method_extract': 'add_openapi_operation',
            'add_openapi_operation': 'run_swagger_generation',
            'run_swagger_generation': 'add_swagger_component',
            'add_swagger_component': 'all_pipeline_steps_finished'
        }

        # ------------------------------------------------

        while self.__state in nexts:

            if confirm_each:

                # pause and require a maunal confirm before execution, for step-by-step debugging

                # pause and require a maunal confirm before execution, for step-by-step debugging

                input(f'Type to run step -> [{self.__state.replace(chr(95), chr(32))}]: ')

            self.__state, state, _ = nexts[self.__state], self.__state, await forward(getattr(self, self.__state, False))

            self.visualize_dependency_graph_full()  # pushup

            self.visualize_dependency_graph_lite()  # pushup

            await forward(on_complete, self, state, self.__state)

        self.__oas_builder.upgrade_apidoc()

        self.__oas_builder.rebuild_apidoc()

        return self.__oas_builder.get_openapi_object()
