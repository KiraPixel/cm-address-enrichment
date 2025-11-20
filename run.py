import os
import time
import logging

from app.main import check_status, get_coords_without_address, process_and_save_addresses
from app.models import get_engine, create_session

int_level=logging.INFO
if os.getenv('DEV', 0) == 1:
    int_level = logging.DEBUG

logging.basicConfig(
    level=int_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('cm_address_enrichment')

engine = get_engine()

if __name__ == "__main__":
    logger.info("Запуск планировщика задач...")
    while True:
        if check_status() == 0:
            logger.info('Модуль отключен. Ожидание 200 секунд')
            time.sleep(200)
        else:
            logger.info('Начинаю обработку координат')
            session = create_session(engine)
            coords = get_coords_without_address(session)
            process_and_save_addresses(session, coords)
            session.close()
            logger.info('Закончил обработку координат. Ожидание 100 секунд')
            time.sleep(100)
