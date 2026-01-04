from expr.utils import *


def normalize_url(url: str) -> tuple[str, str, dict[str, str]]:

    mapper = {}  # old -> new

    std = url.rstrip('/').split('/')

    raw = url.rstrip('/').split('/')

    for k, v in enumerate(std):

        if v.startswith('{') and v.endswith('}'):

            v_map = f'param{len(mapper) + 1}'

            v_std = f'param{len(mapper) + 1}'

            std[k], mapper[v[1:-1]] = '{' + v_map + '}', v_std

    std = '/'.join(std) or '/'

    raw = '/'.join(raw) or '/'

    return mapper, std, raw


def update_oas_3_0(specification: str, result: list[OperationBean]) -> Exception | None:

    try:  # accept oas version 3.0.x and oas version 3.1.x

        model = OASv3_0.OpenAPI.model_validate(jsonref.replace_refs(json.loads(specification)))

        for k, v in model.paths.items():

            extract = normalize_url(k)

            result.extend([OperationBean.load_operation(*extract, 'HEAD', v.parameters, v.head)] if v.head else [])

            result.extend([OperationBean.load_operation(*extract, 'POST', v.parameters, v.post)] if v.post else [])

            result.extend([OperationBean.load_operation(*extract, 'OPTIONS', v.parameters, v.options)] if v.options else [])

            result.extend([OperationBean.load_operation(*extract, 'TRACE', v.parameters, v.trace)] if v.trace else [])

            result.extend([OperationBean.load_operation(*extract, 'GET', v.parameters, v.get)] if v.get else [])

            result.extend([OperationBean.load_operation(*extract, 'PUT', v.parameters, v.put)] if v.put else [])

            result.extend([OperationBean.load_operation(*extract, 'DELETE', v.parameters, v.delete)] if v.delete else [])

            result.extend([OperationBean.load_operation(*extract, 'PATCH', v.parameters, v.patch)] if v.patch else [])

    except Exception as e:

        return e


def update_oas_3_1(specification: str, result: list[OperationBean]) -> Exception | None:

    try:  # accept oas version 3.0.x and oas version 3.1.x

        model = OASv3_1.OpenAPI.model_validate(jsonref.replace_refs(json.loads(specification)))

        for k, v in model.paths.items():

            extract = normalize_url(k)

            result.extend([OperationBean.load_operation(*extract, 'HEAD', v.parameters, v.head)] if v.head else [])

            result.extend([OperationBean.load_operation(*extract, 'POST', v.parameters, v.post)] if v.post else [])

            result.extend([OperationBean.load_operation(*extract, 'OPTIONS', v.parameters, v.options)] if v.options else [])

            result.extend([OperationBean.load_operation(*extract, 'TRACE', v.parameters, v.trace)] if v.trace else [])

            result.extend([OperationBean.load_operation(*extract, 'GET', v.parameters, v.get)] if v.get else [])

            result.extend([OperationBean.load_operation(*extract, 'PUT', v.parameters, v.put)] if v.put else [])

            result.extend([OperationBean.load_operation(*extract, 'DELETE', v.parameters, v.delete)] if v.delete else [])

            result.extend([OperationBean.load_operation(*extract, 'PATCH', v.parameters, v.patch)] if v.patch else [])

    except Exception as e:

        return e


def load_specification(oas: str) -> list[OperationBean]:

    result = []  # flattened operation

    exception1 = update_oas_3_0(oas, result)

    exception2 = update_oas_3_1(oas, result)

    if exception1 and exception2:

        print('failed to load oas string')

        print(f'try oas 3.0.x:\n{exception1}')

        print(f'try oas 3.1.x:\n{exception2}')

    return [i for i in result if i]
