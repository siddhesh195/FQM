

def modify_Touch_Store_init(touch_screen_stings):
    """Modify Touch Store initialization settings of the fly."""
    try:
        touch_screen_stings.title = "Please select your Option"
    except Exception as e:
        log_error(e)

    return touch_screen_stings

def modify_Aliases_init(aliases_settings):
    aliases_settings.office= "counter"
    return aliases_settings
