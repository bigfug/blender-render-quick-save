bl_info = {
    "name": "Quick Save",
    "author": "Alex May",
    "description": "Save the current render to a predefined directory with a unique filename",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "wiki_url": "https://github.com/bigfug/blender-render-quick-save/wiki",
    "tracker_url": "https://github.com/bigfug/blender-render-quick-save/issues",
    "location": "Render > Render Quick Save",
    "category": "Render"
}

import bpy
import os
import datetime

class RenderQuickSavePreferences( bpy.types.AddonPreferences ):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    output_dir: bpy.props.StringProperty(
        name = "Path",
        description = "Output path where images will be saved",
        subtype = "DIR_PATH",
        default = '/tmp'
    )
        
    output_format: bpy.props.StringProperty(
        name = "Format",
        default = '%Y-%m-%d.%%04d.jpg'
    )

    def draw( self, context ):
        layout = self.layout
        layout.label( text = "Renders will be quick saved to the output path. The filename will be passed through strftime() first, and then substitute a unique id" )
        layout.prop( self, "output_dir" )
        layout.prop( self, "output_format" )

class RenderQuickSave( bpy.types.Operator ):
    """Render Quick Save"""
    bl_idname = "render.quick_save"
    bl_label = "Render Quick Save"
    bl_options = { 'REGISTER', 'UNDO' }

    output_id = 0
        
    def execute( self, context ):
        preferences = context.preferences
        addon_prefs = preferences.addons[ __name__ ].preferences

        im = bpy.data.images[ 'Render Result' ]
        
        if not im.has_data:
            self.report( { 'WARNING' }, "Render has no data" )
        else:
            # do the time format substitution
            
            date_now = datetime.datetime.now()
            
            output_format = date_now.strftime( addon_prefs.output_format )

            if not output_format.find( '%' ):           
                self.report( { 'ERROR' }, "Quick Save format string invalid" )
            else:
                while True:
                    # increment the id
                    
                    self.output_id += 1
                                    
                    fp = output_format % self.output_id
                    
                    # create the full file path
                    
                    fp = os.path.join( addon_prefs.output_dir, ( fp ) )
                    
                    if not os.path.exists( fp ):
                        break
                
                im.save_render( fp )

                self.report( { 'INFO' }, "Saved render to " + fp )
        
        return { 'FINISHED' }

def menu_func( self, context ):
    self.layout.operator( RenderQuickSave.bl_idname )

# store keymaps here to access after registration
addon_keymaps = []

def register():
    bpy.utils.register_class( RenderQuickSavePreferences )
    bpy.utils.register_class( RenderQuickSave )
    
    bpy.types.TOPBAR_MT_render.append( menu_func )
    
    wm = bpy.context.window_manager

    kc = wm.keyconfigs.addon
    
    if kc:
        km = wm.keyconfigs.addon.keymaps.new( name = 'Render Quick Save', space_type = 'EMPTY' )
        
        kmi = km.keymap_items.new( RenderQuickSave.bl_idname, 'F12', 'PRESS', ctrl = True, shift = True )
        
        kmi.active = True
        
        addon_keymaps.append( ( km, kmi ) )

def unregister():
    bpy.types.TOPBAR_MT_render.remove( menu_func )

    for km, kmi in addon_keymaps:
        km.keymap_items.remove( kmi )
        
    addon_keymaps.clear()

    bpy.utils.unregister_class( RenderQuickSave )
    bpy.utils.unregister_class( RenderQuickSavePreferences )

if __name__ == "__main__":
    register()
    
