import re
from typing import List, Tuple

class Point:
    def __init__(self, x: int, y: int, f: int):
        self.x = x
        self.y = y
        self.f = f

class Entity:
    def __init__(self, frames_count: int, points: List[Point]):
        self.frames_count = frames_count
        self.points = points

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

    # 1) escala (obrigatória)
    for ln in lines:
        m = PAT_SCALE.search(ln)
        if m:
            scale = int(m.group(1))
            break
    if scale is None:
        raise ValueError("Escala não encontrada no arquivo (formato [XXX]).")

    # 2) entidades linha a linha
    for idx, ln in enumerate(lines, start=1):
        if "(" not in ln:   # ignora linhas sem coordenadas
            continue

        h = PAT_HEADER.match(ln)
        if not h:
            continue

        frames_count = int(h.group(1))
        triples = PAT_TRIPLE.findall(ln)
        if not triples:
            continue

        pts = [Point(int(x), int(y), int(fr)) for (x, y, fr) in triples]
        if len(pts) != frames_count:
            print(f"linha {idx}: frames declarados={frames_count}, lidos={len(pts)}.")

        entities.append(Entity(frames_count=frames_count, points=pts))

    return PathsData(scale=scale, entities=entities)

# ---------- Utilidades ----------
def entity_bbox(points: List[Point]) -> Tuple[int, int, int, int]:
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return min(xs), min(ys), max(xs), max(ys)

# ---------- Exemplo ----------
if __name__ == "__main__":
    path = "./resources/Paths_D.txt"
    data = parse_paths_file(path)

    print(f"Escala encontrada: {data.scale}")
    print(f"Total de entidades: {len(data.entities)}\n")

    for i, ent in enumerate(data.entities[:7], start=1):
        print(f"Entidade {i}: frames_count={ent.frames_count}, pontos_lidos={len(ent.points)}")
        if ent.points:
            xmin, ymin, xmax, ymax = entity_bbox(ent.points)
            print(f"  BBox img: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}")
        print()
