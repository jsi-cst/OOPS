from typing import Any
from typing import Self

from typing import Sequence
from typing import TypeAlias
from typing import Union
from typing import TypeVar

from typing import Optional
from typing import Annotated
from typing import Never
from typing import Literal

from uuid import uuid1
from uuid import uuid3
from uuid import uuid4
from uuid import uuid5

assert Any
assert Self

assert Sequence
assert TypeAlias
assert Union
assert TypeVar

assert Optional
assert Annotated
assert Never
assert Literal

assert uuid1
assert uuid3
assert uuid4
assert uuid5


# ------------------------------------------------


from pydantic import BaseModel
from pydantic import RootModel
from pydantic import Field

from pydantic import PositiveFloat
from pydantic import NonPositiveFloat
from pydantic import PositiveInt
from pydantic import NonPositiveInt

from pydantic import NegativeFloat
from pydantic import NonNegativeFloat
from pydantic import NegativeInt
from pydantic import NonNegativeInt

from pydantic import BeforeValidator
from pydantic import AfterValidator
from pydantic import PlainValidator
from pydantic import WrapValidator

assert BaseModel
assert RootModel
assert Field

assert PositiveFloat
assert NonPositiveFloat
assert PositiveInt
assert NonPositiveInt

assert NegativeFloat
assert NonNegativeFloat
assert NegativeInt
assert NonNegativeInt

assert BeforeValidator
assert AfterValidator
assert PlainValidator
assert WrapValidator


# ------------------------------------------------


import httpx
import networkx
import subprocess
import matplotlib.pyplot
import json
import yaml
import dotenv
import jinja2
import pathlib
import hashlib
import secrets
import os
import sys

assert httpx
assert networkx
assert subprocess
assert matplotlib.pyplot
assert json
assert yaml
assert dotenv
assert jinja2
assert pathlib
assert hashlib
assert secrets
assert os
assert sys


# ------------------------------------------------


import click
import datetime
import instructor
import matplotlib.artist
import math
import time
import random
import pickle
import asyncio
import inspect
import jsonref
import re
import csv

assert click
assert datetime
assert instructor
assert matplotlib.artist
assert math
assert time
assert random
assert pickle
assert asyncio
assert inspect
assert jsonref
assert re
assert csv


# ------------------------------------------------


from agno.agent import Agent
from agno.agent import Message
from agno.agent import Toolkit

from agno.models.base import Model
from agno.models.openai import OpenAIChat
from agno.models.openai import OpenAILike

from base64 import b16encode
from base64 import b16decode

from base64 import b32encode
from base64 import b32decode

from base64 import b64encode
from base64 import b64decode

from collections.abc import Callable
from collections.abc import Iterable

from enum import IntEnum
from enum import StrEnum

assert Agent
assert Message
assert Toolkit

assert Model
assert OpenAIChat
assert OpenAILike

assert b16encode
assert b16decode

assert b32encode
assert b32decode

assert b64encode
assert b64decode

assert Callable
assert Iterable

assert IntEnum
assert StrEnum


# ------------------------------------------------


from openapi_pydantic import *
# from openapi_pydantic.v3.v3_0 import *
# from openapi_pydantic.v3.v3_1 import *

assert Operation
assert Parameter

assert MediaType
assert Reference

assert Schema
assert Header
assert Components
assert OpenAPI
