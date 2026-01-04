from core.shared import FileHandler

from core.shared import normalize_path_params

from core.libraries import *

from core.constants import *

with open(f'{os.path.dirname(__file__)}/prompt.jinja', 'r', encoding='utf-8') as __file:
    prompt: jinja2.Template = jinja2.Template(__file.read())


class EndpointMethodExtractResult(BaseModel, frozen=True):

    path: str = Field(description='The full HTTP request path for the endpoint.')
    arbitrary: bool = Field(description='Whether all HTTP methods are acceptable.')

    head: bool = Field(description='Whether the HEAD method is acceptable.')
    post: bool = Field(description='Whether the POST method is acceptable.')
    options: bool = Field(description='Whether the OPTIONS method is acceptable.')
    trace: bool = Field(description='Whether the TRACE method is acceptable.')

    get: bool = Field(description='Whether the GET method is acceptable.')
    put: bool = Field(description='Whether the PUT method is acceptable.')
    delete: bool = Field(description='Whether the DELETE method is acceptable.')
    patch: bool = Field(description='Whether the PATCH method is acceptable.')


class EndpointMethodExtractRefine(BaseModel, frozen=True):

    path: str = Field(description='The full HTTP request path for the endpoint.')
    arbitrary: bool = Field(description='Whether all HTTP methods are acceptable.')

    head: bool = Field(description='Whether the HEAD method is acceptable.')
    post: bool = Field(description='Whether the POST method is acceptable.')
    options: bool = Field(description='Whether the OPTIONS method is acceptable.')
    trace: bool = Field(description='Whether the TRACE method is acceptable.')

    get: bool = Field(description='Whether the GET method is acceptable.')
    put: bool = Field(description='Whether the PUT method is acceptable.')
    delete: bool = Field(description='Whether the DELETE method is acceptable.')
    patch: bool = Field(description='Whether the PATCH method is acceptable.')


