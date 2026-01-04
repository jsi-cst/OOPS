from core.libraries import *
from core.constants import *


class LLMFactory:

    __model_name: str

    __system_role: str

    __api_url: str

    __api_key: str

    __headers: dict[str, Any] | None

    __cookies: dict[str, Any] | None

    __params: dict[str, Any] | None

    __temperature: float

    __timeout: int

    def __init__(
        self: Self,
        model_name: str,
        system_role: str | None = None,
        api_url: str | None = None,
        api_key: str | None = None,
        headers: dict[str, Any] | None = None,
        cookies: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        temperature: float | None = None,
        timeout: int | None = None
    ):
        self.__model_name = model_name.strip()
        self.__api_url = api_url or os.getenv('LLM_API_URL')
        self.__api_key = api_key or os.getenv('LLM_API_KEY')
        self.__headers = headers if headers else None
        self.__cookies = cookies if cookies else None
        self.__params = params if params else None

        assert self.__api_url  # required with environ
        assert self.__api_key  # required with environ
        self.__timeout = timeout or LLM_HTTP_MAX_TIMEOUT
        self.__temperature = temperature or 0.0
        self.__system_role = system_role or (
            'developer' if 'gpt' in self.__model_name.lower() else
            'developer' if 'o1-' in self.__model_name.lower() else
            'developer' if 'o3-' in self.__model_name.lower() else
            'system'  # other models using OpenAI interface
        )

    def extent_headers(self: Self, kwargs: dict[str, Any]) -> None:

        self.__headers = self.__headers or {}
        self.__headers.update(kwargs)

    def extent_cookies(self: Self, kwargs: dict[str, Any]) -> None:

        self.__cookies = self.__cookies or {}
        self.__cookies.update(kwargs)

    def extent_params(self: Self, kwargs: dict[str, Any]) -> None:

        self.__params = self.__params or {}
        self.__params.update(kwargs)

    # ------------------------------------------------

    def build(self: Self, store: str) -> Model:

        async def log_response(response: httpx.Response) -> None:

            req, res, times, unique = response.request, response, int(time.time() * 1000), secrets.token_hex(16)

            req_payload = json.loads((await req.aread()).decode('utf-8'))

            res_payload = json.loads((await res.aread()).decode('utf-8'))

            with open(f'{store}/log-{times}-{response.status_code}-{unique}.json', 'w', encoding='utf-8') as file:

                record = {'timestamp': times, 'url': str(req.url), 'method': req.method, 'status': res.status_code}

                record['req'] = req_payload  # full log of llm call

                record['res'] = res_payload  # full log of llm call

                json.dump(record, file, indent=2, ensure_ascii=False)

        # ------------------------------------------------

        message_role_dict = {
            'system': self.__system_role,
            'user': 'user',
            'tool': 'tool',
            'assistant': 'assistant',
            'model': 'assistant'
        }

        # use developer for OpenAI, use system for other models using OpenAI interface

        # use developer for OpenAI, use system for other models using OpenAI interface

        return os.makedirs(store, exist_ok=True) or OpenAIChat(
            id=self.__model_name,
            base_url=self.__api_url,
            api_key=self.__api_key,
            temperature=self.__temperature,
            role_map=message_role_dict,
            max_retries=LLM_HTTP_MAX_RETRIES,
            retries=LLM_HTTP_MAX_RETRIES,
            http_client=httpx.AsyncClient(
                timeout=self.__timeout,
                headers=self.__headers,
                cookies=self.__cookies,
                params=self.__params,
                http1=LLM_HTTP_HTTP1,
                http2=LLM_HTTP_HTTP2,
                proxy=LLM_HTTP_PROXY,
                verify=LLM_HTTP_VERIFY,
                event_hooks={'response': [log_response]}
            )
        )

    def get_headers(self: Self) -> dict[str, Any] | None:

        return self.__headers

    def get_cookies(self: Self) -> dict[str, Any] | None:

        return self.__cookies

    def get_params(self: Self) -> dict[str, Any] | None:

        return self.__params

    def get_system_role(self: Self) -> str:

        return self.__system_role

    def get_model_name(self: Self) -> str:

        return self.__model_name
