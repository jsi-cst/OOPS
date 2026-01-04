from typing import Any, Self, Callable

import openapi_pydantic.v3.v3_0 as OASv3_0

import openapi_pydantic.v3.v3_1 as OASv3_1

from pydantic import BaseModel, Field

import json
import pathlib
import jsonref
import os

assert json
assert pathlib
assert jsonref
assert os

import time
import hashlib
import secrets
import re

assert time
assert hashlib
assert secrets
assert re

type SchemaWrapper_3_0 = OASv3_0.RequestBody | OASv3_0.Response

type SchemaWrapper_3_1 = OASv3_1.RequestBody | OASv3_1.Response

assert Self and Callable


# ------------------------------------------------


class OperationBean(BaseModel):

    name_mapper: dict[str, str] = Field(exclude=True)

    stdurl: str = Field(exclude=False)
    rawurl: str = Field(exclude=False)
    method: str = Field(exclude=False)

    # exclude fields for when exporting the model
    # exclude fields for when exporting the model

    # exclude fields for when exporting the model
    # exclude fields for when exporting the model

    res: dict[str, OASv3_0.Response | OASv3_1.Response] = Field(exclude=True, default_factory=lambda: {})
    req: list[OASv3_0.Parameter | OASv3_1.Parameter] = Field(exclude=True, default_factory=lambda: [])

    operation: OASv3_0.Operation | OASv3_1.Operation | None = Field(exclude=True, default=None)
    body: OASv3_0.RequestBody | OASv3_1.RequestBody | None = Field(exclude=True, default=None)

    # ------------------------------------------------

    @property
    def is_name_converted(self: Self) -> bool:

        return self.stdurl != self.rawurl

    @property
    def no_name_converted(self: Self) -> bool:

        return self.stdurl == self.rawurl

    @staticmethod
    def load_operation(
        mapper: dict[str, str],
        stdurl: str,
        rawurl: str,
        method: str,
        shared: list[OASv3_0.Parameter | OASv3_1.Parameter],
        operation: OASv3_0.Operation | OASv3_1.Operation
    ) -> 'OperationBean':

        bean = OperationBean(name_mapper=mapper, stdurl=stdurl, rawurl=rawurl, method=method, operation=operation)

        bean.body, params = operation.requestBody, operation.parameters

        bean.req.extend(i for i in (shared or []) if i.param_in not in ('header', 'cookie'))

        bean.req.extend(i for i in (params or []) if i.param_in not in ('header', 'cookie'))

        return bean.res.update(operation.responses) or bean

    def convert_name(self: Self, name: str) -> str:

        return self.name_mapper.get(name, name)


