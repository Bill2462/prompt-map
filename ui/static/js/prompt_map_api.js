
export function parseMapData(data, isSearchResultFlag) {
    return data.map((element) => {
        element = {x: element.x,
                   y: element.y,
                   isSearchResultFlag: isSearchResultFlag,
                   data: element.data,
                   id: element.id,
                   img_level_1_shown: element.img_level_1_shown,
                   img_level_2_shown: element.img_level_2_shown};
        return element;
    });
}

export async function fetchGeneralLabels() {
    let url = '/api/map/labels/general';

    const response = await fetch(url);
    const result = await response.json();
    if(result.result == 'ok') {
        return parseMapData(result.data, false);
    } else {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}

export async function fetchDetailedLabels(visibleRange, level) {
    let url = '/api/map/labels/detailed';
    url += '?level=' + level;
    url += '&originXStart=' + visibleRange.xMin;
    url += '&originXEnd=' + visibleRange.xMax;
    url += '&originYStart=' + visibleRange.yMin;
    url += '&originYEnd=' + visibleRange.yMax;

    const response = await fetch(url);
    const result = await response.json();
    if(result.result == 'ok') {
        return parseMapData(result.data, false);
    } else {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}

export async function fetchPoints(visibleRange) {
    let url = '/api/map/points';
    url += '?originXStart=' + visibleRange.xMin;
    url += '&originXEnd=' + visibleRange.xMax;
    url += '&originYStart=' + visibleRange.yMin;
    url += '&originYEnd=' + visibleRange.yMax;
    const response = await fetch(url);
    const result = await response.json();
    if(result.result == 'ok') {
        return parseMapData(result.data, false);
    } else {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}

export async function fetchImagePreviewPoints(visibleRange, level) {
    let url = '/api/map/imagePreview';
    url += '?originXStart=' + visibleRange.xMin;
    url += '&originXEnd=' + visibleRange.xMax;
    url += '&originYStart=' + visibleRange.yMin;
    url += '&originYEnd=' + visibleRange.yMax;
    url += '&level=' + level;

    const response = await fetch(url);
    const result = await response.json();
    if(result.result == 'ok') {
        return parseMapData(result.data, false);
    } else {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}

export async function runSearch(querry, searchBy) {
    const url = '/api/search/promptMap?querry=' + querry + '&searchBy=' + searchBy  + '&nPoints=500';

    const response = await fetch(url);
    const result = await response.json();
    if(result.result == 'ok') {
        return parseMapData(result.data, true);
    } else {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}
