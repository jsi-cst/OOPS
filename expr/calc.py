from expr.parse import *
from expr.judge import *


class CompareResultMetric(BaseModel):

    pr: float | None = Field(exclude=False)
    re: float | None = Field(exclude=False)
    fb: float | None = Field(exclude=False)

    tp_num: int = Field(exclude=False)
    fp_num: int = Field(exclude=False)
    fn_num: int = Field(exclude=False)

    tp_log: list[str] = Field(exclude=True)
    fp_log: list[str] = Field(exclude=True)
    fn_log: list[str] = Field(exclude=True)

    @staticmethod
    def use(tac: list[BaseModel], tnc: list[BaseModel], cat: list[BaseModel], cnt: list[BaseModel], beta: float) -> 'CompareResultMetric':

        tpl, tpn = [i.model_dump_json(ensure_ascii=False) for i in tac or cat or []], len(tac or cat)

        fpl, fpn = [i.model_dump_json(ensure_ascii=False) for i in cnt or []], len(cnt)

        fnl, fnn = [i.model_dump_json(ensure_ascii=False) for i in tnc or []], len(tnc)

        _pr = tpn / (tpn + fpn) if tpn + fpn else None  # beware that divisor may be 0

        _re = tpn / (tpn + fnn) if tpn + fnn else None  # beware that divisor may be 0

        _fb = (1 + beta * beta) * _pr * _re / (beta * beta * _pr + _re) if _pr is not None and _re is not None and _pr + _re else None

        return CompareResultMetric(pr=_pr, re=_re, fb=_fb, tp_num=tpn, fp_num=fpn, fn_num=fnn, tp_log=tpl, fp_log=fpl, fn_log=fnl)


