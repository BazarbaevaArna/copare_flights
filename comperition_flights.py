# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Функция для чтения и разбора XML-файла
def extract_flights(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    flights = []
    for flight in root.findall("Flight"):
        flights.append({
            "flight_number": flight.find("НомерРейса").text,
            "from": flight.find("Откуда").text,
            "to": flight.find("Куда").text,
            "departure_time": datetime.fromisoformat(flight.find("ВремяОтправления").text),
            "arrival_time": datetime.fromisoformat(flight.find("ВремяПрибытия").text),
            "price": float(flight.find("Цена").text)
        })
    return sorted(flights, key=lambda f: f["departure_time"])

# Группировка рейсов в маршруты по стыковкам
def group_routes(flights, max_wait=timedelta(hours=3)):
    routes = []
    used = set()

    for i, flight in enumerate(flights):
        if i in used:
            continue
        route = [flight]
        used.add(i)
        current = flight

        for j, next_flight in enumerate(flights):
            if j in used:
                continue
            if (
                current["to"] == next_flight["from"] and
                current["arrival_time"] <= next_flight["departure_time"] <= current["arrival_time"] + max_wait
            ):
                route.append(next_flight)
                used.add(j)
                current = next_flight

        routes.append({
            "flights": route,
            "flight_numbers": [f["flight_number"] for f in route],
            "from": route[0]["from"],
            "to": route[-1]["to"],
            "start_time": route[0]["departure_time"],
            "end_time": route[-1]["arrival_time"],
            "price": sum(f["price"] for f in route)
        })

    return routes

# Функция для сравнения маршрутов
def compare_routes(routes1, routes2):
    def route_signature(r):
        return (
            tuple(r["flight_numbers"]),
            r["from"],
            r["to"],
            r["start_time"].isoformat(),
            r["end_time"].isoformat(),
            round(r["price"], 2)
        )

    set1 = {route_signature(r): r for r in routes1}
    set2 = {route_signature(r): r for r in routes2}

    added = [r for sig, r in set2.items() if sig not in set1]
    removed = [r for sig, r in set1.items() if sig not in set2]

    return added, removed

# Функция для вывода результата
# Функция для сохранения результата в текстовый файл
def save_results_to_file(added, removed, filename="report.txt"):
    lines = []
    lines.append("Результаты сравнения маршрутов:\n")

    if added:
        lines.append("++ Добавленные маршруты:\n")
        for r in added:
            lines.append(f"Маршрут: {r['from']} → {r['to']}")
            lines.append(f"Рейсы: {', '.join(r['flight_numbers'])}")
            lines.append(f"Время отправления: {r['start_time']}")
            lines.append(f"Время прибытия: {r['end_time']}")
            lines.append(f"Цена маршрута: {r['price']} руб.\n")

    if removed:
        lines.append("-- Удалённые маршруты:\n")
        for r in removed:
            lines.append(f"Маршрут: {r['from']} → {r['to']}")
            lines.append(f"Рейсы: {', '.join(r['flight_numbers'])}")
            lines.append(f"Время отправления: {r['start_time']}")
            lines.append(f"Время прибытия: {r['end_time']}")
            lines.append(f"Цена маршрута: {r['price']} руб.\n")

    # Запись в файл
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"\n✅ Результаты сохранены в файл: {filename}")


# Главная функция
def main():
    file1 = 'response1.xml'
    file2 = 'response2.xml'

    flights1 = extract_flights(file1)
    flights2 = extract_flights(file2)

    routes1 = group_routes(flights1)
    routes2 = group_routes(flights2)

    print("Файлы успешно загружены и обработаны.")

    added, removed = compare_routes(routes1, routes2)

    save_results_to_file(added, removed)
    print("Сравнение маршрутов завершено.")

if __name__ == "__main__":
    main()
