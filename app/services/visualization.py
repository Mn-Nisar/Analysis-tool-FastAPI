import matplotlib.pyplot as plt
import os

def generate_plot(data, file_name="plot.png"):
    plt.plot(data)
    path = f"app/static/{file_name}"
    plt.savefig(path)
    plt.close()
    return path