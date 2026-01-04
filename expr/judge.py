from expr.utils import *


def operation_equals(lhs: OperationBean, rhs: OperationBean) -> bool:

    compare = True

    compare = compare and lhs.stdurl == rhs.stdurl

    compare = compare and lhs.method == rhs.method

    return compare


def req_equals(lhs: ReqBean, rhs: ReqBean) -> bool:

    compare = True

    lhs_datatype = 'string' if lhs.location in ('path', 'query') else lhs.datatype

    rhs_datatype = 'string' if rhs.location in ('path', 'query') else rhs.datatype

    compare = compare and lhs.stdurl == rhs.stdurl and lhs.location == rhs.location

    compare = compare and lhs.method == rhs.method and lhs_datatype == rhs_datatype

    return compare and lhs.stdname == rhs.stdname


def res_equals_object(lhs: ResBean, rhs: ResBean) -> bool:

    compare = True

    lhs_datatype = lhs.datatype or 'object'  # with default type

    rhs_datatype = rhs.datatype or 'object'  # with default type

    compare = compare and lhs.stdurl == rhs.stdurl and lhs.respcode == rhs.respcode

    compare = compare and lhs.method == rhs.method and lhs_datatype == rhs_datatype

    return compare


def res_equals_number(lhs: ResBean, rhs: ResBean) -> bool:

    compare = True

    lhs_datatype = lhs.datatype or 'number'  # with default type

    rhs_datatype = rhs.datatype or 'number'  # with default type

    compare = compare and lhs.stdurl == rhs.stdurl and lhs.respcode == rhs.respcode

    compare = compare and lhs.method == rhs.method and lhs_datatype == rhs_datatype

    return compare


def res_equals(lhs: ResBean, rhs: ResBean) -> bool:

    compare = True

    lhs_datatype = lhs.datatype or 'string'  # with default type

    rhs_datatype = rhs.datatype or 'string'  # with default type

    compare = compare and lhs.stdurl == rhs.stdurl and lhs.respcode == rhs.respcode

    compare = compare and lhs.method == rhs.method and lhs_datatype == rhs_datatype

    return compare


def constraint_equals(lhs: ConstraintBean, rhs: ConstraintBean) -> bool:

    compare = True

    compare = compare and lhs.kind == rhs.kind

    compare = compare and lhs.data == rhs.data

    return compare


# ------------------------------------------------


def compare_items(
    context: Any, compare_key: str,
    truth_list: list[BaseModel],
    check_list: list[BaseModel],
    compare: Callable[[BaseModel, BaseModel], bool]
) -> list[tuple[BaseModel, BaseModel]]:

    truth_and_check: list[BaseModel] = getattr(context, f'get_{compare_key}_truth_and_check')()

    truth_not_check: list[BaseModel] = getattr(context, f'get_{compare_key}_truth_not_check')()

    check_and_truth: list[BaseModel] = getattr(context, f'get_{compare_key}_check_and_truth')()

    check_not_truth: list[BaseModel] = getattr(context, f'get_{compare_key}_check_not_truth')()

    truth_check_store: list[tuple[BaseModel, BaseModel]] = []

    check_truth_store: list[tuple[BaseModel, BaseModel]] = []

    for i in truth_list:

        if len(selected := [j for j in check_list if compare(i, j)]) > 1:
            print(f'warning: duplicate matches in {compare_key} comparison')

        elif len(selected) == 1:
            assert not (truth_check_store.append((i, selected[-1] if selected else None)) or truth_and_check.append(i))

        elif len(selected) == 0:
            assert not (truth_check_store.append((i, selected[-1] if selected else None)) or truth_not_check.append(i))

    for i in check_list:

        if len(selected := [j for j in truth_list if compare(i, j)]) > 1:
            print(f'warning: duplicate matches in {compare_key} comparison')

        elif len(selected) == 1:
            assert not (check_truth_store.append((i, selected[-1] if selected else None)) or check_and_truth.append(i))

        elif len(selected) == 0:
            assert not (check_truth_store.append((i, selected[-1] if selected else None)) or check_not_truth.append(i))

    # ------------------------------------------------

    truth_check_store = [i for i in truth_check_store if i[0] and i[1]]

    check_truth_store = [i for i in check_truth_store if i[0] and i[1]]

    return truth_check_store or check_truth_store


def compare_operation(context: Any, truth: list[OperationBean], check: list[OperationBean]) -> list[tuple[OperationBean, OperationBean]]:

    return compare_items(context, 'operation', truth, check, operation_equals)


def compare_req(context: Any, truth: list[ReqBean], check: list[ReqBean]) -> list[tuple[ReqBean, ReqBean]]:

    return compare_items(context, 'req', truth, check, req_equals)


def compare_res(context: Any, truth: list[ResBean], check: list[ResBean]) -> list[tuple[ResBean, ResBean]]:

    return compare_items(context, 'res', truth, check, res_equals)


def compare_constraint(context: Any, truth: list[ConstraintBean], check: list[ConstraintBean]) -> list[tuple[ConstraintBean, ConstraintBean]]:

    return compare_items(context, 'constraint', truth, check, constraint_equals)


