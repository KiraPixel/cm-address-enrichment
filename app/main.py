# module_coord_processing.py

import time
import logging

from sqlalchemy import and_, func, select, union_all, and_, or_
from app.models import CashCesar, CashAxenta, Coord, SystemSettings, get_engine, create_session
from app.modules.location_module import get_address_decorator



logger = logging.getLogger('cm_address_enrichment')


def check_status():
    engine = get_engine()
    try:
        session = create_session(engine)
        result = session.query(SystemSettings).filter(SystemSettings.id == 0).first()
        session.close()
        return result.enable_address_enrichment
    except Exception as e:
        logger.error('Ошибка подключения к БД: {}'.format(e))
        return 0


def get_coords_without_address(session):
    logger.info("Начато получение координат без адреса")


    cesar_query = select(
        func.round(CashCesar.pos_x, 4).label("pos_x"),
        func.round(CashCesar.pos_y, 4).label("pos_y")
    ).where(
        func.round(CashCesar.pos_x, 4) != 0,
        func.round(CashCesar.pos_y, 4) != 0
    )

    axenta_query = select(
        func.round(CashAxenta.pos_x, 4).label("pos_x"),
        func.round(CashAxenta.pos_y, 4).label("pos_y")
    ).where(
        func.round(CashAxenta.pos_x, 4) != 0,
        func.round(CashAxenta.pos_y, 4) != 0
    )

    combined = union_all(cesar_query, axenta_query).subquery("combined")

    coord_query = (
        select(combined.c.pos_x, combined.c.pos_y)
        .distinct()
        .outerjoin(
            Coord,
            and_(
                func.round(Coord.pos_x, 4) == combined.c.pos_x,
                func.round(Coord.pos_y, 4) == combined.c.pos_y
            )
        )
        .where(or_(Coord.id == None, Coord.address == None))
    )

    result = session.execute(coord_query).all()

    coords_without_address = [(x, y) for x, y in result]

    logger.info(f"Получено координат для обработки: {len(coords_without_address)}")
    return coords_without_address



def _safe_get_address(x, y, retries=5, delay=1.5):
    logger.debug(f"Обрабатываю получения адреса для ({x}, {y})")
    for attempt in range(1, retries + 1):
        addr = get_address_decorator((x, y))

        if addr and "Ошибка" not in addr:
            return addr

        logger.warning(f"Ошибка получения адреса для ({x}, {y}), попытка {attempt}/{retries}")
        time.sleep(delay * attempt)

    logger.error(f"Не удалось получить адрес после {retries} попыток для ({x}, {y})")
    return "Ошибка: не удалось определить адрес"


def process_and_save_addresses(session, coords: list, batch_commit=50):
    logger.info("Старт обработки координат")

    current_time = int(time.time())
    counter = 0
    batch = []

    for x, y in coords:

        address = _safe_get_address(x, y)

        new_coord = Coord(
            pos_x=x,
            pos_y=y,
            address=address,
            updated_time=current_time
        )
        batch.append(new_coord)
        session.add(new_coord)

        counter += 1

        if counter % batch_commit == 0:
            session.commit()
            logger.info(f"Сохранено записей: {counter}")

    session.commit()
    logger.info(f"Обработка завершена. Всего обработано {counter} координат.")

