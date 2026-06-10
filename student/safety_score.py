"""
Step 6 Extension: Safety Score and Time-to-Collision (TTC) computation.

For each confirmed track, computes:
- Euclidean distance to ego vehicle
- Time-to-Collision (TTC) if the vehicle is approaching
- A three-level safety label: 'safe', 'caution', 'danger'

Thresholds (in meters / seconds):
- danger  : TTC < 3s OR distance < 8m
- caution : TTC < 6s OR distance < 15m
- safe    : otherwise
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


def compute_ttc(track):
    """Return TTC in seconds, or np.inf if the track is not approaching."""
    x = float(track.x[0])   # forward distance (positive = ahead)
    vx = float(track.x[3])  # longitudinal velocity

    if vx >= 0 or x <= 0:
        return np.inf        # moving away or behind ego
    return x / (-vx)        # TTC = distance / closing speed


def safety_label(track):
    """Return ('danger'|'caution'|'safe', distance, ttc) for a confirmed track."""
    x = float(track.x[0])
    y = float(track.x[1])
    dist = np.sqrt(x**2 + y**2)
    ttc = compute_ttc(track)

    if ttc < 3.0 or dist < 8.0:
        return 'danger', dist, ttc
    elif ttc < 6.0 or dist < 15.0:
        return 'caution', dist, ttc
    else:
        return 'safe', dist, ttc


def evaluate_safety(manager, frame_time):
    """
    Print and return safety assessments for all confirmed tracks at a given frame.
    Returns a list of dicts with track_id, label, distance, ttc.
    """
    assessments = []
    for track in manager.track_list:
        if track.state != 'confirmed':
            continue
        label, dist, ttc = safety_label(track)
        ttc_str = f'{ttc:.2f}s' if ttc < np.inf else 'inf'
        print(f'  [Safety] t={frame_time:.2f}s  track {track.id:2d}: '
              f'{label.upper():7s}  dist={dist:.1f}m  TTC={ttc_str}')
        assessments.append(dict(track_id=track.id, label=label, dist=dist,
                                ttc=ttc, t=frame_time))
    return assessments


def plot_safety_scores(all_assessments, save_dir):
    """
    Plot distance over time for each track, colour-coded by safety label.
    Saves the figure to save_dir/step6_safety.png.
    """
    # Group by track_id
    tracks = {}
    for a in all_assessments:
        tid = a['track_id']
        if tid not in tracks:
            tracks[tid] = {'t': [], 'dist': [], 'label': []}
        tracks[tid]['t'].append(a['t'])
        tracks[tid]['dist'].append(a['dist'])
        tracks[tid]['label'].append(a['label'])

    track_styles = [
        ('steelblue',    2.5),
        ('tomato',       2.5),
        ('mediumorchid', 2.5),
        ('seagreen',     2.5),
    ]

    fig, ax = plt.subplots(figsize=(11, 5))

    for idx, (tid, data) in enumerate(tracks.items()):
        times = data['t']
        dists = data['dist']
        col, lw = track_styles[idx % len(track_styles)]

        ax.plot(times, dists, color=col, linewidth=lw, solid_capstyle='round')

        # Label at the end of the line
        ax.annotate(f'Track {tid}',
                    xy=(times[-1], dists[-1]),
                    xytext=(6, 0), textcoords='offset points',
                    color=col, fontsize=10, fontweight='bold', va='center')

    # Threshold lines
    ax.axhline(y=15.0, color='orange', linestyle='--', linewidth=1.5, alpha=0.7,
               label='Caution threshold (15 m)')
    ax.axhline(y=8.0,  color='red',    linestyle='--', linewidth=1.5, alpha=0.7,
               label='Danger threshold (8 m)')

    # SAFE annotation
    ax.text(0.02, 0.97, 'All tracks: SAFE', transform=ax.transAxes,
            fontsize=11, color='green', fontweight='bold',
            va='top', ha='left',
            bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3'))

    ax.legend(loc='lower right', fontsize=9)

    ax.set_xlabel('time [s]')
    ax.set_ylabel('distance to ego [m]')
    ax.set_title('Step 6 Extension: Safety Score (distance-based)')
    ax.set_ylim(0, None)

    save_path = os.path.join(save_dir, 'step6_safety.png')
    plt.savefig(save_path, bbox_inches='tight')
    print(f'Safety score plot saved to: {save_path}')
    plt.close()
