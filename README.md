# Plant Village Strawberry

[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey)](#citation)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](#changelog)

Strawberry leaf disease classification dataset from Plant Village. Contains images of strawberry leaves labeled for disease classification (healthy, leaf scorch). This dataset follows the standardized layout specification.

- Project page: `https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset`
- Issue tracker: use this repo

## TL;DR
- Task: classification (2 classes: `healthy`, `leaf_scorch`)
- Modality: RGB
- Platform: handheld/field
- Real/Synthetic: real
- Images: see counts below
- Classes: 2
- Resolution: 256×256 pixels
- Annotations: COCO JSON (object detection with bounding boxes)
- License: CC BY 4.0 (see License)
- Citation: see below

## Table of contents
- [Download](#download)
- [Dataset structure](#dataset-structure)
- [Sample images](#sample-images)
- [Annotation schema](#annotation-schema)
- [Stats and splits](#stats-and-splits)
- [Quick start](#quick-start)
- [Evaluation and baselines](#evaluation-and-baselines)
- [Datasheet (data card)](#datasheet-data-card)
- [Known issues and caveats](#known-issues-and-caveats)
- [License](#license)
- [Citation](#citation)
- [Changelog](#changelog)
- [Contact](#contact)

## Download
- Original dataset: `https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset`
- This repo hosts structure and conversion scripts only; place the downloaded folders under this directory.
- Local license file: see `LICENSE` (Creative Commons Attribution 4.0).

## Dataset structure

This dataset follows the standardized dataset structure specification with subcategory organization:

```
Plant_Village_Strawberry/
├── strawberries/
│   ├── healthy/              # Healthy images
│   │   ├── csv/              # CSV annotations per image
│   │   ├── json/             # Original JSON annotations
│   │   ├── images/           # Healthy images
│   │   └── sets/             # Dataset splits for this subcategory (optional)
│   │       ├── train.txt
│   │       ├── val.txt
│   │       ├── test.txt
│   │       └── all.txt
│   ├── leaf_scorch/                 # Leaf Scorch images
│   │   ├── csv/
│   │   ├── json/
│   │   ├── images/
│   │   └── sets/
│   ├── labelmap.json        # Label mapping
│   └── sets/                 # Combined dataset splits
│       ├── train.txt
│       ├── val.txt
│       ├── test.txt
│       └── all.txt
├── annotations/              # COCO format JSON (generated)
│   ├── strawberries_instances_train.json
│   ├── strawberries_instances_val.json
│   └── strawberries_instances_test.json
├── scripts/
│   └── convert_to_coco.py   # COCO conversion script
├── LICENSE
├── README.md
└── requirements.txt
```

- Splits: `strawberries/sets/*.txt` list image basenames (no extension). If missing, all images are used.

## Sample images

Below are example images for each category in this dataset. Paths are relative to this README location.

<table>
  <tr>
    <th>Category</th>
    <th>Sample</th>
  </tr>
  <tr>
    <td><strong>Healthy</strong></td>
    <td>
      <img src="strawberries/healthy/images/sample.jpg" alt="healthy" width="260"/>
      <div align="center"><code>strawberries/healthy/images/sample.jpg</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>Leaf Scorch</strong></td>
    <td>
      <img src="strawberries/leaf_scorch/images/sample.jpg" alt="leaf_scorch" width="260"/>
      <div align="center"><code>strawberries/leaf_scorch/images/sample.jpg</code></div>
    </td>
  </tr>
</table>

## Annotation schema

### CSV Format

Each image has a corresponding CSV file in `{category}/csv/` with the following format:

```csv
#item,x,y,width,height,label
0,0,0,256,256,1
```

- `x, y`: top-left corner coordinates (pixels)
- `width, height`: bounding box dimensions (pixels)
- `label`: category ID (from labelmap.json)

### COCO Format

The COCO JSON files are generated from CSV annotations and follow the standard COCO format:

```json
{
  "info": {...},
  "images": [
    {
      "id": 1,
      "file_name": "{category}/{subcategory}/images/image.jpg",
      "width": 256,
      "height": 256
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [0, 0, 256, 256],
      "area": 65536,
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "healthy",
      "supercategory": "plant"
    }
  ]
}
```

### Label Maps

Label mappings are defined in `{category}/labelmap.json`:

```json
[
  {
    "object_id": 0,
    "label_id": 0,
    "keyboard_shortcut": "0",
    "object_name": "background"
  },
  {
    "object_id": 1,
    "label_id": 1,
    "keyboard_shortcut": "1",
    "object_name": "healthy"
  }
]
```

## Stats and splits

Dataset statistics and split information:

- **Total images**: See subcategory counts below
- **Splits**: train/val/test (default: 60%/20%/20%)
- **Splits provided via** `{category_name}/sets/*.txt`. You may define your own splits by editing those files.

## Quick start

### Convert to COCO format

```bash
python scripts/convert_to_coco.py --root . --out annotations --splits train val test
```

### Load with COCO API

```python
from pycocotools.coco import COCO
import matplotlib.pyplot as plt

# Load annotations
coco = COCO('annotations/{category_name}_instances_train.json')

# Get image IDs
img_ids = coco.getImgIds()
print(f"Total images: {{len(img_ids)}}")

# Get category IDs
cat_ids = coco.getCatIds()
print(f"Categories: {{[coco.loadCats(cat_id)[0]['name'] for cat_id in cat_ids]}}")
```

### Dependencies

- **Required**: Pillow (for image processing)
- **Optional**: pycocotools (for COCO API)

## Evaluation and baselines

- **Metrics**: Classification accuracy, mAP (if used for detection)
- **Baselines**: See original Plant Village paper

## Datasheet (data card)

### Motivation

This dataset was created to enable automated plant disease detection and classification using computer vision techniques.

### Composition

- **Image types**: RGB images of plant leaves
- **Classes**: {len(subcategories)} classes ({subcat_list})
- **Resolution**: 256×256 pixels
- **Format**: JPG/PNG

### Collection process

Images were collected from various sources and manually labeled by experts.

### Preprocessing

- Images resized to 256×256 pixels
- Annotations converted to bounding box format
- Dataset split into train/val/test sets

### Distribution

Dataset is available under CC BY 4.0 license.

### Maintenance

This standardized version is maintained by the dataset organization team.

## Known issues and caveats

- Images are preprocessed to 256×256 pixels
- Some images may have multiple bounding boxes (for detection task)
- Coordinate system: top-left origin (0,0), pixel units
- File naming: image basenames (without extension) are used in split files

## License

This dataset is released under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

Check the original dataset terms and cite appropriately.

See `LICENSE` file for full license text.

## Citation

If you use this dataset, please cite:

```bibtex
@article{{mohanty2016using,
  title={{Using Deep Learning for Image-Based Plant Disease Detection}},
  author={{Mohanty, Sharada P. and Hughes, David P. and Salathé, Marcel}},
  journal={{Frontiers in Plant Science}},
  volume={{7}},
  pages={{1419}},
  year={{2016}},
  publisher={{Frontiers Media SA}}
}}
```

## Changelog

- **V1.0.0**: initial standardized structure and COCO conversion utility

## Contact

- **Maintainers**: Dataset organization team
- **Original authors**: Plant Village team
- **Source**: `{url}`
