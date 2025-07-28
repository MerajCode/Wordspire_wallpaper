import os
import sys
import subprocess  

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.getenv("APPDATA"), "Wordspire_by_merajcode")
    else:
        return os.path.dirname(os.path.abspath(__file__))

def split_quote_for_image(quote_text):
    """
    Intelligently splits a quote into four parts to fit the image template.
    This function remains unchanged.
    """
    words = quote_text.strip().split()
    num_words = len(words)

    if num_words < 4:
        print("Warning: Quote is very short. The result might not look optimal.")
        part1 = words[0] if num_words >= 1 else ""
        part4 = words[1] if num_words >= 2 else ""
        part2_bold = words[2] if num_words >= 3 else ""
        return part1, "", part2_bold, "", part4

    p1_end = max(1, int(num_words * 0.30))
    p2_end = max(p1_end + 1, int(num_words * 0.65))
    p3_end = max(p2_end + 1, int(num_words * 0.80))

    part1_words = words[:p1_end]
    part2_words = words[p1_end:p2_end]
    part3_words = words[p2_end:p3_end]
    part4_words = words[p3_end:]
    
    if not part4_words and part3_words:
        part4_words = [part3_words.pop()]

    part2_normal_words = part2_words[:-1] if len(part2_words) > 0 else []
    part2_bold_word = part2_words[-1] if part2_words else ""

    part1 = " ".join(part1_words)
    part2_normal = " ".join(part2_normal_words)
    part2_bold = part2_bold_word
    part3 = " ".join(part3_words)
    part4 = " ".join(part4_words)
    
    return part1, part2_normal, part2_bold, part3, part4

def quote_image(data, output_file, scale):
    font_size = lambda size: f"{int(size * scale)}px"
    base_path = get_base_path()
    
    p1, p2, p3, p4, p5 = split_quote_for_image(data.get("quote", ""))
    word = data.get("word", "")
    meaning = data.get("meaning", "")
    example = data.get("example", "")
    font_folder = os.path.join(base_path, "font")
    font_regular = os.path.join(font_folder, "Oswald-Regular.ttf").replace("\\", "/")
    font_bold = os.path.join(font_folder, "Oswald-Bold.ttf").replace("\\", "/")

    html = f"""
    <html>
    <head>
        <style>
            @font-face {{ font-family: 'Oswald'; src: url("file:///{font_regular}") format('truetype'); font-weight: 400; }}
            @font-face {{ font-family: 'Oswald'; src: url("file:///{font_bold}") format('truetype'); font-weight: 700; }}
            body {{ width: 1920px; height: 1080px; margin: 0; margin-top:260px; background: black; color: white; font-family: 'Oswald', 'Arial Narrow', sans-serif; overflow: hidden; align-items: center; justify-content: flex-end; }}
            .container {{ margin-left: 45%; text-align: left; text-transform: uppercase; align-items: center; gap: 15px; }}
            .quote {{ text-transform: uppercase; text-align: left; border-left:3px solid white; padding-left:22px; padding-bottom:40px; }}
            .quote p {{ margin: 0; line-height: 1; width:920px; }}
            .win {{ color: #D95D25; font-size: {font_size(64)}; font-weight: 700; }}
            .not-immediately {{ color: #FFFFFF; font-size: {font_size(42)}; }}
            .not-immediately span {{ font-weight: 700; }}
            .but {{ color: #45B0C2; font-size: {font_size(64)}; font-weight: 700; }}
            .definitely {{ color: #E1CD00; font-size: {font_size(96)}; font-weight: 700; letter-spacing: 1px; }}
            .words {{ margin-top:140px; text-transform: uppercase; text-align: left; border-left:3px solid white; padding-left:22px; padding-bottom:40px; }}
            .words p {{ margin: 0; line-height: 1.1; letter-spacing:2px; text-wrap:wrap; width:920px; }}
            .word {{ color: #D95D25; font-size: {font_size(28)}; font-weight: 700; }}
            .meaning {{ color: #FFFFFF; font-size: {font_size(18)}; margin-left:50px; font-style:italic; }}
            .example {{ color: #FFFFFF; font-size: {font_size(22)}; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="quote">
                <p class="win">{p1}</p>
                <p class="not-immediately">{p2}&nbsp;<span>{p3}</span></p>
                <p class="but">{p4}</p>
                <p class="definitely">{p5}</p>
            </div>
            <div class="words">
                <p class="word">{word}</p>
                <p class="meaning">{meaning}</p>
                <p class="example">{example}</p>
            </div>
        </div>
    </body>
    </html>
    """

    path_wkhtmltoimage = os.path.join(base_path, "wkhtmltoimage.exe")

    command = [
        path_wkhtmltoimage,
        '--format', 'jpg',
        '--quality', '100',
        '--width', '1920',
        '--height', '1080',
        '--enable-local-file-access',
        '--quiet',
        '-',  
        output_file 
    ]
    
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        stdout, stderr = process.communicate(input=html.encode('utf-8'))
        
        if process.returncode != 0:
            print(f"Image generation failed: {stderr.decode('utf-8', 'ignore')}")

    except FileNotFoundError:
        print(f"Error: '{path_wkhtmltoimage}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred during image generation: {e}")