async function loadJson(url) {
    const response = await fetch(url);

    if (url.endsWith(".jsonl")) {
        const text = await response.text();
        const lines = text.split('\n').filter(line => line.trim() !== '');
        return lines.map(line => JSON.parse(line));
    }

    return await response.json()
}

async function fetchStickerPacks() {
    const paths = ["data/line.json", "data/tele.json", "data/sticker.json", "data/line_stickers.jsonl"]
    let packs = []
    for (let path of paths) {
        packs = packs.concat(await loadJson(path));
    }
    return packs;
}

function createPackElement(pack, onClick) {
    const div = document.createElement('div');
    div.className = 'pack-item';
    const img = document.createElement('img');
    img.src = pack.iconUrl || pack.thumbImg;
    img.alt = pack.name;
    img.title = pack.name;
    img.width = 64;
    img.height = 64;
    const name = document.createElement('div');
    name.className = 'pack-name';
    name.textContent = pack.name;
    div.appendChild(img);
    div.appendChild(name);
    div.onclick = () => onClick(pack);
    return div;
}

function loadImage(src) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = src;
        img.crossOrigin = "Anonymous";

        img.onload = () => resolve(img);
        img.onerror = (err) => reject(err);
    });
}

async function createGif(url, is_gif = false) {
    console.log(url)

    const spriteSheet = await loadImage(url);
    const width = spriteSheet.width;
    const height = spriteSheet.height;
    console.log(width, height)

    if (!is_gif) {
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const context = canvas.getContext('2d', { willReadFrequently: true });
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(
            spriteSheet,
            0, 0, width, height,
            0, 0, canvas.width, canvas.height
        );
        return canvas.toDataURL()
    }

    var frameSize = Math.min(width, height);
    var frameWidth = frameSize;
    var frameHeight = frameSize;

    const canvas = document.createElement('canvas');
    canvas.width = frameWidth;
    canvas.height = frameHeight;
    var context = canvas.getContext('2d', { willReadFrequently: true });

    const framesX = Math.floor(width / frameWidth);
    const framesY = Math.floor(height / frameHeight);

    console.log(framesX, framesY, frameWidth, frameHeight)

    var encoder = new GIFEncoder();
    encoder.setRepeat(0);
    encoder.setDelay(100);
    encoder.setTransparent(0x000000);
    encoder.setQuality(256)
    encoder.start();

    for (let y = 0; y < framesY; y++) {
        for (let x = 0; x < framesX; x++) {
            context.clearRect(0, 0, canvas.width, canvas.height);
            context.drawImage(
                spriteSheet,
                x * frameWidth, y * frameHeight, frameWidth, frameHeight,
                0, 0, canvas.width, canvas.height
            );

            console.log("Frame", x, y)

            encoder.addFrame(context);
        }
    }

    encoder.finish();
    var buffer = encoder.stream().getData();
    return 'data:image/gif;base64,' + encode64(buffer);
}


async function createStickerElement(sticker) {
    const div = document.createElement('div');
    div.className = 'sticker-item';
    const img = document.createElement('img');
    // img.src = sticker.url;
    var url = sticker.url;
    var spriteUrl = null;
    if (url.includes("combot.org")) {
        url = "https://cors.rin2401.workers.dev/" + url
    } else {
        spriteUrl = url.replace(
            "https://zalo-api.zadn.vn/api/emoticon/sticker/webpc",
            "https://zalo-api.zadn.vn/api/emoticon/sprite",
        )
    }
    url = await createGif(url, false)

    img.src = url
    img.alt = '';
    img.width = 64;
    img.height = 64;
    div.appendChild(img);
    div.onclick = async () => {
        let copied = false;
        try {
            console.log(sticker.url)
            if (spriteUrl) {
                img.src = await createGif(spriteUrl, true)
            }
            const response = await fetch(url);
            const blob = await response.blob();
            console.log("Blob", blob)
            if (window.ClipboardItem) {
                console.log("ClipboardItem")
                const item = new ClipboardItem({ [blob.type]: blob });
                await navigator.clipboard.write([item]);
                copied = true;
            }
        } catch (e) {
            console.log("Error", e)
            await navigator.clipboard.writeText(sticker.url);
        }
        if (copied) {
            div.classList.add('copied');
            setTimeout(() => div.classList.remove('copied'), 1000);
        } else {
            div.classList.add('copy-error');
            setTimeout(() => div.classList.remove('copy-error'), 1000);
        }
    };
    return div;
}

function showPackList(packs) {
    const stickerList = document.getElementById('sticker-list');
    stickerList.innerHTML = '';
    packs.forEach(pack => {
        stickerList.appendChild(createPackElement(pack, packObj => showStickerList(packObj, packs)));
    });
}

function showStickerList(pack, packs) {
    const stickerList = document.getElementById('sticker-list');
    stickerList.innerHTML = '';
    const backBtn = document.createElement('button');
    backBtn.textContent = '← Quay lại';
    backBtn.className = 'back-btn';
    backBtn.onclick = () => showPackList(packs);
    stickerList.appendChild(backBtn);
    pack.stickers.forEach(async (sticker) => {
        stickerList.appendChild(await createStickerElement(sticker));
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const packs = await fetchStickerPacks();
    showPackList(packs);
});