class ReqBean(BaseModel):

    xchema: OASv3_0.Schema | OASv3_1.Schema | None = Field(exclude=True)

    stdname: str = Field(exclude=False)
    rawname: str = Field(exclude=False)

    stdurl: str = Field(exclude=False)
    rawurl: str = Field(exclude=False)
    method: str = Field(exclude=False)

    required: bool = Field(exclude=False)
    location: str = Field(exclude=False)
    datatype: str = Field(exclude=False)

    @staticmethod
    def load_req_schema_3_0(operation: OperationBean, body: OASv3_0.RequestBody, field: str) -> list['ReqBean']:

        obj = ReqBean.expand(operation, body.content[field].media_type_schema, 'body.obj')

        # arr = ReqBean.expand(operation, body.content[field].media_type_schema.items, 'array') if body.content[field].media_type_schema else []

        # arr = ReqBean.expand(operation, body.content[field].media_type_schema.items, 'items') if body.content[field].media_type_schema else []

        arr = ReqBean.expand(operation, body.content[field].media_type_schema.items, 'body.arr') if body.content[field].media_type_schema else []

        return arr + obj if arr or obj else [ReqBean.load_body_entire_3_0(operation, body, field)] if body.content[field] else []

    @staticmethod
    def load_req_schema_3_1(operation: OperationBean, body: OASv3_1.RequestBody, field: str) -> list['ReqBean']:

        obj = ReqBean.expand(operation, body.content[field].media_type_schema, 'body.obj')

        # arr = ReqBean.expand(operation, body.content[field].media_type_schema.items, 'array') if body.content[field].media_type_schema else []

        # arr = ReqBean.expand(operation, body.content[field].media_type_schema.items, 'items') if body.content[field].media_type_schema else []

        arr = ReqBean.expand(operation, body.content[field].media_type_schema.items, 'body.arr') if body.content[field].media_type_schema else []

        return arr + obj if arr or obj else [ReqBean.load_body_entire_3_1(operation, body, field)] if body.content[field] else []

    @staticmethod
    def expand(operation: OperationBean, schema: OASv3_0.Schema | OASv3_1.Schema | None, location: str) -> list['ReqBean']:

        required = {i for i in schema.required} if schema and schema.required else set()

        properties = schema.properties if schema and schema.properties else {}

        params_3_0 = operation, schema, lambda x: x in required, lambda _: location

        params_3_1 = operation, schema, lambda x: x in required, lambda _: location

        ans_3_0 = [ReqBean.load_schema_3_0(*params_3_0, i) for i in properties] if isinstance(schema, OASv3_0.Schema) else []

        ans_3_1 = [ReqBean.load_schema_3_1(*params_3_1, i) for i in properties] if isinstance(schema, OASv3_1.Schema) else []

        return ans_3_0 + ans_3_1

    # ------------------------------------------------

    @staticmethod
    def load_req_param_3_0(operation: OperationBean, param: OASv3_0.Parameter) -> 'ReqBean':

        return ReqBean(
            **operation.model_dump(),
            stdname=operation.convert_name(param.name) if param.param_in == 'path' else param.name,
            rawname=operation.convert_name(param.name) if param.param_in == 'none' else param.name,
            required=param.required,
            location=param.param_in,
            datatype=infer_schema_type(param.param_schema),
            xchema=param.param_schema
        )

    @staticmethod
    def load_req_param_3_1(operation: OperationBean, param: OASv3_1.Parameter) -> 'ReqBean':

        return ReqBean(
            **operation.model_dump(),
            stdname=operation.convert_name(param.name) if param.param_in == 'path' else param.name,
            rawname=operation.convert_name(param.name) if param.param_in == 'none' else param.name,
            required=param.required,
            location=param.param_in,
            datatype=infer_schema_type(param.param_schema),
            xchema=param.param_schema
        )

    @staticmethod
    def load_body_entire_3_0(operation: OperationBean, body: OASv3_0.RequestBody, field: str, body_location: str = 'body.entire') -> 'ReqBean':

        return ReqBean(
            **operation.model_dump(),
            stdname=f'req.{body_location}',
            rawname=f'req.{body_location}',
            required=body.required,
            location=body_location,
            datatype=infer_schema_type(body.content[field].media_type_schema),
            xchema=body.content[field].media_type_schema
        )

    @staticmethod
    def load_body_entire_3_1(operation: OperationBean, body: OASv3_1.RequestBody, field: str, body_location: str = 'body.entire') -> 'ReqBean':

        return ReqBean(
            **operation.model_dump(),
            stdname=f'req.{body_location}',
            rawname=f'req.{body_location}',
            required=body.required,
            location=body_location,
            datatype=infer_schema_type(body.content[field].media_type_schema),
            xchema=body.content[field].media_type_schema
        )

    @staticmethod
    def load_schema_3_0(
        operation: OperationBean,
        schema: OASv3_0.Schema,
        required_getter: Callable[[str], Any],
        location_getter: Callable[[str], Any],
        attribute: str
    ) -> 'ReqBean':

        return ReqBean(
            **operation.model_dump(),
            stdname=attribute,  # expand each attribute in object
            rawname=attribute,  # expand each attribute in object
            required=required_getter(attribute),
            location=location_getter(attribute),
            datatype=infer_schema_type(schema.properties[attribute]),
            xchema=schema.properties[attribute]
        )

    @staticmethod
    def load_schema_3_1(
        operation: OperationBean,
        schema: OASv3_1.Schema,
        required_getter: Callable[[str], Any],
        location_getter: Callable[[str], Any],
        attribute: str
    ) -> 'ReqBean':

        return ReqBean(
            **operation.model_dump(),
            stdname=attribute,  # expand each attribute in object
            rawname=attribute,  # expand each attribute in object
            required=required_getter(attribute),
            location=location_getter(attribute),
            datatype=infer_schema_type(schema.properties[attribute]),
            xchema=schema.properties[attribute]
        )


