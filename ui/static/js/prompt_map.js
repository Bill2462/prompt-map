import { fetchGeneralLabels, fetchDetailedLabels, fetchPoints, runSearch, fetchImagePreviewPoints} from './prompt_map_api.js';
import { splitText, getCookie } from './utils.js';
import { logSearchResultViewed, logMapViewReset, logMapViewChanged } from './log_api.js';

const GENERAL_LABEL_FONT_SIZE = 30;
const DETAILED_LABEL_MAX_FONT_SIZE = 20;
const DETAILED_LABEL_FONT_SIZE_SCALING = 1.5;
const GENERAL_LABEL_FONT_SIZE_SCALING = 10;
const POINT_RADIUS = 2;

const DISPLAY_DETAILED_LABELS_LVL2_THRESHOLD = 7.0;
const DISPLAY_DETAILED_LABELS_LVL1_THRESHOLD = 30.0;
const DISPLAY_DETAILED_POINTS_THRESHOLD = 70.0;

const AREA_THRESHOLD_FOR_DETAILED_LABELS_RELOAD = 0.3;
const AREA_THRESHOLD_FOR_POINTS_RELOAD = 0.3;

const MIN_SCALE = 1.5;
const INITIAL_SCALE = 1.5;
const MAX_SCALE = 200;

const ZOOM_SPEED_FACTOR = 0.05;

const LOADED_RANGE_MARGIN = 0.005;

const MAX_RADIUS_FOR_POPUP = 20;

const INITIAL_POINT_X = -0.25;
const INITIAL_POINT_Y = -0.25;

function getMousePositionInCanvas(canvas, event) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: (event.clientX - rect.left) / canvas.width,
        y: (event.clientY - rect.top) / canvas.height
    };
}

class ImageStore {
    constructor(drawCallback, maxSize = 5000) {
        this.store = new Map();
        this.maxSize = maxSize;
        this.drawCallback = drawCallback;
    }

    addImage(id, base64Image) {
        if (this.store.size >= this.maxSize) {
            this.purgeUnusedImages();
        }
        this.store.set(id, base64Image);
    }

    getImage(id) {
        return this.store.get(id);
    }

    hasImage(id) {
        return this.store.has(id);
    }

    purgeUnusedImages() {
        // Assuming that the PromptMap class will manage the currently displayed points
        // Purge all images not currently displayed
        // This is a simple FIFO purge strategy
        while (this.store.size > this.maxSize) {
            const firstKey = this.store.keys().next().value;
            this.store.delete(firstKey);
        }
    }

    async fetchAndAddImages(ids) {
        const fetchPromises = ids.map(id => {
            return fetch(`/api/getImage?fname=${id}`)
                .then(response => response.blob())
                .then(blob => new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve({ id, base64: reader.result });
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                }));
        });

        const results = await Promise.all(fetchPromises);
        results.forEach(result => this.addImage(result.id, result.base64));

        // Delay the redraw by 0.5 seconds after updating the image store
        setTimeout(() => {
            if (this.drawCallback) {
                this.drawCallback();
            }
        }, 500);
    }
}

function calcFractionOfOverlap(range1, range2){
    const xOverlap = Math.max(0, Math.min(range1.xMax, range2.xMax) - Math.max(range1.xMin, range2.xMin));
    const yOverlap = Math.max(0, Math.min(range1.yMax, range2.yMax) - Math.max(range1.yMin, range2.yMin));
    const overlapArea = xOverlap * yOverlap;
    const cumulativeArea = (range1.xMax - range1.xMin) * (range1.yMax - range1.yMin) + (range2.xMax - range2.xMin) * (range2.yMax - range2.yMin);
    const fractionOfOverlap = overlapArea / cumulativeArea;
    return fractionOfOverlap;
}

export class PromptMap {
    constructor() {
        this.home();
        this.displayImages = true;
        this.imageStore = new ImageStore(this.draw.bind(this));

        this.onMouseWheelTurned = this.onMouseWheelTurned.bind(this);
        this.onMouseDown = this.onMouseDown.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onCanvasResized = this.onCanvasResized.bind(this);
        this.updateInProgress = false;

        // Last positions where detailed labels and points were fetched
        this.rangeForFetchedPoints = null
        this.rangeForFetchedDetailedLabels = null;

        this.densityImage = new Image();
        this.densityImage.src = '/static/map_preview.jpg';

        // Initialize opacity for fading out the density image
        this.densityImageOpacity = 1.0;
    
       this.initTooltip();
    }

