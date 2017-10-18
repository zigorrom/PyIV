##def enum(*enumerated):
##    enums = dict(zip(enumerated,range(len(enumerated))))
##    enums["names"] = enumerated
##    return type('enum',(),enums)()
##
##
##a = enum("asdad","a1")
##print(type(a))


def enum( *enumerated,name_prefix = ""):
    g = [name_prefix+e for e in enumerated]
    i = range(len(enumerated))
    enums = dict(zip(g,i))
    enums["indexes"] = tuple(i)
    enums["names"] = tuple(g)
    enums["values"] = enumerated
    enums["default_value"] = enumerated[0]
    enums["default_name"] = enums["names"][0]
##    enums["__init__"] = lambda self:  #init
    enums["__getitem__"] = lambda self, i: self.values[i] #getitem
##    print(enums)
    return type('enum',(),enums)()


def main():
    AI_CHANNELS = enum("101","102","103","104",name_prefix = "AI_")
    print(AI_CHANNELS.indexes)
    print(AI_CHANNELS.values)
    print(AI_CHANNELS.AI_104)
    print(AI_CHANNELS[AI_CHANNELS.AI_104])
    print(AI_CHANNELS.default_value)
    print(AI_CHANNELS.default_name)

if __name__== "__main__":
    main()