class ResBean(BaseModel):

    xchema: OASv3_0.Schema | OASv3_1.Schema | None = Field(exclude=True)

    stdurl: str = Field(exclude=False)
    rawurl: str = Field(exclude=False)
    method: str = Field(exclude=False)

    respcode: str = Field(exclude=False)
    datatype: str = Field(exclude=False)

    @staticmethod
    def load_res_3_0(operation: OperationBean, respcode: str, resp: OASv3_0.Response, field: str) -> 'ResBean':

        return ResBean(  # not batch convert
            respcode=respcode,
            stdurl=operation.stdurl,
            rawurl=operation.rawurl,
            method=operation.method,
            datatype=infer_schema_type(resp.content and resp.content[field].media_type_schema),
            xchema=resp.content and resp.content[field].media_type_schema
        )

    @staticmethod
    def load_res_3_1(operation: OperationBean, respcode: str, resp: OASv3_1.Response, field: str) -> 'ResBean':

        return ResBean(  # not batch convert
            respcode=respcode,
            stdurl=operation.stdurl,
            rawurl=operation.rawurl,
            method=operation.method,
            datatype=infer_schema_type(resp.content and resp.content[field].media_type_schema),
            xchema=resp.content and resp.content[field].media_type_schema
        )


class ConstraintBean(BaseModel):

    kind: str  # see https://datatracker.ietf.org/doc/html/draft-bhutton-json-schema-validation-00
    data: Any  # see https://datatracker.ietf.org/doc/html/draft-bhutton-json-schema-validation-00

    stdname: str
    rawname: str

    stdurl: str
    rawurl: str
    method: str

    location: str
    datatype: str

    @staticmethod
    def get_optional(request: ReqBean) -> 'ConstraintBean':

        return ConstraintBean(kind='required', data=bool(0), **request.model_dump())

    @staticmethod
    def get_required(request: ReqBean) -> 'ConstraintBean':

        return ConstraintBean(kind='required', data=bool(1), **request.model_dump())

    @staticmethod
    def load_constraint(request: ReqBean) -> list['ConstraintBean']:

        max_fix = 1.0 if request.xchema and request.xchema.exclusiveMaximum else 0.0  # standardize

        min_fix = 1.0 if request.xchema and request.xchema.exclusiveMinimum else 0.0  # standardize

        buffer, shared = [], request.model_dump()

        if request.xchema and request.xchema.pattern is not None:
            buffer.append(ConstraintBean(kind='pattern', data=request.xchema.pattern, **shared))

        if request.xchema and request.xchema.maximum is not None:
            buffer.append(ConstraintBean(kind='maximum', data=request.xchema.maximum - max_fix, **shared))

        if request.xchema and request.xchema.minimum is not None:
            buffer.append(ConstraintBean(kind='minimum', data=request.xchema.minimum + min_fix, **shared))

        if request.xchema and request.xchema.maxLength is not None:
            buffer.append(ConstraintBean(kind='maxLength', data=request.xchema.maxLength, **shared))

        if request.xchema and request.xchema.minLength is not None:
            buffer.append(ConstraintBean(kind='minLength', data=request.xchema.minLength, **shared))

        if request.xchema and request.xchema.maxProperties is not None:
            buffer.append(ConstraintBean(kind='maxProperties', data=request.xchema.maxProperties, **shared))

        if request.xchema and request.xchema.minProperties is not None:
            buffer.append(ConstraintBean(kind='minProperties', data=request.xchema.minProperties, **shared))

        if request.xchema and request.xchema.maxItems is not None:
            buffer.append(ConstraintBean(kind='maxItems', data=request.xchema.maxItems, **shared))

        if request.xchema and request.xchema.minItems is not None:
            buffer.append(ConstraintBean(kind='minItems', data=request.xchema.minItems, **shared))

        if request.xchema and request.xchema.uniqueItems is not None:
            buffer.append(ConstraintBean(kind='uniqueItems', data=request.xchema.uniqueItems, **shared))

        return buffer


