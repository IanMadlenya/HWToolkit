from hwt.hdlObjects.variables import SignalItem
from hwt.serializer.generic.value import GenericSerializer_Value
from hwt.synthesizer.param import Param, evalParam
from hwt.serializer.serializerClases.indent import getIndent


class SimModelSerializer_value(GenericSerializer_Value):

    @classmethod
    def Bits_valAsHdl(cls, dtype, val, ctx):
        return "BitsVal(%d, simBitsT(%d, %r), %d)" % (
            val.val, dtype.bit_length(), dtype.signed, val.vldMask)

    @classmethod
    def SignalItem(cls, si, ctx, declaration=False):
        if declaration:
            raise NotImplementedError()
        else:
            if isinstance(si, Param):
                return cls.Value(evalParam(si), ctx)
            if isinstance(si, SignalItem) and si._const:
                return cls.Value(si._val, ctx)
            if si.hidden and hasattr(si, "origin"):
                return cls.asHdl(si.origin, ctx)
            else:
                return "self.%s._oldVal" % si.name

    @classmethod
    def Integer_valAsHdl(cls, t, i, ctx):
        if i.vldMask:
            return "simHInt(%d)" % i.val
        else:
            return "simHInt(None)"

    @classmethod
    def Dict_valAsHdl(cls, val, ctx):
        sep = (",\n" + getIndent(ctx.indent + 1))

        def sItem(i):
            k, v = i
            return "%d: %s" % (k, cls.Value(v, ctx))

        return "{%s}" % sep.join(map(sItem, val.items()))

    @classmethod
    def HArrayValAsHdl(cls, t, val, ctx):
        return "HArrayVal(%s, %s, %d)" % (
                cls.Dict_valAsHdl(val.val, ctx),
                cls.HdlType(t, ctx),
                val.vldMask)

    @classmethod
    def Slice_valAsHdl(cls, t, val, ctx):
        return "SliceVal((simHInt(%d), simHInt(%d)), SLICE, %d)" % (
                    evalParam(val.val[0]).val,
                    evalParam(val.val[1]).val,
                    val.vldMask)

    @classmethod
    def Enum_valAsHdl(cls, t, val, ctx):
        return "self.%s.%s" % (t.name, val.val)

    @classmethod
    def condAsHdl(cls, cond, ctx):
        cond = list(cond)
        return "%s" % (",".join(map(lambda x: cls.asHdl(x, ctx), cond)))
