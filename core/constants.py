OAS_UPGRADE_CODEGEN: str = 'codegen-3.0.68.jar'

LLM_HTTP_MAX_RETRIES: int = 2

LLM_CORR_MAX_RETRIES: int = 5

LLM_TOOL_CALL_MAX_ITERATE: int = 10

LLM_TOOL_CALL_MAX_TIMEOUT: int = 10

LLM_HTTP_MAX_TIMEOUT: int = 2 * 60

LLM_HTTP_HTTP1: bool = bool(1)

LLM_HTTP_HTTP2: bool = bool(0)

LLM_HTTP_VERIFY: bool | None = False

LLM_HTTP_PROXY: str | None = 'http://192.168.126.1:2222'

LLM_HTTP_PROXY: str | None = 'http://192.168.126.1:8888'

LLM_BATCH_SEMAPHORE: int = 16

FILE_MIN_SIZE: int = 0 * 1024 * 1024  # exclusive

FILE_MAX_SIZE: int = 2 * 1024 * 1024  # exclusive

FILE_IGNORE_PATTERNS: list[str] = [

    '\\.sass$',
    '\\.scss$',
    '\\.less$',

    '\\.md$',
    '\\.sh$',

    '\\.bat$',
    '\\.css$',
    '\\.sql$',
    '\\.svg$',
    '\\.txt$',

    '^dockerfile$',
    '^docker-compose\\.yaml$',
    '^procfile$',
    '^makefile$',
    '^vagrantfile$',
    '^license$',

    '/dockerfile$',
    '/docker-compose\\.yaml$',
    '/procfile$',
    '/makefile$',
    '/vagrantfile$',
    '/license$',

    '^yarn\\.lock$',
    '^package-lock\\.json$',
    '^gemfile\\.lock$',
    '^pipfile\\.lock$',
    '^composer\\.lock$',
    '^go\\.sum$',

    '/yarn\\.lock$',
    '/package-lock\\.json$',
    '/gemfile\\.lock$',
    '/pipfile\\.lock$',
    '/composer\\.lock$',
    '/go\\.sum$',

    '^\\.__pycache__/',
    '^\\.__generated__/',
    '^\\.__snapshots__/',
    '^\\.vscode/',
    '^\\.github/',
    '^\\.gitlab/',
    '^\\.git/',

    '/\\.__pycache__/',
    '/\\.__generated__/',
    '/\\.__snapshots__/',
    '/\\.vscode/',
    '/\\.github/',
    '/\\.gitlab/',
    '/\\.git/',

    '\\.gitignore$',
    '\\.gitattributes$',
    '\\.prettierrc$',
    '\\.prettierignore$',
    '\\.eslintignore$',
    '\\.dockerignore$',
    '\\.editorconfig$',
    '\\.browserslistrc$',
    '\\.gitkeep$',
    '\\.htaccess$',
    '\\.keep$'
]