    home(){
        this.scale = INITIAL_SCALE;
        this.translation = { x: INITIAL_POINT_X, y: INITIAL_POINT_Y };
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.dragTranslationStart = { x: 0, y: 0 };

        // Translation in pixels for moving detailed tooltips
        this.lastMousePosition = null;
        this.translationInPixels = { x: 0, y: 0 };
    }

    initTooltip() {
        this.tooltip = document.createElement('div');
        this.tooltip.style.position = 'absolute';
        this.tooltip.style.backgroundColor = 'white';
        this.tooltip.style.border = '1px solid black';
        this.tooltip.style.padding = '5px';
        this.tooltip.style.display = 'none';
        document.body.appendChild(this.tooltip);
    }

    getVisibleRange() {
        const visibleXMin = -this.translation.x / this.scale;
        const visibleXMax = (1 - this.translation.x) / this.scale;
        const visibleYMin = -this.translation.y / this.scale;
        const visibleYMax = (1 - this.translation.y) / this.scale;

        return {
            xMin: visibleXMin - LOADED_RANGE_MARGIN/2,
            xMax: visibleXMax + LOADED_RANGE_MARGIN/2,
            yMin: visibleYMin - LOADED_RANGE_MARGIN/2,
            yMax: visibleYMax + LOADED_RANGE_MARGIN/2
        };
    }

    getGeneralLabelTextSize(){
        return Math.min(GENERAL_LABEL_FONT_SIZE,
            GENERAL_LABEL_FONT_SIZE_SCALING * this.scale);
    }

    getDetailedLabelTextSize(){
        return Math.min(DETAILED_LABEL_MAX_FONT_SIZE,
                        DETAILED_LABEL_FONT_SIZE_SCALING * this.scale);
    }

    getPointRadius(){
        return POINT_RADIUS;
    }

    shouldFetchDetailedLabelsData(){
        if (this.rangeForFetchedDetailedLabels === null) {
            return true;
        }

        const area = calcFractionOfOverlap(this.getVisibleRange(), this.rangeForFetchedDetailedLabels);
        return area < AREA_THRESHOLD_FOR_DETAILED_LABELS_RELOAD;
    }

    shouldFetchPointsData(){
        if (this.rangeForFetchedPoints === null) {
            return true;
        }

        const area = calcFractionOfOverlap(this.getVisibleRange(), this.rangeForFetchedPoints);
        return area < AREA_THRESHOLD_FOR_POINTS_RELOAD;
    }

    async fetchMapDataFromApi() {
        let promises = [];

        if(this.generalLabels === undefined){
            promises.push(fetchGeneralLabels().then(result => {
                this.generalLabels = result;
            }));
        }

        if(this.scale > DISPLAY_DETAILED_LABELS_LVL2_THRESHOLD &&
        (this.detailedLabelsLvl2 === undefined || this.shouldFetchDetailedLabelsData())){
            const visibleRange = this.getVisibleRange();

            promises.push(fetchDetailedLabels(visibleRange, 1).then(result => {
                this.detailedLabelsLvl1 = result;
            }));
            promises.push(fetchDetailedLabels(visibleRange, 2).then(result => {
                this.detailedLabelsLvl2 = result;
            }));

            promises.push(fetchImagePreviewPoints(this.getVisibleRange(), 2).then(result => {
                this.imagePreviewLevel2 = result;
                const ids = result.map(element => element.id);
                this.imageStore.fetchAndAddImages(ids).then(() => {});
            }));

            this.rangeForFetchedDetailedLabels = visibleRange;
        }

        if(this.scale >= DISPLAY_DETAILED_POINTS_THRESHOLD &&
        (this.points === undefined || this.shouldFetchPointsData())){
            const visibleRange = this.getVisibleRange();
            
            promises.push(fetchPoints(visibleRange).then(result => {
                this.points = result;
            }));

            let ids = [];
            promises.push(fetchImagePreviewPoints(this.getVisibleRange(), 1).then(result => {
                this.imagePreviewLevel1 = result;
                const ids = result.map(element => element.id);
                this.imageStore.fetchAndAddImages(ids).then(() => {});
            }));
            
            this.rangeForFetchedPoints = visibleRange;
        }
        
        await Promise.all(promises);
    }

