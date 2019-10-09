# General Constants
capitals = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
            'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}

lowercase = {x.lower() for x in capitals}

# Type Constants

em_size = 4096

# My Custom Constants

# Initial and final parts group, for example initial part of 'b' when attach to a preciding glyp is member of 'b'
#   and initial part of 'h' when attach to a preciding glyph is member of 'b' ,
initial_groups={
    'a':['a','d','g','q'],
    'b':['b','f','h','k','l'],
    'c':['c'],
    'e':['e'],
    'i':['i','j','u','t','w'],
    'm':['m','n','v','x','y','z'],
    'o':['o'],
    'p':['p','r','s']
}
# final_groups={If I need it will add it in the future}


capitals_ccmp={'A','H','J','K','L','M','N','Q','R','U','W','X','Y','Z'}
capitals_non_ccmp=capitals.union(capitals_ccmp)

    
   