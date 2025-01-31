import { generateImage, submitSolution } from './common_api.js';
import { splitText, getCookie } from './utils.js';
import { logTaskEnd, logTaskStart, resultSelectedAsSolution,
resultDisselectedAsSolution, resultDeleted} from './log_api.js';

let displayedUserOutputs = [];
let solutionIndex = -1;
let firstTaskDone = false;

let usedPrompts = [];

const TASK_1 = `
Imagine that you are in the following scenario:<br><br>

You want to have a custom desktop wallpaper for your computer based on your
favorite book / tv series / movie / videogame. <br><br>

Please create the wallpaper using the the AI image generator.
`;

const TASK_2 = `
Imagine that you are in the following scenario:<br><br>

You want to have a custom desktop wallpaper for your computer based on your
favorite book / tv series / movie / videogame. <br><br>

Please create the wallpaper using the the AI image generator.
`;

function updateDisplayedUserOutputs() {
    const userOutputContainer = document.getElementById('user-output-list');
    const modal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const closeModal = document.querySelector('.modal .close');

    // Clear the container
    while (userOutputContainer.firstChild) {
        userOutputContainer.removeChild(userOutputContainer.firstChild);
    }

    displayedUserOutputs.forEach((userOutput, index) => {
        const userOutputElement = document.createElement('div');
        // Split prompt between multiple lines if it is too long
        const promptLines = splitText(userOutput.prompt, 35);
        const promptHtml = promptLines.map(line => `<span>${line}</span>`).join('<br>');

        userOutputElement.className = 'image-entry';

        if(usedPrompts.length > 2){
            userOutputElement.innerHTML = `
                <img src="data:image/png;base64,${userOutput.image}" class="thumbnail"/>
                <p style="font-size: 16px;">${promptHtml}<br><br>
                <a href="#" class="delete-link" style="font-size: 16px;">Delete Image</a>
                <a href="#" class="solution-link"  style="font-size: 16px; background-color: ${solutionIndex === index ? 'lightgreen' : ''}">Select as Solution</a></p>
            `;
        }
        else{
            userOutputElement.innerHTML = `
                <img src="data:image/png;base64,${userOutput.image}" class="thumbnail"/>
                <p style="font-size: 16px;">${promptHtml}<br><br>
                <a href="#" class="delete-link" style="font-size: 16px;">Delete Image</a>
            `;
        }

        // Add event listeners for the delete and solution actions
        userOutputElement.querySelector('.delete-link').addEventListener('click', (event) => {
            event.preventDefault();
            deleteUserOutput(index);
            resultDeleted(getCookie("prolificPid"), userOutput.imageId);

        });
        
        if(usedPrompts.length > 2){
            userOutputElement.querySelector('.solution-link').addEventListener('click', (event) => {
                event.preventDefault();
                toggleSolutionMark(index);
                if (solutionIndex === index) {
                    resultSelectedAsSolution(getCookie("prolificPid"), userOutput.imageId);
                }
                else {
                    resultDisselectedAsSolution(getCookie("prolificPid"), userOutput.imageId);
                }
            });
        }

        // Add event listener for image click to display in modal
        userOutputElement.querySelector('.thumbnail').addEventListener('click', () => {
            modalImage.src = `data:image/png;base64,${userOutput.image}`;
            modal.style.display = "block";
        });

        userOutputContainer.appendChild(userOutputElement);
    });

    // Add event listener to close modal when the close button is clicked
    closeModal.addEventListener('click', () => {
        modal.style.display = "none";
    });

    // Close the modal when the user clicks anywhere outside the image
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    const windowHeight = window.innerHeight;
    const displayElementHeight = userOutputContainer.firstChild ? userOutputContainer.firstChild.clientHeight : 0;
    const maxNumberofUserOutputs = displayElementHeight ? Math.floor(windowHeight / displayElementHeight) : 0;
    if (displayedUserOutputs.length > maxNumberofUserOutputs &&
        displayedUserOutputs.length < maxNumberofUserOutputs + 2){
            onWindowResize();
    }
}

function deleteUserOutput(index) {
    displayedUserOutputs.splice(index, 1);
    if (solutionIndex === index) {
        solutionIndex = -1;
        hideSolution();
        document.getElementById("submit-solution-bt").disabled = true;
    } else if (solutionIndex > index) {
        solutionIndex--;
    }
    updateDisplayedUserOutputs();
}

function showSolution(solutionIndex) {
    const userOutput = displayedUserOutputs[solutionIndex];
    const prompt = userOutput.prompt;
    const image = userOutput.image;

    const promptLines = splitText(prompt, 35);
    const promptHtml = promptLines.map(line => `<span>${line}</span>`).join('<br>');

    const container = document.getElementById('solution-container');
    container.innerHTML = `
    <img src="data:image/png;base64,${image}"/>
    <p>${promptHtml}<br><br>
    `;
}