    drawGeneralLabels(ctx){
        if(this.generalLabels === undefined){
            return;
        }

        ctx.font = 'bold ' + this.getGeneralLabelTextSize() + 'px Arial'; 
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        this.generalLabels.forEach(element => {
            const windowX = element.x * this.scale + this.translation.x;
            const windowY = element.y * this.scale + this.translation.y;
            ctx.fillText(element.data.label,
                         windowX * this.canvas.width,
                         windowY * this.canvas.height);
        });
    }

    drawDetailedLabels(ctx, lvl, becomesGeneral){
        if(becomesGeneral === true){
            ctx.font = 'bold ' + this.getDetailedLabelTextSize() + 'px Arial';
        }
        else{
            ctx.font = this.getDetailedLabelTextSize() + 'px Arial';
        }

        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        let detailedLabels = null;
        if (lvl === 1) {
            detailedLabels = this.detailedLabelsLvl1;
        }
        if (lvl === 2) {
            detailedLabels = this.detailedLabelsLvl2;
        }

        if(detailedLabels === undefined){
            return;
        }
    
        detailedLabels.forEach(element => {
            const windowX = element.x * this.scale + this.translation.x;
            const windowY = element.y * this.scale + this.translation.y;
            ctx.fillText(element.data.label,
                         windowX * this.canvas.width,
                         windowY * this.canvas.height);
        });
    }

    drawPoints(ctx){
        if(this.points === undefined && this.searchResults === undefined){
            return;
        }

        let points = [];
        if(this.searchResults !== undefined){
            points = points.concat(this.searchResults);
        }

        if(this.points !== undefined && this.scale > DISPLAY_DETAILED_POINTS_THRESHOLD){
            points = points.concat(this.points);
        }
        
    
        points.forEach(element => {
            const windowX = element.x * this.scale + this.translation.x;
            const windowY = element.y * this.scale + this.translation.y;
    
            ctx.beginPath();
            if(element.isSearchResultFlag){
                ctx.arc(windowX * this.canvas.width, windowY * this.canvas.height,
                        this.getPointRadius()*1.5, 0, 2 * Math.PI);
                ctx.fillStyle = 'red';
                ctx.fill();
                ctx.strokeStyle = `red`;
                ctx.stroke();
            }
            else{
                ctx.arc(windowX * this.canvas.width, windowY * this.canvas.height,
                    this.getPointRadius(), 0, 2 * Math.PI);
                ctx.fillStyle = 'black';
                ctx.fill();
                ctx.strokeStyle = `black`;
                ctx.stroke();
            }
        });
    }

    drawImages(ctx) {
        let points = [];

        if(this.imagePreviewLevel2 !== undefined && this.scale >= DISPLAY_DETAILED_LABELS_LVL2_THRESHOLD){
            points = points.concat(this.imagePreviewLevel2);
        }
        if(this.imagePreviewLevel1 !== undefined && this.scale >= DISPLAY_DETAILED_POINTS_THRESHOLD){
            points = points.concat(this.imagePreviewLevel1);
        }
    
        points.forEach(element => {
            const windowX = element.x * this.scale + this.translation.x;
            const windowY = element.y * this.scale + this.translation.y;

            const iconSize = 100; // Adjust size as needed
            const base64Image = this.imageStore.getImage(element.id);

            if (base64Image) {
                let icon = new Image();
                icon.src = base64Image;
                
                ctx.drawImage(icon, 
                              windowX * this.canvas.width - iconSize / 2, 
                              windowY * this.canvas.height - iconSize / 2, 
                              iconSize, iconSize);
            }
        });
    }

    drawDensityImage(ctx) {
        if (this.densityImage.complete) {
            // Calculate the coordinates between which the image should be drawn
            const windowXStart =  this.translation.x;
            const windowYStart =  this.translation.y;
            const windowXEnd = this.scale + this.translation.x;
            const windowYEnd = this.scale + this.translation.y;

    
            // Apply opacity
            ctx.globalAlpha = this.densityImageOpacity;
            
            // Draw the image with stretching to fit the canvas
            ctx.drawImage(this.densityImage,
                            windowXStart * this.canvas.width,
                            windowYStart * this.canvas.height,
                            (windowXEnd - windowXStart) * this.canvas.width,
                            (windowYEnd - windowYStart) * this.canvas.height);
            
            // Reset opacity
            ctx.globalAlpha = 1.0;
        }
    }

