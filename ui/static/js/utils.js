export function splitText(text, maxLineLength) {
    const words = text.replace(/(\r\n|\n|\r)/gm, ' ').split(' ');
    const lines = [];
    let currentLine = '';

    for (const word of words) {
        if ((currentLine + word).length <= maxLineLength) {
            currentLine += (currentLine.length ? ' ' : '') + word;
        } else {
            if (currentLine.length) {
                lines.push(currentLine);
            }
            currentLine = word;
        }
    }

    if (currentLine.length) {
        lines.push(currentLine);
    }

    return lines;
}

export function getCookie(name) {
    let cookieArr = document.cookie.split(";");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if(name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}
