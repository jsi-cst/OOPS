from core.shared import FileHandler

from core.shared import normalize_path_params

from core.libraries import *

from core.constants import *

with open(f'{os.path.dirname(__file__)}/prompt.jinja', 'r', encoding='utf-8') as __file:
    prompt: jinja2.Template = jinja2.Template(__file.read())


class APIEntryDetectionResult(BaseModel, frozen=True):

    path: str | None = Field(description='The HTTP request path, which must begin with a forward slash (/) and have path parameters wrapped in curly braces ({}). Set this to null if it cannot be determined.')
    handler: str = Field(description='The function, class, class method, or object that handles the HTTP request. Use exactly "anonymous" to denote an anonymous implementation.')
    handler_in_same_file: bool = Field(description='Whether the handler\'s implementation is present in the same source code file, rather than being imported.')
    path_is_prefix: bool = Field(description='Whether the path string is a prefix rather than a full path.')
    path_from_string_literal: bool = Field(description='Whether the path string is extracted from a literal string defined in the source code.')
    path_from_naming_convention: bool = Field(description='Whether the path string is derived from a naming convention supported by the framework.')
    is_restful_api: bool = Field(description='Whether the API entry is for a RESTful API, rather than other types of APIs.')
    is_testing_purposes: bool = Field(description='Whether the API entry is intended for testing purposes, such as unit tests or functional tests.')


class APIEntryDetectionRefine(BaseModel, frozen=True):

    path: str | None = Field(description='The HTTP request path, which must begin with a forward slash (/) and have path parameters wrapped in curly braces ({}). Set this to null if it cannot be determined.')
    handler: str = Field(description='The function, class, class method, or object that handles the HTTP request. Use exactly "anonymous" to denote an anonymous implementation.')
    handler_in_same_file: bool = Field(description='Whether the handler\'s implementation is present in the same source code file, rather than being imported.')
    path_is_prefix: bool = Field(description='Whether the path string is a prefix rather than a full path.')
    path_from_string_literal: bool = Field(description='Whether the path string is extracted from a literal string defined in the source code.')
    path_from_naming_convention: bool = Field(description='Whether the path string is derived from a naming convention supported by the framework.')
    is_restful_api: bool = Field(description='Whether the API entry is for a RESTful API, rather than other types of APIs.')
    is_testing_purposes: bool = Field(description='Whether the API entry is intended for testing purposes, such as unit tests or functional tests.')


class APIEntryDetectionResultList(BaseModel, frozen=True):

    # agno does not support list[BaseModel], wrap it

    # agno does not support list[BaseModel], wrap it

    entry: list[APIEntryDetectionResult] = Field(description='List of API entries you found.')


class APIEntryDetectionRefineList(BaseModel, frozen=True):

    # agno does not support list[BaseModel], wrap it

    # agno does not support list[BaseModel], wrap it

    entry: list[APIEntryDetectionRefine] = Field(description='List of API entries you found.')


class FileFilterStatus(BaseModel, frozen=True):

    # add a pre-filtering stage to reduce token cost

    # add a pre-filtering stage to reduce token cost

    contains_api_entries: bool = Field(description='Whether it is possible for this file to contain definitions of REST API endpoints.')

    reason: str = Field(description='The reason for this judgment.')


