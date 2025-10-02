# Importações dos modelos organizados

# Efeitos básicos
from .efeitos import PulseEffect, GlowEffect

# Estrelas
from .estrela import Star, create_star

# Planetas
from .planetas import Planet, create_planets, COLORS, PLANET_CONFIGS, PLANET_DRAWERS

# Background
from .background import BackgroundStars, Nebula, CosmicDust

# Cometas e meteoros
from .cometa import Comet, Meteor, CometSystem, MeteorShower, create_comet

# Sistema solar
from .solarsystem import FireSun, AsteroidBelt, MultipleAsteroidBelts

# Função principal para criar entidades para animação
def create_entities_for_animation(total_entities):
    entities = []
    
    solar_system_config = [
        ("Sun", 0.0, 0.0, 1.2), ("Mercury", 2.0, 0.0, 0.3), ("Venus", 3.0, 0.0, 0.4),
        ("Earth", 4.5, 0.0, 0.5), ("Mars", 6.0, 0.0, 0.4), ("Jupiter", 9.0, 0.0, 1.0),
        ("Saturn", 12.0, 0.0, 0.8), ("Uranus", 15.0, 0.0, 0.6), ("Neptune", 18.0, 0.0, 0.6)
    ]
    
    for i in range(1, total_entities):
        if i - 1 < len(solar_system_config):  # i-1 porque pulamos o player
            name, x, y, size = solar_system_config[i - 1]
            planet = Planet(name, x, y, size, COLORS.get(name.lower(), (1,1,1)))
            entities.append(planet)
        else:
            size = 0.12  
            star = Star(0, 0, 0, 0, size)
            entities.append(star)
    
    return entities

__all__ = [
    'PulseEffect', 'GlowEffect',
    'Star', 'create_star',
    'Planet', 'create_planets', 'COLORS', 'PLANET_CONFIGS', 'PLANET_DRAWERS',
    'BackgroundStars', 'Nebula', 'CosmicDust',
    'Comet', 'Meteor', 'CometSystem', 'MeteorShower', 'create_comet',
    'FireSun', 'AsteroidBelt', 'MultipleAsteroidBelts',
    'create_entities_for_animation'
]