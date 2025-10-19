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
# LOAD AND PREPARE DATA
# =============================================================

df = pd.read_csv(r"Новая форма.csv", encoding='utf-8')

print("=" * 50)
print("SURVEY DATA ANALYSIS")
print("=" * 50)

print("Dataset shape:", df.shape)

scenario_a_columns = df.columns[4:19]
scenario_b_columns = df.columns[19:34]

print(f"Scenario A: {len(scenario_a_columns)} questions")
print(f"Scenario B: {len(scenario_b_columns)} questions")

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
            print(f"⚠️ Warning: column {col[:30]} contains non-numeric values: {non_numeric[:3]}")
            converted_data[col] = pd.to_numeric(converted_data[col], errors='coerce')
    return converted_data

print("\nConverting Scenario A...")
df_scenario_a = safe_convert_ratings(scenario_a_columns, rating_mapping)

print("\nConverting Scenario B...")
df_scenario_b = safe_convert_ratings(scenario_b_columns, rating_mapping)

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

print(f"\nProcessed {len(df)} responses")

# =============================================================
# CALCULATE MEANS AND COMPARISONS
# =============================================================

mean_scenario_a = df_scenario_a.mean(numeric_only=True)
mean_scenario_b = df_scenario_b.mean(numeric_only=True)
overall_mean_a = mean_scenario_a.mean()
overall_mean_b = mean_scenario_b.mean()

print(f"\nAverage scores:")
print(f"Scenario A: {overall_mean_a:.2f}")
print(f"Scenario B: {overall_mean_b:.2f}")
print(f"Difference: {overall_mean_b - overall_mean_a:+.2f}")

save_folder = os.getcwd()

# =============================================================
# GRAPH 1 — Comparison A vs B
# =============================================================

plt.figure(figsize=(14, 10))
x_pos = np.arange(len(question_names))
width = 0.35

bars1 = plt.bar(x_pos - width/2, mean_scenario_a.values, width,
                label='Scenario A', alpha=0.8, color='skyblue', edgecolor='black')
bars2 = plt.bar(x_pos + width/2, mean_scenario_b.values, width,
                label='Scenario B', alpha=0.8, color='lightcoral', edgecolor='black')

plt.xlabel('Questions')
plt.ylabel('Average rating')
plt.title('Comparison of Average Scores: Scenario A vs Scenario B', fontsize=14, fontweight='bold')
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
plt.savefig(os.path.join(save_folder, "comparison_AB.png"), dpi=300)
plt.close()

# =============================================================
# GRAPH 2 — Difference (B - A)
# =============================================================

plt.figure(figsize=(14, 8))
difference = mean_scenario_b.values - mean_scenario_a.values

# Убираем NaN, заменяем их нулями (или можно использовать np.nan_to_num)
difference = np.nan_to_num(difference, nan=0.0)

bars = plt.bar(np.arange(len(question_names)), difference,
               color='#2E8B57', alpha=0.9, edgecolor='black')

plt.xlabel('')
plt.ylabel('Difference (B - A)', fontsize=12)
plt.title('Difference in Average Scores: Scenario B minus Scenario A',
          fontsize=16, fontweight='bold', pad=20)
plt.xticks(np.arange(len(question_names)), [f'Q{i+1}' for i in range(len(question_names))],
           rotation=45, ha='right')
plt.grid(True, alpha=0.3, axis='y')

for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.02,
             f"{height:+.2f}", ha='center', va='bottom',
             fontsize=11, fontweight='bold', color='darkgreen')

y_max = max(difference) if np.isfinite(max(difference)) else 1
plt.ylim(0, y_max + 0.2)

plt.tight_layout()
plt.savefig(os.path.join(save_folder, "difference_AB.png"), dpi=300, bbox_inches='tight')
plt.close()


# =============================================================
# GRAPH 3 — Correlation Heatmap
# =============================================================

