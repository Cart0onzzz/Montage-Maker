from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image, ImageEnhance
import pyscreeze
import os, time, shutil
import glob

location = os.path.dirname(os.path.abspath(__file__)) + "\\"


def info(information):
    print("\n\n************************************************")
    print("\n************************************************")
    print(information)
    print("\n\n************************************************")
    print("\n************************************************")

def ask_user(question):
    use_val = input(question+"\nType 'y/Y' for yes and 'n/N' for no\n")
    if use_val=="y" or use_val=="Y" or use_val=="yes" or use_val=="Yes":
        return True
    elif use_val=="n" or use_val=="N" or use_val=="no" or use_val=="No":
        return False
    else:
        print("Invalid Argument.")
        return ask_user(question)

def main_func():
    info("Welcome to the Montage Maker Program made by Kodi. Before using this, make sure to check the following:\n1.You do not have any file named 'output.mp4' in the output folder.\n2.Delete the videos in input folder if you already use them, otherwise it will be added.\n3.Make sure you have some '.mp3' files in the soundlib as one file is automatically used in the video.")

    input("If you've read and checked everything, press Enter to continue.")

    use_intro = ask_user("\nDo You want to add intro?")
    use_outro = ask_user("\n\n**Do you want to add outro?")

    info("Set the optimal value of the processing. 0 being the highest performance. Optimal value for medium-end pc's is '2'.\nNote:Highest processing might take more cpu usage, Set it with caution.")
    proc_val = int(input("Enter the processing value: "))

    vid_count = 0

    for vid in glob.glob(location+'input/*.mp4'):
        subclip_timings = []
        subclips = []
        clip = VideoFileClip(vid)

        print("Using video clip : ",vid)
        print("Frames per second: ",clip.reader.fps)
        print("Total No. of frames: ",clip.reader.nframes)
        print("Duration (in secs): ",clip.duration)

        kill_relax = 0
        cont_kill = 0

        info("Checking every frame. \nNote: Process might be slow depending upon the speed of the computer.")

        for i in range(0,int(clip.duration)):
            if kill_relax != 0:
                kill_relax -= 1
                continue
            frame = clip.get_frame(i)
            img = Image.fromarray(frame)
            img = img.crop((1100, 380, 1500, 500))
            img = ImageEnhance.Contrast(img)
            img = img.enhance(2)

            # img.save(f"D:\Python\\automation\\video_editing\\fps\\{i}.png")

            count = 0
            r = None
            s = None
            t = None
            u = None
            count = 0

            while r == None and s == None and t == None and u == None and count < 10:

                r = pyscreeze.locate(location+"assets\\res\\"+"100_2.png",img, confidence=.7)
                s = pyscreeze.locate(location+"assets\\res\\"+"100.png",img, confidence=.8)
                t = pyscreeze.locate(location+"assets\\res\\"+"125.png",img, confidence=.7)
                u = pyscreeze.locate(location+"assets\\res\\"+"200.png",img, confidence=.8)
                count += 1


            if r != None or s != None or t != None or u != None: #kill detected:

                print("kill Detected @ ",i)
                if cont_kill < 1:
                    cont_kill = 5
                    subclip_timings.append([i-5,i+1])
                else:
                    subclip_timings[len(subclip_timings)-1][1] = i+1
                kill_relax = 2

            else:
                print("skipping frame ",i)

            if cont_kill >0:
                cont_kill -= 1

            time.sleep(proc_val)

        info("The videos has been processed.")
        for i, kill_cam in enumerate(subclip_timings):
            subclips.append(clip.subclip(kill_cam[0],kill_cam[1]))

        for i, kill in enumerate(subclip_timings):
            with open(location+"assets\\proc\\config.txt","a") as file:
                start_min = kill[0] // 60
                start_sec = kill[0] % 60
                cmnd = f'ffmpeg -ss 00:0{start_min}:{str(start_sec).zfill(2)} -i "{vid}" -to 00:00:{str(kill[1]-kill[0]).zfill(2)} -c copy "{location}assets\\proc\\{vid_count}.mp4"'
                print(cmnd)
                os.system(cmnd)        
                file.write(f"file '{location}assets\proc\{vid_count}.mp4'\n")
                vid_count += 1

        clip.close()

    info("Done checking kills. Initailizing video creator unit. Please Wait...")
    time.sleep(5)

    concat_cmnd = f"ffmpeg -safe 0 -f concat -i {location}\\assets\\proc\\config.txt -c copy {location}assets\\proc\\temp_vid.mp4"
    print(concat_cmnd)
    os.system(concat_cmnd)


    # --------------------------SOUND ADDITION -----------------------------------

    vid = VideoFileClip(location+"assets\\proc\\temp_vid.mp4")

    vid_dur = vid.duration

    vid.close()

    soundlib = []

    strt_param = 1
    end_param = 1

    info(f"Done creating video. Looking sounds in {location}soundlib/ folder. Make sure you have some sound files in it.")

    info("Checking for the best music that suits the video.It can take upto a few minutes depending upon the number of files in the folder.\nPlease Wait...")

    while soundlib == []:

        end_param += 4

        for name in glob.glob(location+'soundlib/*.mp3'):

            audio_clip = AudioFileClip(name)
            if audio_clip.duration > (vid_dur - strt_param) and audio_clip.duration < (vid_dur + end_param):
                soundlib.append([name,audio_clip.duration])
            audio_clip.close()

        print("Don't worry! The program hasn't hanged. Wait...")

    sound_used = soundlib[min(range(len(soundlib)), key = lambda i: abs(soundlib[i][1]-vid_dur))]

    print(sound_used)

    if use_intro:
        sound_cmnd = f"ffmpeg -i {location}assets\\proc\\temp_vid.mp4 -i \"{sound_used[0]}\" -c copy -map 0:0  -map 1:0 -shortest {location}assets\\proc\\final.mp4"
    else:
        sound_cmnd = f"ffmpeg -i {location}assets\\proc\\temp_vid.mp4 -i \"{sound_used[0]}\" -c copy -map 0:0  -map 1:0 -shortest {location}output\\output.mp4"

    print(sound_cmnd)
    os.system(sound_cmnd)

    if use_intro:
        info("Adding intro to your video...")
        if use_outro:
            intro_cmnd = f'ffmpeg -i {location}intro\\intro.mp4 -i {location}assets\\proc\\final.mp4 -filter_complex "[0:v]scale=2340:1080:force_original_aspect_ratio=decrease,pad=2340:1080:-1:-1,setsar=1,fps=30,format=yuv420p[v0]; [1:v]scale=2340:1080:force_original_aspect_ratio=decrease,pad=2340:1080:-1:-1,setsar=1,fps=30,format=yuv420p[v1]; [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -c:a aac -movflags +faststart {location}assets\\proc\\intro_added.mp4'
        else:
            intro_cmnd = f'ffmpeg -i {location}intro\\intro.mp4 -i {location}assets\\proc\\final.mp4 -filter_complex "[0:v]scale=2340:1080:force_original_aspect_ratio=decrease,pad=2340:1080:-1:-1,setsar=1,fps=30,format=yuv420p[v0]; [1:v]scale=2340:1080:force_original_aspect_ratio=decrease,pad=2340:1080:-1:-1,setsar=1,fps=30,format=yuv420p[v1]; [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -c:a aac -movflags +faststart {location}output\\output.mp4'
        os.system(intro_cmnd)


    if use_outro:
        info("Adding Outro to the video...")
        outro_cmnd = f'ffmpeg -i {location}assets\\proc\\intro_added.mp4 -i {location}outro\\outro.mp4 -filter_complex "[0:v]scale=2340:1080:force_original_aspect_ratio=decrease,pad=2340:1080:-1:-1,setsar=1,fps=30,format=yuv420p[v0]; [1:v]scale=2340:1080:force_original_aspect_ratio=decrease,pad=2340:1080:-1:-1,setsar=1,fps=30,format=yuv420p[v1]; [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -c:a aac -movflags +faststart {location}output\\output.mp4'
        os.system(outro_cmnd)

    info("Montage created successfully. Check out the output folder. \nMake sure to delete the video from the inputs folder.")



def gc():
    print("Cleaning up resources...")
    time.sleep(5)
    if os.path.exists(location+"assets\\proc"):
        shutil.rmtree(location+"assets\\proc")
    time.sleep(2)
    os.mkdir(location+"assets\\proc")
    file = open(location+'assets\\proc\\config.txt','w') 
    file.close()
    print("Done.")



def main():
    try: 
        folder_lst = ["assets\\proc","input","intro","output","soundlib","outro"]
        for fldr in folder_lst:
            if not os.path.exists(location+""+fldr):
                os.makedirs(location+""+fldr)
        file = open(location+'assets\\proc\\config.txt','w') 
        file.close()
        main_func()
    finally:
        gc()



if __name__ == "__main__":
    main()
