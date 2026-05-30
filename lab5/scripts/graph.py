import pandas as pd
import matplotlib.pyplot as plt
import os

csv_path = os.path.join(os.path.dirname(__file__), 'results.csv')
df = pd.read_csv(csv_path)

plt.figure(figsize=(10, 6))

for p in sorted(df['Processes'].unique()):
    subset = df[df['Processes'] == p]
    plt.plot(subset['Size'], subset['Time_sec'], marker='o', linewidth=2, label=f'{p} процессов')

plt.title('Результаты на суперкомпьютере "Сергей Королев"', fontsize=14)
plt.xlabel('Размер матрицы (N)', fontsize=12)
plt.ylabel('Время выполнения (сек)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

plot_path = os.path.join(os.path.dirname(__file__), '..', 'lab5_plot.png')
plt.savefig(plot_path, dpi=150)
print(f"✅ График успешно сохранен: {plot_path}")