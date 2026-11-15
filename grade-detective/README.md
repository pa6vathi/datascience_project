# The Grade Detective

A browser game that teaches real machine learning through a detective story. Five chapters take you from messy data to a model defended in court. No install, no build step, no network needed.

## Play
Open `index.html` in any modern browser (double-click works).

## Chapters and what they teach
1. **The Crime Scene** – outliers (absences) and whether to cap, drop or keep them; why dropping grade-0 students from training is dangerous.
2. **The Line-up** – correlation as evidence; accuse the three features that move the grade most.
3. **Ghost Students** – testing hypotheses by comparing groups; discover the "zero absences" feature.
4. **The Profiler** – train a baseline, ridge regression or k-nearest neighbours. Compare cross-validation, training and validation error to spot under- and overfitting. Energy limits how many experiments you can run.
5. **The Courtroom** – one shot on a sealed test set, reported as RMSE, MAE and R² against the baseline.

Scoring: up to 530 points. Hearts count too; three wrong calls and the case is lost. Best score is saved in your browser.

## Project structure
```
index.html        page shell and title screen
css/styles.css    noir case-file theme
js/data.js        packed dataset (395 students) and feature labels
js/ml.js          seeded split, metrics, ridge, kNN, cross-validation
js/charts.js      canvas scatter plots
js/audio.js       WebAudio sound effects (mute is remembered)
js/game.js        state, chapters, scoring and rules
js/ui.js          title screen, how-to panel, menu button
```
Scripts are plain (non-module) files, so the game also runs from `file://`.

## Data
395 secondary-school maths students (the UCI "Student Performance" dataset layout). Train / validation / test split is 237 / 79 / 79 with a fixed seed, so results are reproducible.

## Notes
Educational use only. A model like this must never be used to judge an individual student.
