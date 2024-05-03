from matplotlib import pyplot as plt

from modules.common.src.model import DAG


def show_histogram_chart(dag: DAG, parameter_name: str, include_zero: bool, title: str = '', x_label: str = '', y_label: str = 'count', bins: int = 20) -> None:
    begin = 0 if include_zero else 1
    values = [edge[parameter_name] for edge in dag.edges[begin:]]
    plt.title(title)
    plt.hist(values, bins)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()
