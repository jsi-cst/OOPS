from core.shared import DependencyGraph

from core.shared import FileHandler

from core.shared import LLMFactory

from core.agents import GenerationPartAblationAgent

from core.agents import ExtractionPartAblationAgent

from core.libraries import *

from core.constants import *


class AblationOfExtraction:

    class Config(BaseModel, frozen=True, arbitrary_types_allowed=True):

        default_llm_worker_client: LLMFactory | None = Field(default=None)
        default_llm_parser_client: LLMFactory | None = Field(default=None)

        ignore_sufx: list[str] | None = Field(default=None)
        ignore_path: list[str] | None = Field(default=None)

    __openapi: OpenAPI

    __store: str

    __plang: str

    __frame: str

    __file_handler: FileHandler

    __common_config: Config

    def __init__(self: Self, title: str, version: str, project: str, store: str, plang: str, frame: str, config: Config):

        self.__openapi = OpenAPI(openapi='3.1.0', info=Info(title=title, version=version), paths={})

        self.__common_config, self.__plang = config, plang

        self.__common_config, self.__frame = config, frame

        self.__store, self.__file_handler = store, FileHandler(
            ignore_sufx=config.ignore_sufx,
            ignore_path=config.ignore_path,
            directory=project
        )

    def get_store(self: Self) -> str:

        return self.__store

    def get_plang(self: Self) -> str:

        return self.__plang

    def get_frame(self: Self) -> str:

        return self.__frame

    async def run(self: Self) -> OpenAPI:

        for (_, method), apiurl in {(i.feat, i.method): i.path for i in await self.call()}.items():

            # evaluate endpoint methods only, simplify subsequent steps with LLMs

            # evaluate endpoint methods only, simplify subsequent steps with LLMs

            self.__openapi.paths[apiurl] = self.__openapi.paths.get(apiurl, PathItem())

            # ------------------------------------------------

            if method.upper() == 'HEAD':
                self.__openapi.paths[apiurl].head = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].head.responses = {'200': Response(description='OK')}

            if method.upper() == 'POST':
                self.__openapi.paths[apiurl].post = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].post.responses = {'200': Response(description='OK')}

            if method.upper() == 'OPTIONS':
                self.__openapi.paths[apiurl].options = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].options.responses = {'200': Response(description='OK')}

            if method.upper() == 'TRACE':
                self.__openapi.paths[apiurl].trace = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].trace.responses = {'200': Response(description='OK')}

            # ------------------------------------------------

            if method.upper() == 'GET':
                self.__openapi.paths[apiurl].get = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].get.responses = {'200': Response(description='OK')}

            if method.upper() == 'PUT':
                self.__openapi.paths[apiurl].put = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].put.responses = {'200': Response(description='OK')}

            if method.upper() == 'DELETE':
                self.__openapi.paths[apiurl].delete = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].delete.responses = {'200': Response(description='OK')}

            if method.upper() == 'PATCH':
                self.__openapi.paths[apiurl].patch = Operation(operationId=secrets.token_hex(16))
                self.__openapi.paths[apiurl].patch.responses = {'200': Response(description='OK')}

        return self.__openapi

    async def call(self: Self) -> list[ExtractionPartAblationAgent.Bean]:

        worker_factory = self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.default_llm_parser_client

        return await ExtractionPartAblationAgent.run(
            self.__file_handler,
            worker_factory.build(f'{self.__store}/extraction-part-ablation'),
            parser_factory.build(f'{self.__store}/extraction-part-ablation'),
            self.__plang,
            self.__frame,
            None
        )


# ------------------------------------------------