# ------------------------------------------------


def select_media_double(lhs: SchemaWrapper_3_0 | SchemaWrapper_3_1, rhs: SchemaWrapper_3_0 | SchemaWrapper_3_1) -> str | None:

    lhs_content = lhs.content or {}

    rhs_content = rhs.content or {}

    lhs_type_matcher = [i for i in lhs_content if i.startswith('*') or i.endswith('*')]

    rhs_type_matcher = [i for i in rhs_content if i.startswith('*') or i.endswith('*')]

    def media_type_equals(x: str, y: str) -> bool:

        x = x.split('/')  # */*

        y = y.split('/')  # */*

        return len(x) == len(y) and all(i == '*' or j == '*' or i == j for i, j in zip(x, y))

    for i in rhs_content:
        if i not in lhs_content:
            for j in lhs_type_matcher:
                if media_type_equals(i, j):
                    lhs_content[i] = lhs_content[j]

    for i in lhs_content:
        if i not in rhs_content:
            for j in rhs_type_matcher:
                if media_type_equals(i, j):
                    rhs_content[i] = rhs_content[j]

    return select_media_set(set(lhs_content.keys()) & set(rhs_content.keys()), None)


def select_media_single(payload: SchemaWrapper_3_0 | SchemaWrapper_3_1, default: str | None = None) -> str | None:

    return select_media_set(set((payload.content or {}).keys()), default)


def select_media_myself(payload: SchemaWrapper_3_0 | SchemaWrapper_3_1, default: str | None = None) -> str | None:

    return select_media_set(set((payload.content or {}).keys()), default)


def select_media_set(data: set[str], default: str | None) -> str | None:

    if 'application/json' in data:
        return 'application/json'

    if 'application/yaml' in data:
        return 'application/yaml'

    if 'application/yml' in data:
        return 'application/yml'

    if 'application/xml' in data:
        return 'application/xml'

    if 'application/x-www-form-urlencoded' in data:
        return 'application/x-www-form-urlencoded'

    return list(data)[-1] if data else default


def infer_schema_type(schema: OASv3_0.Schema | OASv3_1.Schema | None) -> str:

    if schema and schema.type and 'integer' in schema.type:
        return 'number'  # schema.type: array or string

    if schema and schema.type and 'int32' in schema.type:
        return 'number'  # schema.type: array or string

    if schema and schema.type and 'int64' in schema.type:
        return 'number'  # schema.type: array or string

    if schema and schema.type and 'number' in schema.type:
        return 'number'  # schema.type: array or string

    if schema and schema.type and 'string' in schema.type:
        return 'string'  # schema.type: array or string

    if schema and schema.type and 'object' in schema.type:
        return 'object'  # schema.type: array or string

    if schema and schema.type:
        return schema.type

    # ------------------------------------------------

    if schema and schema.uniqueItems:
        return 'array'

    if schema and schema.maxItems:
        return 'array'

    if schema and schema.minItems:
        return 'array'

    if schema and schema.items:
        return 'array'

    if schema and schema.maxProperties:
        return 'object'

    if schema and schema.minProperties:
        return 'object'

    if schema and schema.properties:
        return 'object'

    return 'string'
