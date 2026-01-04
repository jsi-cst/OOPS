from core.shared import FileHandler

from core.libraries import *

from core.constants import *

with open(f'{os.path.dirname(__file__)}/prompt.jinja', 'r', encoding='utf-8') as __file:
    prompt: jinja2.Template = jinja2.Template(__file.read())


class FileDependencyAnalyzeResult(BaseModel, frozen=True):

    files: list[str] = Field(description='List of paths to the files that contain the handler implementations.')


class FileDependencyAnalyzeRefine(BaseModel, frozen=True):

    files: list[str] = Field(description='List of paths to the files that contain the handler implementations.')


class FileDependencyAnalyzeAgent:

    class Bean(BaseModel, frozen=True):

        files: set[str]

        @staticmethod
        def wakeup(that: Any) -> 'FileDependencyAnalyzeAgent.Bean':

            if that is None:
                raise RuntimeError()

            if isinstance(that, FileDependencyAnalyzeResult):
                return FileDependencyAnalyzeAgent.Bean(files=that.files)

            if isinstance(that, FileDependencyAnalyzeRefine):
                return FileDependencyAnalyzeAgent.Bean(files=that.files)

            raise RuntimeError()

        @staticmethod
        def verify(that: Any) -> bool:

            if that is None:
                return False

            if isinstance(that, FileDependencyAnalyzeResult):
                return all(os.path.normpath(i) for i in that.files)

            if isinstance(that, FileDependencyAnalyzeRefine):
                return all(os.path.normpath(i) for i in that.files)

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
        paths: list[str],  # for prompt template render
        handlers: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['FileDependencyAnalyzeAgent.Bean']]:

        parameters = [i for i in inspect.signature(FileDependencyAnalyzeAgent.__batch_run).parameters if isinstance(locals()[i], list)]

        plangs = [plangs for _ in files] if isinstance(plangs, str) else plangs

        frames = [frames for _ in files] if isinstance(frames, str) else frames

        assert len({len(locals()[i]) for i in parameters}) == 1  # require all same length

        # ------------------------------------------------

        async def solve(semaphore: asyncio.Semaphore, *args: Any) -> None:  # wrap semaphore

            # args: use fixed order of parameters for simplicity

            # args: use fixed order of parameters for simplicity

            async with semaphore:

                return await FileDependencyAnalyzeAgent.run(context, worker_model, parser_model, *args, extra)

        # ------------------------------------------------

        semaphore = asyncio.Semaphore(LLM_BATCH_SEMAPHORE)

        # limit concurrent connections to prevent risk controls

        # limit concurrent connections to prevent risk controls

        return await asyncio.gather(*[solve(semaphore, *args) for args in zip(
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
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
        files: list[str],  # for prompt template render
        paths: list[str],  # for prompt template render
        handlers: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['FileDependencyAnalyzeAgent.Bean']]:

        return await FileDependencyAnalyzeAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
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
        files: list[str],  # for prompt template render
        paths: list[str],  # for prompt template render
        handlers: list[str],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['FileDependencyAnalyzeAgent.Bean']]:

        return await FileDependencyAnalyzeAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
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
        file: str,  # for prompt template render
        path: str,  # for prompt template render
        handler: str,  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> Optional['FileDependencyAnalyzeAgent.Bean']:

        files, retries = context.get_files(), LLM_CORR_MAX_RETRIES

        output = None  # do self refine for incorrect relative paths

        errors = None  # do self refine for incorrect relative paths

        while retries and (output is None or errors):

            sys_msg = prompt.render(
                role='sys',
                files=files,  # use jinja2 to manage prompt templates
                plang=plang,  # use jinja2 to manage prompt templates
                frame=frame,  # use jinja2 to manage prompt templates
                output=output,  # use jinja2 to manage prompt templates
                errors=errors,  # use jinja2 to manage prompt templates
                file=file,  # use jinja2 to manage prompt templates
                path=path,  # use jinja2 to manage prompt templates
                handler=handler  # use jinja2 to manage prompt templates
            ).strip()

            usr_msg = prompt.render(
                role='usr',
                files=files,  # use jinja2 to manage prompt templates
                plang=plang,  # use jinja2 to manage prompt templates
                frame=frame,  # use jinja2 to manage prompt templates
                output=output,  # use jinja2 to manage prompt templates
                errors=errors,  # use jinja2 to manage prompt templates
                file=file,  # use jinja2 to manage prompt templates
                path=path,  # use jinja2 to manage prompt templates
                handler=handler  # use jinja2 to manage prompt templates
            ).strip()

            result = await Agent(
                system_message=sys_msg,
                model=worker_model,
                output_schema=FileDependencyAnalyzeResult,
                parser_model=parser_model,
                add_datetime_to_context=False,
                add_location_to_context=False,
                add_name_to_context=False,
                tool_call_limit=LLM_TOOL_CALL_MAX_ITERATE,
                tools=[context], **(extra or {})
            ).arun(usr_msg)

            retries, output = retries - 1, sorted({os.path.normpath(i) for i in getattr(result.content, 'files')})

            errors = [i for i in output if i not in files]  # filter outputs using whitelist

            errors = [i for i in output if i not in files]  # filter outputs using whitelist

        rebuild = FileDependencyAnalyzeResult(files={i for i in output if i in files and i != file})

        checker = lambda: FileDependencyAnalyzeAgent.Bean.verify(rebuild)

        convert = lambda: FileDependencyAnalyzeAgent.Bean.wakeup(rebuild)

        return convert() if checker() else None
