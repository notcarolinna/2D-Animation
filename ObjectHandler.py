class ObjectHandler:

    def get_position(obj):
        return (obj.pos.x, obj.pos.y) if hasattr(obj, 'pos') else (obj.x, obj.y)
    
    def set_position(obj, x, y):
        if hasattr(obj, 'set_position'):
            obj.set_position(x, y)
        elif hasattr(obj, 'pos'):
            obj.pos.x, obj.pos.y = x, y
        else:
            obj.x, obj.y = x, y
    
    def get_radius(obj):
        if hasattr(obj, 'size'):
            return obj.size * 3.0
        if hasattr(obj, 'radius'):
            return obj.radius * 1.1
        if hasattr(obj, 'w'):
            return max(obj.w, obj.h) / 2 * 1.1
        return 0.5

    def get_mass(obj):
        return 2.0
    
    def get_pos(obj):
        return ObjectHandler.get_position(obj)
    
    def set_pos(obj, x, y):
        ObjectHandler.set_position(obj, x, y)