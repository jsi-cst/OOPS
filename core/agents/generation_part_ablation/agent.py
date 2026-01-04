from core.shared import FileHandler

from core.shared import unreference_json

from core.libraries import *

from core.constants import *

with open(f'{os.path.dirname(__file__)}/prompt.jinja', 'r', encoding='utf-8') as __file:
    prompt: jinja2.Template = jinja2.Template(__file.read())


class SwaggerGenerationResult(BaseModel, frozen=True):

    def __new__(cls: type[BaseModel]):

        # in contrast, use definitions in openapi-pydantic directly

        # in contrast, use definitions in openapi-pydantic directly

        raise RuntimeError('Customized model not used here')


class SwaggerGenerationRefine(BaseModel, frozen=True):

    def __new__(cls: type[BaseModel]):

        # in contrast, use definitions in openapi-pydantic directly

        # in contrast, use definitions in openapi-pydantic directly

        raise RuntimeError('Customized model not used here')


class GenerationPartAblationAgent:

    class Bean(BaseModel, frozen=True):

        # wrap for scalability

        # wrap for scalability

        operation: Operation

        @staticmethod
        def wakeup(outputs: list[Any]) -> 'GenerationPartAblationAgent.Bean':

            if any(i[0] is None for i in outputs):
                raise RuntimeError()  # rejected

            if any(i[1] is None for i in outputs):
                raise RuntimeError()  # rejected

            choices = sorted(outputs, key=lambda x: len(x[1]), reverse=False)

            return GenerationPartAblationAgent.Bean(operation=choices[0][0])

        @staticmethod
        def verify(outputs: list[Any]) -> bool:

            if not outputs:
                return False

            if any(i[0] is None for i in outputs):
                return False  # unable to sort

            if any(i[1] is None for i in outputs):
                return False  # unable to sort

            return True

    # ------------------------------------------------

    @staticmethod
    async def __batch_run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str] | str,  # same value if is str
        frames: list[str] | str,  # same value if is str
        apiurls: list[str],  # for prompt template render
        methods: list[str],  # for prompt template render
        depends: list[list[Any]],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['GenerationPartAblationAgent.Bean']]:

        parameters = [i for i in inspect.signature(GenerationPartAblationAgent.__batch_run).parameters if isinstance(locals()[i], list)]

        plangs = [plangs for _ in depends] if isinstance(plangs, str) else plangs

        frames = [frames for _ in depends] if isinstance(frames, str) else frames

        assert len({len(locals()[i]) for i in parameters}) == 1  # require all same length

        # ------------------------------------------------

        async def solve(semaphore: asyncio.Semaphore, *args: Any) -> None:  # wrap semaphore

            # args: use fixed order of parameters for simplicity

            # args: use fixed order of parameters for simplicity

            async with semaphore:

                return await GenerationPartAblationAgent.run(context, worker_model, parser_model, *args, extra)

        # ------------------------------------------------

        semaphore = asyncio.Semaphore(LLM_BATCH_SEMAPHORE)

        # limit concurrent connections to prevent risk controls

        # limit concurrent connections to prevent risk controls

        return await asyncio.gather(*[solve(semaphore, *args) for args in zip(
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            apiurls,  # add a comment to disable yapf format
            methods,  # add a comment to disable yapf format
            depends  # add a comment to disable yapf format
        )])

    @staticmethod
    async def batch_run_full(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: list[str],  # for prompt template render
        frames: list[str],  # for prompt template render
        apiurls: list[str],  # for prompt template render
        methods: list[str],  # for prompt template render
        depends: list[list[Any]],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['GenerationPartAblationAgent.Bean']]:

        return await GenerationPartAblationAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            apiurls,  # add a comment to disable yapf format
            methods,  # add a comment to disable yapf format
            depends,  # add a comment to disable yapf format
            extra  # add a comment to disable yapf format
        )

    @staticmethod
    async def batch_run_lite(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plangs: str,  # use same value for each llm call
        frames: str,  # use same value for each llm call
        apiurls: list[str],  # for prompt template render
        methods: list[str],  # for prompt template render
        depends: list[list[Any]],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> list[Optional['GenerationPartAblationAgent.Bean']]:

        return await GenerationPartAblationAgent.__batch_run(
            context,  # add a comment to disable yapf format
            worker_model,  # add a comment to disable yapf format
            parser_model,  # add a comment to disable yapf format
            plangs,  # add a comment to disable yapf format
            frames,  # add a comment to disable yapf format
            apiurls,  # add a comment to disable yapf format
            methods,  # add a comment to disable yapf format
            depends,  # add a comment to disable yapf format
            extra  # add a comment to disable yapf format
        )

    @staticmethod
    async def run(
        context: FileHandler,
        worker_model: Model,
        parser_model: Model,
        plang: str,  # for prompt template render
        frame: str,  # for prompt template render
        apiurl: str,  # for prompt template render
        method: str,  # for prompt template render
        depend: list[Any],  # for prompt template render
        extra: dict[str, Any] | None = None
    ) -> Optional['GenerationPartAblationAgent.Bean']:

        files, retries, outputs = context.get_files(), LLM_CORR_MAX_RETRIES >> 1, []

        sys_msg = prompt.render(
            role='sys',
            files=files,  # use jinja2 to manage prompt templates
            plang=plang,  # use jinja2 to manage prompt templates
            frame=frame,  # use jinja2 to manage prompt templates
            apiurl=apiurl,  # use jinja2 to manage prompt templates
            method=method,  # use jinja2 to manage prompt templates
            depend=depend  # use jinja2 to manage prompt templates
        ).strip()

        usr_msg = prompt.render(
            role='usr',
            files=files,  # use jinja2 to manage prompt templates
            plang=plang,  # use jinja2 to manage prompt templates
            frame=frame,  # use jinja2 to manage prompt templates
            apiurl=apiurl,  # use jinja2 to manage prompt templates
            method=method,  # use jinja2 to manage prompt templates
            depend=depend  # use jinja2 to manage prompt templates
        ).strip()

        while retries and (not outputs or len(outputs[-1][1])):

            # if no errors occur during a generation, return directly

            # if no errors occur during a generation, return directly

            try:  # catch all exceptions

                result = await Agent(
                    system_message=sys_msg,
                    model=worker_model or parser_model,
                    # parser_model=worker_model,
                    # parser_model=parser_model,
                    add_datetime_to_context=False,
                    add_location_to_context=False,
                    add_name_to_context=False,
                    tool_call_limit=LLM_TOOL_CALL_MAX_ITERATE,
                    tools=[context], **(extra or {})
                ).arun(usr_msg)

                payload = str(result.content).rsplit('generated result begins', maxsplit=1)[-1]

                retries, unref = retries - 1, unreference_json(json.loads(payload))

                assert unref[0] is not None  # object -> repair

                assert unref[1] is not None  # object -> errors

                outputs.append((Operation.model_validate(unref[0]), unref[1]))

            except Exception as e:  # return output with the fewest errors

                print(f'failed to generate Operation object due to: {type(e)}')

                print(f'failed to generate Operation object due to: {type(e)}')

                print(f'failed to generate Operation object due to: {type(e)}')

        checker = lambda: GenerationPartAblationAgent.Bean.verify(outputs)

        convert = lambda: GenerationPartAblationAgent.Bean.wakeup(outputs)

        return convert() if checker() else None
