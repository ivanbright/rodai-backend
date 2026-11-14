# RodAI detector provenance

## First prototype detector

- Model: `facebook/detr-resnet-50`
- Framework: PyTorch with Hugging Face Transformers
- Model revision pinned in configuration: `70120ba84d68ca1211e007c4fb61d0cd5424be54`
- Inference device: CPU unless a later hardware review explicitly enables an available accelerator
- Selected output classes: person, bicycle, motorcycle, car, bus and truck
- Confidence cutoff: configurable, default 0.35
- Model repository license metadata: Apache-2.0
- Upstream DETR implementation license: Apache-2.0
- Training data listed by model card: COCO 2017 object detection

The model and weight source were reviewed before selection. The model card and pinned repository identify the model as Apache-2.0; the weights are fetched only when the detector is first used and are cached under `RODAI_MODEL_DIR`. No model checkpoint is committed to Git. RodAI stores the configured model ID and exact revision so a run can be associated with its model source.

## Data provenance and limits

COCO terms distinguish the consortium's annotations from the third-party images. The annotations are CC BY 4.0, while use of images is subject to Flickr's terms. The model card says the checkpoint was trained on COCO 2017. This records provenance; it is not a legal opinion on every downstream use of trained weights. Keep the source attribution with builds and review intended commercial distribution with qualified counsel before release.

This general-purpose COCO detector is a demonstration baseline. It is not trained or evaluated for Rwanda/Kigali traffic, collision prediction, safety decisions, or enforcement. Performance and false detections must be measured on owner-provided footage with documented rights before making product claims. Model outputs can be wrong.

## References

- Upstream implementation and license: [facebookresearch/detr](https://github.com/facebookresearch/detr)
- Model card and listed model license/training data: [facebook/detr-resnet-50](https://huggingface.co/facebook/detr-resnet-50)
- Pinned checkpoint source: [revision 70120ba84d68ca1211e007c4fb61d0cd5424be54](https://huggingface.co/facebook/detr-resnet-50/tree/70120ba84d68ca1211e007c4fb61d0cd5424be54)
- COCO terms: [cocodataset.org/terms](https://cocodataset.org/dataset/termsofuse.htm)
