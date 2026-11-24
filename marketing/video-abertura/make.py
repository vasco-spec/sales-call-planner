import subprocess, os
def run(c): subprocess.run(c, check=True, stdin=subprocess.DEVNULL)
segs=[]
for line in open("lines.txt", encoding="utf-8"):
    k,t=line.rstrip("\n").split("|",1)
    subprocess.run(["python3","-m","piper","-m","../tts/pt.onnx","--length-scale","1.05","-f",f"{k}.wav"],input=t.encode(),check=True,stderr=subprocess.DEVNULL)
    d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{k}.wav"]))
    T=round(d+0.7,2); out=f"seg_{k}.mp4"
    enc=["-r","30","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-ar","44100","-ac","2","-t",str(T),out]
    if os.path.exists(f"{k}a.png"):
        H=round(T/2,2)
        run(["ffmpeg","-loglevel","error","-y","-loop","1","-t",str(H),"-i",f"{k}a.png","-loop","1","-t",str(T-H),"-i",f"{k}b.png","-i",f"{k}.wav","-filter_complex",f"[0][1]concat=n=2:v=1[v];[2]apad=whole_dur={T}[a]","-map","[v]","-map","[a]"]+enc)
    else:
        run(["ffmpeg","-loglevel","error","-y","-loop","1","-t",str(T),"-i",f"{k}.png","-i",f"{k}.wav","-filter_complex",f"[1]apad=whole_dur={T}[a]","-map","0:v","-map","[a]"]+enc)
    segs.append(out); print(k,T)
open("list.txt","w").write("".join(f"file '{s}'\n" for s in segs))
run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i","list.txt","-c","copy","/home/user/videos/abertura-de-atividade-v1.mp4"])
