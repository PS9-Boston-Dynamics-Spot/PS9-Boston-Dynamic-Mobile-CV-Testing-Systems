import matplotlib.pyplot as plt
import numpy as np
import math

parameters = {
    "min_value": 20.0,
    "max_value": 25.0,
    "min_score": 0.0,
    "left_scale": 7.0,
    "left_power": 2.0,
    "right_scale": 7.0,
    "right_power": 2.0,
}

score_function_str = "1 if min_value <= x <= max_value else min_score+(1-min_score)*exp(-pow((min_value-x)/left_scale,left_power)) if x < min_value else min_score+(1-min_score)*exp(-pow((x-max_value)/right_scale,right_power))"

score_function = lambda x: eval(
    score_function_str, {"exp": math.exp, "pow": math.pow, **parameters, "x": x}
)

x_min = parameters["min_value"] - 3 * parameters["left_scale"]
x_max = parameters["max_value"] + 3 * parameters["right_scale"]
x_values = np.linspace(x_min, x_max, 500)
y_values = [score_function(x) for x in x_values]

test_points = [5, 8, 10, 12, 14, 15, 20, 35, 50, 55, 60, 65, 70]

plt.figure(figsize=(10, 5))
plt.plot(x_values, y_values, label="Score Funktion")
plt.scatter(
    test_points,
    [score_function(x) for x in test_points],
    color="red",
    label="Testpunkte",
)
plt.xlabel("x")
plt.ylabel("Score")
plt.title("Soft-Interval Score Funktion")
plt.grid(True)
plt.legend()

plt.savefig("score_function_plot.png", dpi=300)
print("Plot gespeichert als score_function_plot.png")
