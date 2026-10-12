# Digital synthesizer and audio-effect rack assignment

## Deliverables and assessment

Build a MIDI-to-audio synthesizer followed by a configurable series of audio effects, using Python or MATLAB. Package source, report, figures, and audio outputs together. The original naming convention is Project-StudentNo1_StudentNo2_StudentNo3.zip. Supply the report PDF and its LaTeX source when using LaTeX. The course submission requires a GitHub repository. The grading table assigns synthesis 0.45 plus 0.1 bonus, GitHub 0.05, LaTeX/report structure 0.2, and effects 1.2. The stated compulsory/bonus cap applies to the course score. It is not necessary to implement every listed effect to reach the maximum. Keep implemented and proposed features distinguishable.

## Notes, rhythm, and MIDI timing

MIDI describes musical events rather than recorded waveform samples. Equal temperament uses a frequency ratio of 2^(1/12) per semitone, with A4 = 440 Hz. For MIDI note n, f(n) = 440*2^((n-69)/12) Hz. Thus A3 = 220 Hz and A5 = 880 Hz. A periodic tone can contain harmonics at integer multiples of its fundamental; the fundamental need not be the largest spectral coefficient. The tables' MIDI CC heading refers here to note numbers, not control-change identifiers. Read note_on and note_off messages, channel, note number, velocity, and delta time. Channels share a common timeline and must be mixed rather than concatenated. A note_on with zero velocity is ordinarily a note-off event. Pair events by channel and note and define a policy for repeated overlapping notes. Tempo is measured in microseconds per quarter note, and the file specifies ticks per quarter note. Convert delta ticks using the tempo active during that interval. The example tempo 576923, resolution 192 ticks/quarter, and duration 96 ticks give 288461.5 microseconds, approximately 0.288 seconds. A tempo change requires segment-wise conversion. 

## Oscillator synthesis

The mandatory synthesis stage combines a periodic source with an amplitude envelope. Implement sine, sawtooth, triangle, and square waveforms. Parameters include waveform, phase, fundamental frequency, volume, and detuning; optional oscillator filtering uses a VCF. Phase and time delay are related for an individual sinusoid but are not interchangeable parameters for an arbitrary waveform. A Gaussian-noise source may be added; its amplitude is adjustable, but it has no unique fundamental or phase. Combine several oscillators as a weighted sum. Detuning uses nearby frequency offsets and weights: x_detuned(t) = sum_i A_i*x(2*pi*(f_b+f_i)*t). The assignment permits a justified choice of oscillator count, offsets, and weights as functions of the detune control. Preserve amplitude headroom when mixing voices. Naively sampled nonsinusoidal waveforms can alias; discuss this limitation rather than treating every generated high harmonic as physically meaningful.

## AHDSR envelope

Implement adjustable Attack, Hold, Decay, Sustain, and Release. Attack rises to peak, Hold stays at peak, Decay falls toward the sustain level, Sustain continues until note release, and Release falls to silence after note-off. Use exponential-like transitions as requested. A normalized exponential segment must have explicit endpoint behavior; the illustrative piecewise exponentials in the assignment should not be copied with discontinuities or without amplitude offsets. Support zero Hold and the specified zero-Sustain behavior. Velocity controls a documented amplitude mapping. Release must begin from the current envelope level when a short note ends before attack/decay has finished. Preserve the original envelope diagrams, including the exponential example.

## Shared effect interface

An effect receives audio and returns transformed audio. A rack cascades several effects in an ordered chain. Every effect has input gain, output gain, and a wet/dry parameter w from zero to one; mix as (1-w)*dry + w*wet, with defined gain placement. Order matters for nonlinear effects. Expose parameters and sample rate rather than embedding unexplained constants.

