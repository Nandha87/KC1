# tele_GUI.py
from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from luma.core.render import canvas
from PIL import ImageFont
import time
from pathlib import Path

# OLED setup
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = ssd1309(serial, width=128, height=64)

# Load a better font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except:
    font = ImageFont.load_default()

line_height = font.getsize("A")[1] + 2

def load_script(file_path):
    file_path = Path(file_path)  
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            script_text = f.read()
    except Exception as e:
        script_text = f"Error loading file:\n{e}"

    lines = script_text.split('\n')
    scroll_text = [(line, i * line_height) for i, line in enumerate(lines)]
    return scroll_text

def scroll_teleprompter(scroll_text):
    y_offset = device.height
    total_height = len(scroll_text) * line_height

    while True:
        with canvas(device) as draw:
            for text, y in scroll_text:
                ypos = y + y_offset
                if -line_height < ypos < device.height:
                    draw.text((0, ypos), text, fill="white", font=font)
        y_offset -= 1
        if y_offset < -total_height:
            y_offset = device.height
        time.sleep(0.05)

def start_teleprompter(file_path):
    scroll_text = load_script(file_path)
    scroll_teleprompter(scroll_text)

if __name__ == "__main__":
    print("This module is meant to be imported, not run directly.")
