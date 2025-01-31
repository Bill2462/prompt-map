import { generateImage } from './common_api.js';
import { splitText, getCookie } from './utils.js';

const TASK_1 = `
<h4> Welcome to the quick tutorial for AI image generator</h4>

To start, please write a simple caption describing a scene in a textbox labelled "Prompt".<br><br>
Then press the "Generate Image" button to make an image. <br><br>

Example captions:

<ol>
<li>Red car on a highway</li>
<li>Dragon in a lush forest</li>
<li>Sunset on a tropical beach</li>
</ol>
<br>

Note: You can can click on the generated image to make the preview bigger.<br><br>

To unlock the next step, you need to generate new image.
`;

const TASK_2 = `
AI image generator that we use can also understand more complex captions. <br><br>

Now, add more details to your original caption and generate a new image. <br><br>

Examples:

<ol>
<li>Red sports car driving on a highway through a desert</li>
<li>Magnificent yellow dragon playing guitar on a small clearing in a misty forest</li>
<li>Sun setting behind storm clouds with lightning, seen from a tropical beach</li>
</ol><br><br>

To unlock the next step, you need to generate new image.
`;

const TASK_3 = `
You can also modify the image's medium. <br><br>

A medium can be, for example: “oil painting”, “watercolor painting”, “sketch”, etc.<br><br>

Medium is often placed either on the beginning or at the end of a prompt.<br><br>

For example:
<ol>
<li>Oil painting of a penguin plushy on the wooden desk</li>
<li>Surface of a desolated planet, oil painting</li>
</ol>

<br>
Now, please modify your image by changing its medium.<br><br>

To unlock the next step, you need to generate new image.
`;

const TASK_4 = `
Finally, you can also specify lighting, color palette, mood, and atmosphere of the image. <br><br>

Those parameters are often added to the end of the prompt.<br><br>

For example: “Blue car in the forest, eerie atmosphere, cold colors” <br><br>


Examples:
<ol>
<li>Atmosphere added: Container ship sailing through a sea, mysterious atmosphere</li>
<li>Color Palette added: Aquarel painting showing a cute lizard sitting on the rock</li>
<li>Lighting added: Living room in a wooden cottage, warm, soft light</li>
<li>Mood added: Person sitting on a rock on the side of the lake, somber, reflective mood</li>
</ol>

<br>
Now, please modify your image to change the atmosphere, color palette, lighting, or mood of your image.<br><br>

To unlock the next step, you need to generate new image.
`;

const TASK_5 = `
This is the end of the AI image generator tutorial! <br><br>

You can also try out some other prompts if you want to experiment a bit. <br><br>

When you are ready, please click on this link to move to the next part of the study:
`;

let currentTask = 1;
let unlockedTasks = [true, false, false, false, false];

let displayedUserOutputs = [];

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
        userOutputElement.innerHTML = `
            <img src="data:image/png;base64,${userOutput.image}" class="thumbnail"/>
            <p style="font-size: 16px;">${promptHtml}<br><br>
        `;

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
}

function onGenImageButtonClicked() {
    document.getElementById("gen-image-bt").disabled = true;
    document.getElementById("gen-image-bt").innerText = "Generating...";

    const prompt = document.getElementById('prompt-text-area').value;

    generateImage(prompt, 'tutorial', getCookie("prolificPid")).then((data) => {
        document.getElementById("gen-image-bt").disabled = false;
        document.getElementById("gen-image-bt").innerText = "Generate Image";
        const userOutput = {
            prompt: prompt,
            image: data.data
        };
        displayedUserOutputs.push(userOutput);
        updateDisplayedUserOutputs();

        // Unlock the next task
        if (currentTask < unlockedTasks.length) {
            unlockedTasks[currentTask] = true;
        }
        // Optionally: Move to the next task
        // currentTask++;
        updateTask();
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

function updateTask() {
    let taskDescription = '';
    if (currentTask === 1) {
        taskDescription = TASK_1;
    } else if (currentTask === 2) {
        taskDescription = TASK_2;
    } else if (currentTask === 3) {
        taskDescription = TASK_3;
    } else if (currentTask === 4) {
        taskDescription = TASK_4;
    } else if (currentTask >= 5) {
        const userId = getCookie("prolificPid");
        taskDescription = TASK_5 + `<a href="https://koala-sharp-endlessly.ngrok-free.app/uiTutorial?prolificPid=${userId}">Next Phase</a>`;
    }

    // Add Prev and Next navigation links at the bottom
    let navigationLinks = '<br><br><div id="task-navigation">';

    // Add Prev link (disabled if on the first task)
    if (currentTask > 1) {
        navigationLinks += `<button class="prev-link">Previous tutorial step</button> `;
    } else {
        navigationLinks += `<button style="color: grey;" disabled>Previous tutorial step</button> `;
    }

    // Add Next link (disabled if the next task is not unlocked)
    if (currentTask < unlockedTasks.length && unlockedTasks[currentTask]) {
        navigationLinks += `<button  class="next-link">Next tutorial step</button>`;
    } else {
        navigationLinks += `<button style="color: grey;" disabled>Next tutorial step</button>`;
    }

    navigationLinks += '</div>';

    document.getElementById("task-field").innerHTML = taskDescription + navigationLinks;

    // Add event listeners for Prev and Next links
    const prevLink = document.querySelector('.prev-link');
    const nextLink = document.querySelector('.next-link');

    if (prevLink) {
        prevLink.addEventListener('click', (event) => {
            event.preventDefault();
            if (currentTask > 1) {
                currentTask--;
                updateTask();
            }
        });
    }

    if (nextLink) {
        nextLink.addEventListener('click', (event) => {
            event.preventDefault();
            if (currentTask < unlockedTasks.length && unlockedTasks[currentTask]) {
                currentTask++;
                updateTask();
            }
        });
    }
}

async function init() {
    document.getElementById('gen-image-bt').addEventListener('click', onGenImageButtonClicked);
    document.getElementById("prompt-text-area").addEventListener("input", onPromptBoxInput);

    // To make sure the button is disabled when the page is loaded
    onPromptBoxInput();
    updateTask();
}

// When the page is loaded, call the init function
window.onload = init;
