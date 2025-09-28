import re
from typing import List, Tuple

class Coordinate:
    def __init__(self, x: int, y: int, f: int):
        self.x = x
        self.y = y
        self.f = f

class Entity:
    def __init__(self, frames_count: int, coordinates: List[Coordinate]):
        self.frames_count = frames_count
        self.coordinates = coordinates

class PathsData:
    def __init__(self, scale: int, entities: List[Entity]):
        self.scale = scale
        self.entities = entities

PAT_SCALE  = re.compile(r"\[\s*(\d+)\s*\]")   
PAT_HEADER = re.compile(r"^\s*(\d+)\s*")                  
PAT_TRIPLE = re.compile(r"\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)") 

def parse_paths_file(path: str) -> PathsData:
    entities: List[Entity] = []
    scale: int | None = None

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for ln in lines:
        m = PAT_SCALE.search(ln)
        if m:
            scale = int(m.group(1))
            break
    if scale is None:
        raise ValueError("Escala não encontrada no arquivo (formato [XXX]).")

    for idx, ln in enumerate(lines, start=1):
        if "(" not in ln:  
            continue

        h = PAT_HEADER.match(ln)
        if not h:
            continue

        frames_count = int(h.group(1))
        triples = PAT_TRIPLE.findall(ln)
        if not triples:
            continue

        pts = [Coordinate(int(x), int(y), int(fr)) for (x, y, fr) in triples]
        if len(pts) != frames_count:
            print(f"linha {idx}: frames declarados={frames_count}, lidos={len(pts)}.")

        entities.append(Entity(frames_count=frames_count, coordinates=pts))

    return PathsData(scale=scale, entities=entities)

def entity_bbox(coordinates: List[Coordinate]) -> Tuple[int, int, int, int]:
    xs = [p.x for p in coordinates]
    ys = [p.y for p in coordinates]
    return min(xs), min(ys), max(xs), max(ys)