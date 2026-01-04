from core.libraries import *
from core.constants import *


class OASBuilder:

    __payload: dict[str, str | dict[str, Any]]

    __spec_version: str

    __temp_upgrade: str

    __apidoc: OpenAPI | None

    def __init__(self: Self, title: str, upgrade: str, version: str):

        self.__spec_version = version  # use https://github.com/swagger-api/swagger-codegen for version upgrade

        self.__temp_upgrade = upgrade  # use https://github.com/swagger-api/swagger-codegen for version upgrade

        self.__payload = {'swagger': '2.0', 'info': {'title': title, 'version': version}, 'paths': {}}

    def get_spec_version(self: Self) -> str:

        return self.__spec_version

    def get_temp_upgrade(self: Self) -> str:

        return self.__temp_upgrade

    def emplace_apidoc(self: Self, apiurl: str, method: str, req: Any, res: Any) -> None:

        req_buf = []  # search the outermost key for nested object

        res_buf = []  # search the outermost key for nested object

        def search_obj(obj: Any, clz: Any, key: str, buf: list[tuple[int, Any]], level: int = 0) -> None:

            if isinstance(obj, dict):

                buf.extend((level, v) for k, v in obj.items() if k == key and isinstance(v, clz))

                # search sub dict by key

                # search sub dict by key

                for i in obj.values():

                    search_obj(i, clz, key, buf, level + 1)

        # ------------------------------------------------

        req_key, res_key, fields = 'parameters', 'responses', {'name', 'in', 'description', 'required', 'schema'}

        req_buf = search_obj(req, list, req_key, req_buf) or sorted(req_buf, key=lambda x: x[0])

        res_buf = search_obj(res, dict, res_key, res_buf) or sorted(res_buf, key=lambda x: x[0])

        req_obj: list[dict[str, Any]] | dict[str, dict[str, Any]] = req_buf[0][1] if req_buf else req

        res_obj: list[dict[str, Any]] | dict[str, dict[str, Any]] = res_buf[0][1] if res_buf else res

        if not isinstance(req_obj, list):

            return print(f'failed to parse req: not list\n{req}')

        if not isinstance(res_obj, dict):

            return print(f'failed to parse res: not dict\n{res}')

        if len(req_obj) < 0:  # accept

            return print('failed to parse req: empty object')

        if len(res_obj) < 1:  # reject

            return print('failed to parse res: empty object')

        if 'html' in json.dumps(req_obj).lower():

            return print(f'failed to parse req: not REST\n{req}')

        if 'html' in json.dumps(res_obj).lower():

            return print(f'failed to parse res: not REST\n{res}')

        # ------------------------------------------------

        if all(not i.startswith('2') for i in res_obj):

            return print(f'failed to parse res: no success\n{res}')

        if all(not i.startswith('2') for i in res_obj):

            return print(f'failed to parse res: no success\n{res}')

        def replace_type(obj: Any) -> None:

            for i in obj if isinstance(obj, (list, dict)) else []:

                if isinstance(obj, dict) and i == 'type' and obj[i] == 'file':
                    obj[i] = 'string'  # reset file to string, remain format

                elif isinstance(obj, dict) and i == 'type' and obj[i] == 'base16':
                    obj[i] = 'string'  # reset base16 to string, remain format

                elif isinstance(obj, dict) and i == 'type' and obj[i] == 'base32':
                    obj[i] = 'string'  # reset base32 to string, remain format

                elif isinstance(obj, dict) and i == 'type' and obj[i] == 'base64':
                    obj[i] = 'string'  # reset base64 to string, remain format

                elif isinstance(obj, dict) and i == 'type' and obj[i] == 'binary':
                    obj[i] = 'string'  # reset binary to string, remain format

                else:  # recursively process child elements in object
                    replace_type(i if isinstance(obj, list) else obj[i])

        def is_valid(response_code: str) -> bool:

            if response_code.startswith('x-'):
                return True

            if response_code.startswith('2'):
                return True

            if response_code.startswith('3'):
                return True

            if response_code.startswith('4'):
                return True

            if response_code.startswith('5'):
                return True

            return response_code == 'default'

        replace_type(req_obj)  # fix invalid type in JSON schema

        replace_type(res_obj)  # fix invalid type in JSON schema

        req_obj = [i for i in req_obj if isinstance(i, dict) and i.get('in') and i.get('name')]

        res_obj = {k: v for k, v in res_obj.items() if is_valid(k)}

        # ------------------------------------------------

        items = [i.lower() for i in apiurl.split('/') if i] + [method.lower()]

        items = (i.replace('{', '') for i in items)

        items = (i.replace('}', '') for i in items)

        opid = ''.join([v.capitalize() if k else v for k, v in enumerate(items)])

        for k, v in enumerate(req_obj):

            if v['in'] == 'body':

                include: dict[str, str | bool | dict[str, Any]] = {l: r for l, r in v.items() if (l in fields) == bool(1)}

                exclude: dict[str, str | bool | dict[str, Any]] = {l: r for l, r in v.items() if (l in fields) == bool(0)}

                include['schema'] = include.get('schema', {})

                for l, r in exclude.items():

                    # [
                    #   { "name": "username", "in": "body", "required": true, "type": "string" },
                    #   { "name": "password", "in": "body", "required": true, "type": "string" },
                    # ]
                    #
                    # [
                    #   {
                    #     "name": "body",
                    #     "in": "body",
                    #     "required": true,
                    #     "schema": {
                    #       "type": "object",
                    #       "properties": {
                    #         "username": { "type": "string" },
                    #         "password": { "type": "string" },
                    #       }
                    #     }
                    #   }
                    # ]

                    include['schema'][l] = include['schema'].get(l, r)

                req_obj[k] = include

        req_include_body = [i for i in req_obj if i['in'] == 'body']

        req_exclude_body = [i for i in req_obj if i['in'] != 'body']

        if req_include_body:

            description = chr(32).join([i['description'] for i in req_obj if i['in'] == 'body' and i.get('description')]).strip()

            merge = {'name': 'body', 'in': 'body', 'description': description, 'required': any(i.get('required', False) for i in req_include_body)}

            # merge = {'name': 'data', 'in': 'body', 'description': description, 'required': any(i.get('required', False) for i in req_include_body)}

            # merge = {'name': 'json', 'in': 'body', 'description': description, 'required': any(i.get('required', False) for i in req_include_body)}

            schema = {'type': 'object', 'properties': {i['name']: i['schema'] for i in req_include_body}} if len(req_include_body) != 1 else None

            req_obj = req_exclude_body + [{**merge, 'schema': schema or req_include_body[0]['schema']}]

        # ------------------------------------------------

        unique: dict[str, int] = {}

        from core.shared import sha256sum

        from core.shared import sha384sum

        for k, v in enumerate(req_obj):

            feature = json.dumps(v, sort_keys=True)

            k1 = sha256sum(feature)  # hash of a JSON object

            k2 = sha384sum(feature)  # hash of a JSON object

            unique[k1 + k2] = unique.get(k1 + k2, k)

        req_obj = [req_obj[i] for i in unique.values()]

        # ------------------------------------------------

        operation = {'operationId': opid}

        operation[req_key] = req_obj

        operation[res_key] = res_obj

        self.__payload['paths'][apiurl] = self.__payload['paths'].get(apiurl, {})

        self.__payload['paths'][apiurl][method.lower()] = operation

    # ------------------------------------------------

    def upgrade_apidoc(self: Self, silent: bool = False) -> None:

        base, dist = f'{self.__temp_upgrade}/upgrade', f'{self.__temp_upgrade}/upgrade/swagger.json'

        os.makedirs(base, exist_ok=True)  # require exists

        os.makedirs(base, exist_ok=True)  # require exists

        with open(f'{base}/swagger.json', 'w', encoding='utf-8') as file:

            json.dump(self.__payload, file, indent=2, ensure_ascii=False)

        # ------------------------------------------------

        command = ['java', '-jar', f'{os.path.dirname(__file__)}/{OAS_UPGRADE_CODEGEN}', 'generate', '-l', 'openapi']

        command.extend(('-i', os.path.abspath(dist)))

        command.extend(('-o', os.path.abspath(base)))

        result = subprocess.run(chr(32).join(command), cwd=f'{self.__temp_upgrade}/upgrade', check=False, timeout=60,
            stdout=subprocess.PIPE,  # collect output from stdout
            stderr=subprocess.PIPE,  # collect output from stderr
            shell=True, encoding='utf-8', env={'LANG': 'en_US.UTF-8'})

        assert not (not silent and print(result.stdout.strip()))

        assert not (not silent and print(result.stderr.strip()))

        with open(f'{base}/openapi.json', 'r', encoding='utf-8') as file:

            result = jsonref.replace_refs(json.load(file), lazy_load=False)

        # ------------------------------------------------

        # self.__apidoc = OpenAPI.model_validate({'openapi': '3.0.0', 'info': result['info'], 'paths': result['paths']})

        # self.__apidoc = OpenAPI.model_validate({'openapi': '3.0.4', 'info': result['info'], 'paths': result['paths']})

        self.__apidoc = OpenAPI.model_validate({'openapi': '3.1.0', 'info': result['info'], 'paths': result['paths']})

    def get_swagger_object(self: Self) -> OpenAPI:

        return self.__apidoc  # always use OpenAPI version 3.x.x

    def get_openapi_object(self: Self) -> OpenAPI:

        return self.__apidoc  # always use OpenAPI version 3.x.x

    def rebuild_apidoc(self: Self) -> None:

        from core.shared import sha256sum

        store: dict[str, Schema] = {}
        hlist: list[Header] = []
        plist: list[Parameter] = []
        mlist: list[MediaType] = []

        def search_object(obj: Any) -> None:

            if isinstance(obj, Header):
                if getattr(obj, 'param_schema', None) or getattr(obj, 'media_type_schema', None):
                    hlist.append(obj)

            if isinstance(obj, Parameter):
                if getattr(obj, 'param_schema', None) or getattr(obj, 'media_type_schema', None):
                    plist.append(obj)

            if isinstance(obj, MediaType):
                if getattr(obj, 'param_schema', None) or getattr(obj, 'media_type_schema', None):
                    mlist.append(obj)

            elif isinstance(obj, BaseModel):
                for i in obj.__dict__.keys():
                    search_object(getattr(obj, i))

            elif isinstance(obj, list):
                for i in obj:
                    search_object(i if isinstance(obj, list) else obj[i])

            elif isinstance(obj, dict):
                for i in obj:
                    search_object(i if isinstance(obj, list) else obj[i])

        # ------------------------------------------------

        search_object(self.__apidoc)  # search for objects that require reference rebuilding

        for i in hlist:
            key = sha256sum(json.dumps(i.param_schema.model_dump(by_alias=True), sort_keys=True))[:32]
            store[key] = i.param_schema  # merge duplicate schemas
            i.param_schema = Reference(ref=f'#/components/schemas/{key}')

        for i in plist:
            key = sha256sum(json.dumps(i.param_schema.model_dump(by_alias=True), sort_keys=True))[:32]
            store[key] = i.param_schema  # merge duplicate schemas
            i.param_schema = Reference(ref=f'#/components/schemas/{key}')

        for i in mlist:
            key = sha256sum(json.dumps(i.media_type_schema.model_dump(by_alias=True), sort_keys=True))[:32]
            store[key] = i.media_type_schema  # merge duplicate schemas
            i.media_type_schema = Reference(ref=f'#/components/schemas/{key}')

        self.__apidoc.components = Components(schemas=store)
