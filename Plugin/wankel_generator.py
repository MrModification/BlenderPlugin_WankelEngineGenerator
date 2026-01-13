import bpy
import math
from bpy.props import IntProperty, FloatProperty, BoolProperty

bl_info = {
    "name": "Wankel Engine Generator",
    "author": "MrModification",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Add > Mesh > Wankel Engine",
    "description": "Generates a Simple Wankel Engine with some adjustable properties, Not engineer grade",
    "warning": "",
    "doc_url": "https://github.com/MrModification/BlenderPlugin_WankelEngineGenerator/blob/main/README.md",
    "tracker_url": "https://github.com/MrModification/BlenderPlugin_WankelEngineGenerator/issues",
    "category": "Add Mesh",
}

def create_wankel_nodes():
    group_name = "Wankel_3D_Core"
    if group_name in bpy.data.node_groups:
        return bpy.data.node_groups[group_name]
        
    group = bpy.data.node_groups.new(group_name, 'GeometryNodeTree')
    itf = group.interface
    
    sockets = [
        ("Apex Count", 'NodeSocketInt', 3),
        ("Radius", 'NodeSocketFloat', 10.0),
        ("Eccentricity", 'NodeSocketFloat', 1.5),
        ("Face Bulge", 'NodeSocketFloat', 0.08),
        ("Apex Sharpness", 'NodeSocketFloat', 14),
        ("Groove Width", 'NodeSocketFloat', 0.04),
        ("Groove Depth", 'NodeSocketFloat', 0.7),
        ("Clearance", 'NodeSocketFloat', 0.447),
        ("Housing Height", 'NodeSocketFloat', 2.0),
        ("Rotor Height", 'NodeSocketFloat', 1.9),
        ("Housing Thickness", 'NodeSocketFloat', 3.0),
        ("Shaft Rotation", 'NodeSocketFloat', 0.0)
    ]
    
    for name, socket_type, default in sockets:
        s = itf.new_socket(name=name, in_out='INPUT', socket_type=socket_type)
        if hasattr(s, "default_value"): s.default_value = default
    itf.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    n, l = group.nodes, group.links
    for node in n: n.remove(node)
    inp = n.new('NodeGroupInput')
    out = n.new('NodeGroupOutput')

    h_inner = n.new('GeometryNodeCurvePrimitiveCircle'); h_inner.inputs[0].default_value = 512
    h_sp = n.new('GeometryNodeSplineParameter')
    h_tau = n.new('ShaderNodeMath'); h_tau.operation = 'MULTIPLY'; h_tau.inputs[1].default_value = 6.283185
    l.new(h_sp.outputs[0], h_tau.inputs[0])
    
    h_freq = n.new('ShaderNodeMath'); h_freq.operation = 'MULTIPLY'
    l.new(h_tau.outputs[0], h_freq.inputs[0]); l.new(inp.outputs[0], h_freq.inputs[1])

    hcx = n.new('ShaderNodeMath'); hcx.operation = 'COSINE'; l.new(h_tau.outputs[0], hcx.inputs[0])
    hsx = n.new('ShaderNodeMath'); hsx.operation = 'SINE';   l.new(h_tau.outputs[0], hsx.inputs[0])
    hcf = n.new('ShaderNodeMath'); hcf.operation = 'COSINE'; l.new(h_freq.outputs[0], hcf.inputs[0])
    hsf = n.new('ShaderNodeMath'); hsf.operation = 'SINE';   l.new(h_freq.outputs[0], hsf.inputs[0])

    hx = n.new('ShaderNodeMath'); hx.operation = 'ADD'
    hx1 = n.new('ShaderNodeMath'); hx1.operation = 'MULTIPLY'; l.new(inp.outputs[1], hx1.inputs[0]); l.new(hcx.outputs[0], hx1.inputs[1])
    hx2 = n.new('ShaderNodeMath'); hx2.operation = 'MULTIPLY'; l.new(inp.outputs[2], hx2.inputs[0]); l.new(hcf.outputs[0], hx2.inputs[1])
    l.new(hx1.outputs[0], hx.inputs[0]); l.new(hx2.outputs[0], hx.inputs[1])

    hy = n.new('ShaderNodeMath'); hy.operation = 'ADD'
    hy1 = n.new('ShaderNodeMath'); hy1.operation = 'MULTIPLY'; l.new(inp.outputs[1], hy1.inputs[0]); l.new(hsx.outputs[0], hy1.inputs[1])
    hy2 = n.new('ShaderNodeMath'); hy2.operation = 'MULTIPLY'; l.new(inp.outputs[2], hy2.inputs[0]); l.new(hsf.outputs[0], hy2.inputs[1])
    l.new(hy1.outputs[0], hy.inputs[0]); l.new(hy2.outputs[0], hy.inputs[1])

    h_set = n.new('GeometryNodeSetPosition')
    h_comb = n.new('ShaderNodeCombineXYZ'); l.new(hx.outputs[0], h_comb.inputs[0]); l.new(hy.outputs[0], h_comb.inputs[1])
    l.new(h_inner.outputs[0], h_set.inputs[0]); l.new(h_comb.outputs[0], h_set.inputs[2])

    h_outer = n.new('GeometryNodeCurvePrimitiveCircle'); h_outer.inputs[0].default_value = 128
    h_out_r = n.new('ShaderNodeMath'); h_out_r.operation = 'ADD'
    l.new(inp.outputs[1], h_out_r.inputs[0]); l.new(inp.outputs[10], h_out_r.inputs[1])
    l.new(h_out_r.outputs[0], h_outer.inputs[4])

    h_join = n.new('GeometryNodeJoinGeometry'); l.new(h_set.outputs[0], h_join.inputs[0]); l.new(h_outer.outputs[0], h_join.inputs[0])
    h_fill = n.new('GeometryNodeFillCurve'); l.new(h_join.outputs[0], h_fill.inputs[0])
    h_ext = n.new('GeometryNodeExtrudeMesh'); l.new(h_fill.outputs[0], h_ext.inputs[0]); l.new(inp.outputs[8], h_ext.inputs['Offset Scale'])

    r_dim = n.new('ShaderNodeMath'); r_dim.operation = 'SUBTRACT'; l.new(inp.outputs[1], r_dim.inputs[0]); l.new(inp.outputs[7], r_dim.inputs[1])
    r_circ = n.new('GeometryNodeCurvePrimitiveCircle'); r_circ.inputs[0].default_value = 1024
    r_sp = n.new('GeometryNodeSplineParameter')
    r_tau = n.new('ShaderNodeMath'); r_tau.operation = 'MULTIPLY'; r_tau.inputs[1].default_value = 6.283185; l.new(r_sp.outputs[0], r_tau.inputs[0])

    sec = n.new('ShaderNodeMath'); sec.operation = 'DIVIDE'; sec.inputs[0].default_value = 6.283185; l.new(inp.outputs[0], sec.inputs[1])
    half_sec = n.new('ShaderNodeMath'); half_sec.operation = 'DIVIDE'; half_sec.inputs[1].default_value = 2.0; l.new(sec.outputs[0], half_sec.inputs[0])
    a_sh = n.new('ShaderNodeMath'); a_sh.operation = 'ADD'; l.new(r_tau.outputs[0], a_sh.inputs[0]); l.new(half_sec.outputs[0], a_sh.inputs[1])
    mod_v = n.new('ShaderNodeMath'); mod_v.operation = 'MODULO'; l.new(a_sh.outputs[0], mod_v.inputs[0]); l.new(sec.outputs[0], mod_v.inputs[1])
    dist_v = n.new('ShaderNodeMath'); dist_v.operation = 'SUBTRACT'; l.new(mod_v.outputs[0], dist_v.inputs[0]); l.new(half_sec.outputs[0], dist_v.inputs[1])
    abs_v = n.new('ShaderNodeMath'); abs_v.operation = 'ABSOLUTE'; l.new(dist_v.outputs[0], abs_v.inputs[0])
    g_m = n.new('ShaderNodeMath'); g_m.operation = 'LESS_THAN'; l.new(abs_v.outputs[0], g_m.inputs[0]); l.new(inp.outputs[5], g_m.inputs[1])
    g_d = n.new('ShaderNodeMath'); g_d.operation = 'MULTIPLY'; l.new(g_m.outputs[0], g_d.inputs[0]); l.new(inp.outputs[6], g_d.inputs[1])

    r_nm1 = n.new('ShaderNodeMath'); r_nm1.operation = 'SUBTRACT'; r_nm1.inputs[1].default_value = 1.0; l.new(inp.outputs[0], r_nm1.inputs[0])
    r_f = n.new('ShaderNodeMath'); r_f.operation = 'MULTIPLY'; l.new(r_tau.outputs[0], r_f.inputs[0]); l.new(r_nm1.outputs[0], r_f.inputs[1])
    rcf = n.new('ShaderNodeMath'); rcf.operation = 'COSINE'; l.new(r_f.outputs[0], rcf.inputs[0])
    rsf = n.new('ShaderNodeMath'); rsf.operation = 'SINE';   l.new(r_f.outputs[0], rsf.inputs[0])

    rb_m = n.new('ShaderNodeMath'); rb_m.operation = 'SUBTRACT'; l.new(r_dim.outputs[0], rb_m.inputs[0]); l.new(inp.outputs[2], rb_m.inputs[1])
    rl_m = n.new('ShaderNodeMath'); rl_m.operation = 'MULTIPLY'; l.new(inp.outputs[2], rl_m.inputs[0]); l.new(inp.outputs[3], rl_m.inputs[1])
    rc1 = n.new('ShaderNodeMath'); rc1.operation = 'COSINE'; l.new(r_tau.outputs[0], rc1.inputs[0])
    rs1 = n.new('ShaderNodeMath'); rs1.operation = 'SINE';   l.new(r_tau.outputs[0], rs1.inputs[0])

    rx_a = n.new('ShaderNodeMath'); rx_a.operation = 'MULTIPLY'; l.new(rb_m.outputs[0], rx_a.inputs[0]); l.new(rc1.outputs[0], rx_a.inputs[1])
    rx_bm = n.new('ShaderNodeMath'); rx_bm.operation = 'MULTIPLY'; l.new(rcf.outputs[0], rx_bm.inputs[0]); l.new(inp.outputs[4], rx_bm.inputs[1])
    rx_b = n.new('ShaderNodeMath'); rx_b.operation = 'MULTIPLY'; l.new(rl_m.outputs[0], rx_b.inputs[0]); l.new(rx_bm.outputs[0], rx_b.inputs[1])
    rx_t = n.new('ShaderNodeMath'); rx_t.operation = 'ADD'; l.new(rx_a.outputs[0], rx_t.inputs[0]); l.new(rx_b.outputs[0], rx_t.inputs[1])

    ry_a = n.new('ShaderNodeMath'); ry_a.operation = 'MULTIPLY'; l.new(rb_m.outputs[0], ry_a.inputs[0]); l.new(rs1.outputs[0], ry_a.inputs[1])
    ry_bm = n.new('ShaderNodeMath'); ry_bm.operation = 'MULTIPLY'; l.new(rsf.outputs[0], ry_bm.inputs[0]); l.new(inp.outputs[4], ry_bm.inputs[1])
    ry_b = n.new('ShaderNodeMath'); ry_b.operation = 'MULTIPLY'; l.new(rl_m.outputs[0], ry_b.inputs[0]); l.new(ry_bm.outputs[0], ry_b.inputs[1])
    ry_t = n.new('ShaderNodeMath'); ry_t.operation = 'SUBTRACT'; l.new(ry_a.outputs[0], ry_t.inputs[0]); l.new(ry_b.outputs[0], ry_t.inputs[1])

    r_coord = n.new('ShaderNodeCombineXYZ'); l.new(rx_t.outputs[0], r_coord.inputs[0]); l.new(ry_t.outputs[0], r_coord.inputs[1])
    
    r_norm = n.new('ShaderNodeVectorMath'); r_norm.operation = 'NORMALIZE'; l.new(r_coord.outputs[0], r_norm.inputs[0])
    r_scale = n.new('ShaderNodeVectorMath'); r_scale.operation = 'SCALE'; l.new(r_norm.outputs[0], r_scale.inputs[0]); l.new(g_d.outputs[0], r_scale.inputs[3])
    r_final_pos = n.new('ShaderNodeVectorMath'); r_final_pos.operation = 'SUBTRACT'; l.new(r_coord.outputs[0], r_final_pos.inputs[0]); l.new(r_scale.outputs[0], r_final_pos.inputs[1])

    r_set = n.new('GeometryNodeSetPosition'); l.new(r_circ.outputs[0], r_set.inputs[0]); l.new(r_final_pos.outputs[0], r_set.inputs[2])
    r_fill = n.new('GeometryNodeFillCurve'); l.new(r_set.outputs[0], r_fill.inputs[0])
    r_ext = n.new('GeometryNodeExtrudeMesh'); l.new(r_fill.outputs[0], r_ext.inputs[0]); l.new(inp.outputs[9], r_ext.inputs['Offset Scale'])

    r_spin = n.new('GeometryNodeTransform')
    spin_math = n.new('ShaderNodeMath'); spin_math.operation = 'DIVIDE'; l.new(inp.outputs[11], spin_math.inputs[0]); l.new(inp.outputs[0], spin_math.inputs[1])
    spin_rot = n.new('ShaderNodeCombineXYZ'); l.new(spin_math.outputs[0], spin_rot.inputs[2])
    l.new(spin_rot.outputs[0], r_spin.inputs['Rotation'])

    r_orbit = n.new('GeometryNodeTransform')
    o_cos = n.new('ShaderNodeMath'); o_cos.operation = 'COSINE'; l.new(inp.outputs[11], o_cos.inputs[0])
    o_sin = n.new('ShaderNodeMath'); o_sin.operation = 'SINE';   l.new(inp.outputs[11], o_sin.inputs[0])
    ox = n.new('ShaderNodeMath'); ox.operation = 'MULTIPLY'; l.new(inp.outputs[2], ox.inputs[0]); l.new(o_cos.outputs[0], ox.inputs[1])
    oy = n.new('ShaderNodeMath'); oy.operation = 'MULTIPLY'; l.new(inp.outputs[2], oy.inputs[0]); l.new(o_sin.outputs[0], oy.inputs[1])
    o_loc = n.new('ShaderNodeCombineXYZ'); l.new(ox.outputs[0], o_loc.inputs[0]); l.new(oy.outputs[0], o_loc.inputs[1])
    l.new(o_loc.outputs[0], r_orbit.inputs['Translation'])

    join = n.new('GeometryNodeJoinGeometry')
    l.new(h_ext.outputs[0], join.inputs[0]); l.new(r_ext.outputs[0], r_spin.inputs[0])
    l.new(r_spin.outputs[0], r_orbit.inputs[0]); l.new(r_orbit.outputs[0], join.inputs[0])
    l.new(join.outputs[0], out.inputs[0])
    
    return group

