import re
import os

class Reader:
    def __init__(self, paths_file="./resources/Paths_D.txt"):
        self.paths_file = paths_file
        self.scale = None
        self.entities = []
        self.load_data()
    
    def load_data(self):
        print(f"DEBUG: Carregando arquivo: {self.paths_file}")
        
        if not os.path.exists(self.paths_file):
            print(f"ERRO: Arquivo {self.paths_file} não encontrado!")
            return
        
        with open(self.paths_file, 'r') as file:
            lines = file.readlines()
        
        print(f"DEBUG: Arquivo carregado com {len(lines)} linhas")
        
        scale_match = re.search(r'\[(\d+)\]', lines[0])
        if scale_match:
            self.scale = int(scale_match.group(1))
            print(f"DEBUG: Escala encontrada: {self.scale}")
        else:
            print("ERRO: Escala não encontrada na primeira linha!")
            return
        
        entity_pattern = re.compile(r'(\d+)\s+(.+)')
        point_pattern = re.compile(r'\((\d+),(\d+),(\d+)\)')
        
        for i, line in enumerate(lines[1:], 1): 
            line = line.strip()
            if not line:
                continue
                
            match = entity_pattern.match(line)
            if not match:
                continue
            
            num_points = int(match.group(1))
            coordinates_str = match.group(2)
            
            points = point_pattern.findall(coordinates_str)
            
            if len(points) != num_points:
                print(f"DEBUG: Entidade {len(self.entities)}: esperado {num_points} pontos, encontrado {len(points)}")
            
            trajectory = []
            for x, y, f in points:
                norm_x = int(x) / self.scale
                norm_y = int(y) / self.scale
                trajectory.append([norm_x, norm_y])
            
            self.entities.append(trajectory)
            
            print(f"DEBUG: Entidade {len(self.entities)-1}: {len(trajectory)} pontos")
            if trajectory:
                print(f"DEBUG: Primeiro ponto: {trajectory[0]}")
                print(f"DEBUG: Último ponto: {trajectory[-1]}")
        
        print(f"DEBUG: Total de {len(self.entities)} entidades carregadas")
    
    def get_entity_trajectory(self, entity_index):
        print(f"DEBUG: Solicitando trajetória da entidade {entity_index}")
        
        if entity_index < len(self.entities):
            trajectory = self.entities[entity_index]
            print(f"DEBUG: Retornando {len(trajectory)} pontos para entidade {entity_index}")
            return trajectory
        else:
            print(f"DEBUG: Entidade {entity_index} não existe (total: {len(self.entities)})")
            return []
    
    def get_all_entities_count(self):
        return len(self.entities)
    
    def print_entities_summary(self):
        print(f"\n=== RESUMO DAS ENTIDADES ===")
        print(f"Arquivo: {self.paths_file}")
        print(f"Escala: {self.scale}")
        print(f"Total de entidades: {len(self.entities)}")
        
        for i, entity in enumerate(self.entities):
            print(f"Entidade {i}: {len(entity)} pontos")
            if entity:
                print(f"  Primeiro: {entity[0]}")
                print(f"  Último: {entity[-1]}")