| Effect | Main points | Bonus points |
|---|---:|---:|
| Phaser | 0.05 | 0.05 |
| Flanger | 0.05 | 0.05 |
| Chorus | 0.05 | 0.05 |
| Delay | 0.10 | 0.10 |
| Reverberation | 0.20 | none |
| Pitch shifter | 0.40 | none |
| Vocoder | 0.30 | none |
| Saturation | 0.25 | none |
| Compressor | 0.25 | none |
| Voltage-controlled filter | 0.10 | none |

## Saturation and compression

Implement hard clipping to [-T,T], soft clipping T*tanh(x/T), and the specified variable saturation T*abs(x/T)^a*sign(x). Drive D and bias b change the input to f(D*x+b). Define T > 0 and parameter ranges. This variable-power law is not necessarily a bounded clipper outside its intended range. Nonlinear processing can generate harmonics and aliasing. The compressor has threshold, ratio, attack, and release controls. Above a threshold in decibels, the steady-state level is T+(L-T)/R. Convert the resulting gain reduction back to a linear multiplier. Do not mix linear amplitudes with decibel thresholds or interpret a compression ratio as a fixed number of decibels. Use an appropriate level/envelope detector and discretize attack/release behavior. The source suggests averaging recent samples for smoother response; specify whether the detector uses magnitude, RMS, or another quantity.

## Delay, phaser, flanger, and chorus

Delay uses z^(-n) and an optional H(z) in the delayed branch. Convert time delay to samples using the sample rate. H(z)=1 gives the simple echo path; filtering or low-frequency modulation can add the stated extensions. Phaser mixes a dry signal with a cascade of all-pass-filter outputs. Phase differences produce frequency-dependent cancellation and peaks. Flanger uses a short delayed branch, optionally with feedback and modulation. Chorus uses multiple differently delayed/modulated branches to suggest several voices. Preserve the source diagrams and distinguish these related structures. The original typical-setting tables list phasing 0-3 ms with a little feedback, large modulation width, and slow speed; flanging 3-13 ms with substantial feedback and medium width/speed; chorus 13-30 ms with no feedback, small width, and medium speed. Earlier prose gives a 5-10 ms starting range for flanger/chorus. These are illustrative settings, not universal definitions. Optional LFO modulation applies to the three effects.

## Reverberation and filters

Digital reverb can combine delayed branches with gains, using relatively prime delay lengths as suggested. A realistic sustained decay needs a defined network or sufficiently rich finite response; three isolated feedforward delays alone produce only a few echoes. Convolution reverb filters audio with a measured room impulse response. Match sample rates, manage output length, and document the impulse-response source. The VCF exposes low-pass, high-pass, band-pass, or band-stop behavior and adjustable cutoff. IIR implementations include direct forms I, II, and transposed structures. Keep coefficients and filter state separate. Direct form II stores internal state rather than merely a list of raw recent input samples. An LFO below approximately 20 Hz can vary oscillator frequency or filter cutoff. Recompute coefficients from a stable filter design; arbitrary coefficient perturbation may make poles unstable. Vibrato is frequency modulation and tremolo is amplitude modulation.

## Vocoder and pitch shifting

For the vocoder, divide the useful spectrum into logarithmically spaced bands, filter the carrier and speech modulator in each band, estimate modulator envelopes, apply each envelope to its carrier band, and sum. The assignment gives y[n] = sum_i abs(m_i[n])*c_i[n]; practical smoothing of the rectified envelope improves behavior. Use roughly a dozen or more bands, stable filters, and a useful lower frequency bound. Preserve carrier duration by padding or truncating the modulator. For pitch shifting, a three-semitone shift maps C-sharp4 to E4 and uses frequency ratio 2^(3/12), not a literal ratio of three. Simple resampling changes duration. The proposed phase-vocoder method first changes time scale without changing pitch, then resamples to restore duration. Analysis uses STFT, processing tracks/corrects phase with optional phase locking, and synthesis uses inverse STFT and overlap-add with compatible windows/hops. Preserve the original phase-vocoder diagram and explain the chosen implementation's artifacts and limits. 
