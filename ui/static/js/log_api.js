export async function sendLog(prolificPid, payload, url) {
    payload.prolificPid = prolificPid;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (result.result !== 'ok') {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}

export async function logSearch(prolificPid, searchQuerry, searchBy) {
    const url = '/api/log/search';

    const requestBody = {
        searchQuerry: searchQuerry,
        searchBy: searchBy
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function logSearchResultViewed(prolificPid, imgId){
    const url = '/api/log/searchResultViewed';

    const requestBody = {
        imgId: imgId
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function resultSelectedAsSolution(prolificPid, imgId){
    const url = '/api/log/resultSelectedAsSolution';

    const requestBody = {
        imgId: imgId
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function resultDisselectedAsSolution(prolificPid, imgId){
    const url = '/api/log/resultDisselectedAsSolution';

    const requestBody = {
        imgId: imgId
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function resultDeleted(prolificPid, imgId){
    const url = '/api/log/resultDeleted';

    const requestBody = {
        imgId: imgId
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function logTaskStart(prolificPid, task){
    const url = '/api/log/taskStart';

    const requestBody = {
        task: task
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function logTaskEnd(prolificPid, task){
    const url = '/api/log/taskEnd';

    const requestBody = {
        task: task
    };

    await sendLog(prolificPid, requestBody, url);
}

export async function logMapViewReset(prolificPid){
    const url = '/api/log/mapViewReset';

    const requestBody = {};

    await sendLog(prolificPid, requestBody, url);
}

export async function logMapViewChanged(prolificPid, position, zoom){
    const url = '/api/log/mapViewChanged';

    const requestBody = {
        position: position,
        zoom: zoom
    };

    await sendLog(prolificPid, requestBody, url);
}