    draw() {
        let ctx = this.canvas.getContext('2d');
    
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        ctx.save();
        
        // Draw the density image in the background
        if (this.scale < DISPLAY_DETAILED_POINTS_THRESHOLD) {
            this.densityImageOpacity = 1.0 - ((this.scale - DISPLAY_DETAILED_LABELS_LVL1_THRESHOLD) / (DISPLAY_DETAILED_POINTS_THRESHOLD - DISPLAY_DETAILED_LABELS_LVL1_THRESHOLD));
            this.drawDensityImage(ctx);
        } else {
            this.densityImageOpacity = 0.0;
        }
        
        if(this.scale < DISPLAY_DETAILED_LABELS_LVL1_THRESHOLD)
        {
            this.drawGeneralLabels(ctx);
        }

        if(this.scale >= DISPLAY_DETAILED_LABELS_LVL2_THRESHOLD){
            const bolded = this.scale >= DISPLAY_DETAILED_LABELS_LVL1_THRESHOLD;
            this.drawDetailedLabels(ctx, 2, bolded);
        }

        if(this.scale >= DISPLAY_DETAILED_LABELS_LVL1_THRESHOLD){
            this.drawDetailedLabels(ctx, 1, false);
        }
    
        this.drawPoints(ctx);

        if(this.displayImages){
            this.drawImages(ctx);
        }

        ctx.restore();
    }

    fetchAndDraw() {
        if(this.updateInProgress || this.isDragging){
            this.draw();
            return;
        }

        this.updateInProgress = true
        this.fetchMapDataFromApi().then(() => {
            this.draw();
            this.updateInProgress = false;
        });
    }

