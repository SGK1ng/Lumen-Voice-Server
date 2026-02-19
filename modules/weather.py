import requests
from num2words import num2words

from config import OPENWEATHER_API_KEY

DEFAULT_CITY = "Москва"
REQUEST_TIMEOUT = 5

translate_dict = {
    # Clear
    "clear sky": "ясно",
    # Clouds
    "few clouds": "немного облачно",
    "scattered clouds": "переменная облачность",
    "broken clouds": "облачно",
    "overcast clouds": "пасмурно",
    # Thunderstorm (2xx)
    "thunderstorm with light rain": "гроза с небольшим дождём",
    "thunderstorm with rain": "гроза с дождём",
    "thunderstorm with heavy rain": "гроза с сильным дождём",
    "light thunderstorm": "небольшая гроза",
    "thunderstorm": "гроза",
    "heavy thunderstorm": "сильная гроза",
    "ragged thunderstorm": "рваная гроза",
    "thunderstorm with light drizzle": "гроза с мелким дождём",
    "thunderstorm with drizzle": "гроза с моросью",
    "thunderstorm with heavy drizzle": "гроза с сильной моросью",
    # Drizzle (3xx)
    "light intensity drizzle": "лёгкая морось",
    "drizzle": "морось",
    "heavy intensity drizzle": "сильная морось",
    "light intensity drizzle rain": "лёгкий моросящий дождь",
    "drizzle rain": "моросящий дождь",
    "heavy intensity drizzle rain": "сильный моросящий дождь",
    "shower rain and drizzle": "ливень с моросью",
    "heavy shower rain and drizzle": "сильный ливень с моросью",
    "shower drizzle": "моросящий ливень",
    # Rain (5xx)
    "light rain": "идёт небольшой дождь",
    "moderate rain": "идёт дождь",
    "heavy intensity rain": "идёт сильный дождь",
    "very heavy rain": "идёт очень сильный дождь",
    "extreme rain": "идёт проливной дождь",
    "freezing rain": "идёт ледяной дождь",
    "light intensity shower rain": "идёт небольшой ливень",
    "shower rain": "идёт ливень",
    "heavy intensity shower rain": "идёт сильный ливень",
    "ragged shower rain": "идёт неравномерный ливень",
    "rain": "идёт дождь",
    # Snow (6xx)
    "light snow": "идёт небольшой снег",
    "snow": "идёт снег",
    "heavy snow": "идёт сильный снегопад",
    "sleet": "идёт мокрый снег",
    "light shower sleet": "идёт небольшой мокрый снег",
    "shower sleet": "идёт ливневой мокрый снег",
    "light rain and snow": "идёт дождь со снегом",
    "rain and snow": "идёт дождь со снегом",
    "light shower snow": "идёт небольшой снег",
    "shower snow": "идёт снегопад",
    "heavy shower snow": "идёт сильный снегопад",
    # Atmosphere (7xx)
    "mist": "туман",
    "smoke": "дым",
    "haze": "дымка",
    "sand/dust whirls": "песчаные вихри",
    "fog": "туман",
    "sand": "песчаная буря",
    "dust": "пыльно",
    "volcanic ash": "вулканический пепел",
    "squalls": "шквалы",
    "tornado": "торнадо",
}


def format_degrees(num: int) -> str:
    last_digit = num % 10
    last_two_digits = num % 100

    if 11 <= last_two_digits <= 14:
        return "градусов"

    if last_digit == 1:
        return "градус"
    if 2 <= last_digit <= 4:
        return "градуса"

    return "градусов"


def format_city_name(city: str) -> str:
    if not city or len(city) < 2:
        return city

    last_letter = city[-1]

    if last_letter == "и":
        return city

    elif last_letter == "а":
        return city[:-1] + "е"

    return city + "е"


def format_temperature_text(
    temp: int, feels_like: int, description: str, city: str
) -> str:
    return (
        (
            f"Сейчас в {city} {description}, "
            f"температура воздуха {num2words(temp, lang='ru')} {format_degrees(temp)}, "
            f"ощущается как {num2words(feels_like, lang='ru')}."
        )
        if feels_like != temp
        else (
            f"Сейчас в {city} {description}, температура воздуха {num2words(temp, lang='ru')} {format_degrees(temp)}."
        )
    )


def get_weather(city: str = DEFAULT_CITY) -> str:
    """
    Получает текущую погоду для указанного города.

    Args:
        city: Название города (по умолчанию Москва)

    Returns:
        str: Текстовое описание погоды или сообщение об ошибке
    """
    try:
        # Геокодирование
        geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        geo = requests.get(geo_url, timeout=REQUEST_TIMEOUT).json()

        if not geo:
            return f"Город {city} не найден"

        # Погода
        lat, lon = geo[0]["lat"], geo[0]["lon"]
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
        weather = requests.get(weather_url, timeout=5).json()

        # Обработка данных
        city_formatted = format_city_name(city)
        raw_description = weather["weather"][0]["description"]
        description = translate_dict.get(raw_description) or raw_description
        temp = round(weather["main"]["temp"])
        feels_like = round(weather["main"]["feels_like"])

        return format_temperature_text(temp, feels_like, description, city_formatted)

    except requests.exceptions.RequestException as e:
        return f"Ошибка подключения к API: {e}"

    except (KeyError, IndexError) as e:
        return f"Ошибка обработки данных: {e}"


print(get_weather())
