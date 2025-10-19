# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
from scipy import stats
import warnings
import os

warnings.filterwarnings('ignore')

plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'DejaVu Sans'
sns.set_palette("husl")

# =============================================================
# ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ
# =============================================================

df = pd.read_csv(r"Новая форма.csv", encoding='utf-8')

print("=" * 50)
print("АНАЛИЗ ДАННЫХ ОПРОСА")
print("=" * 50)

print("Размерность данных:", df.shape)

scenario_a_columns = df.columns[4:19]
scenario_b_columns = df.columns[19:34]

print(f"Сценарий А: {len(scenario_a_columns)} вопросов")
print(f"Сценарий Б: {len(scenario_b_columns)} вопросов")

rating_mapping = {
    'Strongly disagree | Мүлде келіспеймін | Совершенно не согласен': 1,
    'Disagree | Келіспеймін | Не согласен': 2,
    'Neutral | Бейтарап | Нейтрален': 3,
    'Agree | Келісемін | Согласен': 4,
    'Strongly agree | Толықтай келісемін | Полностью согласен': 5
}


def safe_convert_ratings(df_columns, rating_map):
    converted_data = pd.DataFrame()
    for col in df_columns:
        converted_data[col] = df[col].astype(str).replace(rating_map)
        unique_vals = converted_data[col].unique()
        non_numeric = [val for val in unique_vals if not str(val).isdigit()]
        if non_numeric:
            print(f"⚠️ Внимание: в колонке {col[:30]}... найдены нечисловые значения: {non_numeric[:3]}")
            converted_data[col] = pd.to_numeric(converted_data[col], errors='coerce')
    return converted_data


print("\nПреобразование сценария А...")
df_scenario_a = safe_convert_ratings(scenario_a_columns, rating_mapping)

print("\nПреобразование сценария Б...")
df_scenario_b = safe_convert_ratings(scenario_b_columns, rating_mapping)

df_demographic = pd.DataFrame()
df_demographic['Age'] = pd.to_numeric(df['  Age / Жасы / Возраст '], errors='coerce')
df_demographic['Gender'] = df['  Gender / Жынысы / Пол  ']
df_demographic['Field'] = df['  Field of study / Profession / Оқу бағыты немесе мамандығы / Сфера обучения или профессия:  ']

question_names = [
    'Fair treatment',
    'Fair criteria',
    'Chance to be heard',
    'Similar cases',
    'Trust in practice',
    'Care about users',
    'Comfort with decisions',
    'Problems handled',
    'Know responsible',
    'Clear challenge',
    'Human oversight',
    'Follow-up',
    'End-users involved',
    'Appeal process',
    'Quality control'
]

print(f"\nОбработано {len(df)} ответов")

# =============================================================
# АНАЛИЗ СЦЕНАРИЕВ
# =============================================================

mean_scenario_a = df_scenario_a.mean(numeric_only=True)
mean_scenario_b = df_scenario_b.mean(numeric_only=True)

overall_mean_a = mean_scenario_a.mean()
overall_mean_b = mean_scenario_b.mean()

print(f"\nОбщий средний балл:")
print(f"Сценарий А: {overall_mean_a:.2f}")
print(f"Сценарий Б: {overall_mean_b:.2f}")
print(f"Разница: {overall_mean_b - overall_mean_a:+.2f}")

# =============================================================
# ГРАФИК 1: Сравнение средних значений по вопросам
# =============================================================

plt.figure(figsize=(14, 10))
x_pos = np.arange(len(question_names))
width = 0.35

bars1 = plt.bar(x_pos - width/2, mean_scenario_a.values, width,
                label='Сценарий А', alpha=0.8, color='skyblue', edgecolor='black')
bars2 = plt.bar(x_pos + width/2, mean_scenario_b.values, width,
                label='Сценарий Б', alpha=0.8, color='lightcoral', edgecolor='black')

