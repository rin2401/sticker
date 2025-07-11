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
    const paths = ["data/tele.json", "data/sticker.json", "data/line_stickers.jsonl"]
    let packs = []
    for (let path of paths) {
        packs = packs.concat(await loadJson(path));
    }
    return packs;
}

async function getFavoritePacks() {
    return JSON.parse(localStorage.getItem('favoritePacks') || '[]');
}
async function setFavoritePacks(favs) {
    return localStorage.setItem('favoritePacks', JSON.stringify(favs));
}


const heartPath = `M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41 0.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z`;
const heartFilled = `<svg width="18" height="18" viewBox="0 0 24 24" fill="#e25555" xmlns="http://www.w3.org/2000/svg"><path d="${heartPath}"/></svg>`;
const heartOutline = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e25555" stroke-width="2" xmlns="http://www.w3.org/2000/svg"><path d="${heartPath}"/></svg>`;

function createPackElement(pack, onClick) {
    let packId = pack.id;
    let div = document.createElement('div');
    div.className = 'pack-item';
    div.style.position = 'relative';

    let heartBtn = document.createElement('button');
    heartBtn.className = 'favorite-btn';
    heartBtn.style.position = 'absolute';
    heartBtn.style.top = '4px';
    heartBtn.style.right = '4px';
    heartBtn.style.background = 'transparent';
    heartBtn.style.border = 'none';
    heartBtn.style.cursor = 'pointer';
    heartBtn.style.padding = '0';
    heartBtn.style.zIndex = '2';
    heartBtn.innerHTML = heartOutline;
    div.appendChild(heartBtn);

    (async () => {
        const favs = await getFavoritePacks();
        if (favs.includes(packId)) {
            heartBtn.innerHTML = heartFilled;
            heartBtn.setAttribute('data-fav', '1');
        } else {
            heartBtn.innerHTML = heartOutline;
            heartBtn.setAttribute('data-fav', '0');
        }
    })();

    heartBtn.onclick = async (e) => {
        e.stopPropagation();
        let favs = await getFavoritePacks();
        if (favs.includes(packId)) {
            favs = favs.filter(id => id !== packId);
            heartBtn.innerHTML = heartOutline;
            heartBtn.setAttribute('data-fav', '0');
        } else {
            favs.push(packId);
            heartBtn.innerHTML = heartFilled;
            heartBtn.setAttribute('data-fav', '1');
        }
        await setFavoritePacks(favs);
    };

    let img = document.createElement('img');
    img.src = pack.iconUrl || pack.thumbImg;
    img.alt = pack.name;
    img.title = pack.name;
    img.width = 64;
    img.height = 64;
    let name = document.createElement('div');
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

async function createImgBase64(url, is_gif = false) {
    const response = await fetch(url);
    const buffer = await response.arrayBuffer()
    const bytes = new Uint8Array(buffer);
    let binary = '';
    bytes.forEach(byte => binary += String.fromCharCode(byte));
    const base64 = btoa(binary);

    if (is_gif) {
        return 'data:image/gif;base64,' + base64;
    }
    return 'data:image/png;base64,' + base64;
}

async function createGifBase64(url) {
    const spriteSheet = await loadImage(url);
    const width = spriteSheet.width;
    const height = spriteSheet.height;

    let frameSize = Math.min(width, height);
    let frameWidth = frameSize;
    let frameHeight = frameSize;

    const canvas = document.createElement('canvas');
    canvas.width = frameWidth;
    canvas.height = frameHeight;
    let context = canvas.getContext('2d', { willReadFrequently: true });

    let framesX = Math.floor(width / frameWidth);
    let framesY = Math.floor(height / frameHeight);

    let encoder = new GIFEncoder();
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
            encoder.addFrame(context);
        }
    }

    encoder.finish();
    var buffer = encoder.stream().getData();
    return 'data:image/gif;base64,' + btoa(buffer);
}


async function createStickerElement(sticker) {
    const div = document.createElement('div');
    div.className = 'sticker-item';
    const img = document.createElement('img');
    // img.src = sticker.url;
    img.alt = '';
    img.width = 64;
    img.height = 64;
    div.appendChild(img);

    var url = sticker.url;
    var spriteUrl = null;
    var animationUrl = null;

    if (url.includes("combot.org")) {
        url = "https://cors.rin2401.workers.dev/" + url
    } else if (url.includes("zalo-api.zadn.vn")) {
        spriteUrl = url.replace(
            "https://zalo-api.zadn.vn/api/emoticon/sticker/webpc",
            "https://zalo-api.zadn.vn/api/emoticon/sprite",
        )
        url = url.replace("size=130", "size=240")
    } else if (url.includes("line-scdn.net") && url.includes("sticker@")) {
        animationUrl = url.replace(
            "sticker@",
            "sticker_animation@",
        )
    }

    base64_url = await createImgBase64(url)

    img.src = base64_url
    div.onclick = async () => {
        let copied = false;
        try {
            console.log(url)
            if (spriteUrl) {
                console.log("Sprite URL:", spriteUrl)
                img.src = await createGifBase64(spriteUrl)
            } else if (animationUrl) {
                console.log("Animation URL:", animationUrl)
                img.src = await createImgBase64(animationUrl, true)
            }
            const response = await fetch(base64_url);
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

async function showPackList(packs) {
    const stickerList = document.getElementById('sticker-list');
    stickerList.innerHTML = '';

    let favs = await getFavoritePacks();
    packs = packs.sort((a, b) => favs.includes(a.id) ? -1 : 1);

    packs.forEach(pack => {
        stickerList.appendChild(createPackElement(pack, packObj => showStickerList(packObj, packs)));
    });
}

function showStickerList(pack, packs) {
    const stickerList = document.getElementById('sticker-list');
    stickerList.innerHTML = '';
    const backBtn = document.createElement('div');
    backBtn.className = 'back-btn sticker-item copied';
    const img = document.createElement('img');
    img.alt = 'Quay lại';
    img.width = 64;
    img.height = 64;
    img.src = "back.png"
    backBtn.appendChild(img);
    backBtn.onclick = () => showPackList(packs);
    stickerList.appendChild(backBtn);
    pack.stickers.forEach(async (sticker) => {
        stickerList.appendChild(await createStickerElement(sticker));
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const packs = await fetchStickerPacks();
    showPackList(packs);

    const searchInput = document.getElementById('search-bar');
    const searchBtn = document.getElementById('search-btn');

    function filterPacks() {
        const query = searchInput.value.trim().toLowerCase();
        if (!query) {
            showPackList(packs);
            return;
        }
        const filtered = packs.filter(pack => pack.name && pack.name.toLowerCase().includes(query));
        showPackList(filtered);
    }

    searchInput.addEventListener('input', filterPacks);
    searchBtn.addEventListener('click', filterPacks);
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') filterPacks();
    });
});