class APIEntryDetectionAgent:

    class Bean(BaseModel, frozen=True):

        path: str
        feat: str
        handler: str
        tag: str

        @staticmethod
        def wakeup(that: Any) -> 'APIEntryDetectionAgent.Bean':

            if that is None:
                raise RuntimeError()

            if isinstance(that, APIEntryDetectionResult):
                tag = 'local' if that.handler_in_same_file or that.handler.lower().strip() == 'anonymous' else 'ref'
                return APIEntryDetectionAgent.Bean(**normalize_path_params(that.path), handler=that.handler, tag=tag)

            if isinstance(that, APIEntryDetectionRefine):
                tag = 'local' if that.handler_in_same_file or that.handler.lower().strip() == 'anonymous' else 'ref'
                return APIEntryDetectionAgent.Bean(**normalize_path_params(that.path), handler=that.handler, tag=tag)

            raise RuntimeError()

        @staticmethod
        def verify(that: Any) -> bool:

            if that is None:
                return False

            if isinstance(that, APIEntryDetectionResult):
                valid_path = that.path is not None and (that.path_from_string_literal or that.path_from_naming_convention)
                return valid_path and (that.path_is_prefix or that.is_restful_api) and not that.is_testing_purposes

            if isinstance(that, APIEntryDetectionRefine):
                valid_path = that.path is not None and (that.path_from_string_literal or that.path_from_naming_convention)
                return valid_path and (that.path_is_prefix or that.is_restful_api) and not that.is_testing_purposes

            return False

    # ------------------------------------------------

    @staticmethod
    async def __batch_run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str] | str,  # same value if is str
        frames: list[str] | str,  # same value if is str
        files: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[list['APIEntryDetectionAgent.Bean']]:

        parameters = [i for i in inspect.signature(APIEntryDetectionAgent.__batch_run).parameters if isinstance(locals()[i], list)]

        plangs = [plangs for _ in files] if isinstance(plangs, str) else plangs

        frames = [frames for _ in files] if isinstance(frames, str) else frames

        assert len({len(locals()[i]) for i in parameters}) == 1  # require all same length

        # ------------------------------------------------

        async def solve(semaphore: asyncio.Semaphore, *args: Any) -> None:  # wrap semaphore

            # args: use fixed order of parameters for simplicity

            # args: use fixed order of parameters for simplicity

            async with semaphore:

                return await APIEntryDetectionAgent.run(context, worker_model, parser_model, *args, extra)

        # ------------------------------------------------

        semaphore = asyncio.Semaphore(LLM_BATCH_SEMAPHORE)

        # limit concurrent connections to prevent risk controls

        # limit concurrent connections to prevent risk controls

        return await asyncio.gather(*[solve(semaphore, *args) for args in zip(
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            files  # add a comment to disable yapf format
        )])

    @staticmethod
    async def batch_run_full(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str],  # for prompt template render
        frames: list[str],  # for prompt template render
        files: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[list['APIEntryDetectionAgent.Bean']]:

        return await APIEntryDetectionAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            files,  # add a comment to disable yapf format
            extra  # add a comment to disable yapf format
        )

    @staticmethod
    async def batch_run_lite(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: str,  # use same value for each llm call
        frames: str,  # use same value for each llm call
        files: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[list['APIEntryDetectionAgent.Bean']]:

        return await APIEntryDetectionAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            files,  # add a comment to disable yapf format
            extra  # add a comment to disable yapf format
        )

    @staticmethod
    async def run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plang: str,  # for prompt template render
        frame: str,  # for prompt template render
        file: str,  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list['APIEntryDetectionAgent.Bean']:

        entries: list[APIEntryDetectionResult] = []

        prep_sys_msg = prompt.render(role='sys-prep', plang=plang, frame=frame, file=file).strip()

        prep_usr_msg = prompt.render(role='usr-prep', plang=plang, frame=frame, file=file).strip()

        result = await Agent(
            system_message=prep_sys_msg,
            model=worker_model,
            output_schema=FileFilterStatus,
            add_datetime_to_context=False,
            add_location_to_context=False,
            add_name_to_context=False,
            **(extra or {})
        ).arun(prep_usr_msg)

        if FileFilterStatus.model_validate(result.content).contains_api_entries:

            files, retries = context.get_files(), LLM_CORR_MAX_RETRIES

            unique = set()  # do self refine for incomplete output

            extend = set()  # do self refine for incomplete output

            while retries and (isinstance(extend, set) or extend):

                loop_sys_msg = prompt.render(
                    role='sys-loop',
                    files=files,  # use jinja2 to manage prompt templates
                    plang=plang,  # use jinja2 to manage prompt templates
                    frame=frame,  # use jinja2 to manage prompt templates
                    entries=[i.model_dump_json(ensure_ascii=False) for i in entries],
                    file=file  # use jinja2 to manage prompt templates
                ).strip()

                loop_usr_msg = prompt.render(
                    role='usr-loop',
                    files=files,  # use jinja2 to manage prompt templates
                    plang=plang,  # use jinja2 to manage prompt templates
                    frame=frame,  # use jinja2 to manage prompt templates
                    entries=[i.model_dump_json(ensure_ascii=False) for i in entries],
                    file=file  # use jinja2 to manage prompt templates
                ).strip()

                result = await Agent(
                    system_message=loop_sys_msg,
                    model=worker_model,
                    output_schema=APIEntryDetectionResultList,
                    parser_model=parser_model,
                    add_datetime_to_context=False,
                    add_location_to_context=False,
                    add_name_to_context=False,
                    **(extra or {})
                ).arun(loop_usr_msg)

                retries, extend = retries - 1, False

                for i in APIEntryDetectionResultList.model_validate(result.content).entry:

                    feature = normalize_path_params(i.path)['feat']

                    # if an undiscovered entry point is found, continue iterating

                    # if an undiscovered entry point is found, continue iterating

                    if (feature, i.handler) not in unique:

                        extend = unique.add(entries.append(i) or (feature, i.handler)) or True

        checker = lambda x: APIEntryDetectionAgent.Bean.verify(x)

        convert = lambda x: APIEntryDetectionAgent.Bean.wakeup(x)

        return [convert(i) for i in entries if checker(i)]