plt.xlabel('Вопросы')
plt.ylabel('Средний рейтинг')
plt.title('Сравнение средних баллов: Сценарий А vs Сценарий Б', fontsize=14, fontweight='bold')
plt.xticks(x_pos, [f'Q{i+1}' for i in range(len(question_names))], rotation=45, ha='right')
plt.ylim(0, 5.5)
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                 f'{height:.2f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.axhline(y=overall_mean_a, color='blue', linestyle='--', alpha=0.7)
plt.axhline(y=overall_mean_b, color='red', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("comparison_AB.png", dpi=300)
plt.close()

# =============================================================
# ДОПОЛНИТЕЛЬНЫЕ ВИЗУАЛИЗАЦИИ
# =============================================================

save_folder = os.getcwd()

# --- 1. Тепловая карта корреляций ---
plt.figure(figsize=(10, 8))
corr_matrix = df_scenario_b.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdPu", vmin=0.3, vmax=0.93)
plt.title("Корреляция между ответами на вопросы", fontsize=14, fontweight="bold", pad=20)
plt.xlabel("Номер вопроса")
plt.ylabel("Номер вопроса")
plt.tight_layout()
plt.savefig(os.path.join(save_folder, "correlation_matrix.png"), dpi=300)
plt.close()

# --- 2. Распределение ответов по каждому вопросу ---
fig, axes = plt.subplots(5, 3, figsize=(18, 10))
axes = axes.flatten()
plt.suptitle("Распределение ответов по всем вопросам", fontsize=16, fontweight='bold', y=1.02)

for i, col in enumerate(df_scenario_b.columns):
    counts = df_scenario_b[col].value_counts().sort_index()
    axes[i].bar(counts.index, counts.values, color=['#FF6F61', '#FFA631', '#FFD700', '#7EC8E3', '#3CB371'])
    axes[i].set_title(f"Q{i+1}: {question_names[i]}", fontsize=10, fontweight='bold')
    axes[i].set_xlabel("")
    axes[i].set_ylabel("Количество")
    for x, y in zip(counts.index, counts.values):
        axes[i].text(x, y + 0.2, str(y), ha='center', va='bottom', fontsize=9, fontweight='bold')

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig(os.path.join(save_folder, "answers_distribution.png"), dpi=300, bbox_inches='tight')
plt.close()

# --- 3. Средние рейтинги по всем вопросам ---
mean_ratings = df_scenario_b.mean().sort_values(ascending=False)
plt.figure(figsize=(12, 7))
bars = plt.barh([f"Q{i+1}: {question_names[i]}" for i in mean_ratings.index.argsort()[::-1]],
                mean_ratings.sort_values(), color=sns.color_palette("viridis", len(mean_ratings)))
for bar, val in zip(bars, mean_ratings.sort_values()):
    plt.text(val + 0.05, bar.get_y() + bar.get_height() / 2, f"{val:.2f}",
             va='center', fontsize=10, fontweight='bold')

plt.title("Средние оценки справедливости и доверия к системе", fontsize=14, fontweight='bold')
plt.xlabel("Средний рейтинг (1-5)")
plt.tight_layout()
plt.savefig(os.path.join(save_folder, "mean_ratings.png"), dpi=300, bbox_inches='tight')
plt.close()

print(f"\n✅ Все графики сохранены в папку: {save_folder}")

# =============================================================
# АНАЛИЗ ТЕКСТОВЫХ ОТВЕТОВ (из твоего исходного кода)
# =============================================================

print("\n" + "=" * 50)
print("АНАЛИЗ ТЕКСТОВЫХ ОТВЕТОВ")
print("=" * 50)

text_columns = [
    '  What made this system feel more or less fair or trustworthy? | Бұл жүйенің әділ немесе сенімді болуына не әсер етті? | Что сделало эту систему более или менее справедливой и достоверной?  ',
    '   Which feature most improves accountability? | Қай элемент жүйенің жауапкершілігін арттырады? | Какой элемент лучше всего повышает ответственность системы?  '
]

all_text = ''
for col in text_columns:
    if col in df.columns:
        non_empty = df[col].dropna().astype(str)
        print(f"Колонка '{col[:30]}...': {len(non_empty)} ответов")
        all_text += ' '.join(non_empty) + ' '

if all_text.strip():
    stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                 'a', 'an', 'the', 'some', 'any', 'my', 'your', 'his', 'her', 'our', 'their',
                 'system', 'process', 'would', 'should', 'could', 'please', 'select', 'agree'}

    wordcloud = WordCloud(width=1000, height=500, background_color='white',
                          colormap='viridis', max_words=80, stopwords=stopwords,
                          relative_scaling=0.4, min_font_size=8).generate(all_text)

    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Облако слов из текстовых ответов', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig("wordcloud.png", dpi=300)
    plt.close()

print("\n" + "=" * 50)
print("АНАЛИЗ ЗАВЕРШЕН!")
print("=" * 50)
