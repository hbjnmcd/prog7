import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Целевая функция (для максимизации меняем знак)
c = [-8000, -12000]  # Минимизируем -P

# Матрица ограничений-неравенств A_ub @ x <= b_ub
A_ub = [
    [2, 3],    # Процессорное время
    [4, 6],    # Оперативная память
    [1, 2]     # Аккумуляторы
]
b_ub = [240, 480, 150]

# Границы переменных (x >= 0)
bounds = [(0, None), (0, None)]

# Решение задачи
result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

# Вывод результатов
print("=== Задача оптимизации производства электроники ===")
print(f"Статус: {result.message}")
print(f"Оптимальное количество смартфонов: {result.x[0]:.0f} шт.")
print(f"Оптимальное количество планшетов: {result.x[1]:.0f} шт.")
print(f"Максимальная прибыль: {-result.fun:.0f} руб.")

# Анализ результатов
print("\n=== Анализ результатов ===")
print(f"1. Оптимальный план: {result.x[0]:.0f} смартфонов, {result.x[1]:.0f} планшетов")
print(f"2. Максимальная прибыль: {-result.fun:.0f} руб.")

# Анализ использования ресурсов
used_cpu = 2*result.x[0] + 3*result.x[1]
used_ram = 4*result.x[0] + 6*result.x[1]
used_bat = result.x[0] + 2*result.x[1]

print(f"\n3. Использование ресурсов:")
print(f"   - Процессорное время: {used_cpu:.0f} / 240 часов ({used_cpu/240*100:.1f}%)")
print(f"   - Оперативная память: {used_ram:.0f} / 480 ГБ ({used_ram/480*100:.1f}%)")
print(f"   - Аккумуляторы: {used_bat:.0f} / 150 шт. ({used_bat/150*100:.1f}%)")

# Определяем активные ограничения
print(f"\n4. Активные ограничения (используются полностью):")
if abs(used_cpu - 240) < 0.1:
    print("   - Процессорное время")
if abs(used_ram - 480) < 0.1:
    print("   - Оперативная память")
if abs(used_bat - 150) < 0.1:
    print("   - Аккумуляторы")

# Анализ чувствительности
print(f"\n5. Чувствительность:")
print("   а) При увеличении процессорного времени на 10 часов:")
print(f"      Новая прибыль ≈ {-result.fun + 10 * result.slack[0]:.0f} руб.")
print(f"      Прирост: {10 * result.slack[0]:.0f} руб.")

# Находим наиболее дефицитный ресурс
shadow_prices = result.slack[:3]
resource_names = ["Процессорное время", "Оперативная память", "Аккумуляторы"]
most_deficient = resource_names[np.argmax(shadow_prices)]
print(f"   б) Наиболее дефицитный ресурс: {most_deficient}")


fig, ax = plt.subplots(figsize=(10, 8))

# Диапазон значений x1
x1 = np.linspace(0, 120, 400)

# Границы ограничений (x2 через x1)
x2_cpu = (240 - 2*x1) / 3      # 2x1 + 3x2 <= 240
x2_ram = (480 - 4*x1) / 6      # 4x1 + 6x2 <= 480
x2_bat = (150 - x1) / 2        # x1 + 2x2 <= 150

# Построение прямых ограничений
ax.plot(x1, x2_cpu, 'r-', linewidth=2, label='Процессорное время: $2x_1 + 3x_2 \\leq 240$')
ax.plot(x1, x2_ram, 'g-', linewidth=2, label='Оперативная память: $4x_1 + 6x_2 \\leq 480$')
ax.plot(x1, x2_bat, 'b-', linewidth=2, label='Аккумуляторы: $x_1 + 2x_2 \\leq 150$')

# Вершины допустимой области (находим пересечения)
vertices = []
# Пересечение с осями
vertices.append([0, 0])
vertices.append([0, min(80, 75)])  # min(240/3, 150/2)
vertices.append([min(120, 150), 0])  # min(240/2, 150/1)

# Пересечения ограничений
# CPU и RAM параллельны (второе ограничение избыточно)
# CPU и Battery
x1_cpu_bat = (2*150 - 240) / (2*2 - 3)  # Решаем систему
x2_cpu_bat = (240 - 2*x1_cpu_bat) / 3
if x1_cpu_bat >= 0 and x2_cpu_bat >= 0:
    vertices.append([x1_cpu_bat, x2_cpu_bat])

# RAM и Battery
x1_ram_bat = (4*150 - 480) / (4*2 - 6)  # Решаем систему
x2_ram_bat = (480 - 4*x1_ram_bat) / 6
if x1_ram_bat >= 0 and x2_ram_bat >= 0:
    vertices.append([x1_ram_bat, x2_ram_bat])

# Оставляем уникальные вершины и сортируем
vertices = np.array(sorted(set(tuple(v) for v in vertices if v[0] >= 0 and v[1] >= 0)))

# Закрашивание допустимой области
polygon = Polygon(vertices, alpha=0.2, color='yellow', label='Допустимая область')
ax.add_patch(polygon)

# Оптимальная точка (из решения)
optimal_x1 = result.x[0]
optimal_x2 = result.x[1]
ax.plot(optimal_x1, optimal_x2, 'ro', markersize=10, label=f'Оптимум: ({optimal_x1:.0f}, {optimal_x2:.0f})')

# Линии уровня целевой функции (изопрофиты)
profit_levels = [200000, 400000, 600000, -result.fun]
for level in profit_levels:
    x2_profit = (level - 8000*x1) / 12000
    ax.plot(x1, x2_profit, 'k--', alpha=0.5, linewidth=0.8)

ax.set_xlabel('$x_1$ (смартфоны, шт.)', fontsize=12)
ax.set_ylabel('$x_2$ (планшеты, шт.)', fontsize=12)
ax.set_title('Задача оптимизации производства: Геометрическое представление', fontsize=14)
ax.set_xlim(0, 130)
ax.set_ylim(0, 90)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
plt.show()