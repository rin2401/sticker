async function fetchStickerPacks() {
    // Đọc sticker.json từ thư mục extension
    const response = await fetch('data/sticker.json');
    return await response.json();
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

function createStickerElement(sticker) {
    const div = document.createElement('div');
    div.className = 'sticker-item';
    const img = document.createElement('img');
    img.src = sticker.url;
    img.alt = '';
    img.width = 64;
    img.height = 64;
    div.appendChild(img);
    div.onclick = async () => {
        let copied = false;
        try {
            const response = await fetch(sticker.url);
            const blob = await response.blob();
            if (window.ClipboardItem) {
                const item = new ClipboardItem({ [blob.type]: blob });
                await navigator.clipboard.write([item]);
                copied = true;
            }
        } catch (e) {
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
    pack.stickers.forEach(sticker => {
        stickerList.appendChild(createStickerElement(sticker));
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    const packs = await fetchStickerPacks();
    showPackList(packs);
});
