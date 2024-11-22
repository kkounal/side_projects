
import os
import time
import argparse
import textwrap
import platform
import subprocess
import sys
from datetime import timedelta

try:
    import whisper
    import yt_dlp
    from deep_translator import GoogleTranslator
    from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
    from moviepy.video.tools.subtitles import SubtitlesClip
except ImportError as err:
    sys.stdout.write("Error: failed to import module ({})".format(err))
    time.sleep(1)
    print("Needed dependencies not found, Automatically install them? Y/n?")
    response = input()
    if response == "Y" or response == "y":
        print("trying to install dependencies")

        def install_libraries():
            required_libraries = ['whisper', 'yt_dlp', 'moviepy','deep-translator']
            current_os = platform.system()
            
            if current_os == 'Windows':
                package_manager = 'pip'
            elif current_os == 'Darwin':
                package_manager = 'pip3'
            elif current_os == 'Linux':
                package_manager = 'pip3'
            else:
                print("unsupported operating system, skipping install")
                return
            
            for library in required_libraries:
                try:
                    subprocess.check_call([package_manager, 'install', library])
                    print(f"{library} installed successfully, run the script again")
                except subprocess.CalledProcessError:
                    print(f"failed to install {library}")
                    time.sleep(5)
                    exit()

        install_libraries()
    else:
        print("Automatic installation of dependencies denied, exiting")
        time.sleep(3)
        raise SystemExit


# Credit goes to/this is an improvement/expansion of
# https://github.com/pacifio/autocap


YT_ATTACH = "youtube-a"
YT_GENERATE = "youtube-g"
YT_CAPTION = "youtube-c"
YT_ALL = "youtube-all"

VALID_MODES = ("attach", "generate","translate","all", YT_ATTACH, YT_GENERATE,YT_ALL,"caption", YT_CAPTION)
YT_MODES = (YT_ATTACH, YT_GENERATE,YT_ALL,YT_CAPTION)

TEMP_FILE = "temp.mp3"
YT_VID = "ytvid_temp.mp4"
TEMP_FILES = [TEMP_FILE,YT_VID]

OUTPUT_SRT = "subs.srt"
TRANSLATED_SRT = "translated_subs.srt"
OUTPUT_VID = "output.mp4"

def pprint_dict(dictionary):
    import json
    print(json.dumps(dictionary, indent=4))

def progressbar(it,count=0, prefix="", size=60, out=sys.stdout): # Python3.6+
    if count == 0:
        count = len(it)
    start = time.time() # time estimate start
    def show(j):
        x = int(size*j/count)
        # time estimate calculation and string
        remaining = ((time.time() - start) / j) * (count - j)        
        mins, sec = divmod(remaining, 60) # limited to minutes
        time_str = f"{int(mins):02}:{sec:03.1f}"
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count} Estimated time left {time_str}", end='\r', file=out, flush=True)
    show(0.1) # avoid div/0 
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)



LANGUAGES = {
    'auto': 'automatically detect, (input lang only)',
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'he': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'or': 'odia',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'ug': 'uyghur',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu'
}

class Utility:
    def __init__(self, path: str, youtube: bool) -> None:
        self.path = path
        self.youtube = youtube

    def file_exists(self) -> bool:
        if self.youtube:
            return True
        if self.path is None:
            return True
        return len(self.path) > 0 and os.path.exists(path=self.path)
    
    def user_lang_info(self) -> tuple[str, str]:
        print("Choose input and output lang:")
        pprint_dict(LANGUAGES)
        
        print("Input lang:")
        in_lang = input()
        if in_lang not in LANGUAGES:
            print("invalid lang, quitting")  
            time.sleep(3)
            exit()
        
        print("Output lang:")
        out_lang = input()
        if out_lang not in LANGUAGES:
            print("invalid lang, quitting")  
            time.sleep(3)
            exit()
        return in_lang,out_lang

    def ask_user_for_cleanup(self) -> None:
        print("Clean up temporary audio/video files? Y/n?")
        response = input()
        if response == "Y" or response == "y":
            print("Cleaning...")
            self.cleanup()
        
    
    def cleanup(self) -> None:
        for file in TEMP_FILES:
            if os.path.exists(file):
                os.remove(file)

class VideoManager:
    def __init__(self, path: str, youtube: bool, srt_flag: bool) -> None:
        self.path = path
        self.youtube = youtube
        if not self.youtube and path is not None:
            self.video = VideoFileClip(path)
        if not srt_flag:
            self.extract_audio()
        
           

    def download(self) -> None:
        print("Downloading youtube video")
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": YT_VID,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as dl:
            dl.download([self.path])
        self.video = VideoFileClip(YT_VID)

    def extract_audio(self) -> None:
        if self.youtube:
            self.download()

        if self.video.audio is not None:
            self.video.audio.write_audiofile("temp.mp3", codec="mp3")
        else:
            print("video has no audio, quitting")
            time.sleep(3)

