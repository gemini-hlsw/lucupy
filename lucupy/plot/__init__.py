from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from lucupy.minimodel.ids import ObservationID
from lucupy.minimodel.site import Site


def airmass(obs_airmass: npt.NDArray[float],
            obs_id: ObservationID,
            time_interval: Optional[npt.NDArray[int]] = None) -> None:
    """Plot airmass values for an observation given a specific time interval
         obs_airmass (npt.NDArray[float]): Array of airmass values.
         obs_id (ObservationID): Observation ID.
         time_interval: Optional[npt.NDArray[int]]: Interval of time to plot. Defaults to None if the
         plot is for the entire night.
    """

    x = np.array([i for i in range(len(obs_airmass))], dtype=int)
    p = plt.plot(obs_airmass)
    colour = p[-1].get_color()
    if time_interval is not None:
        plt.plot(x[time_interval], obs_airmass[time_interval], color=colour, linewidth=4)
    plt.ylim(2.5, 0.95)
    plt.title(obs_id.id)
    plt.xlabel('Time Slot')
    plt.ylabel('Airmass')
    plt.show()


def interval(score: npt.NDArray[int],
             interval_to_plot: npt.NDArray[int],
             best_interval: npt.NDArray[int],
             label: str = "") -> None:
    """Plot the interval on time slots vs score.
        score (npt.NDArray[int]): Array of scores to plot in the interval.
        interval_to_plot (npt.NDArray[int]): Array of indices indicating the time slots.
        best_interval (npt.NDArray[int]): Best time slots for that observation.
        label (str): Label for the plot. Defaults to an empty string.
    """

    x = np.array([i for i in range(len(score))], dtype=int)
    p = plt.plot(x, score)
    colour = p[-1].get_color()
    if best_interval is not None:
        plt.plot(x[best_interval], score[best_interval], color=colour, linewidth=4)

    plt.axvline(interval_to_plot[0], ymax=1.0, color='black')
    plt.axvline(interval_to_plot[-1], ymax=1.0, color='black')
    plt.ylabel('Score', fontsize=12)
    plt.xlabel('Time Slot', fontsize=12)
    if label != '':
        plt.title(label)
    plt.show()


def timelines(obs_order: List[Tuple[int, int, int]],
              sites: List[Site],
              obs_id: ObservationID,
              obs_airmass: npt.NDArray[int],
              scores: npt.NDArray[int],
              night: int = 0) -> None:
    """Airmass and Score vs time/slot plot of the timelines for a night.
        obs_order (List[Tuple[int, int, int]]): List of observations in order (with start and finish).
        sites (List[Site]): List of sites.
        obs_id (ObservationID):  Observation ID.
        obs_airmass (npt.NDArray[int]): Array of airmass values for the observation.
        scores (npt.NDArray[int]): Array of scores for the observation.
        night (int): Night index. Defaults to 0 or the first (or only) night.
    """

    for site in sites:
        fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))
        for idx, start, end in obs_order:
            if idx != -1:
                x = np.array([i for i in range(len(obs_airmass))], dtype=int)
                p = ax1.plot(x, obs_airmass)
                ax2.plot(x, np.log10(scores))

                colour = p[-1].get_color()
                ax1.plot(x[start:end + 1], obs_airmass[start:end + 1], linewidth=4, color=colour,
                         label=obs_id.id)
                ax2.plot(x[start:end + 1], np.log10(scores[start:end + 1]), linewidth=4, color=colour,
                         label=obs_id.id)

        ax1.axhline(2.0, xmax=1.0, color='black')
        ax1.set_ylim(2.5, 0.95)
        ax1.set_xlabel('Time Slot')
        ax1.set_ylabel('Airmass')
        ax1.set_title(f"Night {night + 1}: {site.name}")
        ax1.legend()

        ax2.set_xlabel('Time Slot')
        ax2.set_ylabel('log(Score)')
        ax2.set_title(f"Night {night + 1}: {site.name}")
        plt.show()
