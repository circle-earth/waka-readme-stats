from typing import Dict
import numpy as np

import matplotlib.pyplot as plt
from manager_download import DownloadManager as DM
from manager_file import FileManager as FM


MAX_LANGUAGES = 5  # Number of top languages to add to chart, for each year quarter
GRAPH_PATH = f"{FM.ASSETS_DIR}/bar_graph.png"  # Chart saving path.


def smooth_data(y, window_size=5):
    """Smooths data using a moving average with numpy convolve."""
    if len(y) < window_size:
        return y
    box = np.ones(window_size) / window_size
    y_smooth = np.convolve(y, box, mode='same')
    # Fix the edges which convolve doesn't handle perfectly for area charts
    y_smooth[0] = y[0]
    y_smooth[-1] = y[-1]
    return y_smooth


async def create_loc_graph(yearly_data: Dict, save_path: str):
    """
    Draws graph of lines of code written by user by quarters of years.
    Uses a smooth stacked area chart design with a vibrant theme.

    :param yearly_data: GitHub user yearly data.
    :param save_path: Path to save the graph file.
    """
    colors_data = await DM.get_remote_yaml("linguist")
    if colors_data is None:
        colors_data = dict()

    # Prepare data points (X = quarters over time, Y = LOC)
    sorted_years = sorted(yearly_data.keys())
    x_labels = []
    x_indices = []
    
    # Flatten quarters into a continuous timeline
    data_points_count = 0
    raw_indices = []
    
    for i, y in enumerate(sorted_years):
        for q in sorted(yearly_data[y].keys()):
            x_labels.append(f"Q{q} {y}" if q == 1 else f"Q{q}")
            raw_indices.append(data_points_count)
            data_points_count += 1
            
    if data_points_count < 2:
        return # Not enough data to draw

    x_indices = np.array(raw_indices)
    
    actual_y_arrays = {}
    # We need to collect points for all languages that appeared in ANY quarter
    all_langs = set()
    for y in sorted_years:
        for q in yearly_data[y]:
            all_langs.update(yearly_data[y][q].keys())

    # Filter for top languages overall to keep chart clean
    lang_totals = {lang: 0 for lang in all_langs}
    for y in sorted_years:
        for q in yearly_data[y]:
            for lang, vals in yearly_data[y][q].items():
                lang_totals[lang] += vals["add"]
    
    top_langs = sorted(all_langs, key=lambda l: lang_totals[l], reverse=True)[:MAX_LANGUAGES]

    for lang in top_langs:
        actual_y_arrays[lang] = np.zeros(data_points_count)

    for idx, (y, q_idx) in enumerate([(y, q) for y in sorted_years for q in sorted(yearly_data[y].keys())]):
        for lang in top_langs:
            if lang in yearly_data[y][q_idx]:
                actual_y_arrays[lang][idx] = yearly_data[y][q_idx][lang]["add"]

    # Interpolate for more points to make smoothing look better
    x_interp = np.linspace(0, data_points_count - 1, data_points_count * 10)
    y_smoothed_list = []
    lang_names = []
    lang_colors = []

    for lang in top_langs:
        y_values = actual_y_arrays[lang]
        # Linear interpolation first
        y_interp = np.interp(x_interp, x_indices, y_values)
        # Then moving average smoothing
        y_smooth = smooth_data(y_interp, window_size=min(15, len(y_interp)//2))
        y_smoothed_list.append(np.maximum(0, y_smooth))
        lang_names.append(lang)
        lang_colors.append(colors_data.get(lang, {}).get("color", "#888888"))

    # Plotting
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')

    # Stackplot for area chart
    if y_smoothed_list:
        ax.stackplot(x_interp, *y_smoothed_list, labels=lang_names, colors=lang_colors, alpha=0.85, edgecolor='none')

    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#30363d')
    ax.spines['bottom'].set_color('#30363d')
    
    ax.tick_params(axis='x', colors='#8b949e', labelsize=8)
    ax.tick_params(axis='y', colors='#8b949e', labelsize=8)
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels(x_labels, rotation=30, ha='right')
    
    ax.grid(True, linestyle='-', alpha=0.05, color='#ffffff')
    
    # Custom Legend
    if lang_names:
        legend = ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=False, fontsize=9)
        plt.setp(legend.get_texts(), color='#c9d1d9')

    plt.tight_layout()
    plt.savefig(save_path, transparent=True, bbox_inches='tight')
    plt.close(fig)
