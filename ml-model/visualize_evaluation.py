import os

import pandas as pd
import matplotlib.pyplot as plt


RESULTS_FILE = "evaluation_results.csv"

OUTPUT_DIRECTORY = "evaluation_plots"


def load_results():

    if not os.path.exists(RESULTS_FILE):

        raise FileNotFoundError(
            f"Evaluation results not found: {RESULTS_FILE}"
        )

    results = pd.read_csv(
        RESULTS_FILE
    )

    if results.empty:

        raise ValueError(
            "Evaluation results file is empty."
        )

    return results


def create_output_directory():

    os.makedirs(
        OUTPUT_DIRECTORY,
        exist_ok=True
    )


def plot_precision(results):

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        results["K"],
        results["Content-Based Precision@K"],
        marker="o",
        label="Content-Based"
    )

    plt.plot(
        results["K"],
        results["Hybrid Precision@K"],
        marker="o",
        label="Hybrid"
    )

    plt.title(
        "Precision@K Comparison"
    )

    plt.xlabel(
        "K"
    )

    plt.ylabel(
        "Precision"
    )

    plt.xticks(
        results["K"]
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    output_file = os.path.join(
        OUTPUT_DIRECTORY,
        "precision_at_k.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


def plot_recall(results):

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        results["K"],
        results["Content-Based Recall@K"],
        marker="o",
        label="Content-Based"
    )

    plt.plot(
        results["K"],
        results["Hybrid Recall@K"],
        marker="o",
        label="Hybrid"
    )

    plt.title(
        "Recall@K Comparison"
    )

    plt.xlabel(
        "K"
    )

    plt.ylabel(
        "Recall"
    )

    plt.xticks(
        results["K"]
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    output_file = os.path.join(
        OUTPUT_DIRECTORY,
        "recall_at_k.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


def plot_hit_rate(results):

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        results["K"],
        results["Content-Based Hit Rate@K"],
        marker="o",
        label="Content-Based"
    )

    plt.plot(
        results["K"],
        results["Hybrid Hit Rate@K"],
        marker="o",
        label="Hybrid"
    )

    plt.title(
        "Hit Rate@K Comparison"
    )

    plt.xlabel(
        "K"
    )

    plt.ylabel(
        "Hit Rate"
    )

    plt.xticks(
        results["K"]
    )

    plt.grid(
        True,
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    output_file = os.path.join(
        OUTPUT_DIRECTORY,
        "hit_rate_at_k.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


def create_summary_table(results):

    summary = results[
        [
            "K",
            "Content-Based Precision@K",
            "Content-Based Recall@K",
            "Content-Based Hit Rate@K",
            "Hybrid Precision@K",
            "Hybrid Recall@K",
            "Hybrid Hit Rate@K"
        ]
    ].copy()

    summary = summary.round(
        4
    )

    output_file = os.path.join(
        OUTPUT_DIRECTORY,
        "evaluation_summary.csv"
    )

    summary.to_csv(
        output_file,
        index=False
    )

    print(
        f"Saved: {output_file}"
    )

    return summary


def print_summary(summary):

    print(
        "\n" + "=" * 80
    )

    print(
        "EVALUATION SUMMARY"
    )

    print(
        "=" * 80
    )

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        "\n" + "=" * 80
    )


def main():

    print(
        "\n" + "=" * 80
    )

    print(
        "MOVIE RECOMMENDATION SYSTEM"
    )

    print(
        "EVALUATION VISUALIZATION"
    )

    print(
        "=" * 80
    )

    # Load results

    results = load_results()

    print(
        f"\nLoaded evaluation results: "
        f"{len(results)} rows"
    )

    # Create directory

    create_output_directory()

    # Generate graphs

    print(
        "\nGenerating evaluation graphs..."
    )

    plot_precision(
        results
    )

    plot_recall(
        results
    )

    plot_hit_rate(
        results
    )

    # Create summary

    summary = create_summary_table(
        results
    )

    # Print summary

    print_summary(
        summary
    )

    print(
        "\nEvaluation visualization completed."
    )

    print(
        f"Graphs saved in: "
        f"{OUTPUT_DIRECTORY}/"
    )


if __name__ == "__main__":

    main()