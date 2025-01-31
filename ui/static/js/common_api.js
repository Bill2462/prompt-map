
export async function generateImage(prompt, phase, prolificPid) {
    let url = '/api/makeImage?prompt=' + prompt;
    url += '&phase=' + phase;
    url += '&prolificPid=' + prolificPid;

    const response = await fetch(url);
    const result = await response.json();
    if(result.result == 'ok') {
        return result;
    } else {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}

export async function submitSolution(prolificPid, imgId, task) {
    const url = '/api/log/solution';

    const requestBody = {
        prolificPid: prolificPid,
        imgId: imgId,
        task: task
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
    });

    const result = await response.json();
    if (result.result !== 'ok') {
        throw new Error('Error fetching data from API: ' + result.message);
    }
}