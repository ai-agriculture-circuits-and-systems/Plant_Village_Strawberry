#!/usr/bin/env python3
"""
Convert strawberries dataset annotations to COCO JSON format.
Based on the standardized dataset structure specification.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image

def read_split_list(split_file: Path) -> List[str]:
    """Read image base names (without extension) from a split file."""
    if not split_file.exists():
        return []
    lines = [line.strip() for line in split_file.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]

def image_size(image_path: Path) -> Tuple[int, int]:
    """Return (width, height) for an image path using PIL."""
    with Image.open(image_path) as img:
        return img.width, img.height

def parse_csv_boxes(csv_path: Path) -> List[Dict]:
    """Parse a single CSV file and return bounding boxes."""
    if not csv_path.exists():
        return []
    
    boxes = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x = float(row.get('x', 0))
                y = float(row.get('y', 0))
                width = float(row.get('width', 0))
                height = float(row.get('height', 0))
                label = int(row.get('label', 1))
                
                if width > 0 and height > 0:
                    boxes.append({
                        'bbox': [x, y, width, height],
                        'area': width * height,
                        'category_id': label
                    })
            except (ValueError, KeyError):
                continue
    
    return boxes

def load_labelmap(labelmap_path: Path) -> Dict[int, str]:
    """Load labelmap and create ID to name mapping."""
    if not labelmap_path.exists():
        return {}
    
    with open(labelmap_path, 'r', encoding='utf-8') as f:
        labelmap = json.load(f)
    
    id_to_name = {}
    for item in labelmap:
        if item['object_name'] != 'background':
            id_to_name[item['label_id']] = item['object_name']
    
    return id_to_name

def collect_annotations_for_category(
    category_root: Path,
    split: str,
    category_name: str,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Collect COCO dictionaries for images, annotations, and categories."""
    labelmap_path = category_root / "labelmap.json"
    id_to_name = load_labelmap(labelmap_path)
    
    # 读取类别级别的划分文件
    sets_dir = category_root / "sets"
    split_file = sets_dir / f"{split}.txt"
    image_stems = set(read_split_list(split_file))
    
    images: List[Dict] = []
    anns: List[Dict] = []
    
    # 创建类别列表
    categories: List[Dict] = []
    for label_id, name in sorted(id_to_name.items()):
        categories.append({
            "id": label_id,
            "name": name,
            "supercategory": category_name[:-1] if category_name.endswith('s') else category_name
        })
    
    image_id_counter = 1
    ann_id_counter = 1
    
    # 遍历所有子类别
    for subcat_dir in category_root.iterdir():
        if not subcat_dir.is_dir() or subcat_dir.name in ['sets']:
            continue
        
        subcategory_name = subcat_dir.name
        images_dir = subcat_dir / "images"
        annotations_dir = subcat_dir / "csv"
        
        if not images_dir.exists():
            continue
        
        # 获取该子类别的图像
        subcat_images = {p.stem for p in images_dir.glob("*.jpg")}
        subcat_images.update({p.stem for p in images_dir.glob("*.JPG")})
        subcat_images.update({p.stem for p in images_dir.glob("*.png")})
        subcat_images.update({p.stem for p in images_dir.glob("*.PNG")})
        
        # 只处理在划分文件中的图像
        for stem in sorted(image_stems & subcat_images):
            img_path = None
            for ext in ['.jpg', '.JPG', '.png', '.PNG', '.bmp', '.BMP']:
                potential_path = images_dir / f"{stem}{ext}"
                if potential_path.exists():
                    img_path = potential_path
                    break
            
            if not img_path or not img_path.exists():
                continue
            
            width, height = image_size(img_path)
            images.append({
                "id": image_id_counter,
                "file_name": f"{category_name}/{subcategory_name}/images/{img_path.name}",
                "width": width,
                "height": height,
            })
            
            csv_path = annotations_dir / f"{stem}.csv"
            for box in parse_csv_boxes(csv_path):
                anns.append({
                    "id": ann_id_counter,
                    "image_id": image_id_counter,
                    "category_id": box['category_id'],
                    "bbox": box['bbox'],
                    "area": box['area'],
                    "iscrowd": 0,
                })
                ann_id_counter += 1
            
            image_id_counter += 1
    
    return images, anns, categories

def build_coco_dict(
    images: List[Dict],
    anns: List[Dict],
    categories: List[Dict],
    description: str,
    url: str,
    year: int,
) -> Dict:
    """Build a complete COCO dict from components."""
    return {
        "info": {
            "year": year,
            "version": "1.0.0",
            "description": description,
            "url": url,
        },
        "images": images,
        "annotations": anns,
        "categories": categories,
        "licenses": [],
    }

def main():
    parser = argparse.ArgumentParser(description="Convert strawberries annotations to COCO JSON")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Dataset root directory",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory for COCO JSON files (default: <root>/annotations)",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train", "val", "test"],
        choices=["train", "val", "test"],
        help="Dataset splits to generate (default: train val test)",
    )
    
    args = parser.parse_args()
    
    if args.out is None:
        args.out = args.root / "annotations"
    
    args.out.mkdir(parents=True, exist_ok=True)
    
    category_name = "strawberries"
    category_root = args.root / category_name
    
    if not category_root.exists():
        print(f"Error: Category directory {category_name} not found")
        sys.exit(1)
    
    for split in args.splits:
        images, anns, cat_list = collect_annotations_for_category(
            category_root, split, category_name
        )
        desc = f"PlantVillage {category_name} {split} split"
        url = "https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset"
        coco = build_coco_dict(images, anns, cat_list, desc, url, 2015)
        out_path = args.out / f"{category_name}_instances_{split}.json"
        out_path.write_text(json.dumps(coco, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Generated: {out_path} ({len(images)} images, {len(anns)} annotations)")

if __name__ == "__main__":
    main()
