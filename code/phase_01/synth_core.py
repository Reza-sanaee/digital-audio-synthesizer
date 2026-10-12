"""MIDI timeline rendering and bounded PCM conversion."""
from collections import defaultdict, deque
import numpy as np
import mido

def to_pcm16(audio):
    audio = np.nan_to_num(np.asarray(audio, dtype=float))
    peak = np.max(np.abs(audio)) if audio.size else 0.0
    if peak > 1.0:
        audio = audio / peak
    return np.rint(np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)

def render_midi(midi_file, sample_rate=44100, attack=0.01, decay=0.1,
                sustain=0.7, release=0.2):
    midi = mido.MidiFile(midi_file)
    if midi.type == 2:
        raise ValueError("Independent type-2 sequences need a track selection")
    active = defaultdict(deque)
    notes = []
    now = 0.0
    # MidiFile iteration merges tracks and converts deltas using tempo changes.
    for msg in midi:
        now += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            active[(msg.channel, msg.note)].append((now, msg.velocity))
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            key = (msg.channel, msg.note)
            if active[key]:
                start, velocity = active[key].popleft()
                notes.append((start, now, msg.note, velocity))
    for (_, note), queue in active.items():
        for start, velocity in queue:
            notes.append((start, now, note, velocity))
    end = max([now] + [stop + release for _, stop, _, _ in notes])
    audio = np.zeros(int(np.ceil(end * sample_rate)))
    for start, stop, note, velocity in notes:
        held = max(0, int(round((stop-start) * sample_rate)))
        if held == 0:
            continue
        a = min(held, int(round(attack * sample_rate)))
        d = min(held-a, int(round(decay * sample_rate)))
        env = np.empty(held + int(round(release * sample_rate)))
        if a:
            env[:a] = np.linspace(0, 1, a)
        level = 1.0 if a else 1.0
        if d:
            env[a:a+d] = np.linspace(level, sustain, d)
        env[a+d:held] = sustain if d or held > a else level
        last = env[held-1]
        if len(env)>held:
            env[held:] = np.linspace(last, 0, len(env)-held)
        t = np.arange(len(env)) / sample_rate
        voice = (velocity/127.0) * np.sin(2*np.pi*440*2**((note-69)/12)*t) * env
        offset = int(round(start*sample_rate))
        if offset+len(voice)>len(audio):
            audio = np.pad(audio, (0, offset+len(voice)-len(audio)))
        audio[offset:offset+len(voice)] += voice
    return audio
