I_IDLE = 1
I_WORK = 2
I_HANDLERA = 3
I_HANDLERB = 4
I_DEVA = 5
I_DEVB = 6

K_DEV = 1000
K_WORK = 1001


BUFSIZE = 4
BUFSIZE_RANGE = [0, 1, 2, 3]

class Packet:
    def append_to(self, lst):
        self.link = None
        if lst is None:
            return self
        p = lst
        next = p.link
        while next is not None:
            p = next
            next = p.link
        p.link = self
        return lst

    def __init__(self, l, i, k):
        self.link = l
        self.ident = i
        self.kind = k
        self.daturm = 0
        self.data = [0,0,0,0]

class TaskRec:
    pass

class DeviceTaskRec(TaskRec):

    def __init__(self):
        self.pending = None

class IdleTaskRec(TaskRec):

    def __init__(self):
        self.control = 1
        self.count = 10000

class HandlerTaskRec(TaskRec):

    def deviceInAdd(self, p):
        x = p.append_to(self.device_in)
        self.device_in = x
        return x

    def workInAdd(self, p):
        x = p.append_to(self.work_in)
        self.work_in = x
        return x

    def __init__(self):
        self.work_in = None
        self.device_in = None

class WorkTaskRec(TaskRec):

    def __init__(self):
        self.destination = I_HANDLERA
        self.count = 0

class TaskState:

    def isWaitingWithPacket(self):
        return self.packet_pending and self.task_waiting and not self.task_holding

    def isTaskHoldingOrWaiting(self):
        return self.task_holding or (not self.packet_pending and self.task_waiting)

    def isTaskHolding(self):
        return self.task_holding

    def isTaskWaiting(self):
        return self.task_waiting

    def isPacketPending(self):
        return self.packet_pending

    def waitingWithPacket(self):
        self.packet_pending = True
        self.task_waiting = True
        self.task_holding = False
        return self

    def running(self):
        self.packet_pending = False
        self.task_waiting = False
        self.task_holding = False
        return self

    def waiting(self):
        self.packet_pending = False
        self.task_waiting = True
        self.task_holding = False
        return self

    def packetPending(self):
        self.packet_pending = True
        self.task_waiting = False
        self.task_holding = False
        return self

    def __init__(self):
        self.packet_pending = True
        self.task_waiting = False
        self.task_holding = False

TASKTABSIZE = 10

layout = 0;


def trace(a):
    layout = layout - 1
    if layout <= 0:
        print("\n")
        layout = 50
    print "%s" % a

class TaskWorkArea:

    def reset(self):
        self.taskTab = []
        for i in xrange(0, TASKTABSIZE):
            self.taskTab.append(None)
        self.taskList = None
        self.holdCount = 0
        self.qpktCount = 0

    def __init__(self):
        self.reset()

class Task (TaskState):

    def findtcb(self, id):
        t = taskWorkArea.taskTab[id]
        if t is None:
            raise Exception("Bad task id")
        return t

    def qpkt(self, pkt):
        t = self.findtcb(pkt.ident)
        taskWorkArea.qpktCount += 1
        pkt.link = None
        pkt.ident = self.ident
        return t.addPacket(pkt, self)

    def release(self, i):
        t = self.findtcb(i)
        t.task_holding = False
        if t.priority > self.priority:
            return t
        else:
            return self

    def hold(self):
        taskWorkArea.holdCount += 1
        self.task_holding = True
        return self.link

    def waitTask(self):
        self.task_waiting = True
        return self

    def runTasks(self):
        if self.isWaitingWithPacket():
            msg = self.input
            self.input = msg.link
            if self.input is None:
                self.running()
            else:
                self.packetPending()
        else:
            msg = None
        return self.fn(msg, self.handle)

    def addPacket(self, p, old):
        if self.input is None:
            self.input = p
            self.packet_pending = True
            if self.priority > old.priority:
                return self
        else:
            p.append_to(self.input)
        return old

    def __init__(self, i, p, w, initialState, r):
        self.link = taskWorkArea.taskList
        self.ident = i
        self.priority = p
        self.input = w

        self.packet_pending = initialState.isPacketPending()
        self.task_waiting = initialState.isTaskWaiting()
        self.task_holding = initialState.isTaskHolding()

        self.handle = r

        taskWorkArea.taskList = self
        taskWorkArea.taskTab[i] = self

