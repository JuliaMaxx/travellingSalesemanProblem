import { config } from "./config.js";
import { 
    canvas, playBtn, pauseBtn, stopBtn, manual, averageCheck, averageRange, populationRange, greedyRange, selectionSelect, tournamentSizeRange, eliteCheck, eliteSizeRange, crossoverSelect, mutationSelect, mutationRange, epochRange, pointRange, algorithmSelect, paths, elapsedTime, bestDistance, worseDistance, averageDistance, epoch, distance } from "./dom.js";
import { circleGroup, lineGroup } from "./canvas.js";
import { socket } from "./socket.js";
import { stopTimer } from "./timer.js";

export function toggleCursor(isSelecting){
    canvas.style.cursor = isSelecting? "pointer": "default" ;
}

export function removeAllCirles(){
    circleGroup.selectAll('circle').remove();
}

export function removeAllPaths(){
    lineGroup.selectAll('path').remove();
}

export function toggleElementDisplay(element, show){
    element.style.display = show ? "block" : "none";
}

export function toggleButtonState(button, isDisabled){
    button.disabled = isDisabled;
}

export function toggleControls(play, pause, stop){
    toggleButtonState(stopBtn, stop);
    toggleButtonState(pauseBtn, pause);
    toggleButtonState(playBtn, play);
}

export function togglePlayButtonText(isPaused){
    playBtn.innerText = isPaused? "Resume": "Play";
}

export function toggleManualButtonText(isSelecting){
    manual.innerText = isSelecting? "Manual": "Finish";
}

export function getAlgorithmParams(selectedAlgorithm) {
    if (selectedAlgorithm === "random") {
        return { averageNum: averageCheck.checked ? parseInt(averageRange.value) : 1 };
    } 
    
    if (selectedAlgorithm === "genetic") {
        return {
            populationSize: parseInt(populationRange.value),
            greedyRatio: parseInt(greedyRange.value) / 100,
            selection: selectionSelect.value === "tournament" ? 1 : 2,
            tournamentSize: parseInt(tournamentSizeRange.value),
            elite: eliteCheck.checked,
            eliteSize: parseInt(eliteSizeRange.value),
            crossover : crossoverSelect.value == "ordered"? 1:
                        crossoverSelect.value == "partially matched"? 2: 3,
            mutation: mutationSelect.value === "swap" ? 1 : 2,
            mutationProbability: parseInt(mutationRange.value) / 100,
            epochNum: parseInt(epochRange.value),
        };
    }
}

export function factorial(n) {
    if (n <= 1) return 1;
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

export function getRandomHSL() {
    let h;
    // Loop to generate a hue outside the green range (80° - 160°)
    do {
      h = Math.floor(Math.random() * 360);
    } while (h >= 70 && h <= 170);
  
    const s = Math.floor(Math.random() * 31) + 70;
    const l = Math.floor(Math.random() * 20) + 2;
    return `hsl(${h}, ${s}%, ${l}%)`;
}

export function calculatePossiblePaths(numPoints) {
    // Calculate factorial (numPoints - 1)!
    let fact = factorial(numPoints - 1);

    // Find the exponent of 10
    let exponent = Math.floor(Math.log10(fact));
    
    // Normalize the number in the form of n * 10^m
    let mantissa = fact / Math.pow(10, exponent);
    
    // Round mantissa to 3 decimal places for simplicity
    mantissa = mantissa.toFixed(3);
    if (isNaN(mantissa)){
        return "Possibilities: infinity"
    }
    return `Possibilities: ${mantissa} * 10^${exponent}`;
}

export function resetToInitialState(){
    socket.emit('get_points', { numPoints: config.numPoints, manual: false });
    socket.emit('stop_algorithm', {});
    stopTimer(config.intervalId);
    removeAllPaths();
    toggleCursor(false);
    [pointRange, manual, algorithmSelect].forEach(el => toggleButtonState(el, false));
    toggleControls(true, true, true);
    resetAllText();
    config.isPaused = false;
    paths.forEach(path => {
        path.style.fill = getRandomHSL();
    });
}

export function resetAllText(){
    elapsedTime.textContent = "Elapsed: 0";
    bestDistance.textContent = "Best: 0";
    worseDistance.textContent = "Worse: 0";
    averageDistance.textContent = "Average: 0";
    epoch.textContent = "Epoch: 0";
    distance.textContent = "Distance: 0";
    playBtn.innerText = "Play";
    toggleManualButtonText(true);
}