class EndpointMethodExtractAgent:

    class Bean(BaseModel, frozen=True):

        path: str
        feat: str
        methods: set[str]

        @staticmethod
        def wakeup(that: Any) -> 'EndpointMethodExtractAgent.Bean':

            if that is None:
                raise RuntimeError()

            if isinstance(that, EndpointMethodExtractResult):
                basic = ('POST', 'GET', 'PUT', 'DELETE', 'PATCH')  # ignore HEAD/OPTIONS/TRACE for simplicity
                methods = {'ANY'} if that.arbitrary else {i for i in basic if getattr(that, i.lower())}
                return EndpointMethodExtractAgent.Bean(**normalize_path_params(that.path), methods=methods)

            if isinstance(that, EndpointMethodExtractRefine):
                basic = ('POST', 'GET', 'PUT', 'DELETE', 'PATCH')  # ignore HEAD/OPTIONS/TRACE for simplicity
                methods = {'ANY'} if that.arbitrary else {i for i in basic if getattr(that, i.lower())}
                return EndpointMethodExtractAgent.Bean(**normalize_path_params(that.path), methods=methods)

            raise RuntimeError()

        @staticmethod
        def verify(that: Any) -> bool:

            if that is None:
                return False

            if isinstance(that, EndpointMethodExtractResult):
                return any(i is not None for i in that.model_dump().values())

            if isinstance(that, EndpointMethodExtractRefine):
                return any(i is not None for i in that.model_dump().values())

            return False

    # ------------------------------------------------

    @staticmethod
    async def __batch_run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str] | str,  # same value if is str
        frames: list[str] | str,  # same value if is str
        depends: list[list[str]],  # for prompt template render
        files: list[str],  # for prompt template render
        paths: list[str],  # for prompt template render
        handlers: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['EndpointMethodExtractAgent.Bean']]:

        parameters = [i for i in inspect.signature(EndpointMethodExtractAgent.__batch_run).parameters if isinstance(locals()[i], list)]

        plangs = [plangs for _ in files] if isinstance(plangs, str) else plangs

        frames = [frames for _ in files] if isinstance(frames, str) else frames

        assert len({len(locals()[i]) for i in parameters}) == 1  # require all same length

        # ------------------------------------------------

        async def solve(semaphore: asyncio.Semaphore, *args: Any) -> None:  # wrap semaphore

            # args: use fixed order of parameters for simplicity

            # args: use fixed order of parameters for simplicity

            async with semaphore:

                return await EndpointMethodExtractAgent.run(context, worker_model, parser_model, *args, extra)

        # ------------------------------------------------

        semaphore = asyncio.Semaphore(LLM_BATCH_SEMAPHORE)

        # limit concurrent connections to prevent risk controls

        # limit concurrent connections to prevent risk controls

        return await asyncio.gather(*[solve(semaphore, *args) for args in zip(
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            depends,  # add a comment to disable yapf format
            files,  # add a comment to disable yapf format
            paths,  # add a comment to disable yapf format
            handlers  # add a comment to disable yapf format
        )])

    @staticmethod
    async def batch_run_full(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str],  # for prompt template render
        frames: list[str],  # for prompt template render
        depends: list[list[str]],  # for prompt template render
        files: list[str],  # for prompt template render
        paths: list[str],  # for prompt template render
        handlers: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['EndpointMethodExtractAgent.Bean']]:

        return await EndpointMethodExtractAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            depends,  # add a comment to disable yapf format
            files,  # add a comment to disable yapf format
            paths,  # add a comment to disable yapf format
            handlers,  # add a comment to disable yapf format
            extra  # add a comment to disable yapf format
        )

    @staticmethod
    async def batch_run_lite(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: str,  # use same value for each llm call
        frames: str,  # use same value for each llm call
        depends: list[list[str]],  # for prompt template render
        files: list[str],  # for prompt template render
        paths: list[str],  # for prompt template render
        handlers: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['EndpointMethodExtractAgent.Bean']]:

        return await EndpointMethodExtractAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            depends,  # add a comment to disable yapf format
            files,  # add a comment to disable yapf format
            paths,  # add a comment to disable yapf format
            handlers,  # add a comment to disable yapf format
            extra  # add a comment to disable yapf format
        )

    @staticmethod
    async def run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plang: str,  # for prompt template render
        frame: str,  # for prompt template render
        depend: list[str],  # for prompt template render
        file: str,  # for prompt template render
        path: str,  # for prompt template render
        handler: str,  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> Optional['EndpointMethodExtractAgent.Bean']:

        sys_msg = prompt.render(
            role='sys',
            files=context.get_files(),  # use jinja2 to manage prompt templates
            plang=plang,  # use jinja2 to manage prompt templates
            frame=frame,  # use jinja2 to manage prompt templates
            depend=depend,  # use jinja2 to manage prompt templates
            file=file,  # use jinja2 to manage prompt templates
            path=path,  # use jinja2 to manage prompt templates
            handler=handler  # use jinja2 to manage prompt templates
        ).strip()

        usr_msg = prompt.render(
            role='usr',
            files=context.get_files(),  # use jinja2 to manage prompt templates
            plang=plang,  # use jinja2 to manage prompt templates
            frame=frame,  # use jinja2 to manage prompt templates
            depend=depend,  # use jinja2 to manage prompt templates
            file=file,  # use jinja2 to manage prompt templates
            path=path,  # use jinja2 to manage prompt templates
            handler=handler  # use jinja2 to manage prompt templates
        ).strip()

        result = await Agent(
            system_message=sys_msg,
            model=worker_model,
            output_schema=EndpointMethodExtractResult,
            parser_model=parser_model,
            add_datetime_to_context=False,
            add_location_to_context=False,
            add_name_to_context=False,
            **(extra or {})
        ).arun(usr_msg)

        checker = lambda: EndpointMethodExtractAgent.Bean.verify(result.content)

        convert = lambda: EndpointMethodExtractAgent.Bean.wakeup(result.content)

        return convert() if checker() else None
