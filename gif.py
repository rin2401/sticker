import json
from PIL import Image


def create_gif_from_spritesheet(
    spritesheet_path, output_file, frame_size=None, duration=100, loop=0, scale=1
):
    sprite_sheet = Image.open(spritesheet_path)
    width, height = sprite_sheet.size

    if not frame_size:
        frame_width = min(width, height)
        frame_height = min(width, height)
    else:
        frame_width, frame_height = frame_size

    frames_x = width // frame_width
    frames_y = height // frame_height

    frames = []
    for y in range(frames_y):
        for x in range(frames_x):
            left = x * frame_width
            upper = y * frame_height
            right = left + frame_width
            lower = upper + frame_height

            frame = sprite_sheet.crop((left, upper, right, lower))

            frame = frame.resize((frame_width * scale, frame_height * scale))

            frames.append(frame)

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        optimize=True,
    )

    print(f"GIF created successfully at {output_file}")


with open("data/sticker.json") as f:
    data = json.load(f)


def get_spritesheet_path(cid):
    for s in data:
        for sticker in s["stickers"]:
            if cid in sticker["url"]:
                path = f"data/sprite/{s['id']}/{sticker['id']}.png"
                return path


if __name__ == "__main__":
    path = get_spritesheet_path("50506")

    create_gif_from_spritesheet(
        path,
        "test.gif",
        duration=100,
        loop=0,
    )