class MESH_OT_wankel_gen_pro(bpy.types.Operator):
    bl_idname = "mesh.wankel_gen_pro"
    bl_label = "Add Wankel Engine"
    bl_options = {'REGISTER', 'UNDO'}

    apex_count: IntProperty(name="Apex Count", default=3, min=2)
    radius: FloatProperty(name="Radius", default=10.0)
    eccentricity: FloatProperty(name="Eccentricity", default=1.5)
    bulge: FloatProperty(name="Face Bulge", default=0.08)
    sharpness: FloatProperty(name="Apex Sharpness", default=14)
    g_width: FloatProperty(name="Groove Width", default=0.04)
    g_depth: FloatProperty(name="Groove Depth", default=0.7)
    clearance: FloatProperty(name="Clearance", default=0.447)
    h_height: FloatProperty(name="Housing Height", default=2.0)
    r_height: FloatProperty(name="Rotor Height", default=1.9)
    h_thick: FloatProperty(name="Housing Thickness", default=3.0)
    rotation: FloatProperty(name="Shaft Rotation", default=0.0)
    
    reset_to_defaults: BoolProperty(name="Reset Values", default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "apex_count")
        
        box = layout.box()
        box.label(text="Rotor & Housing", icon='MESH_ICOSPHERE')
        box.prop(self, "radius")
        box.prop(self, "eccentricity")
        box.prop(self, "bulge")
        box.prop(self, "sharpness")
        box.prop(self, "clearance")

        box = layout.box()
        box.label(text="Grooves", icon='MOD_EDGESPLIT')
        box.prop(self, "g_width")
        box.prop(self, "g_depth")

        box = layout.box()
        box.label(text="Dimensions", icon='MOD_SOLIDIFY')
        box.prop(self, "h_height")
        box.prop(self, "r_height")
        box.prop(self, "h_thick")
        
        layout.prop(self, "rotation")
        layout.separator()
        layout.prop(self, "reset_to_defaults", toggle=True, icon='LOOP_BACK')

    def execute(self, context):
        if self.reset_to_defaults:
            self.apex_count = 3
            self.radius = 10.0
            self.eccentricity = 1.5
            self.bulge = 0.08
            self.sharpness = 14.0
            self.g_width = 0.04
            self.g_depth = 0.7
            self.clearance = 0.447
            self.h_height = 2.0
            self.r_height = 1.9
            self.h_thick = 3.0
            self.rotation = 0.0
            self.reset_to_defaults = False

        mesh = bpy.data.meshes.new("WankelEngine")
        obj = bpy.data.objects.new("WankelEngine", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        
        mod = obj.modifiers.new(name="Wankel_Core", type='NODES')
        nt = create_wankel_nodes()
        mod.node_group = nt
        
        props = {
            "Apex Count": self.apex_count, "Radius": self.radius,
            "Eccentricity": self.eccentricity, "Face Bulge": self.bulge,
            "Apex Sharpness": self.sharpness, "Groove Width": self.g_width,
            "Groove Depth": self.g_depth, "Clearance": self.clearance,
            "Housing Height": self.h_height, "Rotor Height": self.r_height,
            "Housing Thickness": self.h_thick, "Shaft Rotation": self.rotation
        }
        
        itf_items = nt.interface.items_tree if hasattr(nt.interface, "items_tree") else nt.interface.items
        for item in itf_items:
            if item.name in props:
                mod[item.identifier] = props[item.name]

        obj.location = context.scene.cursor.location
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MESH_OT_wankel_gen_pro.bl_idname, icon='GEOMETRY_NODES')

def register():
    bpy.utils.register_class(MESH_OT_wankel_gen_pro)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(MESH_OT_wankel_gen_pro)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()