# ------------------------------------------------


def diff_req_truth_only(context: Any, bean: OperationBean) -> list[tuple[ReqBean, ReqBean]]:

    lhs, rhs = [], []

    lhs.extend([ReqBean.load_req_param_3_0(bean, i) for i in bean.req] if isinstance(bean.operation, OASv3_0.Operation) else [])

    lhs.extend([ReqBean.load_req_param_3_1(bean, i) for i in bean.req] if isinstance(bean.operation, OASv3_1.Operation) else [])

    if bean.body and (field := select_media_single(bean.body)):

        lhs.extend(ReqBean.load_req_schema_3_0(bean, bean.body, field) if isinstance(bean.operation, OASv3_0.Operation) else [])

        lhs.extend(ReqBean.load_req_schema_3_1(bean, bean.body, field) if isinstance(bean.operation, OASv3_1.Operation) else [])

    return compare_req(context, lhs, rhs)


def diff_req_check_only(context: Any, bean: OperationBean) -> list[tuple[ReqBean, ReqBean]]:

    lhs, rhs = [], []

    rhs.extend([ReqBean.load_req_param_3_0(bean, i) for i in bean.req] if isinstance(bean.operation, OASv3_0.Operation) else [])

    rhs.extend([ReqBean.load_req_param_3_1(bean, i) for i in bean.req] if isinstance(bean.operation, OASv3_1.Operation) else [])

    if bean.body and (field := select_media_single(bean.body)):

        rhs.extend(ReqBean.load_req_schema_3_0(bean, bean.body, field) if isinstance(bean.operation, OASv3_0.Operation) else [])

        rhs.extend(ReqBean.load_req_schema_3_1(bean, bean.body, field) if isinstance(bean.operation, OASv3_1.Operation) else [])

    return compare_req(context, lhs, rhs)


def diff_req_main(context: Any, truth: OperationBean, check: OperationBean) -> list[tuple[ReqBean, ReqBean]]:

    lhs, rhs = [], []

    lhs.extend([ReqBean.load_req_param_3_0(truth, i) for i in truth.req] if isinstance(truth.operation, OASv3_0.Operation) else [])

    lhs.extend([ReqBean.load_req_param_3_1(truth, i) for i in truth.req] if isinstance(truth.operation, OASv3_1.Operation) else [])

    rhs.extend([ReqBean.load_req_param_3_0(check, i) for i in check.req] if isinstance(check.operation, OASv3_0.Operation) else [])

    rhs.extend([ReqBean.load_req_param_3_1(check, i) for i in check.req] if isinstance(check.operation, OASv3_1.Operation) else [])

    if (common := select_media_double(truth.body, check.body) if truth.body and check.body else None):

        lhs.extend(ReqBean.load_req_schema_3_0(truth, truth.body, common) if isinstance(truth.operation, OASv3_0.Operation) else [])

        lhs.extend(ReqBean.load_req_schema_3_1(truth, truth.body, common) if isinstance(truth.operation, OASv3_1.Operation) else [])

        rhs.extend(ReqBean.load_req_schema_3_0(check, check.body, common) if isinstance(check.operation, OASv3_0.Operation) else [])

        rhs.extend(ReqBean.load_req_schema_3_1(check, check.body, common) if isinstance(check.operation, OASv3_1.Operation) else [])

    elif truth.body and (field := select_media_single(truth.body)):

        lhs.extend(ReqBean.load_req_schema_3_0(truth, truth.body, field) if isinstance(truth.operation, OASv3_0.Operation) else [])

        lhs.extend(ReqBean.load_req_schema_3_1(truth, truth.body, field) if isinstance(truth.operation, OASv3_1.Operation) else [])

    elif check.body and (field := select_media_single(check.body)):

        rhs.extend(ReqBean.load_req_schema_3_0(check, check.body, field) if isinstance(check.operation, OASv3_0.Operation) else [])

        rhs.extend(ReqBean.load_req_schema_3_1(check, check.body, field) if isinstance(check.operation, OASv3_1.Operation) else [])

    return compare_req(context, lhs, rhs)


# ------------------------------------------------


def diff_res_truth_only(context: Any, bean: OperationBean) -> list[tuple[ResBean, ResBean]]:

    lhs, rhs, share = [], [], {i for i in bean.res.keys() if not any(i.startswith(j) for j in ('4', '5', 'def'))}

    for i in share or bean.res.keys():

        field = select_media_single(bean.res[i], '*')

        lhs.extend([ResBean.load_res_3_0(bean, i, bean.res[i], field)] if isinstance(bean.operation, OASv3_0.Operation) else [])

        lhs.extend([ResBean.load_res_3_1(bean, i, bean.res[i], field)] if isinstance(bean.operation, OASv3_1.Operation) else [])

    return compare_res(context, lhs, rhs)


