"""Plotting functions for model evaluation."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import roc_curve, auc

plt.rcParams.update({"figure.dpi": 150, "font.size": 10})


def plot_roc_curves(model_results, save_path=None):
    """ROC curves for all models."""
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = plt.cm.Set2(np.linspace(0, 1, max(len(model_results), 8)))

    for i, (name, (y_true, y_prob)) in enumerate(model_results.items()):
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        ax.plot(fpr, tpr, color=colors[i], lw=2, label=f"{name} (AUC={auc(fpr, tpr):.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random (AUC=0.500)")
    ax.set(xlabel="False Positive Rate", ylabel="True Positive Rate",
           title="ROC Curves: ML Models vs Magic Formula Baseline")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig


def plot_shap_summary(model, X_test, feature_names, model_name="XGBoost", save_path=None):
    """SHAP beeswarm plot showing feature importance."""
    import shap
    explainer = shap.TreeExplainer(model)
    X = X_test if isinstance(X_test, pd.DataFrame) else pd.DataFrame(X_test, columns=feature_names)
    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]

    fig, ax = plt.subplots(figsize=(10, 6))
    shap.summary_plot(shap_values, X, feature_names=feature_names, show=False, max_display=15)
    plt.title(f"SHAP Feature Importance: {model_name}")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    return plt.gcf()


def plot_feature_correlation(df, feature_cols, save_path=None):
    """Correlation heatmap of features."""
    available = [c for c in feature_cols if c in df.columns]
    corr = df[available].corr()

    fig, ax = plt.subplots(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1, annot_kws={"size": 7})
    ax.set_title("Feature Correlation Matrix")
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig


def plot_metrics_table(metrics_df, save_path=None):
    """Metrics comparison table as a styled image."""
    metrics = [m for m in ["roc_auc", "spearman_ic", "precision_at_k", "f1"] if m in metrics_df.columns]

    rows = []
    for model in metrics_df["model"].unique():
        md = metrics_df[metrics_df["model"] == model]
        row = {"Model": model}
        for fs in ["MF_only", "All_features"]:
            fs_data = md[md["feature_set"] == fs]
            for m in metrics:
                val = fs_data.iloc[0].get(m) if not fs_data.empty else None
                row[f"{m}\n({fs})"] = f"{val:.3f}" if val is not None else "N/A"
        rows.append(row)

    table_df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(14, len(rows) * 0.6 + 1.5))
    ax.axis("off")

    table = ax.table(cellText=table_df.values, colLabels=table_df.columns.tolist(),
                     cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)

    # Header styling
    for j in range(len(table_df.columns)):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Alternating row colors
    for i in range(len(rows)):
        for j in range(len(table_df.columns)):
            table[i + 1, j].set_facecolor("#D9E2F3" if i % 2 == 0 else "white")

    ax.set_title("Model Performance: Layer A (MF) vs Layer B (All Features)",
                 fontsize=12, fontweight="bold", pad=20)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    return fig
