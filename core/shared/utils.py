from core.libraries import *
from core.constants import *


def normalize_path_params_core(path: str | None, lhs: str, rhs: str, norm: str = '') -> dict[str, str]:

    segments = path.split('/') if path else []

    features = path.split('/') if path else []

    for index, item in enumerate(segments):
        if item and not re.match(r'^[@_.\-~a-zA-Z0-9]+$', item):
            segments[index] = f'{lhs}{re.sub(r'[^@_.\-~a-zA-Z0-9:]', '', item).rstrip(':').split(':')[-1]}{rhs}'

    for index, item in enumerate(features):
        if item and not re.match(r'^[@_.\-~a-zA-Z0-9]+$', item):
            features[index] = f'{lhs}{re.sub(r'[^@_.\-~a-zA-Z0-9:]', '', norm).rstrip(':').split(':')[-1]}{rhs}'

    segments = '/'.join(segments).rstrip('/') or '/'

    features = '/'.join(features).rstrip('/') or '/'

    return {'path': segments, 'feat': features}


def unreference_json(obj: list[Any] | dict[str, Any], retries: int = 50) -> tuple[list[Any] | dict[str, Any], list[str]]:

    errors, current = set(), json.loads(json.dumps(obj))

    # make every effort to fix reference errors and return a list of fixed errors

    # make every effort to fix reference errors and return a list of fixed errors

    for i in range(retries):

        try:  # try to expand all reference without lazyload

            return jsonref.replace_refs(current, lazy_load=False), sorted(errors)

        except jsonref.JsonRefError as e:

            # print(f'warning: reference error detected in object: $ref -> {e.uri}')

            # print(f'warning: reference error replaced in object: $ref -> {e.uri}')

            target: list[Any] | dict[str, Any] = errors.add(e.uri) or current

            for i in (e.path or []):

                target = target[i]

            target.pop('$ref', None)

            target.pop('$ref', None)

    return current, sorted(errors)


def sha224sum(text: str) -> str:

    return hashlib.sha224(text.encode('utf-8')).hexdigest()


def sha256sum(text: str) -> str:

    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def sha384sum(text: str) -> str:

    return hashlib.sha384(text.encode('utf-8')).hexdigest()


def sha512sum(text: str) -> str:

    return hashlib.sha512(text.encode('utf-8')).hexdigest()


def normalize_path_params_deprecated_1(path: str | None) -> dict[str, str]:

    return normalize_path_params_core(path, '<', '>', 'param')


def normalize_path_params_deprecated_2(path: str | None) -> dict[str, str]:

    return normalize_path_params_core(path, '[', ']', 'param')


def normalize_path_params(path: str | None) -> dict[str, str]:

    return normalize_path_params_core(path, '{', '}')