def diff_res_check_only(context: Any, bean: OperationBean) -> list[tuple[ResBean, ResBean]]:

    lhs, rhs, share = [], [], {i for i in bean.res.keys() if not any(i.startswith(j) for j in ('4', '5', 'def'))}

    for i in share or bean.res.keys():

        field = select_media_single(bean.res[i], '*')

        rhs.extend([ResBean.load_res_3_0(bean, i, bean.res[i], field)] if isinstance(bean.operation, OASv3_0.Operation) else [])

        rhs.extend([ResBean.load_res_3_1(bean, i, bean.res[i], field)] if isinstance(bean.operation, OASv3_1.Operation) else [])

    return compare_res(context, lhs, rhs)


def diff_res_main(context: Any, truth: OperationBean, check: OperationBean) -> list[tuple[ResBean, ResBean]]:

    lhs, truth_code = [], {i for i in truth.res.keys() if not any(i.startswith(j) for j in ('4', '5', 'def'))}

    rhs, check_code = [], {i for i in check.res.keys() if not any(i.startswith(j) for j in ('4', '5', 'def'))}

    for i in (truth_code | check_code) or (set(truth.res.keys()) | set(check.res.keys())):

        if i in truth.res and i in check.res:

            if (common := select_media_double(truth.res[i], check.res[i]) if truth.res[i].content and check.res[i].content else None):

                lhs.extend([ResBean.load_res_3_0(truth, i, truth.res[i], common)] if isinstance(truth.operation, OASv3_0.Operation) else [])

                lhs.extend([ResBean.load_res_3_1(truth, i, truth.res[i], common)] if isinstance(truth.operation, OASv3_1.Operation) else [])

                rhs.extend([ResBean.load_res_3_0(check, i, check.res[i], common)] if isinstance(check.operation, OASv3_0.Operation) else [])

                rhs.extend([ResBean.load_res_3_1(check, i, check.res[i], common)] if isinstance(check.operation, OASv3_1.Operation) else [])

            if not common and (field := select_media_single(truth.res[i], '*')):

                lhs.extend([ResBean.load_res_3_0(truth, i, truth.res[i], field)] if isinstance(truth.operation, OASv3_0.Operation) else [])

                lhs.extend([ResBean.load_res_3_1(truth, i, truth.res[i], field)] if isinstance(truth.operation, OASv3_1.Operation) else [])

            if not common and (field := select_media_single(check.res[i], '*')):

                rhs.extend([ResBean.load_res_3_0(check, i, check.res[i], field)] if isinstance(check.operation, OASv3_0.Operation) else [])

                rhs.extend([ResBean.load_res_3_1(check, i, check.res[i], field)] if isinstance(check.operation, OASv3_1.Operation) else [])

        elif i in truth.res and (field := select_media_single(truth.res[i], '*')):

            lhs.extend([ResBean.load_res_3_0(truth, i, truth.res[i], field)] if isinstance(truth.operation, OASv3_0.Operation) else [])

            lhs.extend([ResBean.load_res_3_1(truth, i, truth.res[i], field)] if isinstance(truth.operation, OASv3_1.Operation) else [])

        elif i in check.res and (field := select_media_single(check.res[i], '*')):

            rhs.extend([ResBean.load_res_3_0(check, i, check.res[i], field)] if isinstance(check.operation, OASv3_0.Operation) else [])

            rhs.extend([ResBean.load_res_3_1(check, i, check.res[i], field)] if isinstance(check.operation, OASv3_1.Operation) else [])

    return compare_res(context, lhs, rhs)


# ------------------------------------------------


def diff_constraint_truth_only(context: Any, bean: ReqBean) -> list[tuple[ConstraintBean, ConstraintBean]]:

    lhs, rhs = ConstraintBean.load_constraint(bean), []

    lhs.extend([ConstraintBean.get_required(bean)] if bean.required else [])

    lhs = [i for i in lhs if isinstance(i, ConstraintBean) and (i.kind != 'required' or i.data is not False)]

    rhs = [i for i in rhs if isinstance(i, ConstraintBean) and (i.kind != 'required' or i.data is not False)]

    return compare_constraint(context, lhs, rhs)


def diff_constraint_check_only(context: Any, bean: ReqBean) -> list[tuple[ConstraintBean, ConstraintBean]]:

    rhs, lhs = ConstraintBean.load_constraint(bean), []

    rhs.extend([ConstraintBean.get_required(bean)] if bean.required else [])

    lhs = [i for i in lhs if isinstance(i, ConstraintBean) and (i.kind != 'required' or i.data is not False)]

    rhs = [i for i in rhs if isinstance(i, ConstraintBean) and (i.kind != 'required' or i.data is not False)]

    return compare_constraint(context, lhs, rhs)


def diff_constraint_main(context: Any, truth: ReqBean, check: ReqBean) -> list[tuple[ConstraintBean, ConstraintBean]]:

    lhs = ConstraintBean.load_constraint(truth)

    rhs = ConstraintBean.load_constraint(check)

    lhs.extend([ConstraintBean.get_required(truth)] if truth.required else [])

    rhs.extend([ConstraintBean.get_required(check)] if check.required else [])

    lhs = [i for i in lhs if isinstance(i, ConstraintBean) and (i.kind != 'required' or i.data is not False)]

    rhs = [i for i in rhs if isinstance(i, ConstraintBean) and (i.kind != 'required' or i.data is not False)]

    return compare_constraint(context, lhs, rhs)
