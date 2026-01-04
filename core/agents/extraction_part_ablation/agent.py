from core.shared import FileHandler

from core.shared import normalize_path_params

from core.libraries import *

from core.constants import *

with open(f'{os.path.dirname(__file__)}/prompt.jinja', 'r', encoding='utf-8') as __file:
    prompt: jinja2.Template = jinja2.Template(__file.read())


class EndpointMethodExtractResult(BaseModel, frozen=True):

    path: str = Field(description='The full HTTP request path for the endpoint.')
    method: str = Field(description='The supported HTTP method for the endpoint.')


class EndpointMethodExtractRefine(BaseModel, frozen=True):

    path: str = Field(description='The full HTTP request path for the endpoint.')
    method: str = Field(description='The supported HTTP method for the endpoint.')


class EndpointMethodExtractResultList(BaseModel, frozen=True):

    # agno does not support list[BaseModel], wrap it

    # agno does not support list[BaseModel], wrap it

    items: list[EndpointMethodExtractResult] = Field(description='List of endpoint methods you found.')


class EndpointMethodExtractRefineList(BaseModel, frozen=True):

    # agno does not support list[BaseModel], wrap it

    # agno does not support list[BaseModel], wrap it

    items: list[EndpointMethodExtractRefine] = Field(description='List of endpoint methods you found.')


class ExtractionPartAblationAgent:

    class Bean(BaseModel, frozen=True):

        path: str
        feat: str
        method: str

        @staticmethod
        def wakeup(that: Any) -> 'ExtractionPartAblationAgent.Bean':

            if that is None:
                raise RuntimeError()

            if isinstance(that, EndpointMethodExtractResult):
                normalize, method = normalize_path_params(that.path), that.method
                return ExtractionPartAblationAgent.Bean(**normalize, method=method)

            if isinstance(that, EndpointMethodExtractRefine):
                normalize, method = normalize_path_params(that.path), that.method
                return ExtractionPartAblationAgent.Bean(**normalize, method=method)

            raise RuntimeError()

        @staticmethod
        def verify(that: Any) -> bool:

            if that is None:
                return False

            if isinstance(that, EndpointMethodExtractResult):
                valid = ('HEAD', 'POST', 'OPTIONS', 'TRACE', 'GET', 'PUT', 'DELETE', 'PATCH')
                return bool(that.path and that.method.upper() in valid)  # filter by method

            if isinstance(that, EndpointMethodExtractRefine):
                valid = ('HEAD', 'POST', 'OPTIONS', 'TRACE', 'GET', 'PUT', 'DELETE', 'PATCH')
                return bool(that.path and that.method.upper() in valid)  # filter by method

            return False

    # ------------------------------------------------

    @staticmethod
    async def batch_run_full(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str],  # for prompt template render
        frames: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[list['ExtractionPartAblationAgent.Bean']]:

        assert context or worker_model or plangs or extra

        assert context or parser_model or frames or extra

        raise RuntimeError('Method is not implemented')

    @staticmethod
    async def batch_run_lite(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: str,  # use same value for each llm call
        frames: str,  # use same value for each llm call
        extra: dict[str, Any] | None = None
    ) -> list[list['ExtractionPartAblationAgent.Bean']]:

        assert context or worker_model or plangs or extra

        assert context or parser_model or frames or extra

        raise RuntimeError('Method is not implemented')

    @staticmethod
    async def run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plang: str,  # for prompt template render
        frame: str,  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list['ExtractionPartAblationAgent.Bean']:

        info = context.run_command('ls')['stdout'].strip() or parser_model

        sys_msg = prompt.render(role='sys', plang=plang, frame=frame, info=info).strip()

        usr_msg = prompt.render(role='usr', plang=plang, frame=frame, info=info).strip()

        result = await Agent(
            system_message=sys_msg,
            model=worker_model,
            output_schema=EndpointMethodExtractResultList,
            # parser_model=worker_model,
            # parser_model=parser_model,
            add_datetime_to_context=False,
            add_location_to_context=False,
            add_name_to_context=False,
            tool_call_limit=LLM_TOOL_CALL_MAX_ITERATE,
            tools=[context], **(extra or {})
        ).arun(usr_msg)

        items = EndpointMethodExtractResultList.model_validate(result.content).items

        checker = lambda x: ExtractionPartAblationAgent.Bean.verify(x)

        convert = lambda x: ExtractionPartAblationAgent.Bean.wakeup(x)

        return [convert(i) for i in items if checker(i)]
