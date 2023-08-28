from scipy.io import wavfile
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse


def make_lock_in_signals(lock_in_freq, sample_rate, n_samples):
    """Needed to do the lock-in amplification."""
    offset = 0
    sine = np.array([np.sin((i - offset) / sample_rate * lock_in_freq * 2 * np.pi) for i in range(n_samples)])
    cosine = np.array([np.cos((i) / sample_rate * lock_in_freq * 2 * np.pi) for i in range(n_samples)])
    return sine, cosine


def calc_signal_strength(file_name, lock_in_freq, integration_time_s=1.):
    """Multiply input data with lock-in sines and calculate the vector length and angle of the filtered signal.

    Fun fact: the signal strength (r) is still found if it is out of phase from integration periods to integration
    period.
    """
    sample_rate, data = wavfile.read(file_name)
    sine, cosine = make_lock_in_signals(lock_in_freq, sample_rate, len(data))

    integration_segment_size = round(integration_time_s * sample_rate)

    # May skip last segment or filter badly due to too short integration time.
    number_of_integration_segments = round(len(data) / integration_segment_size)

    r_list = []
    theta_deg_list = []
    for segment_counter in range(number_of_integration_segments):
        segment_start = integration_segment_size * segment_counter
        segment_end = integration_segment_size * (segment_counter + 1)
        if segment_counter == number_of_integration_segments:  # Off by one?
            segment_end = len(data)
        data_times_sine = pd.Series(sine * data).iloc[segment_start:segment_end]
        data_times_cosine = pd.Series(cosine * data).iloc[segment_start:segment_end]
        r = np.sqrt(data_times_sine.mean()**2 + data_times_cosine.mean()**2)
        theta_rad = np.arctan(data_times_cosine.mean() / data_times_sine.mean())
        theta_deg = theta_rad * 180 / np.pi
        r_list.append(r)
        theta_deg_list.append(theta_deg)
    return r_list, theta_deg_list


def plot_filtered_signal(lock_in_freq, r_list, theta_deg_list=None, save_to_file=False, r_plot_max=None,
                         output_file_base="analysis"):
    fig, r_ax = plt.subplots()
    theta_deg_ax = r_ax.twinx()
    r_ax.plot(pd.Series(r_list), label="r")
    r_ax.set_ylabel("r / arbitrary units")
    if theta_deg_list:
        theta_deg_ax.plot(pd.Series(theta_deg_list), label="theta", linewidth=0.5, color="C1")
        theta_deg_ax.set_ylabel("theta / deg")
    if r_plot_max:
        r_ax.set_ylim(0, r_plot_max)
    r_ax.set_xlabel("Integration segment #")
    plt.title(f"{lock_in_freq:.2f} Hz")
    if save_to_file:
        fig.savefig(f"{output_file_base}_{lock_in_freq:07.2f}.png")
    else:
        plt.show()
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform lock-in amplification on the input file. Plot or save result "
                                                 "as PNG.")
    parser.add_argument("--input_file_name", required=True, help='Input file name. E.g. "440_Hz.wav".')
    parser.add_argument('--lock_in_freq', type=float, required=True, help='Which frequency to amplify. E.g. "440.0".')
    parser.add_argument("--integration_time_s", type=float,
                        help='Integration time in seconds. E.g. "1.0". Default 1 s.', default=1.)
    parser.add_argument("--save_png", action='store_true', help="Save plot to PNG file if set. Otherwise show.")
    parser.add_argument("--y_axis_max", type=float, help="Maximum of the y-axis label. To keep scaling between runs. "
                        "Arbitrary units.")
    args = parser.parse_args()

    r_list, theta_deg_list = calc_signal_strength(args.input_file_name, args.lock_in_freq, args.integration_time_s)
    plot_filtered_signal(args.lock_in_freq, r_list, theta_deg_list, save_to_file=args.save_png,
                         r_plot_max=args.y_axis_max)