plt.figure(figsize=(10, 8))
corr_matrix = df_scenario_b.corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdPu", vmin=0.3, vmax=0.93)
plt.title("Correlation Between Question Responses", fontsize=14, fontweight="bold", pad=20)
plt.xlabel("Question number")
plt.ylabel("Question number")
plt.tight_layout()
plt.savefig(os.path.join(save_folder, "correlation_matrix.png"), dpi=300)
plt.close()

# =============================================================
# GRAPH 4 — Distribution of Answers
# =============================================================

fig, axes = plt.subplots(5, 3, figsize=(18, 10))
axes = axes.flatten()
plt.suptitle("Distribution of Answers per Question", fontsize=16, fontweight='bold', y=1.02)

for i, col in enumerate(df_scenario_b.columns):
    counts = df_scenario_b[col].value_counts().sort_index()
    axes[i].bar(counts.index, counts.values, color=['#FF6F61', '#FFA631', '#FFD700', '#7EC8E3', '#3CB371'])
    axes[i].set_title(f"Q{i+1}: {question_names[i]}", fontsize=10, fontweight='bold')
    axes[i].set_xlabel("")
    axes[i].set_ylabel("Count")
    for x, y in zip(counts.index, counts.values):
        axes[i].text(x, y + 0.2, str(y), ha='center', va='bottom', fontsize=9, fontweight='bold')

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig(os.path.join(save_folder, "answers_distribution.png"), dpi=300, bbox_inches='tight')
plt.close()

# =============================================================
# GRAPH 5 — Average Ratings
# =============================================================

mean_ratings = df_scenario_b.mean().sort_values(ascending=False)
plt.figure(figsize=(12, 7))
bars = plt.barh([f"Q{i+1}: {question_names[i]}" for i in mean_ratings.index.argsort()[::-1]],
                mean_ratings.sort_values(), color=sns.color_palette("viridis", len(mean_ratings)))
for bar, val in zip(bars, mean_ratings.sort_values()):
    plt.text(val + 0.05, bar.get_y() + bar.get_height() / 2, f"{val:.2f}",
             va='center', fontsize=10, fontweight='bold')

plt.title("Average Fairness and Trust Ratings", fontsize=14, fontweight='bold')
plt.xlabel("Average rating (1–5)")
plt.tight_layout()
plt.savefig(os.path.join(save_folder, "mean_ratings.png"), dpi=300, bbox_inches='tight')
plt.close()

# =============================================================
# WORD CLOUD — Text Responses
# =============================================================

print("\n" + "=" * 50)
print("TEXT RESPONSE ANALYSIS")
print("=" * 50)

text_columns = [
    '  What made this system feel more or less fair or trustworthy? | Бұл жүйенің әділ немесе сенімді болуына не әсер етті? | Что сделало эту систему более или менее справедливой и достоверной?  ',
    '   Which feature most improves accountability? | Қай элемент жүйенің жауапкершілігін арттырады? | Какой элемент лучше всего повышает ответственность системы?  '
]

all_text = ''
for col in text_columns:
    if col in df.columns:
        non_empty = df[col].dropna().astype(str)
        print(f"Column '{col[:30]}...': {len(non_empty)} responses")
        all_text += ' '.join(non_empty) + ' '

if all_text.strip():
    stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                 'a', 'an', 'some', 'any', 'my', 'your', 'his', 'her', 'our', 'their',
                 'system', 'process', 'please', 'agree'}

    wordcloud = WordCloud(width=1000, height=500, background_color='white',
                          colormap='viridis', max_words=80, stopwords=stopwords,
                          relative_scaling=0.4, min_font_size=8).generate(all_text)

    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud from Open-Ended Responses', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(save_folder, "wordcloud.png"), dpi=300)
    plt.close()

print(f"\n✅ All graphs saved to: {save_folder}")
print("\n" + "=" * 50)
print("ANALYSIS COMPLETED!")
print("=" * 50)
