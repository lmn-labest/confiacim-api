from sqlalchemy import distinct, func, select

from confiacim_api.database import Session
from confiacim_api.models import FormResult, ResultStatus, TencimResult


def count_tasks(celery_workers: dict[str, list] | None) -> int:
    """
    Soma o numero total de tasks por todos os workers

    Parameters:
        celery_workers: Dicionario como os worker e suas tasks

    Returns:
        A soma do número de tasks
    """

    if not celery_workers:
        return 0
    return sum(len(tasks) for tasks in celery_workers.values())


def count_case_with_simulation_success(session: Session) -> int:
    """
    Soma o número de casos com pelo menos um simulação com status sucesso. Não
    import o tipo da simulação, se do Tencim, Form ou outra.

    Parameters:
        session: secção com banco de dados

    Returns:
        A soma de casos com simulação
    """

    case_id_tencim_result = session.scalars(
        select(distinct(TencimResult.case_id)).where(TencimResult.status == ResultStatus.SUCCESS)
    ).all()
    case_id_form_result = session.scalars(
        select(distinct(FormResult.case_id)).where(FormResult.status == ResultStatus.SUCCESS)
    ).all()

    case_id_set = set(case_id_form_result).union(case_id_tencim_result)
    return len(case_id_set)


def total_success_simulations(session: Session):
    """
    Soma o todas as simulações com status de sucesso

    Parameters:
        session: secção com banco de dados

    Returns:
        Valor da soma
    """

    form_result_count = select(func.count()).select_from(FormResult).where(FormResult.status == ResultStatus.SUCCESS)
    tencim_result_count = (
        select(func.count()).select_from(TencimResult).where(TencimResult.status == ResultStatus.SUCCESS)
    )
    query = select(form_result_count.scalar_subquery() + tencim_result_count.scalar_subquery())

    return session.execute(query).scalar()