    clampScale() {
        this.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, this.scale));
    }

    // Check if the mouse is hovering over a point and display tooltip
    checkMouseHover(mouseXpixels, mouseYpixels) {
        let points = [];
        if(this.searchResults !== undefined){
            points = points.concat(this.searchResults);
        }
        if(this.points !== undefined && this.scale >= DISPLAY_DETAILED_POINTS_THRESHOLD){
            points = points.concat(this.points);
        }
        if(this.imagePreviewLevel2 !== undefined && this.scale >= DISPLAY_DETAILED_LABELS_LVL2_THRESHOLD && this.displayImages){
            points = points.concat(this.imagePreviewLevel2);
        }
        if(this.imagePreviewLevel1 !== undefined && this.scale >= DISPLAY_DETAILED_POINTS_THRESHOLD && this.displayImages){
            points = points.concat(this.imagePreviewLevel1);
        }

        let closestPoint = null;
        let minDistance = Infinity;
        
        const rect = this.canvas.getBoundingClientRect();
        const mouseX = mouseXpixels - rect.left + 15;
        const mouseY = mouseYpixels - rect.top + 15;

        for (const point of points) {
            const windowX = point.x * this.scale + this.translation.x;
            const windowY = point.y * this.scale + this.translation.y;
    
            const distance = Math.abs(windowX * this.canvas.width - mouseX) +
                             Math.abs(windowY * this.canvas.height - mouseY);

            if (distance < minDistance) {
                closestPoint = point;
                minDistance = distance;
            }
        }

        this.closestPoint = { point: closestPoint, distance: minDistance,
                              x: mouseXpixels, y: mouseYpixels};
        if(closestPoint === null){
            this.hideTooltip();
            return;
        }
        let distanceThreshold;
        if(closestPoint.img_level_1_shown === true || closestPoint.img_level_2_shown === true){
            distanceThreshold = MAX_RADIUS_FOR_POPUP * 4;
        }
        else{
            distanceThreshold = MAX_RADIUS_FOR_POPUP;
        }

        if (minDistance <= distanceThreshold) {
            this.showTooltip(closestPoint, mouseXpixels, mouseYpixels);
        } else {
            this.hideTooltip();
        }
    }

    // Show tooltip near the hovered point
    showTooltip(point, mouseXpixels, mouseYpixels) {
        const pointData = point.data;
        this.tooltip.innerHTML = pointData.prompt;
        this.tooltip.style.left = `${mouseXpixels + 10}px`;
        this.tooltip.style.top = `${mouseYpixels + 10}px`;
        this.tooltip.style.display = 'block';

        const promptLines = splitText(pointData.prompt, 40).join('<br>');

        // Add content to the detailed tooltip
        this.tooltip.innerHTML = `
        <div style="display: flex; align-items: start;">
                <img src=/api/getImage?fname=${point.id} alt="Image Preview" style="max-width: 250px; margin-right: 10px;">
                <div style="font-size: 16px;">
                    <button class="close-tooltip" style="position: absolute; top: 5px; right: 5px; background: none; border: none; font-size: 18px; cursor: pointer;">X</button>
                    <p><strong>Prompt: </strong> ${promptLines}</p>
                    <p><strong>Location: </strong> ${pointData.location}</p>
                    <p><strong>Subject: </strong> ${pointData.subject}</p>
                    <p><strong>Lighting: </strong> ${pointData.lighting}</p>
                    <p><strong>Tone: </strong> ${pointData.tone} </p>
                    <p><strong>Mood: </strong> ${pointData.mood} </p>
                    <p><strong>Genre: </strong> ${pointData.genre} </p>
                    <button id="copy-prompt-bt" style="font-size: 16px;">Use Prompt</button>
                </div>
        </div>
        `;
    }

    // Hide the tooltip
    hideTooltip() {
        this.tooltip.style.display = 'none';
    }

    displayInfoWithPointData(pointData){
        const detailTooltip = document.createElement('div');
        detailTooltip.classList.add('detail-tooltip');
        detailTooltip.style.position = 'absolute';
        detailTooltip.style.backgroundColor = 'white';
        detailTooltip.style.border = '1px solid black';
        detailTooltip.style.padding = '10px';
        detailTooltip.style.zIndex = '1';
        detailTooltip.style.left = `${ pointData.x + 10}px`;
        detailTooltip.style.top = `${pointData.y + 10}px`;

        // Remove the previous tooltip if it exists
        if(this.detailedTooltip !== undefined){
            document.body.removeChild(this.detailedTooltip);
        }

        const params = pointData.point.data;
        const promptLines = splitText(params.prompt, 40).join('<br>');
        
        logSearchResultViewed(getCookie('prolificPid'), pointData.point.id);
        // Add content to the detailed tooltip
        detailTooltip.innerHTML = `
        <div style="display: flex; align-items: start;">
                <img src=/api/getImage?fname=${pointData.point.id} alt="Image Preview" style="max-width: 250px; margin-right: 10px;">
                <div style="font-size: 16px;">
                    <button class="close-tooltip" style="position: absolute; top: 5px; right: 5px; background: none; border: none; font-size: 18px; cursor: pointer;">X</button>
                    <p><strong>Prompt: </strong> ${promptLines}</p>
                    <p><strong>Location: </strong> ${params.location}</p>
                    <p><strong>Subject: </strong> ${params.subject}</p>
                    <p><strong>Lighting: </strong> ${params.lighting}</p>
                    <p><strong>Tone: </strong> ${params.tone} </p>
                    <p><strong>Mood: </strong> ${params.mood} </p>
                    <p><strong>Genre: </strong> ${params.genre} </p>
                    <button id="copy-prompt-bt" style="font-size: 16px;">Use Prompt</button>
                </div>
        </div>
        `;

        // Add close button functionality
        detailTooltip.querySelector('.close-tooltip').addEventListener('click', () => {
            document.body.removeChild(detailTooltip);
            this.detailedTooltip = undefined;
        });

        detailTooltip.querySelector('#copy-prompt-bt').addEventListener('click', () => {
            const prompt = params.prompt;
            this.setPrompt(prompt);
        });

        document.body.appendChild(detailTooltip);
        this.detailedTooltip = detailTooltip;
    }

    setPrompt(prompt){
        document.getElementById("prompt-text-area").value = prompt;
        document.getElementById("gen-image-bt").disabled = false;
    }

    onMouseWheelTurned(event){
        event.preventDefault();
    
        const wheelDelta = -event.deltaY;
        
        const zoomFactor = wheelDelta > 0 ? (1.0+ZOOM_SPEED_FACTOR) : (1.0-ZOOM_SPEED_FACTOR);
        const prevScale = this.scale;
        this.scale *= zoomFactor;
        this.clampScale();

        const mousePosition = getMousePositionInCanvas(this.canvas, event);
    
        const scaleChange = this.scale / prevScale;
        this.translation.x = mousePosition.x - (mousePosition.x - this.translation.x) * (scaleChange);
        this.translation.y = mousePosition.y - (mousePosition.y - this.translation.y) * (scaleChange);
    
        this.fetchAndDraw();

        if(this.lastScrollLogTimestampMs === undefined){
            this.lastScrollLogTimestampMs = Date.now();
        }

        if(Date.now() - this.lastScrollLogTimestampMs > 2000){
            const positionPayload = {
                x: this.translation.x,
                y: this.translation.y
            }
            logMapViewChanged(getCookie('prolificPid'), positionPayload, this.scale);
            this.lastScrollLogTimestampMs = undefined;
        }
    }

    onMouseDown(event){
        const mousePosition = getMousePositionInCanvas(this.canvas, event);
        this.isDragging = true;
        this.dragStart = { x: mousePosition.x, y: mousePosition.y };
        this.dragTranslationStart = { x: this.translation.x, y: this.translation.y };
        this.dragStartPixels = { x: event.clientX, y: event.clientY };
        this.lastMousePosition = { x: event.clientX, y: event.clientY };

        if(this.closestPoint === undefined || this.closestPoint === null){
            return;
        }

        let distanceThreshold;
        if(this.closestPoint.point.img_level_1_shown === true || this.closestPoint.point.img_level_2_shown === true){
            distanceThreshold = MAX_RADIUS_FOR_POPUP * 4;
        }
        else{
            distanceThreshold = MAX_RADIUS_FOR_POPUP;
        }


        if(this.closestPoint.distance <= distanceThreshold){
            this.displayInfoWithPointData(this.closestPoint);
        }
        else{
            if(this.detailedTooltip !== undefined){
                document.body.removeChild(this.detailedTooltip);
                this.detailedTooltip = undefined;
            }
        }
    }
    
    onMouseUp(event){
        this.isDragging = false;
        this.fetchAndDraw();
        
        const positionPayload = {
            x: this.translation.x,
            y: this.translation.y
        }

        logMapViewChanged(getCookie('prolificPid'), positionPayload, this.scale);
    }

    onMouseMove(event){
        const mousePosition = getMousePositionInCanvas(this.canvas, event);
    
        if (this.isDragging) {
            // Close the detailed tooltip if it is open
            if(this.detailedTooltip !== undefined){
                document.body.removeChild(this.detailedTooltip);
                this.detailedTooltip = undefined;
            }
            const dx = mousePosition.x - this.dragStart.x;
            const dy = mousePosition.y - this.dragStart.y;
            this.translation.x = this.dragTranslationStart.x + dx;
            this.translation.y = this.dragTranslationStart.y + dy;
            
            const mouseX = event.clientX;
            const mouseY = event.clientY
            if(this.lastMousePosition === null){
                this.lastMousePosition = { x: mouseX, y: mouseY };
            }
            else{
                const dx = mouseX - this.lastMousePosition.x;
                const dy = mouseY - this.lastMousePosition.y;
                this.translationInPixels = { x: dx, y: dy };
                this.lastMousePosition = { x: mouseX, y: mouseY };
            }

            this.fetchAndDraw();
        }
        else{
            this.checkMouseHover(event.clientX, event.clientY);
        }
    }

    onCanvasResized() {
        this.fetchAndDraw();
    }

    setCanvas(canvas) {
        this.canvas = canvas;
    }

    onSearchBtClicked(querry, searchBy) {
        runSearch(querry, searchBy).then((data) => {
            this.home();
            this.searchResults = data;
            this.draw();
        }).catch((error) => {
            console.error(error);
        });
    }

    resetCanvasView(){
        this.home();
        this.draw();
        // Close the detailed tooltip if it is open
        if(this.detailedTooltip !== undefined){
            document.body.removeChild(this.detailedTooltip);
            this.detailedTooltip = undefined;
        }

        logMapViewReset(getCookie('prolificPid'));
    }

    hideSearchResults(){
        this.searchResults = undefined;
        this.draw();
    }
    toggleImagePreview(){
        this.displayImages = !(this.displayImages);
        this.draw();
    }
}