class AblationOfGeneration:

    class Config(BaseModel, frozen=True, arbitrary_types_allowed=True):

        default_llm_worker_client: LLMFactory | None = Field(default=None)
        default_llm_parser_client: LLMFactory | None = Field(default=None)

        ignore_sufx: list[str] | None = Field(default=None)
        ignore_path: list[str] | None = Field(default=None)

    __openapi: OpenAPI

    __store: str

    __plang: str

    __frame: str

    __file_handler: FileHandler

    __common_config: Config

    def __init__(self: Self, title: str, version: str, project: str, store: str, context: Any, config: Config):

        plang = getattr(context, '_MainPipeline__plang')  # force recover attributes

        frame = getattr(context, '_MainPipeline__frame')  # force recover attributes

        tasks: Iterable[DependencyGraph.Outlet] = getattr(context, '_MainPipeline__swagger_components')

        graph: DependencyGraph = getattr(context, '_MainPipeline__dependency_graph')

        self.__openapi = OpenAPI(openapi='3.1.0', info=Info(title=title, version=version), paths={})

        self.__common_config, self.__dependency_graph, self.__plang = config, graph, plang

        self.__common_config, self.__dependency_graph, self.__frame = config, graph, frame

        self.__store, self.__tasks, self.__file_handler = store, [i for i in tasks if i], FileHandler(
            ignore_sufx=config.ignore_sufx,
            ignore_path=config.ignore_path,
            directory=project
        )

    def get_store(self: Self) -> str:

        return self.__store

    def get_plang(self: Self) -> str:

        return self.__plang

    def get_frame(self: Self) -> str:

        return self.__frame

    async def run(self: Self) -> OpenAPI:

        for k, operation in [(k, v.operation) for k, v in zip(self.__tasks, await self.call()) if v]:

            # reuse results of endpoint method extract to reduce LLM token usage

            # reuse results of endpoint method extract to reduce LLM token usage

            self.__openapi.paths[k.apiurl] = self.__openapi.paths.get(k.apiurl, PathItem())

            # ------------------------------------------------

            if k.method in ('ANY', 'ALL', 'HEAD'):
                self.__openapi.paths[k.apiurl].head = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].head.operationId = secrets.token_hex(16)

            if k.method in ('ANY', 'ALL', 'POST'):
                self.__openapi.paths[k.apiurl].post = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].post.operationId = secrets.token_hex(16)

            if k.method in ('ANY', 'ALL', 'OPTIONS'):
                self.__openapi.paths[k.apiurl].options = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].options.operationId = secrets.token_hex(16)

            if k.method in ('ANY', 'ALL', 'TRACE'):
                self.__openapi.paths[k.apiurl].trace = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].trace.operationId = secrets.token_hex(16)

            # ------------------------------------------------

            if k.method in ('ANY', 'ALL', 'GET'):
                self.__openapi.paths[k.apiurl].get = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].get.operationId = secrets.token_hex(16)

            if k.method in ('ANY', 'ALL', 'PUT'):
                self.__openapi.paths[k.apiurl].put = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].put.operationId = secrets.token_hex(16)

            if k.method in ('ANY', 'ALL', 'DELETE'):
                self.__openapi.paths[k.apiurl].delete = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].delete.operationId = secrets.token_hex(16)

            if k.method in ('ANY', 'ALL', 'PATCH'):
                self.__openapi.paths[k.apiurl].patch = operation  # matches JSON schema
                self.__openapi.paths[k.apiurl].patch.operationId = secrets.token_hex(16)

        return self.__openapi

    async def call(self: Self) -> list[GenerationPartAblationAgent.Bean | None]:

        mapper = self.__dependency_graph.get_operation_implements

        worker_factory = self.__common_config.default_llm_worker_client

        parser_factory = self.__common_config.default_llm_parser_client

        return await GenerationPartAblationAgent.batch_run_lite(
            self.__file_handler,
            worker_factory.build(f'{self.__store}/generation-part-ablation'),
            parser_factory.build(f'{self.__store}/generation-part-ablation'),
            self.__plang,
            self.__frame,
            [i.apiurl for i in self.__tasks],
            [i.method for i in self.__tasks],
            [mapper(i) for i in self.__tasks]
        )
