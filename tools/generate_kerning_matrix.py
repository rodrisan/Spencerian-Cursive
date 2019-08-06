import fontforge

final_forms = {'a': ['a', 'd', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'r', 't', 'u', 'x'],
               'c': ['c', 'e'],
               'b': ['b', 'v', 'w']}
pairs = set()

my_type = fontforge.open('../sources/SpencerianCursive.sfd')
my_type.selection.all()

for glyph in my_type:

    ccmp_lookup_lovercase = my_type[glyph].getPosSub("'ccmp' [Lowercase]")
    ccmp_lookup_uppercase = my_type[glyph].getPosSub("'ccmp' [Uppercase]")
    ccmp_lookup_s = my_type[glyph].getPosSub("'ccmp' [s] + *")

    ccmp_lookup = tuple()

    if len(ccmp_lookup_lovercase):
            ccmp_lookup = ccmp_lookup_lovercase
    elif len(ccmp_lookup_uppercase):
            ccmp_lookup = ccmp_lookup_uppercase
    elif len(ccmp_lookup_s):
            ccmp_lookup=ccmp_lookup_s

    if len(ccmp_lookup) == 1:
        # becaue it like (((x,x),(x,x)),)
        ccmp_lookup_refined=ccmp_lookup[0][2:]
        pairs=pairs | {(ccmp_lookup_refined[x], ccmp_lookup_refined[x+1])
                         for x in range(len(ccmp_lookup_refined)-1)}


print(len(pairs))