class CompareSpecification:

    class CompareResultBean(BaseModel):

        operation: CompareResultMetric
        req: CompareResultMetric
        res: CompareResultMetric
        constraint: CompareResultMetric

    __operation_truth_and_check: list[OperationBean]
    __req_truth_and_check: list[ReqBean]
    __res_truth_and_check: list[ResBean]
    __constraint_truth_and_check: list[ConstraintBean]

    __operation_truth_not_check: list[OperationBean]
    __req_truth_not_check: list[ReqBean]
    __res_truth_not_check: list[ResBean]
    __constraint_truth_not_check: list[ConstraintBean]

    __operation_check_and_truth: list[OperationBean]
    __req_check_and_truth: list[ReqBean]
    __res_check_and_truth: list[ResBean]
    __constraint_check_and_truth: list[ConstraintBean]

    __operation_check_not_truth: list[OperationBean]
    __req_check_not_truth: list[ReqBean]
    __res_check_not_truth: list[ResBean]
    __constraint_check_not_truth: list[ConstraintBean]

    __truth_oas: str
    __check_oas: str

    def __init__(self: Self, truth: str, check: str):

        self.__operation_truth_and_check = []
        self.__req_truth_and_check = []
        self.__res_truth_and_check = []
        self.__constraint_truth_and_check = []

        self.__operation_truth_not_check = []
        self.__req_truth_not_check = []
        self.__res_truth_not_check = []
        self.__constraint_truth_not_check = []

        self.__operation_check_and_truth = []
        self.__req_check_and_truth = []
        self.__res_check_and_truth = []
        self.__constraint_check_and_truth = []

        self.__operation_check_not_truth = []
        self.__req_check_not_truth = []
        self.__res_check_not_truth = []
        self.__constraint_check_not_truth = []

        self.__truth_oas = truth
        self.__check_oas = check

    def get_truth_oas(self: Self) -> str:

        return self.__truth_oas

    def get_check_oas(self: Self) -> str:

        return self.__check_oas

    # ------------------------------------------------

    def get_operation_truth_and_check(self: Self) -> list[OperationBean]:

        return self.__operation_truth_and_check

    def get_operation_truth_not_check(self: Self) -> list[OperationBean]:

        return self.__operation_truth_not_check

    def get_operation_check_and_truth(self: Self) -> list[OperationBean]:

        return self.__operation_check_and_truth

    def get_operation_check_not_truth(self: Self) -> list[OperationBean]:

        return self.__operation_check_not_truth

    # ------------------------------------------------

    def get_req_truth_and_check(self: Self) -> list[ReqBean]:

        return self.__req_truth_and_check

    def get_req_truth_not_check(self: Self) -> list[ReqBean]:

        return self.__req_truth_not_check

    def get_req_check_and_truth(self: Self) -> list[ReqBean]:

        return self.__req_check_and_truth

    def get_req_check_not_truth(self: Self) -> list[ReqBean]:

        return self.__req_check_not_truth

    # ------------------------------------------------

    def get_res_truth_and_check(self: Self) -> list[ResBean]:

        return self.__res_truth_and_check

    def get_res_truth_not_check(self: Self) -> list[ResBean]:

        return self.__res_truth_not_check

    def get_res_check_and_truth(self: Self) -> list[ResBean]:

        return self.__res_check_and_truth

    def get_res_check_not_truth(self: Self) -> list[ResBean]:

        return self.__res_check_not_truth

    # ------------------------------------------------

    def get_constraint_truth_and_check(self: Self) -> list[ConstraintBean]:

        return self.__constraint_truth_and_check

    def get_constraint_truth_not_check(self: Self) -> list[ConstraintBean]:

        return self.__constraint_truth_not_check

    def get_constraint_check_and_truth(self: Self) -> list[ConstraintBean]:

        return self.__constraint_check_and_truth

    def get_constraint_check_not_truth(self: Self) -> list[ConstraintBean]:

        return self.__constraint_check_not_truth

    # ------------------------------------------------

    def compare(self: Self, slim: bool = False, beta: float = 1.0) -> CompareResultBean:

        truth_operations = load_specification(self.__truth_oas)

        check_operations = load_specification(self.__check_oas)

        matched_operations = compare_operation(self, truth_operations, check_operations)

        matched_req, matched_res = [], []

        # ------------------------------------------------

        for truth, check in matched_operations:

            matched_req.extend(diff_req_main(self, truth, check))

        for i in [] if slim else self.get_operation_truth_not_check():

            assert diff_req_truth_only(self, i) is not None

        for i in [] if slim else self.get_operation_check_not_truth():

            assert diff_req_check_only(self, i) is not None

        # ------------------------------------------------

        for truth, check in matched_operations:

            matched_res.extend(diff_res_main(self, truth, check))

        for i in [] if slim else self.get_operation_truth_not_check():

            assert diff_res_truth_only(self, i) is not None

        for i in [] if slim else self.get_operation_check_not_truth():

            assert diff_res_check_only(self, i) is not None

        # ------------------------------------------------

        for truth, check in matched_res and matched_req or matched_req:

            assert diff_constraint_main(self, truth, check) is not None

        for i in [] if slim else self.get_req_truth_not_check():

            assert diff_constraint_truth_only(self, i) is not None

        for i in [] if slim else self.get_req_check_not_truth():

            assert diff_constraint_check_only(self, i) is not None

        # ------------------------------------------------

        assert len(self.__operation_check_and_truth) == len(self.__operation_truth_and_check)

        assert len(self.__req_check_and_truth) == len(self.__req_truth_and_check)

        assert len(self.__res_check_and_truth) == len(self.__res_truth_and_check)

        assert len(self.__constraint_check_and_truth) == len(self.__constraint_truth_and_check)

        # ------------------------------------------------

        operation_result = CompareResultMetric.use(
            self.__operation_truth_and_check,
            self.__operation_truth_not_check,
            self.__operation_check_and_truth,
            self.__operation_check_not_truth,
            beta  # f1 by default
        )

        req_result = CompareResultMetric.use(
            self.__req_truth_and_check,
            self.__req_truth_not_check,
            self.__req_check_and_truth,
            self.__req_check_not_truth,
            beta  # f1 by default
        )

        res_result = CompareResultMetric.use(
            self.__res_truth_and_check,
            self.__res_truth_not_check,
            self.__res_check_and_truth,
            self.__res_check_not_truth,
            beta  # f1 by default
        )

        constraint_result = CompareResultMetric.use(
            self.__constraint_truth_and_check,
            self.__constraint_truth_not_check,
            self.__constraint_check_and_truth,
            self.__constraint_check_not_truth,
            beta  # f1 by default
        )

        # ------------------------------------------------

        return CompareSpecification.CompareResultBean(
            operation=operation_result,
            req=req_result,
            res=res_result,
            constraint=constraint_result
        )
