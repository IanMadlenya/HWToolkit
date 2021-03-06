from hwt.hdl.hdlObject import HdlObject


class HWProcess(HdlObject):
    """
    Hdl process container

    :ivar name: name used as id in target HDL
    :ivar statements: list of statements in body of process
    :ivar sensitivityList: set of RtlSignals or event operators which
        are describing when should this process be revevaluated
    :ivar inputs: all input signals for this process
    :ivar outputs: all output signals for this process
    :note: HWProcess do not have to be process in target HDL, for example
        simple process which contains only unconditional assignment will
        be rendered just as assignment
    """

    def __init__(self, name, statements, sensitivityList, inputs, outputs):
        self.name = name
        self.statements = statements
        self.sensitivityList = sensitivityList
        self.inputs = inputs
        self.outputs = outputs