class DeviceTask(Task):

    def fn(self, pkt, r):
        d = r
        if not isinstance(d, DeviceTaskRec):
            raise Exception("not a DeviceTaskRec")
        if not pkt:
            pkt = d.pending
            if pkt is None:
                return self.waitTask()
            d.pending = None
            return self.qpkt(pkt)
        d.pending = pkt
        if TRACING:
            trace(pkt.datum)
        return self.hold()

class HandlerTask(Task):

    def fn(self, pkt, r):
        h = r
        if not isinstance(h, HandlerTaskRec):
            raise Exception("not a HandlerTaskRec")
        if pkt is not None:
            if pkt.kind == K_WORK:
                h.workInAdd(pkt)
            else:
                h.deviceInAdd(pkt)
        work = h.work_in
        if work is None:
            return self.waitTask()
        count = work.datum
        if count >= BUFSIZE:
            h.work_in = work.link
            return self.qpkt(work)

        dev = h.device_in
        if dev is None:
            return self.waitTask()

        h.device_in = dev.link
        dev.datum = work.data[count]
        work.datum = count + 1
        return self.qpkt(dev)

class IdleTask(Task):

    def fn(self, pkt, r):
        i = r
        if not isinstance(i, IdleTaskRec):
            raise Exception("not an IdleTaskRec")
        i.count -= 1
        if i.count == 0:
            return self.hold()
        elif (i.control & 1) == 0:
            i.control = i.control / 2
            return self.release(I_DEVA)
        i.control = (i.control / 2) ^ 53256 # 0xd008
        return self.release(I_DEVB)

class WorkTask(Task):

    def fn(self, pkt, r):
        w = r
        if pkt is None:
            return self.waitTask()

        if w.destination == I_HANDLERA:
            dest = I_HANDLERB
        else:
            dest = I_HANDLERA

        w.destination = dest
        pkt.ident = dest
        pkt.datum = 0

        pkt.data[3] = 1
        for i in xrange(0, BUFSIZE):
            w.count += 1
            if w.count > 26:
                w.count = 1
            temp = ord("A") + w.count - 1
            pkt.data[i] = ord("A") + w.count - 1

        return self.qpkt(pkt)

TRACING = 0


def schedule():
    t = taskWorkArea.taskList
    while t is not None:
        pkt = None
        if TRACING:
            print "tcp = %d" % (t.indent)
        if t.isTaskHoldingOrWaiting():
            t = t.link
        else:
            if TRACING:
                trace(chr(ord("0") + t.indent))
            t = t.runTasks()

class Richards:

    def run(self, iterations):
        for i in xrange(0, iterations):
            taskWorkArea.reset()
            task_state = TaskState()
            IdleTask(I_IDLE, 1, 10000, task_state.running(), IdleTaskRec())

            wkq = Packet(None, 0, K_WORK)
            wkq = Packet(wkq, 0, K_WORK)
            task_state = TaskState()
            WorkTask(I_WORK, 1000, wkq, task_state.waitingWithPacket(), WorkTaskRec())

            wkq = Packet(None, I_DEVA, K_DEV)
            wkq = Packet(wkq, I_DEVA, K_DEV)
            wkq = Packet(wkq, I_DEVA, K_DEV)
            task_state = TaskState()
            HandlerTask(I_HANDLERA, 2000, wkq, task_state.waitingWithPacket(), HandlerTaskRec())

            wkq = Packet(None, I_DEVB, K_DEV)
            wkq = Packet(wkq, I_DEVB, K_DEV)
            wkq = Packet(wkq, I_DEVB, K_DEV)
            task_state = TaskState()
            HandlerTask(I_HANDLERB, 3000, wkq, task_state.waitingWithPacket(), HandlerTaskRec())

            wkq = None

            task_state = TaskState()
            DeviceTask(I_DEVA, 4000, wkq, task_state.waiting(), DeviceTaskRec())
            task_state = TaskState()
            DeviceTask(I_DEVB, 5000, wkq, task_state.waiting(), DeviceTaskRec())

            schedule()

            if not (taskWorkArea.holdCount == 9297 and taskWorkArea.qpktCount == 23246):
                return False
        return True

taskWorkArea = None

def run_iter(n):
    global taskWorkArea
    taskWorkArea = TaskWorkArea()
    r = Richards()
    res = r.run(n)
    assert res

run_iter(10)