class SubtitleGenerator:
    def __init__(self, videomanager: VideoManager) -> None:
        self.videomanager = videomanager
        self.subs = OUTPUT_SRT

    def generate(self) -> None:
        # Credit goes to
        # https://github.com/openai/whisper/discussions/98#discussioncomment-3725983
        # github.com/lectair

        model = whisper.load_model("base")
        transcribe = model.transcribe(audio=TEMP_FILE, fp16=False)
        segments = transcribe["segments"]
       
        for seg in  segments:
            start = str(0) + str(timedelta(seconds=int(seg["start"]))) + ",000"
            end = str(0) + str(timedelta(seconds=int(seg["end"]))) + ",000"
            text = seg["text"]
            segment_id = seg["id"] + 1
            segment = f"{segment_id}\n{start} --> {end}\n{text[1:] if text[0] == ' ' else text}\n\n"
            with open(OUTPUT_SRT, "a", encoding="utf-8") as f:
                f.write(segment)

        print("subtitles generated")

    def translate_subs(self,in_lang,out_lang) -> None:
        i = 0
        num_lines = 0
        with open(self.subs, "r", encoding="utf-8") as input_file:
                num_lines = sum(1 for line in input_file)

        with open(self.subs, "r", encoding="utf-8") as input_file:
            with open(TRANSLATED_SRT, "w", encoding="utf-8") as output_file:
                for input_line in progressbar(input_file,num_lines, "translating: ", 40):
                    i += 1
                    if (i % 3 != 0):
                        output_line = input_line
                        output_file.write(output_line)
                    else:
                        output_line = GoogleTranslator(source=in_lang, target=out_lang).translate(input_line)
                        output_file.write(output_line)
                        output_file.write(u'\n') 
                        time.sleep(1)
                    if i == 4:
                        i = 0

                    
        self.subs = TRANSLATED_SRT
            
        print("translated subtitles generated")    

    def attach(self) -> None:
        if os.path.exists(self.subs):
            if os.path.exists(self.videomanager.path):
               subprocess.run(["ffmpeg", "-i",self.videomanager.path,"-vf","subtitles="+self.subs,OUTPUT_VID]) 
            else:
               subprocess.run(["ffmpeg", "-i",ytvid_temp.mp4,"-vf",self.subs,OUTPUT_VID]) 
            print(f"saved to {OUTPUT_VID}")

def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0 and 'ffmpeg' in result.stdout
    except FileNotFoundError:
        return False

def action_gen(subtitle_generator):
    print("Generating subs for video...")
    subtitle_generator.generate()

def action_attach(subtitle_generator):
    print("Attaching subs to video...")
    subtitle_generator.attach()


def action_translate(utility,subtitle_generator,in_lang=None,out_lang=None,mode="full") -> tuple[str,str]:
    if mode == "full" or mode == "only_input":
        in_lang,out_lang = utility.user_lang_info()
    
    if mode == "full" or mode == "only_translate":
        if utility.file_exists():
            print("Translating...")
            subtitle_generator.translate_subs(in_lang,out_lang)
        else:
            print("invalid file path, quitting")
            time.sleep(3)
            exit()
    
    return in_lang,out_lang 

def main() -> None:
    parser = argparse.ArgumentParser(description="auto caption generator v2.0",formatter_class=argparse.RawDescriptionHelpFormatter,epilog=textwrap.dedent('''\
        User Manual:
        ====================
         functions:
            generate: generate subtitles (srt) file for a video
                                                                                                      
            attach: attach/embed a srt file to/inside a video
                                                                                                      
            caption: caption a video, (generate then attach)    
                                                                                                                                                                                          
            translate: translate a srt file to another language
                                                                                                      
            all: generate, translate and attach a srt file to a video
                                                                                                         
        ====================
        ====================
         usage examples:
                                                                                                      
            python3 captions.py generate <path_to_video>
            python3 captions.py attach <path_to_video> (the srt you wish to attach is assumed to be created by this script, i.e. named according to OUTPUT_SRT)
                                                                                                      
            python3 captions.py translate (the srt you wish to translate is assumed to be created by this script, i.e. named according to OUTPUT_SRT)
                                                                                                      
            python3 captions.py youtube-c <youtube_link>  
                                                                                                      
            python3 captions.py youtube-all <youtube_link>   
                                                                                                                                                                    
        ====================
                                                                                                      
         '''))
    parser.add_argument(
        "mode", metavar="mode", type=str, help="operation mode, valid values:  %s" % str(VALID_MODES)
    )
    parser.add_argument("path", nargs="?", metavar="path", type=str, help="filepath or link of the video")
    args = parser.parse_args()
    mode = args.mode
    path = args.path
    

    if not check_ffmpeg():
        print("ffmpeg must be installed to run this script, quitting")
        time.sleep(3)
        exit()

    if len(mode) > 0:
        yt_mode = True if mode in YT_MODES else False
        utility = Utility(path, yt_mode)

        if mode in VALID_MODES and (utility.file_exists() or mode == "translate"):
            flag = 0
            if  mode == VALID_MODES[0] or mode == VALID_MODES[2] or mode == VALID_MODES[4]:
                flag = 1
            videomanager = VideoManager(utility.path, yt_mode,flag)
            subtitle_generator = SubtitleGenerator(videomanager)

            if mode == VALID_MODES[1] or mode == VALID_MODES[5]:
                action_gen(subtitle_generator)
            elif mode == VALID_MODES[0] or mode == VALID_MODES[4]:
                videomanager.video = VideoFileClip(path)
                action_attach(subtitle_generator)
            elif mode == VALID_MODES[2]:
                action_translate(utility,subtitle_generator)
            elif mode == VALID_MODES[3]:
                action_gen(subtitle_generator)
                action_translate(utility,subtitle_generator)
                action_attach(subtitle_generator)
            elif mode == VALID_MODES[6]:
                l1,l2 = action_translate(utility,subtitle_generator,None,None,"only_input")
                action_gen(subtitle_generator)
                action_translate(utility,subtitle_generator,l1,l2,"only_translate")
                action_attach(subtitle_generator)
            elif mode == VALID_MODES[7] or mode == VALID_MODES[8]:
                action_gen(subtitle_generator)
                action_attach(subtitle_generator)
            utility.ask_user_for_cleanup()
              
        else:
            print("======================")
            print("invalid mode or file path, use \"python3 captions.py -h\" or see below for usage instructions, quitting")
            print("======================\n\n\n")
            parser.print_help()
            time.sleep(3)
            exit()
            


if __name__ == "__main__":
    main()
   
