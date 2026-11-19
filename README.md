
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
