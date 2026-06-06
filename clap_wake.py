import sys
import time
import subprocess
import numpy as np
import sounddevice as sd

# Configuration
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024
COOLDOWN = 2.0  
SENSITIVITY = 12.0  
MIN_ABS_THRESHOLD = 0.02  

running_noise_floor = 0.002
noise_alpha = 0.05
last_detection_time = 0

def audio_callback(indata, frames, time_info, status):
    global running_noise_floor, last_detection_time
    
    if status:
        return
        
    rms = np.sqrt(np.mean(indata**2))
    
    # Update running background noise average slowly when input is relatively quiet
    if rms < running_noise_floor * 2.0:
        running_noise_floor = (1 - noise_alpha) * running_noise_floor + noise_alpha * rms
    else:
        # Prevent noise floor tracking from locking up under sudden sustained noise
        running_noise_floor = (1 - noise_alpha * 0.1) * running_noise_floor + (noise_alpha * 0.1) * rms

    running_noise_floor = max(running_noise_floor, 0.0001)

    now = time.time()
    if now - last_detection_time < COOLDOWN:
        return

    # Detect clap (sudden loud transient peak)
    if rms > running_noise_floor * SENSITIVITY and rms > MIN_ABS_THRESHOLD:
        print(f"\n[Clap Wake] Clap detected! RMS: {rms:.4f} (Ambient noise floor: {running_noise_floor:.4f})")
        last_detection_time = now
        raise sd.CallbackAbort

def play_chime(rising=True):
    sr = 44100
    duration = 0.15
    t = np.linspace(0, duration, int(sr * duration), False)
    
    if rising:
        f1, f2 = 523.25, 659.25
    else:
        f1, f2 = 659.25, 523.25  
        
    tone1 = np.sin(2 * np.pi * f1 * t)
    tone2 = np.sin(2 * np.pi * f2 * t)
    

    fade_len = int(sr * 0.02)
    fade = np.linspace(0, 1, fade_len)
    tone1[:fade_len] *= fade
    tone1[-fade_len:] *= fade[::-1]
    tone2[:fade_len] *= fade
    tone2[-fade_len:] *= fade[::-1]
    
    audio = np.concatenate([tone1, tone2])
    audio = audio * 0.25  
    
    try:
        sd.play(audio, sr)
        sd.wait()
    except Exception as e:
        print(f"[Clap Wake] Error playing chime: {e}")

def run_agent():
    print("[Clap Wake] Waking up T.A.R.A...")
    play_chime(rising=True)
    
    try:
        print("[Clap Wake] Starting Voice Agent session...")
        cmd = [sys.executable, "agent_tara.py", "console"]
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("\n[Clap Wake] Session interrupted by user.")
    except Exception as e:
        print(f"[Clap Wake] Error running agent process: {e}")
        
    print("[Clap Wake] T.A.R.A going to sleep...")
    play_chime(rising=False)

def main():
    global last_detection_time
    print("==========================================================")
    print("T.A.R.A. Clap to Wake Active")
    print("----------------------------------------------------------")
    print("Listen mode: Offline clap detection is active.")
    print("Double-clap or clap loudly to wake up T.A.R.A.")
    print("==========================================================")
    
    while True:
        try:
            # Start the input stream
            with sd.InputStream(callback=audio_callback, blocksize=BLOCK_SIZE, samplerate=SAMPLE_RATE, channels=1):
                while True:
                    sd.sleep(100)
        except sd.CallbackAbort:
            run_agent()
            last_detection_time = time.time()  
        except KeyboardInterrupt:
            print("\n[Clap Wake] Stopping clap detector. Goodbye.")
            break
        except Exception as e:
            print(f"[Clap Wake] Stream error: {e}. Retrying in 3 seconds...")
            time.sleep(3)

if __name__ == "__main__":
    main()