function hideSolution() {
    document.getElementById('solution-container').innerHTML = "";
}

function toggleSolutionMark(index) {
    if (solutionIndex === index) {
        solutionIndex = -1; // Unmark if already marked
        document.getElementById("submit-solution-bt").disabled = true;
        hideSolution();
    } else {
        solutionIndex = index; // Mark the new solution
        document.getElementById("submit-solution-bt").disabled = false;
        showSolution(solutionIndex);
    }
    updateDisplayedUserOutputs();
}

function onGenImageButtonClicked() {
    document.getElementById("gen-image-bt").disabled = true;
    document.getElementById("gen-image-bt").innerText = "Generating...";

    const prompt = document.getElementById('prompt-text-area').value;

    generateImage(prompt, 'study', getCookie("prolificPid")).then((data) => {
        document.getElementById("gen-image-bt").disabled = false;
        document.getElementById("gen-image-bt").innerText = "Generate Image";
        const userOutput = {
            prompt: prompt,
            image: data.data,
            imageId: data.imageId
        };
        if (!usedPrompts.includes(prompt)) {
            usedPrompts.push(prompt);
        }
        displayedUserOutputs.push(userOutput);
        updateDisplayedUserOutputs();
    }).catch((error) => {
        document.getElementById("gen-image-bt").disabled = false;
        document.getElementById("gen-image-bt").innerText = "Generate Image";
        console.error(error);
    });
}

function onPromptBoxInput(event) {
    if (document.getElementById("prompt-text-area").value.trim() === "") {
        document.getElementById("gen-image-bt").disabled = true;
    } else {
        document.getElementById("gen-image-bt").disabled = false;
    }
}

function clearUi() {
    displayedUserOutputs = [];
    usedPrompts = [];
    solutionIndex = -1;
    updateDisplayedUserOutputs();
    document.getElementById('prompt-text-area').value = "";
    document.getElementById("gen-image-bt").disabled = true;
    document.getElementById("submit-solution-bt").disabled = true;
    hideSolution();
}

function onSubmitSolutionButtonClicked() {
    if (solutionIndex === -1) {
        return;
    }

    const userId = getCookie("prolificPid");
    const imageId = displayedUserOutputs[solutionIndex].imageId
    const firstTask = getCookie("firstTask");

    let taskId = -1;
    if (firstTaskDone) {
        if (firstTask === '1') {
            taskId = 2;
        } else {
            taskId = 1;
        }
    } else {
        if (firstTask === '1') {
            taskId = 1;
        } else {
            taskId = 2;
        }
    }

    logTaskEnd(userId, taskId);
    submitSolution(userId, imageId, taskId).then(() => {
        if(firstTaskDone){
            // Redirect to survey
            window.location.href = "/terminateStudy?prolificPid=" + userId;
        }
        firstTaskDone = true;
        clearUi();
    }).catch((error) => {
        console.error(error);
    });

    if (taskId === 1) {
        taskId = 2;
        document.getElementById('task-field').innerHTML = TASK_2;
        logTaskStart(userId, 2);

    }
    else {
        taskId = 1;
        document.getElementById('task-field').innerHTML = TASK_1;
        logTaskStart(userId, 1);
    }
}

async function init() {
    document.getElementById('gen-image-bt').addEventListener('click', onGenImageButtonClicked);
    document.getElementById('prompt-text-area').addEventListener('input', onPromptBoxInput);
    document.getElementById('submit-solution-bt').addEventListener('click', onSubmitSolutionButtonClicked);

    // To make sure the button is disabled when the page is loaded
    onPromptBoxInput();
    document.getElementById("submit-solution-bt").disabled = true;

    firstTaskDone = getCookie("firstTaskDone") === "true";

    if (getCookie("firstTask") === '1') {
        if (firstTaskDone) {
            document.getElementById('task-field').innerHTML = TASK_2
            logTaskStart(getCookie("prolificPid"), 2);
        }
        else {
            document.getElementById('task-field').innerHTML = TASK_1;
            logTaskStart(getCookie("prolificPid"), 1);
        }
    }
    else {
        if (firstTaskDone) {
            document.getElementById('task-field').innerHTML = TASK_1;
            logTaskStart(getCookie("prolificPid"), 1);
        }
        else {
            document.getElementById('task-field').innerHTML = TASK_2;
            logTaskStart(getCookie("prolificPid"), 2);
        }
    }
}

// When the page is loaded, call the init function
window.onload = init;
