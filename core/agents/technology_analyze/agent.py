from core.shared import FileHandler

from core.libraries import *

from core.constants import *

with open(f'{os.path.dirname(__file__)}/prompt.jinja', 'r', encoding='utf-8') as __file:
    prompt: jinja2.Template = jinja2.Template(__file.read())


class TechnologyAnalyzeResult(BaseModel, frozen=True):
    language: str = Field(description='The primary programming language of this project.')
    framework: str = Field(description='The primary development framework of this project.')


class TechnologyAnalyzeRefine(BaseModel, frozen=True):
    language: str = Field(description='The primary programming language of this project.')
    framework: str = Field(description='The primary development framework of this project.')


class TechnologyAnalyzeAgent:

    class Bean(BaseModel, frozen=True):

        plang: str
        frame: str

        @staticmethod
        def wakeup(that: Any) -> 'TechnologyAnalyzeAgent.Bean':

            if that is None:
                raise RuntimeError()

            if isinstance(that, TechnologyAnalyzeResult):
                return TechnologyAnalyzeAgent.Bean(plang=that.language, frame=that.framework)

            if isinstance(that, TechnologyAnalyzeRefine):
                return TechnologyAnalyzeAgent.Bean(plang=that.language, frame=that.framework)

            raise RuntimeError()

        @staticmethod
        def verify(that: Any) -> bool:

            if that is None:
                return False

            if isinstance(that, TechnologyAnalyzeResult):
                return bool(that.language and that.framework)

            if isinstance(that, TechnologyAnalyzeRefine):
                return bool(that.language and that.framework)

            return False

    # ------------------------------------------------

    @staticmethod
    async def batch_run_full(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        extra: dict[str, Any] | None = None  # all the same
    ) -> list[Optional['TechnologyAnalyzeAgent.Bean']]:

        assert context or worker_model or extra

        assert context or parser_model or extra

        raise RuntimeError('Method is not implemented')

    @staticmethod
    async def batch_run_lite(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        extra: dict[str, Any] | None = None  # all the same
    ) -> list[Optional['TechnologyAnalyzeAgent.Bean']]:

        assert context or worker_model or extra

        assert context or parser_model or extra

        raise RuntimeError('Method is not implemented')

    @staticmethod
    async def run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        extra: dict[str, Any] | None = None  # kwargs
    ) -> Optional['TechnologyAnalyzeAgent.Bean']:

        info = context.run_command('ls')['stdout'].strip()

        sys_msg = prompt.render(role='sys', mode='backend', info=info).strip()

        usr_msg = prompt.render(role='usr', mode='backend', info=info).strip()

        result = await Agent(
            system_message=sys_msg,
            model=worker_model,
            output_schema=TechnologyAnalyzeResult,
            parser_model=parser_model,
            add_datetime_to_context=False,
            add_location_to_context=False,
            add_name_to_context=False,
            tool_call_limit=LLM_TOOL_CALL_MAX_ITERATE,
            tools=[context], **(extra or {})
        ).arun(usr_msg)

        checker = lambda: TechnologyAnalyzeAgent.Bean.verify(result.content)

        convert = lambda: TechnologyAnalyzeAgent.Bean.wakeup(result.content)

        return convert() if checker() else None
