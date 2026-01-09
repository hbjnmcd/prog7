import numpy as np
from scipy.optimize import linprog

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Целевая функция: минимизировать транспортные расходы
# Переменные: [x_11, x_12, x_13, x_21, x_22, x_23]
c = [8, 6, 10, 9, 7, 5]

# Ограничения-равенства A_eq @ x = b_eq
A_eq = [
    [1, 1, 1, 0, 0, 0],  # Склад 1: x_11 + x_12 + x_13 = 150
    [0, 0, 0, 1, 1, 1],  # Склад 2: x_21 + x_22 + x_23 = 250
    [1, 0, 0, 1, 0, 0],  # База Альфа: x_11 + x_21 = 120
    [0, 1, 0, 0, 1, 0],  # База Бета: x_12 + x_22 = 180
    [0, 0, 1, 0, 0, 1]   # База Гамма: x_13 + x_23 = 100
]

b_eq = [150, 250, 120, 180, 100]

# Границы переменных (все >= 0)
bounds = [(0, None) for _ in range(6)]

# Решение задачи
result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

# Вывод результатов
print("=== Транспортная задача снабжения военных баз ===")
print(f"Статус: {result.message}")
print("\nОптимальный план перевозок:")
print(f"x_11 (Склад 1 → Альфа): {result.x[0]:.1f} тонн")
print(f"x_12 (Склад 1 → Бета):  {result.x[1]:.1f} тонн")
print(f"x_13 (Склад 1 → Гамма): {result.x[2]:.1f} тонн")
print(f"x_21 (Склад 2 → Альфа): {result.x[3]:.1f} тонн")
print(f"x_22 (Склад 2 → Бета):  {result.x[4]:.1f} тонн")
print(f"x_23 (Склад 2 → Гамма): {result.x[5]:.1f} тонн")
print(f"\nМинимальная стоимость транспортировки: {result.fun:.0f} усл. ед.")


fig, ax = plt.subplots(figsize=(14, 10))

# Координаты узлов
warehouses = {'Склад 1': (2, 8), 'Склад 2': (2, 3)}
bases = {'Альфа': (10, 10), 'Бета': (10, 5.5), 'Гамма': (10, 1)}

# Рисуем склады (прямоугольники)
for name, (x, y) in warehouses.items():
    rect = FancyBboxPatch((x - 1, y - 0.5), 2, 1,
                          boxstyle="round,pad=0.1",
                          facecolor='lightblue', edgecolor='darkblue',
                          linewidth=2, alpha=0.8)
    ax.add_patch(rect)
    ax.text(x, y, f"{name}\nЗапас: {150 if name == 'Склад 1' else 250} т",
            ha='center', va='center', fontsize=11, fontweight='bold')

# Рисуем базы (прямоугольники)
for name, (x, y) in bases.items():
    rect = FancyBboxPatch((x - 1, y - 0.5), 2, 1,
                          boxstyle="round,pad=0.1",
                          facecolor='lightgreen', edgecolor='darkgreen',
                          linewidth=2, alpha=0.8)
    ax.add_patch(rect)
    need = {'Альфа': 120, 'Бета': 180, 'Гамма': 100}[name]
    ax.text(x, y, f"{name}\nПотребность: {need} т",
            ha='center', va='center', fontsize=11, fontweight='bold')

# Оптимальные потоки (из решения)
flows = [
    ('Склад 1', 'Альфа', result.x[0], 8),
    ('Склад 1', 'Бета', result.x[1], 6),
    ('Склад 1', 'Гамма', result.x[2], 10),
    ('Склад 2', 'Альфа', result.x[3], 9),
    ('Склад 2', 'Бета', result.x[4], 7),
    ('Склад 2', 'Гамма', result.x[5], 5)
]

# Словари для координат
node_pos = {**warehouses, **bases}

