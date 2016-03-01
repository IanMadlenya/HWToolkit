#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from vhdl_toolkit.hdlObjects.reference import VhdlRef 
from vhdl_toolkit.nonRedefDict import NonRedefDict
from vhdl_toolkit.types import VHDLType, Unconstrained
from vhdl_toolkit.hdlObjects.entity import Entity
from vhdl_toolkit.hdlObjects.architecture import Architecture


class RequireImportErr(Exception):
    """Is raised when program can not approach without importing specific reference"""
    def __init__(self, reference):
        super(RequireImportErr, self).__init__()
        self.reference = reference
        self.fileName = None
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.fileName:
            fileName = 'file %s' % self.fileName
        else:
            fileName = '' 
        return "<RequireImportErr %s require to import %s first>" % (fileName, str(self.reference))
    
class HDLParseErr(Exception):
    pass

class HDLCtx(NonRedefDict):
    """
    Context of hdl, contains all hdl objects hidden behind references
    """
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        
        self.entities = NonRedefDict()
        self.architectures = []
        self.packages = NonRedefDict()
        
    def importLibFromGlobal(self, ref):
        """
        Import for example lib.package to local context
        """
        top = self
        while top.parent is not None:
            top = top.parent
        try:
            toImport = top
            for n in ref.names:
                toImport = toImport[n]
            if ref.all:
                for n in toImport:
                    self[n] = toImport[n]
            else:
                raise NotImplementedError()
        except KeyError:
            raise RequireImportErr(ref)
        
    def lookupGlobal(self, ref):
        """
        lookup reference upside down
        """
        p = self
        n = ref.names[0]  # [TODO]
        while p.parent is not None:
            p = p.parent
        if p is None:
            raise RequireImportErr(ref)
        try:
            for n in ref.names:
                p = p[n]
            return p
        except KeyError:
            raise RequireImportErr(ref)
        
    def lookupLocal(self, locRef):
        """[DEPRECATED]
        lookup only in this context
        """
        p = self
        n = locRef.names[-1]  # [TODO]
        while p is not None:
            try:
                return p[n]
            except KeyError:
                p = p.parent
        
        raise Exception("Identificator %s not defined" % n)
    
    def insertObj(self, obj):
        """
        insert Entity, PackageHeader or Architecture in this context
        """
        from vhdl_toolkit.hdlObjects.package import PackageHeader
        if isinstance(obj, Entity):
            n = obj.name.lower()
            self.entities[n] = obj
            self.insert(VhdlRef([n]), obj)
        elif isinstance(obj, PackageHeader):
            n = obj.name.lower()
            self.packages[n] = obj
            self.insert(VhdlRef([n]), obj)
        elif isinstance(obj, Architecture):
            self.architectures.append(obj)
        else:
            raise NotImplementedError()
    
    def insert(self, ref, val):
        """
        insert any reference
        """
        c = self
        # for all names create or reuse hiearchy
        for n in ref.names[:-1]:
            c = c.setdefault(n, HDLCtx(n, c))
        # store actual object at the end of hierarhy
        c[ref.names[-1]] = val
    
    def copyFrom(self, other):
        """
        copy everything from other HdlContext
        """
        for _, v in other.items():
            self.insertObj(v)
        self.parent = other.parent
        self.name = other.name
               
    def __str__(self):
        return "\n".join([
                    "\n".join([str(e) for _, e in self.entities.items()]),
                    "\n".join([str(a) for a in self.architectures]),
                    "\n".join([str(p) for p in self.packages]),
                    ])

def mkType(name, width, minimum=None):
    t = VHDLType()
    t.name = name
    t.width = width
    t.min = minimum
    return t

class FakeStd_logic_1164():
    """mock of Std_logic_1164 from vhdl"""
    std_logic_vector = mkType("std_logic_vector", Unconstrained)
    std_logic_vector_ref = VhdlRef(["ieee", "std_logic_1164", "std_logic_vector"])
    std_logic = mkType("std_logic", 1)
    std_logic_ref = VhdlRef(["ieee", "std_logic_1164", "std_logic"])
    numeric_std_ref = VhdlRef(["ieee", "numeric_std"])
    numeric_std = HDLCtx('numeric_std', None) 
        

class BaseVhdlContext():
    integer = mkType("integer", int)
    positive = mkType("positive", int, 1)
    natural = mkType("natural", int, 0)
    boolean = mkType("boolean", bool)
    string = mkType("string", str)
    float = mkType("float", float)
   
    @classmethod
    def importFakeLibs(cls, ctx):
        BaseVhdlContext.importFakeIEEELib(ctx)

    @classmethod 
    def importFakeIEEELib(cls, ctx):
        ctx.insert(FakeStd_logic_1164.std_logic_vector_ref, FakeStd_logic_1164.std_logic_vector)
        ctx.insert(FakeStd_logic_1164.std_logic_ref, FakeStd_logic_1164.std_logic)
        ctx.insert(VhdlRef(['ieee', 'std_logic_unsigned', 'CONV_INTEGER']), None)
        ctx.insert(VhdlRef(['ieee', 'std_logic_arith', 'IS_SIGNED']), None)
        ctx.insert(FakeStd_logic_1164.numeric_std_ref, FakeStd_logic_1164.numeric_std)
    
    @classmethod
    def getBaseCtx(cls):
        d = HDLCtx(None, None)
        for n in [cls.integer, cls.positive, cls.natural,
                   cls.boolean, cls.string, cls.float]:
            d[n.name] = n
        d['true'] = True
        d['false'] = False
        return d


