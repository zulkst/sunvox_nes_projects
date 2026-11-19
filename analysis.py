"""
=============================================================================
NES RICOH 2A03 vs. SUNVOX MODULAR SYNTHESIS — SPECTRAL & ACOUSTIC ANALYSIS
DSP Measurement & Verification Script
Author: rdxcrack
=============================================================================
"""

import os
import sys
import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_spectral_analysis(wav_file="Contra_Aliens_Lair_Stage8_RENDERED.wav"):
    output_dir = "spectral_analysis"
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(wav_file):
        # Look in current folder or parent
        if os.path.exists(os.path.join("..", wav_file)):
            wav_file = os.path.join("..", wav_file)
        else:
            print(f"[Warning] '{wav_file}' not found in current directory.")
            print("To analyze a custom audio file, run: python analysis.py <path_to_audio.wav>")
            return
        
    print(f"Loading rendered audio: {wav_file}")
    data, sr = sf.read(wav_file)
    if data.ndim > 1:
        mono = np.mean(data, axis=1)
    else:
        mono = data
        
    # Styling configuration
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'figure.titlesize': 14,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--'
    })

    # =========================================================================
    # FIGURE 1: 4-PANEL MASTER COMPOSITE FIGURE
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    
    # -------------------------------------------------------------------------
    # PANEL 1 (Top-Left): Full Spectral Distribution (FFT)
    # -------------------------------------------------------------------------
    ax1 = axes[0, 0]
    dur = len(mono) / float(sr)
    start_sec = min(15.0, dur * 0.2)
    end_sec = min(25.0, dur * 0.5)
    start_samp = int(start_sec * sr)
    end_samp = int(end_sec * sr)
    chunk = mono[start_samp:end_samp]
    
    n_fft = 65536
    window = np.hanning(len(chunk))
    fft_vals = np.abs(np.fft.rfft(chunk * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0/sr)
    
    fft_db = 20 * np.log10(fft_vals / (np.max(fft_vals) + 1e-9) + 1e-9)
    
    # Theoretical ideal unfiltered digital baseline
    omega = 2 * np.pi * freqs
    hpf_gain = omega / np.sqrt(omega**2 + (2 * np.pi * 37)**2 + 1e-9)
    lpf_gain = 1.0 / np.sqrt(1.0 + (freqs / 14000.0)**2)
    ideal_unfiltered_db = fft_db - 20 * np.log10(hpf_gain * lpf_gain + 1e-9)
    ideal_unfiltered_db = np.clip(ideal_unfiltered_db, -90, 0)
    
    ax1.plot(freqs, ideal_unfiltered_db, color='#888888', alpha=0.5, linewidth=1.0, label='Naive Digital Synthesis (No Motherboard RC)')
    ax1.plot(freqs, fft_db, color='#00e676', linewidth=1.2, label='SunVox Native 2A03 Model (With Pin Mixing & RC Filters)')
    ax1.axvline(37, color='#ff5252', linestyle=':', linewidth=1.5, label='37 Hz Motherboard HPF (DC Decouple)')
    ax1.axvline(14000, color='#ffab00', linestyle=':', linewidth=1.5, label='14 kHz Motherboard LPF (Anti-Imaging)')
    
    ax1.set_xscale('log')
    ax1.set_xlim(20, 20000)
    ax1.set_ylim(-80, 5)
    ax1.set_title('A. Full Audio Spectrum & Motherboard Filtering (FFT)')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('Magnitude (dBFS)')
    ax1.legend(loc='lower left', fontsize=8)

    # -------------------------------------------------------------------------
    # PANEL 2 (Top-Right): Triangle DAC: Continuous vs 32-Step Staircase
    # -------------------------------------------------------------------------
    ax2 = axes[0, 1]
    t = np.linspace(0, 1/110, 1000)
    tri_cont = 2 * np.abs(2 * (t * 110 - np.floor(t * 110 + 0.5))) - 1.0
    
    step_indices = np.floor((t * 110) * 32).astype(int) % 32
    dac_table = np.array([
        15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0,
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
    ], dtype=float)
    tri_stepped = (dac_table[step_indices] - 7.5) / 7.5
    
    ax2.plot(t * 1000, tri_cont, color='#7c4dff', linestyle='--', linewidth=1.5, label='Pure Mathematical Triangle (1/n² harmonics)')
    ax2.step(t * 1000, tri_stepped, where='post', color='#00b0ff', linewidth=2.0, label='2A03 & SunVox 32-Step 4-Bit DAC Ladder')
    
    ax2.set_xlim(0, 1000 / 110)
    ax2.set_ylim(-1.2, 1.2)
    ax2.set_title('B. 4-Bit Triangle DAC Resistor Ladder (One Cycle @ 110 Hz)')
    ax2.set_xlabel('Time (milliseconds)')
    ax2.set_ylabel('Normalized Voltage')
    ax2.legend(loc='upper right', fontsize=8)

    # -------------------------------------------------------------------------
    # PANEL 3 (Bottom-Left): Non-Linear Summing Transfer Curves (Pin 1 & Pin 2)
    # -------------------------------------------------------------------------
    ax3 = axes[1, 0]
    vol_sum = np.linspace(0, 30, 200)
    
    with np.errstate(divide='ignore'):
        v_pulse_raw = np.where(vol_sum > 0, 95.88 / (8128.0 / vol_sum + 100.0), 0.0)
    v_pulse_norm = v_pulse_raw / (95.88 / (8128.0 / 30.0 + 100.0))
    v_linear = vol_sum / 30.0
    
    ax3.plot(vol_sum, v_linear, color='#ff1744', linestyle='--', linewidth=1.5, label='Linear Summing (Standard Modern DAW)')
    ax3.plot(vol_sum, v_pulse_norm, color='#ffea00', linewidth=2.2, label='2A03 Pin 1 Hardware Curve (SunVox WaveShaper)')
    
    ax3.set_xlim(0, 30)
    ax3.set_ylim(0, 1.1)
    ax3.set_title('C. Pin 1 Non-Linear Mixing Transfer Function')
    ax3.set_xlabel('Input Register Sum (Pulse 1 + Pulse 2 Volume)')
    ax3.set_ylabel('Normalized Output Level')
    ax3.legend(loc='lower right', fontsize=8)

    # -------------------------------------------------------------------------
    # PANEL 4 (Bottom-Right): Time-Frequency Spectrogram
    # -------------------------------------------------------------------------
    ax4 = axes[1, 1]
    spec_start = int(start_sec * sr)
    spec_end = int(min(start_sec + 6.0, dur) * sr)
    spec_data = mono[spec_start:spec_end]
    
    Pxx, freqs_spec, bins, im = ax4.specgram(
        spec_data, NFFT=1024, Fs=sr, noverlap=768, 
        cmap='magma', vmin=-80, vmax=0
    )
    ax4.set_ylim(0, 16000)
    ax4.set_title("D. Spectrogram: Time-Frequency Distribution")
    ax4.set_xlabel('Time (seconds into slice)')
    ax4.set_ylabel('Frequency (Hz)')
    
    cbar = fig.colorbar(im, ax=ax4, format='%+2.0f dB')
    cbar.set_label('Power Spectral Density (dBFS)')

    fig.suptitle("Contra (NES) Stage 8: Alien's Lair — Acoustic Physics & SunVox Modular Synthesis Verification", fontsize=15, fontweight='bold', y=0.98)
    
    master_png = os.path.join(output_dir, "contra_aliens_lair_spectral_analysis_master.png")
    plt.savefig(master_png, bbox_inches='tight')
    plt.close()
    print(f"[Done] Master figure saved to: {master_png}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "Contra_Aliens_Lair_Stage8_RENDERED.wav"
    generate_spectral_analysis(target)
