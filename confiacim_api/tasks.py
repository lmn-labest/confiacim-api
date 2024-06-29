# from sqlalchemy import select

# from confiacim_api.celery import celery_app
# from confiacim_api.database import SessionFactory
# from confiacim_api.models import Simulation


# @celery_app.task()
# def simulation_run(simulation_id) -> dict[str, str]:
#     tag = None

#     with SessionFactory() as session:
#         db_simulation = session.scalar(select(Simulation).where(Simulation.id == simulation_id))
#         if db_simulation:
#             tag = db_simulation.tag

#     import time

#     time.sleep(20)

#     return {"status": f"Simulação {tag} rodou."}
