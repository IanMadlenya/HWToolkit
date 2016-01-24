from vhdl_toolkit.formater import formatVhdl
from vhdl_toolkit.synthetisator.rtlLevel.context import Context


if __name__ == "__main__":
    width = 8
  
    c = Context("simpleRegister")
    s_out = c.sig("s_out", 8)
    s_in = c.sig("s_in", 8)
        
    clk = c.sig("clk")
    syncRst = c.sig("rst")
    val = c.sig("val", width, clk, syncRst, 0)
    val.assignFrom(s_in)
    s_out.assignFrom(val)
    
    interf = [clk, syncRst, s_in, s_out]
    
    for o in c.synthetize(interf):
            print(formatVhdl(str(o)))

    