# Рисуем потоки (стрелки)
for source, target, flow, cost in flows:
    if flow > 0.1:  # Показываем только ненулевые потоки
        start = node_pos[source]
        end = node_pos[target]

        # Толщина стрелки пропорциональна объёму
        linewidth = 0.5 + flow / 50

        arrow = FancyArrowPatch(start, end,
                                arrowstyle='-|>',
                                color='red' if cost >= 8 else 'orange',
                                linewidth=linewidth,
                                alpha=0.7,
                                mutation_scale=15)
        ax.add_patch(arrow)

        # Подпись посередине стрелки
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2

        # Смещаем подпись от стрелки
        offset_x = 0.5 if start[0] < end[0] else -0.5
        offset_y = 0.3

        ax.text(mid_x + offset_x, mid_y + offset_y,
                f"{flow:.0f} т\n({cost} у.е./т)",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

ax.set_xlim(0, 12)
ax.set_ylim(0, 12)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Оптимальный план снабжения военных баз', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()


# Анализ результатов
print("\n=== Анализ результатов ===")

# Интерпретация решения
print("1. Используемые маршруты:")
for i, (source, target, flow, cost) in enumerate(flows):
    if flow > 0.1:
        print(f"   - {source} → {target}: {flow:.0f} тонн (стоимость: {cost} у.е./т)")

print("\n2. Неиспользуемые маршруты:")
for i, (source, target, flow, cost) in enumerate(flows):
    if flow <= 0.1:
        print(f"   - {source} → {target}: не используется (слишком дорого или невыгодно)")

print(f"\n3. Минимальная общая стоимость: {result.fun:.0f} усл. ед.")

# Военно-логистический анализ
print("\n4. Военно-логистический анализ:")
print("   а) Получение баз:")
for base_name, base_pos in bases.items():
    total_received = sum(flow for source, target, flow, cost in flows
                        if target == base_name and flow > 0.1)
    need = {'Альфа': 120, 'Бета': 180, 'Гамма': 100}[base_name]
    status = "✓ выполнена" if abs(total_received - need) < 0.1 else "✗ не выполнена"
    print(f"      {base_name}: {total_received:.0f}/{need} т {status}")

print("\n   б) Разгрузка складов:")
for wh_name, wh_pos in warehouses.items():
    total_shipped = sum(flow for source, target, flow, cost in flows
                       if source == wh_name and flow > 0.1)
    capacity = {'Склад 1': 150, 'Склад 2': 250}[wh_name]
    status = "✓ полностью" if abs(total_shipped - capacity) < 0.1 else "✗ не полностью"
    print(f"      {wh_name}: отправлено {total_shipped:.0f}/{capacity} т {status}")

print("\n   в) Основные поставщики:")
for base_name in bases.keys():
    suppliers = [(source, flow) for source, target, flow, cost in flows
                if target == base_name and flow > 0.1]
    if suppliers:
        main_supplier = max(suppliers, key=lambda x: x[1])
        print(f"      {base_name}: {main_supplier[0]} ({main_supplier[1]:.0f} т)")

# Анализ устойчивости
print("\n5. Анализ устойчивости:")
print("   а) Если стоимость маршрута 'Склад 2 → Гамма' увеличится до 8 у.е.:")
print("      Этот маршрут станет менее выгодным. Возможно перераспределение")
print("      части груза через Склад 1 → Гамма, что увеличит общую стоимость.")

print("\n   б) Если потребность Базы Альфа увеличится на 20 тонн:")
print("      Общая потребность станет 420 т при запасе 400 т.")
print("      Задача станет несбалансированной. Необходимо:")
print("      - Добавить фиктивный склад с недостающими 20 т")
print("      - Или ввести штраф за недопоставку")
print("      Решение: увеличить поставки с ближайших/дешёвых маршрутов")

# Двойственные переменные (теневые цены)
print("\n6. Теневые цены (множители Лагранжа):")
print("   Эти значения показывают, насколько изменится минимальная стоимость")
print("   при изменении запасов/потребностей на 1 единицу.")
print("   (Для их получения нужно решить двойственную задачу)")



