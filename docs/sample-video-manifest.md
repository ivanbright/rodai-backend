# Sample video manifest

## Pexels road traffic clip

- Source page: https://www.pexels.com/video/a-car-is-driving-down-a-road-with-a-lot-of-cars-20669311/
- Creator: Amanat Ali Warraich
- Retrieval date: 2026-11-14
- Listed source properties: 7 seconds; 1080×1920; 60 FPS; cars and motorcycles on an urban road
- License: Pexels Free Stock Photo & Video License. The Pexels license page says videos may be downloaded, used, and modified for free and attribution is not required. It prohibits implying endorsement and places restrictions on presenting identifiable people offensively or in a bad light.
- Intended use in RodAI: private local pipeline smoke test only. It is not Rwanda/Kigali footage, a representative acceptance sample, or permission to share identifiable people/plates externally.
- Camera type/location: fixed roadside view; exact location is not stated by the source.
- Inspection: reviewed frames at 0.25s, 3.0s and 6.5s. The clip contains cars, a bus/truck, motorcycles/bicycles and pedestrians. Plates are visible at small size; no close-up identifiable faces were visible in those sampled frames. Do not share this original externally without a privacy review and plate blurring.
- SHA-256 of retrieved source: `DA268A8C7F9320E0EDF0E78FAF75416461668B9C39D34A9F4F7402B7C7A22041`.
- Storage: `.temp/samples/cars-motorcycles-pexels-20669311.mp4` (ignored by Git); do not commit the source. A 14-frame/2-FPS local smoke-test derivative is `.temp/samples/cars-motorcycles-pexels-20669311-demo.avi`. Session upload retention remains configurable at 7 days.
- Detector smoke check: the pinned DETR checkpoint ran on three source frames and returned high-confidence truck/car detections at 0.25s, multiple person/bicycle/car/truck detections at 3.0s, and motorcycle/truck/car/person detections at 6.5s. This is a pipeline smoke test only, not an accuracy benchmark.

Pexels source and license: [clip page](https://www.pexels.com/video/a-car-is-driving-down-a-road-with-a-lot-of-cars-20669311/), [Pexels license](https://www.pexels.com/license/).
