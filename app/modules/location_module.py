import time
from geopy.geocoders import Nominatim

from app.models import Coord

geolocator = Nominatim(user_agent="KiraPixel1")


def get_address(x: int, y: int):
    if x == 0 or y == 0:
        return None
    try:
        location = geolocator.reverse((x, y), exactly_one=True)
        return location
    except:
        return f"Convert error"


def get_address_decorator(coords=None):
    try:
        if coords is None:
            return ''

        x, y = coords
        if x == 0 or y == 0:
            return ''

        location = geolocator.reverse((x, y), exactly_one=True, language='ru')
        if location is None:
            return 'Ошибка определения'

        address = location.raw.get('address', {})

        # Попробуем получить нужные части адреса
        city = address.get('city') or address.get('state') or address.get('town') or \
               address.get('county')

        road = address.get('road') or address.get('city_district', '') or address.get('county') or \
               address.get('municipality') or address.get('suburb') or address.get('house') or \
               address.get('industrial') or address.get('hamlet') or address.get('neighbourhood') or \
               address.get('town')

        house_number = address.get('house_number') or address.get('amenity') or address.get('village') or \
                       address.get('neighbourhood') or address.get('municipality') or address.get('postcode') or \
                       address.get("quarter") or address.get('road') or address.get("region")

        # Формируем сокращенный адрес
        short_address = f"{city}, {road}, {house_number}".strip(', ')
        if short_address == 'Химки, Коммунальный проезд, 141410':
            short_address = "Химки, Коммунальный проезд, 2"

        return short_address

    except Exception as e:
        return f'Ошибка определения адреса'


def get_address_from_coords(x, y, session):
    if not x or not y or x == 0 or y == 0:
        return "Convert error"

    # Округляем до 4 знаков после запятой
    x = float(f"{float(x):.4f}")
    y = float(f"{float(y):.4f}")

    # Ищем с небольшой погрешностью
    epsilon = 0.0001
    coord = session.query(Coord).filter(
        Coord.pos_x.between(x - epsilon, x + epsilon),
        Coord.pos_y.between(y - epsilon, y + epsilon)
    ).first()

    current_time = int(time.time())

    new_address = get_address(x, y)
    if new_address == "Convert error":
        return "Time out to convert"
    if coord:
        coord.address = new_address
        coord.updated_time = current_time
    else:
        new_coord = Coord(
            pos_x=x,
            pos_y=y,
            address=new_address,
            updated_time=current_time
        )
        session.add(new_coord)
    session.commit()
    return new_address
