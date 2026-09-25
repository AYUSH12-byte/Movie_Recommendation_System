import os

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_FILE = "evaluation_results_v2.csv"

OUTPUT_DIR = "evaluation_plots_v2"

SUMMARY_FILE = os.path.join(
    OUTPUT_DIR,
    "evaluation_summary_v2.csv"
)


# ============================================================
# LOAD RESULTS
# ============================================================

def load_results():

    if not os.path.exists(RESULTS_FILE):

        raise FileNotFoundError(
            f"Evaluation results not found: "
            f"{RESULTS_FILE}"
        )

    results = pd.read_csv(
        RESULTS_FILE
    )

    required_columns = {
        "model",
        "k",
        "precision",
        "recall",
        "hit_rate",
        "f1"
    }

    missing_columns = (
        required_columns
        - set(results.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing columns in evaluation results: "
            f"{missing_columns}"
        )

    return results


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

def create_output_directory():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


# ============================================================
# CREATE SUMMARY
# ============================================================

def create_summary(results):

    summary = (
        results
        .groupby(
            [
                "model",
                "k"
            ]
        )[
            [
                "precision",
                "recall",
                "hit_rate",
                "f1"
            ]
        ]
        .mean()
        .reset_index()
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    return summary


# ============================================================
# GENERIC METRIC PLOT
# ============================================================

def plot_metric(
    summary,
    metric,
    title,
    ylabel,
    filename
):

    plt.figure(
        figsize=(9, 6)
    )

    for model in summary["model"].unique():

        model_data = (
            summary[
                summary["model"] == model
            ]
            .sort_values("k")
        )

        plt.plot(
            model_data["k"],
            model_data[metric],
            marker="o",
            linewidth=2,
            label=model
        )

    plt.xlabel(
        "Number of Recommendations (K)"
    )

    plt.ylabel(
        ylabel
    )

    plt.title(
        title
    )

    plt.xticks(
        sorted(
            summary["k"].unique()
        )
    )

    plt.ylim(
        0,
        1
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Created: {output_path}"
    )


# ============================================================
# CREATE ALL PLOTS
# ============================================================

def create_plots(summary):

    print(
        "\nGenerating evaluation graphs..."
    )

    plot_metric(
        summary,
        metric="precision",
        title="Precision@K Comparison",
        ylabel="Precision",
        filename="precision_at_k_v2.png"
    )

    plot_metric(
        summary,
        metric="recall",
        title="Recall@K Comparison",
        ylabel="Recall",
        filename="recall_at_k_v2.png"
    )

    plot_metric(
        summary,
        metric="hit_rate",
        title="Hit Rate@K Comparison",
        ylabel="Hit Rate",
        filename="hit_rate_at_k_v2.png"
    )

    plot_metric(
        summary,
        metric="f1",
        title="F1@K Comparison",
        ylabel="F1 Score",
        filename="f1_at_k_v2.png"
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(summary):

    print("\n")

    print("=" * 70)

    print(
        "EVALUATION VISUALIZATION SUMMARY"
    )

    print("=" * 70)

    for model in summary["model"].unique():

        print(
            f"\nModel: {model}"
        )

        model_data = (
            summary[
                summary["model"] == model
            ]
            .sort_values("k")
        )

        for _, row in model_data.iterrows():

            k = int(
                row["k"]
            )

            print(
                f"\nK = {k}"
            )

            print(
                f"Precision@{k}: "
                f"{row['precision']:.4f}"
            )

            print(
                f"Recall@{k}: "
                f"{row['recall']:.4f}"
            )

            print(
                f"Hit Rate@{k}: "
                f"{row['hit_rate']:.4f}"
            )

            print(
                f"F1@{k}: "
                f"{row['f1']:.4f}"
            )

    print(
        "\n" + "=" * 70
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "MOVIE RECOMMENDATION SYSTEM"
    )

    print(
        "EVALUATION VISUALIZATION V2"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    create_output_directory()

    # --------------------------------------------------------
    # Load evaluation results
    # --------------------------------------------------------

    print(
        "\nLoading evaluation results..."
    )

    results = load_results()

    print(
        f"Rows loaded: {len(results):,}"
    )

    # --------------------------------------------------------
    # Create summary
    # --------------------------------------------------------

    summary = create_summary(
        results
    )

    print(
        f"Summary saved to: "
        f"{SUMMARY_FILE}"
    )

    # --------------------------------------------------------
    # Create charts
    # --------------------------------------------------------

    create_plots(
        summary
    )

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print_summary(
        summary
    )

    print(
        "\nVisualization completed successfully."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()