from Reader import Reader

class AnimationSystem:
    def __init__(self, paths_file=None):
        if paths_file:
            self.reader = Reader(paths_file)
        else:
            self.reader = Reader()  
            
        # Dicionários para gerenciar múltiplas animações
        self.animated_objects = {}  # entity_id -> objeto
        self.trajectories = {}      # entity_id -> trajetória
        self.trajectory_indices = {} # entity_id -> índice atual
        self.animation_speeds = {}   # entity_id -> velocidade
        self.original_positions = {} # entity_id -> (x, y) original
        
        self.enabled = True
        self.total_entities = self.reader.get_all_entities_count()
        
        # Velocidade padrão para todas as entidades
        self.default_speed = 30.0
        
        print(f"DEBUG AnimationSystem: {self.total_entities} entidades disponíveis")
    
    def add_animated_object(self, entity_id, obj, animation_speed=None):
        """
        Adiciona um objeto para ser animado por uma entidade específica
        """
        if entity_id >= self.total_entities:
            print(f"ERRO: Entidade {entity_id} não existe (máximo: {self.total_entities-1})")
            return False
            
        trajectory = self.reader.get_entity_trajectory(entity_id)
        
        if not trajectory:
            print(f"AVISO: Entidade {entity_id} não tem trajetória válida")
            return False
        
        # Usar velocidade padrão se não especificada
        if animation_speed is None:
            animation_speed = self.default_speed
        
        # Salvar posição original
        self.original_positions[entity_id] = (obj.x, obj.y)
        
        # Registrar objeto para animação
        self.animated_objects[entity_id] = obj
        self.trajectories[entity_id] = trajectory
        self.trajectory_indices[entity_id] = 0.0
        self.animation_speeds[entity_id] = animation_speed
        
        print(f"DEBUG: Objeto adicionado para entidade {entity_id} com {len(trajectory)} pontos (velocidade: {animation_speed})")
        return True
    
    def setup_planets_animation(self, planets):
        """
        Configura animação para todos os planetas disponíveis - MESMA VELOCIDADE
        """
        print("DEBUG: Configurando animação dos planetas...")
        
        animated_count = 0
        for i, planet in enumerate(planets):
            if i < self.total_entities:
                # MESMA velocidade para todos os planetas
                success = self.add_animated_object(i, planet, self.default_speed)
                
                if success:
                    animated_count += 1
                    print(f"DEBUG: Planeta {i} configurado (velocidade: {self.default_speed})")
        
        print(f"DEBUG: {animated_count} planetas configurados para animação")
        return animated_count
    
    def setup_comets_animation(self, comets, start_entity_id):
        """
        Configura animação para cometas usando entidades restantes - MESMA VELOCIDADE
        """
        print(f"DEBUG: Configurando animação dos cometas a partir da entidade {start_entity_id}...")
        
        animated_count = 0
        for i, comet in enumerate(comets):
            entity_id = start_entity_id + i
            
            if entity_id < self.total_entities:
                # MESMA velocidade para todos os cometas
                success = self.add_animated_object(entity_id, comet, self.default_speed)
                
                if success:
                    animated_count += 1
                    print(f"DEBUG: Cometa {i} configurado para entidade {entity_id} (velocidade: {self.default_speed})")
        
        print(f"DEBUG: {animated_count} cometas configurados para animação")
        return animated_count
    
    def update(self, delta_time):
        """
        Atualiza todas as animações ativas
        """
        if not self.enabled:
            return
        
        for entity_id in list(self.animated_objects.keys()):
            self._update_single_animation(entity_id, delta_time)
    
    def _update_single_animation(self, entity_id, delta_time):
        """
        Atualiza a animação de uma entidade específica
        """
        if entity_id not in self.animated_objects:
            return
        
        obj = self.animated_objects[entity_id]
        trajectory = self.trajectories[entity_id]
        animation_speed = self.animation_speeds[entity_id]
        
        # Avançar na trajetória
        self.trajectory_indices[entity_id] += animation_speed * delta_time
        
        # Loop da trajetória
        if self.trajectory_indices[entity_id] >= len(trajectory):
            self.trajectory_indices[entity_id] = 0.0
        
        # Interpolação entre pontos
        current_index = int(self.trajectory_indices[entity_id])
        next_index = (current_index + 1) % len(trajectory)
        interpolation_factor = self.trajectory_indices[entity_id] - current_index
        
        current_point = trajectory[current_index]
        next_point = trajectory[next_index]
        
        # Atualizar posição do objeto
        obj.x = current_point[0] + (next_point[0] - current_point[0]) * interpolation_factor
        obj.y = current_point[1] + (next_point[1] - current_point[1]) * interpolation_factor
    
    def set_enabled(self, enabled):
        """
        Liga/desliga todas as animações
        """
        self.enabled = enabled
        
        if not enabled:
            # Restaurar todas as posições originais
            for entity_id, obj in self.animated_objects.items():
                if entity_id in self.original_positions:
                    orig_x, orig_y = self.original_positions[entity_id]
                    obj.x = orig_x
                    obj.y = orig_y
        
        print(f"DEBUG: Todas as animações {'ATIVADAS' if enabled else 'DESATIVADAS'}")
    
    def reset_all(self):
        """
        Reseta todas as animações
        """
        for entity_id in self.trajectory_indices:
            self.trajectory_indices[entity_id] = 0.0
        
        if not self.enabled:
            # Se desabilitado, restaurar posições originais
            for entity_id, obj in self.animated_objects.items():
                if entity_id in self.original_positions:
                    orig_x, orig_y = self.original_positions[entity_id]
                    obj.x = orig_x
                    obj.y = orig_y
        
        print("DEBUG: Todas as animações resetadas")
    
    def set_animation_speed(self, entity_id, speed):
        """
        Define a velocidade de uma animação específica
        """
        if entity_id in self.animation_speeds:
            self.animation_speeds[entity_id] = speed
            print(f"DEBUG: Velocidade da entidade {entity_id} alterada para {speed}")
    
    def set_all_speeds(self, new_speed):
        """
        Define a MESMA velocidade para todas as animações
        """
        self.default_speed = new_speed
        for entity_id in self.animation_speeds:
            self.animation_speeds[entity_id] = new_speed
        
        print(f"DEBUG: Todas as velocidades alteradas para {new_speed}")
    
    def get_animated_objects_count(self):
        """
        Retorna o número de objetos sendo animados
        """
        return len(self.animated_objects)
    
    def print_status(self):
        """
        Imprime o status de todas as animações
        """
        print(f"\n=== STATUS DO SISTEMA DE ANIMAÇÃO ===")
        print(f"Ativo: {self.enabled}")
        print(f"Velocidade padrão: {self.default_speed}")
        print(f"Entidades disponíveis: {self.total_entities}")
        print(f"Objetos animados: {len(self.animated_objects)}")
        
        # Mostrar resumo das entidades do Reader
        print("\n--- Resumo das Entidades ---")
        self.reader.print_entities_summary()
        
        # Mostrar status de cada objeto animado
        print("\n--- Objetos Animados ---")
        for entity_id, obj in self.animated_objects.items():
            trajectory = self.trajectories[entity_id]
            current_index = int(self.trajectory_indices[entity_id])
            orig_x, orig_y = self.original_positions[entity_id]
            
            print(f"Entidade {entity_id}:")
            print(f"  Posição atual: ({obj.x:.2f}, {obj.y:.2f})")
            print(f"  Posição original: ({orig_x:.2f}, {orig_y:.2f})")
            print(f"  Pontos na trajetória: {len(trajectory)}")
            print(f"  Índice atual: {current_index}")
            print(f"  Velocidade: {self.animation_speeds[entity_id]}")
        
        print("=====================================\n")

    # Métodos de compatibilidade com a versão anterior (para o sol)
    def set_sun(self, sun_object):
        """Método de compatibilidade - configura o sol como entidade 0"""
        return self.add_animated_object(0, sun_object, self.default_speed)
    
    def set_sun_speed(self, speed):
        """Método de compatibilidade - altera velocidade da entidade 0"""
        self.set_animation_speed(0, speed)
    
    @property
    def sun(self):
        """Propriedade de compatibilidade"""
        return self.animated_objects.get(0, None)