from fontTools.ttLib import TTFont

class Lookups:
    def __init__(self,ttf_path):
        """
        ttf_path is a path to a ttf font like './.temp/font.ttf'
        """

        # Opening the target font in the '.temp' directory
        type_face = TTFont(ttf_path)
        # Retrive GSUB lookups from the GSUB table
        self.gsub_lookups = type_face['GSUB'].table.LookupList.Lookup

        # Retrive LookupTypes, including LookupType 1, LookupType 2 and LookupType 6
        self.lookupType1s, self.lookupType2s, self.lookupType6s = [], [], []

        for lookup in self.gsub_lookups:
            if lookup.LookupType == 1:
                self.lookupType1s.append(lookup)
            elif lookup.LookupType == 2:
                self.lookupType2s.append(lookup)
            elif lookup.LookupType == 6:
                self.lookupType6s.append(lookup)


        # In order to know more about GSUB lookup types visit: https://docs.microsoft.com/en-us/typography/opentype/spec/gsub
        # The Follow tree is a list of information base on above linked referernce that I need for above codes:
        #   LookupType 1(Single Substitution Subtable)
        #   LookupType 2(Multiple Substitution Subtable)
        #   LookupType 6(Chaining Contextual Substitution Subtable)
        #       Format1(Simple Glyph Contexts)
        #       Format2(Class-Base Glyph Contexts)
        #       Format3(Coverage-Base Glyph Contexts)