
# Physics of NES Ricoh 2A03 Audio Silicon vs. Modular Emulation in SunVox

A mathematical and circuit-level breakdown comparing the discrete electrical physics of the Nintendo Entertainment System's **Ricoh 2A03 Audio Processing Unit (APU)** against its modular reconstruction inside **SunVox**.

---

## 1. The Real NES Audio Circuitry (Discrete Physics)

Unlike modern digital synthesizers that linearly add audio buffers ($S = A + B$), the NES 2A03 mixes voices using **non-linear analog resistive voltage ladders** connected directly to the chip's physical pins.
#### A. Pulse Channel Saturation Formula (Pin 1)
When Pulse 1 and Pulse 2 play together, they don't just add up linearly. The hardware causes them to compress and saturate:

$$
V_{\text{pulse}} = \frac{95.88}{\frac{8128}{\text{pulse}_1 + \text{pulse}_2} + 100}
$$

#### B. Triangle, Noise, and DPCM Formula (Pin 2)
The remaining channels exit through Pin 2 through their own non-linear resistance network:

```math
V_{\text{tnd}} = \frac{159.79}{\frac{1}{\frac{\text{tri}}{8227} + \frac{\text{noise}}{12241} + \frac{\text{dpcm}}{22638}} + 100}
```

### C. The 4-Bit Discrete Staircase DAC (Triangle Channel)
A mathematical continuous triangle wave only contains odd harmonics dropping off at $1/n^2$. However, the NES 2A03 Triangle channel is **not** smooth. It is driven by a 5-bit shift register cycling through an unattenuated **32-step 4-bit resistor ladder**:

$$
\text{DAC}(k) = \begin{cases} 15 - k & 0 \le k \le 15 \\ k - 16 & 16 \le k \le 31 \end{cases}
$$

This discrete 32-step staircase injects high-order quantization harmonics into the bass frequencies, producing the signature buzzy, aggressive bite heard in Konami basslines.

---

### D. Motherboard Analog Filtering (Passive RC Networks)
Before the mixed audio leaves the console's RCA or RF jack, it passes through two passive RC filter stages on the NES motherboard:

1. **DC Blocking High-Pass Filter (HPF):**
$$
f_c = \frac{1}{2\pi R_1 C_1} \approx 37 \text{ Hz}
$$
Blocks DC bias while gently rolling off sub-rumble below 37 Hz.

2. **RF / Parasitic Low-Pass Filter (LPF):**
$$
f_c = \frac{1}{2\pi R_2 C_2} \approx 14 \text{ kHz}
$$
Rounds off ultra-high square wave harmonics, creating the warm analog tone characteristic of authentic hardware.
